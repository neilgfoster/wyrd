"""Beat/arc entry and exit conditions, and thread-matched selection.

docs/design/18-arcs-and-beats.md: an arc or beat may declare an `entry` block (what must already
be true for it to be reachable: `requires_threads`, `requires_state`, `hooks`) and an `exit`
block (what it leaves behind: `emits_threads`, `changes`, `leads_to`). `wyrd.entity` already
validates the common entity schema and containment; `wyrd.session` (#309) already covers
containment enforcement and the session loop. Neither has any notion of entry/exit, and nothing
yet selects the next beat by matching live threads -- this module adds both: `validate_entry_exit`
checks the shape of an entity's optional entry/exit blocks, and `select` matches a caller-supplied
set of live threads against a pool of candidates' `entry.requires_threads`, falling back to
`leads_to` only when nothing matches ("Selection, and why leads_to is only a hint").

This module holds no persistent state and tracks no live-thread set of its own -- that is the
chronicle/campaign state layer under sibling epics #300/#301, not built yet. A caller passes the
live-thread set and candidate pool in as plain arguments, matching every other `engine/wyrd/*`
module's contract.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import entity

# entry/exit fields whose value, when present, must be a plain list -- no further per-item
# structure beyond what _validate_emits_threads checks separately for exit.emits_threads.
_ENTRY_LIST_FIELDS = ("requires_threads", "requires_state", "hooks")
_EXIT_LIST_FIELDS = ("changes",)


def _validate_emits_threads(emits_threads) -> str | None:
    if not isinstance(emits_threads, list):
        return "exit.emits_threads is not a list"
    for i, emitted in enumerate(emits_threads):
        if not isinstance(emitted, dict):
            return f"exit.emits_threads[{i}] is not a mapping"
        if not emitted.get("tag"):
            return f"exit.emits_threads[{i}] missing required field 'tag'"
        if "if" in emitted and emitted["if"] is not None and not isinstance(emitted["if"], str):
            return f"exit.emits_threads[{i}].if is not a string"
    return None


def validate_entry_exit(frontmatter: dict) -> dict:
    """Check an entity's optional `entry`/`exit` blocks against their schema.

    Returns {"valid": True} or {"valid": False, "error": "<which field, missing or invalid>"}.
    An entity carrying neither block validates -- both are optional, consistent with a
    `status: stub` entity that has not yet declared either.
    """
    entry = frontmatter.get("entry")
    if entry is not None:
        if not isinstance(entry, dict):
            return {"valid": False, "error": "entry is not a mapping"}
        for field in _ENTRY_LIST_FIELDS:
            value = entry.get(field)
            if value is not None and not isinstance(value, list):
                return {"valid": False, "error": f"entry.{field} is not a list"}

    exit_block = frontmatter.get("exit")
    if exit_block is not None:
        if not isinstance(exit_block, dict):
            return {"valid": False, "error": "exit is not a mapping"}
        emits_threads = exit_block.get("emits_threads")
        if emits_threads is not None:
            problem = _validate_emits_threads(emits_threads)
            if problem:
                return {"valid": False, "error": problem}
        for field in _EXIT_LIST_FIELDS:
            value = exit_block.get(field)
            if value is not None and not isinstance(value, list):
                return {"valid": False, "error": f"exit.{field} is not a list"}
        leads_to = exit_block.get("leads_to")
        if leads_to is not None and not isinstance(leads_to, str):
            return {"valid": False, "error": "exit.leads_to is not a string"}

    return {"valid": True}


def _thread_match(frontmatter: dict, live_threads: set[str]) -> bool:
    """True if `frontmatter`'s `entry.requires_threads` (default []) is a subset of
    `live_threads`. An empty or absent requirement is always satisfied."""
    entry = frontmatter.get("entry") or {}
    required = entry.get("requires_threads") or []
    return set(required) <= set(live_threads)


def select(
    live_threads,
    candidates: list[dict],
    *,
    current: dict | None = None,
) -> list[dict]:
    """Select the next beat/arc from `candidates` by matching `live_threads`.

    Returns every candidate whose `entry.requires_threads` is a subset of `live_threads`
    (docs/design/18-arcs-and-beats.md, "Selection"). `leads_to` is consulted only as a fallback,
    and only when the thread match returns nothing: `current`'s `exit.leads_to` (if any) is
    resolved (via `entity.resolve_wikilink`) and looked up by id in `candidates`. Returns `[]`
    when neither a thread match nor a valid `leads_to` target exists -- never raises.

    Selection operates purely on `candidates` as given -- it never descends into a selected
    entity's children, so an undecomposed `status: stub` arc is selected on exactly the same
    footing as a fully-decomposed arc or beat, judged only by its own `entry` block.
    """
    matches = [candidate for candidate in candidates if _thread_match(candidate, live_threads)]
    if matches:
        return matches

    if current is None:
        return []

    exit_block = current.get("exit") or {}
    leads_to = exit_block.get("leads_to")
    if not leads_to:
        return []

    target_id = entity.resolve_wikilink(leads_to)
    for candidate in candidates:
        if candidate.get("id") == target_id:
            return [candidate]
    return []
