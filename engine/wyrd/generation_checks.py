"""Anti-inflation checks for generated content (#421).

specs/161-adventure-and-campaign-generation (#99, merged) specifies five anti-inflation checks,
stated as checkable rules rather than prose intention, that every generated candidate must pass
before it can be offered for acceptance (FR-007 through FR-011). This module implements exactly
those five checks, plus one thin aggregator, as pure, side-effect-free functions. It does not
build the `GenerationRequest`/`GenerationResult` shapes those checks run against (`generation.py`,
#420), does not commit an accepted result anywhere (FR-012-015), and does not generate any content
itself (FR-016-020) -- those are separate, dependent sibling features.

Each check function returns one `{rule, outcome, detail}` entry -- `outcome` is `pass`, `reject`,
or (FR-010 only) `narrowed` -- matching the shape `GenerationResult.checks` (#420) carries, so a
rejection is explainable rather than silent (data-model.md). `run_checks` runs all five in
FR-007..FR-011 order and returns their entries as a list, ready to pass straight into
`generation.new_result`'s `checks` argument.

FR-009 reuses `corpus_scenario.scale_danger` -- the existing danger-scaling wrapper issue #421
itself names -- rather than recomputing the ratio formula (`03-rules.md` section 7, ADR 0024).
FR-010's connectionless-new-threat leg reuses `threat.validate_connections` rather than
re-deriving what counts as "no connection" (`19-campaign.md`: "a threat with no connection is
scenery").

Two of the five checks read data #420's `GenerationRequest` does not itself carry
(specs/163-anti-inflation-checks/spec.md's Assumptions): `check_entity_membership` takes the
setting's known-entity list as its own explicit parameter, since `live-play` requests have no
request-object equivalent of `existing_entities`.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import corpus_scenario, threat

# FR-008: prophecy claims a candidate's own `prophecy_claim` field may carry.
_FORBIDDEN_PROPHECY_CLAIMS = ("destiny", "hidden_bloodline", "prewritten_fate")

# FR-010: the escalation `check_scale_drift` permits under `scale_drift: suppressed` before an
# existing threat's change must be narrowed rather than passed as asked.
_MAX_SUPPRESSED_IMMINENCE_DELTA = 1
_MAX_SUPPRESSED_AMBIENT_ADD = 1


def _entry(rule: str, outcome: str, detail: str = "") -> dict:
    """Build one `{rule, outcome, detail}` check entry (data-model.md's shared shape)."""
    return {"rule": rule, "outcome": outcome, "detail": detail}


def check_entity_membership(request: dict, candidate: dict, known_entities: list[str]) -> dict:
    """FR-007: every named entity must come from one of three closed sources.

    (a) `known_entities` -- the setting's `entities/` store, supplied by the caller rather than
    read off `request` (spec.md Assumptions: `live-play` requests carry no such field).
    (b) the request's own `threads`/`threat_state` ids (`live-play` mode).
    (c) newly invented and labelled `invented, per Phase 1 Q3` (`setting-authoring` mode only,
    and only when `request['invention_permitted']` is `True`).

    Rejects naming every entity absent from all three; `pass` when every named entity is
    accounted for.
    """
    known = set(known_entities or [])
    grounded_ids = {t.get("id") for t in (request.get("threads") or [])}
    grounded_ids |= {t.get("entity_id") for t in (request.get("threat_state") or [])}
    invention_allowed = (
        request.get("mode") == "setting-authoring" and request.get("invention_permitted") is True
    )

    missing = []
    for named in candidate.get("named_entities") or []:
        name = named if isinstance(named, str) else named.get("name")
        labelled_invented = not isinstance(named, str) and named.get("invented") is True
        if name in known or name in grounded_ids:
            continue
        if invention_allowed and labelled_invented:
            continue
        missing.append(name)

    if missing:
        return _entry(
            "FR-007",
            "reject",
            f"named entities not in the setting, request state, or a Phase 1 Q3 invention "
            f"label: {missing}",
        )
    return _entry("FR-007", "pass")


def check_prophecy(request: dict, candidate: dict) -> dict:
    """FR-008: closed-vocabulary comparison of `tone_contract.prophecy` against a candidate's
    `prophecy_claim` and each `threat_updates` entry's `known_to_player`.

    Under `prophecy: forbidden`, a non-`none` `prophecy_claim`, or any `threat_updates` entry at
    `known_to_player: understood`, is rejected (spec.md Assumptions). `rare`/`central` never gate
    either field -- rejection is `forbidden`'s own behaviour.
    """
    prophecy = (request.get("tone_contract") or {}).get("prophecy")
    if prophecy != "forbidden":
        return _entry("FR-008", "pass")

    claim = candidate.get("prophecy_claim", "none")
    if claim in _FORBIDDEN_PROPHECY_CLAIMS:
        return _entry(
            "FR-008", "reject", f"prophecy_claim={claim!r} forbidden under tone_contract.prophecy"
        )

    for update in candidate.get("threat_updates") or []:
        if update.get("known_to_player") == "understood":
            return _entry(
                "FR-008",
                "reject",
                f"threat {update.get('entity_id')!r} known_to_player=understood forbidden under "
                "tone_contract.prophecy",
            )

    return _entry("FR-008", "pass")


def check_danger_band(request: dict, candidate: dict) -> dict:
    """FR-009: the candidate's own `danger` must not exceed `request['danger_rating']`, banded
    through `corpus_scenario.scale_danger` -- the existing danger-scaling arithmetic (research.md)
    -- rather than compared as a raw number.

    `danger_rating` is a `live-play`-only field (`generation.py`'s `_LIVE_PLAY_FIELDS`) --
    `validate_request` rejects a `setting-authoring` request that sets it, so a well-formed
    `setting-authoring` request always has `danger_rating: None` here. There is no chronicle
    danger rating to band against yet in that mode, so this check has nothing to enforce and
    passes unconditionally, rather than comparing against `None`.
    """
    danger_rating = request.get("danger_rating")
    if danger_rating is None:
        return _entry("FR-009", "pass")

    written_for = request.get("written_for")
    record = {"danger": candidate.get("danger"), "written_for": written_for}
    effective = corpus_scenario.scale_danger(record, written_for)

    if effective > danger_rating:
        return _entry(
            "FR-009",
            "reject",
            f"candidate danger {effective} exceeds the band for danger_rating {danger_rating}",
        )
    return _entry("FR-009", "pass")


def check_scale_drift(request: dict, candidate: dict) -> dict:
    """FR-010: under `scale_drift: suppressed` only, an escalating `threat_updates` entry is
    `narrowed` (an existing threat's imminence/ambient change, reduced to what the contract
    permits) or `reject`ed (a new threat introduced with no connection -- narrowing cannot invent
    one, `19-campaign.md`'s "a threat with no connection is scenery", checked via
    `threat.validate_connections`). Never gates under `scale_drift: allowed`.
    """
    if (request.get("tone_contract") or {}).get("scale_drift") != "suppressed":
        return _entry("FR-010", "pass")

    for update in candidate.get("threat_updates") or []:
        if update.get("entity_id") is None:
            fake_entity = {"threat": {"connection": update.get("connection")}}
            if threat.validate_connections([fake_entity]):
                return _entry(
                    "FR-010",
                    "reject",
                    "a new threat with no specific connection to the player or a companion "
                    "cannot be narrowed under scale_drift: suppressed",
                )
            continue

        imminence_delta = update.get("imminence_delta", 0)
        ambient_add = update.get("ambient_add") or []
        if imminence_delta > _MAX_SUPPRESSED_IMMINENCE_DELTA:
            return _entry(
                "FR-010",
                "narrowed",
                f"threat {update.get('entity_id')!r} imminence_delta narrowed from "
                f"{imminence_delta} to {_MAX_SUPPRESSED_IMMINENCE_DELTA} under "
                "scale_drift: suppressed",
            )
        if len(ambient_add) > _MAX_SUPPRESSED_AMBIENT_ADD:
            return _entry(
                "FR-010",
                "narrowed",
                f"threat {update.get('entity_id')!r} ambient_add narrowed from {len(ambient_add)} "
                f"to {_MAX_SUPPRESSED_AMBIENT_ADD} new cost(s) under scale_drift: suppressed",
            )

    return _entry("FR-010", "pass")


def check_favourable_coincidence(request: dict, candidate: dict) -> dict:
    """FR-011: a candidate's `coincidences` entry MUST be grounded in the request's own supplied
    state (`threads`/`threat_state` for `live-play`, `existing_entities` for `setting-
    authoring`) -- otherwise it is an unrequested, unearned favourable coincidence
    (`01-principles.md` principle 4) and is rejected.
    """
    grounded_ids = {t.get("id") for t in (request.get("threads") or [])}
    grounded_ids |= {t.get("entity_id") for t in (request.get("threat_state") or [])}
    grounded_ids |= set(request.get("existing_entities") or [])

    for coincidence in candidate.get("coincidences") or []:
        supported_by = coincidence.get("supported_by")
        if supported_by is None or supported_by not in grounded_ids:
            return _entry(
                "FR-011",
                "reject",
                f"coincidence {coincidence.get('claim')!r} not supported by the request's own "
                "state",
            )

    return _entry("FR-011", "pass")


def run_checks(request: dict, candidate: dict, known_entities: list[str]) -> list[dict]:
    """Run all five checks in FR-007..FR-011 order and return their entries as a list, matching
    `GenerationResult.checks`' shape (#420). A thin aggregator -- no check logic of its own.
    """
    return [
        check_entity_membership(request, candidate, known_entities),
        check_prophecy(request, candidate),
        check_danger_band(request, candidate),
        check_scale_drift(request, candidate),
        check_favourable_coincidence(request, candidate),
    ]
