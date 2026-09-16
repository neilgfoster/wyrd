"""Commit-back path for accepted generated content (#422).

specs/161-adventure-and-campaign-generation (#99, merged) specifies adventure/campaign generation
at any scale. This module implements its FR-012 through FR-015 -- accepting or declining a
`GenerationResult` (#420, `generation.py`) that has already been run through the five
anti-inflation checks (#421, `generation_checks.py`). It does not build the `GenerationRequest`/
`GenerationResult` shapes, does not run the anti-inflation checks themselves, and does not
generate any content (FR-016-020, the sibling generation-pipeline feature) -- those are separate,
already-landed or still-dependent features.

Two public functions, matching `generation.py`/`generation_checks.py`'s report-don't-raise
convention for an ordinary (non-programming-error) outcome:

- `can_commit` -- the shared gate (FR-006 of specs/164): a result is committable only when its
  `checks` list is non-empty and every entry's outcome is `pass` or `narrowed`.
- `accept_result` -- writes an accepted result as an ordinary `arc`/`beat` entity via
  `entity.py`/`state.py`'s existing schema and I/O (FR-012), then applies whatever thread/threat
  changes the candidate declares by calling `thread.py`'s `new_thread`/`touch` and `threat.py`'s
  `promote` directly, or mutating an existing threat's `imminence`/`ambient` the same inline way
  `threat.py` itself documents doing it (FR-013) -- never a parallel implementation. Refuses (with
  no I/O and no mutation) when `can_commit` is `False` (FR-015).
- `reject_result` -- the explicit-decline half of FR-015: always refuses, regardless of `checks`,
  with no I/O and no mutation.

This module adds no update/rewrite path for an entity once written (FR-014/FR-007 of specs/164,
`29-evolution.md`'s "the past is a fact") -- `accept_result` only ever creates a new file at the
caller-supplied `path`; it never opens or re-validates an existing one.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib

from wyrd import arc_selection, entity, generation, state, thread, threat

_COMMITTABLE_ENTITY_TYPES = ("arc", "beat")


def can_commit(result: dict) -> bool:
    """True only when `result['checks']` is non-empty and every entry's `outcome` is `pass` or
    `narrowed` (data-model.md's Commit outcome, FR-006). `False` for an empty `checks` list
    (treated as "not yet evaluated", not as an absence of rejection) or any `reject` entry.
    """
    checks = result.get("checks") or []
    if not checks:
        return False
    return all(entry.get("outcome") in ("pass", "narrowed") for entry in checks)


def reject_result(result: dict) -> dict:
    """FR-005/FR-015's explicit-decline path. Always returns `{"committed": False, "reason":
    "declined"}` -- never inspects `result['checks']`, never performs I/O, never calls a
    thread/threat mutation function, regardless of what `result` itself contains.
    """
    return {"committed": False, "reason": "declined"}


def _rejection_detail(result: dict) -> list[str]:
    checks = result.get("checks") or []
    if not checks:
        return ["no checks were run"]
    return [entry.get("detail", "") for entry in checks if entry.get("outcome") == "reject"]


def _apply_thread_updates(thread_updates: list[dict], live_threads: dict[str, dict]) -> None:
    """Apply each `thread_updates` entry (data-model.md) via `thread.py`'s own functions,
    mutating `live_threads` in place. Raises `ValueError` for an `action: "touch"` entry naming
    an id absent from `live_threads` -- a candidate cannot legitimately reference a thread that
    does not exist.
    """
    for update in thread_updates:
        action = update.get("action")
        thread_id = update.get("id")
        if action == "new":
            live_threads[thread_id] = thread.new_thread(
                id=thread_id,
                opened=update["opened"],
                summary=update["summary"],
                hooks=update["hooks"],
                heat=update.get("heat", 0),
            )
        elif action == "touch":
            if thread_id not in live_threads:
                raise ValueError(f"thread_updates: {thread_id!r} is not in live_threads")
            live_threads[thread_id] = thread.touch(live_threads[thread_id])
        else:
            raise ValueError(f"thread_updates: unknown action {action!r}")


def _apply_threat_updates(threat_updates: list[dict], live_entities: dict[str, dict]) -> None:
    """Apply each `threat_updates` entry (data-model.md, reusing #421's own shape) via
    `threat.promote` for a newly introduced threat, or a direct `imminence`/`ambient` mutation on
    an existing one -- `threat.py`'s own documented convention for exactly this change
    (research.md). Mutates `live_entities` in place. Raises `ValueError` for a malformed or
    unresolvable entry.
    """
    for update in threat_updates:
        entity_id = update.get("entity_id")
        if entity_id is None:
            target_id = update.get("target_entity_id")
            objective = update.get("objective")
            imminence = update.get("imminence")
            if target_id is None or objective is None or imminence is None:
                raise ValueError(
                    "threat_updates: a new threat requires target_entity_id, objective, "
                    "and imminence"
                )
            if target_id not in live_entities:
                raise ValueError(f"threat_updates: {target_id!r} is not in live_entities")
            threat_block = {
                "imminence": imminence,
                "connection": update.get("connection"),
                "ambient": list(update.get("ambient_add") or []),
                "effects": update.get("effects", {}),
            }
            live_entities[target_id] = threat.promote(
                live_entities[target_id], threat_block, objective
            )
        else:
            if entity_id not in live_entities:
                raise ValueError(f"threat_updates: {entity_id!r} is not in live_entities")
            target = live_entities[entity_id]
            threat_block = dict(target.get("threat") or {})
            threat_block["imminence"] = threat_block.get("imminence", 0) + update.get(
                "imminence_delta", 0
            )
            ambient_add = update.get("ambient_add") or []
            if ambient_add:
                threat_block["ambient"] = list(threat_block.get("ambient") or []) + list(
                    ambient_add
                )
            live_entities[entity_id] = {**target, "threat": threat_block}


def accept_result(
    result: dict,
    *,
    entity_id: str,
    entity_type: str,
    name: str,
    setting: str,
    mode: str,
    body: str,
    path: pathlib.Path,
    parent: str | None = None,
    entry: dict | None = None,
    exit: dict | None = None,
    tags: list[str] | None = None,
    thread_updates: list[dict] | None = None,
    threat_updates: list[dict] | None = None,
    live_threads: dict[str, dict] | None = None,
    live_entities: dict[str, dict] | None = None,
) -> dict:
    """FR-012/FR-013's accept path.

    When `can_commit(result)` is `False`, returns `{"committed": False, "reason":
    "checks_failed", "detail": [...]}` with no I/O and no mutation (FR-015) -- every other
    argument is not even inspected in that case.

    Otherwise, builds an ordinary `arc`/`beat` entity frontmatter (`status: drafted`, never
    `stub` -- it did not come from decomposing one) carrying one additive `sources[]` entry of
    `{generated: true, mode: <the request's mode>, consumed: result['consumed']}`, validates it
    with `entity.validate` (and `arc_selection.validate_entry_exit` when `entry`/`exit` are
    given), writes it via `state.save_entity`, then applies every `thread_updates`/
    `threat_updates` entry via `thread.py`'s/`threat.py`'s own functions.

    Raises `ValueError` for `entity_type` outside `{"arc", "beat"}`, or for a built frontmatter
    that fails validation -- a caller error, never a partial write.
    """
    if not can_commit(result):
        return {
            "committed": False,
            "reason": "checks_failed",
            "detail": _rejection_detail(result),
        }

    if entity_type not in _COMMITTABLE_ENTITY_TYPES:
        raise ValueError(
            f"entity_type must be one of {_COMMITTABLE_ENTITY_TYPES}, got {entity_type!r}"
        )
    if mode not in generation.MODES:
        raise ValueError(f"mode must be one of {generation.MODES}, got {mode!r}")

    generated_source = {
        "generated": True,
        "mode": mode,
        "consumed": list(result.get("consumed") or []),
    }

    frontmatter: dict = {
        "id": entity_id,
        "type": entity_type,
        "name": name,
        "setting": setting,
        "status": "drafted",
        "tags": list(tags or []),
        "sources": [generated_source],
    }
    if parent is not None:
        frontmatter["parent"] = parent
    if entry is not None:
        frontmatter["entry"] = entry
    if exit is not None:
        frontmatter["exit"] = exit

    validity = entity.validate(frontmatter)
    if not validity["valid"]:
        raise ValueError(f"generated entity failed validation: {validity['error']}")

    source_validity = entity.validate_source(generated_source, status="drafted")
    if not source_validity["valid"]:
        raise ValueError(f"generated source failed validation: {source_validity['error']}")

    if entry is not None or exit is not None:
        entry_exit_validity = arc_selection.validate_entry_exit(frontmatter)
        if not entry_exit_validity["valid"]:
            raise ValueError(
                f"generated entity's entry/exit invalid: {entry_exit_validity['error']}"
            )

    state.save_entity(frontmatter, body, path)

    threads_out = dict(live_threads or {})
    entities_out = dict(live_entities or {})
    _apply_thread_updates(list(thread_updates or []), threads_out)
    _apply_threat_updates(list(threat_updates or []), entities_out)

    return {
        "committed": True,
        "path": path,
        "entity": frontmatter,
        "threads": threads_out,
        "entities": entities_out,
    }
