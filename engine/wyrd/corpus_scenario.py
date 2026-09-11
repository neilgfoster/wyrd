"""Scenario index schema and deterministic selection: scenarios.json's deterministic half (#356).

docs/design/26-corpus-index.md: the fifth and largest corpus index, the scenario record. Its
thematic fields (`tone`, `themes`, `shape`) are model-generated elsewhere ("Haiku-tier") and are
out of scope here entirely -- this module owns only the deterministic fields: schema validation,
danger scaling, and requirement/helped-by reporting.

"Almost nothing gates. Most things modulate." Party size scales `danger` through the engine's
existing `adversary.danger_effective` formula (#98) -- it never excludes a scenario, however
small or large the party. `needs_access`/`needs_capability` are things that must be supplied by
someone (the player character, a companion, or hired help) and obtaining them may itself become
play; `helped_by` is a flag only. None of the three filters a scenario out -- they are reported,
never gated on, matching the design's own "inputs, not walls" framing (research.md). The one
genuine hard exclusion this module implements is `settings` membership -- "the genuine exclusions
are few: wrong setting."

Four pure functions, no I/O, matching every sibling module in this epic (`corpus_document.py`,
`corpus_terms.py`, `threat.py`, `scenario_selection.py`).

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import adversary

_SCALES = frozenset(
    {"village", "town", "city", "wilderness", "underground", "waterway", "road", "ship", "fortress"}
)
_SEASONS = frozenset({"any", "winter", "harvest", "festival"})


def validate_scenario_record(record: dict) -> dict:
    """Validate `record`'s `scale` and `season` against their closed vocabularies (FR-001,
    FR-002). Returns `record` unchanged on success; raises `ValueError` naming the offending
    field otherwise (FR-003)."""
    if record.get("scale") not in _SCALES:
        raise ValueError(f"scale {record.get('scale')!r} is not one of {sorted(_SCALES)}")
    if record.get("season") not in _SEASONS:
        raise ValueError(f"season {record.get('season')!r} is not one of {sorted(_SEASONS)}")
    return record


def scale_danger(record: dict, party: int):
    """Scale `record`'s `danger` against `party` via `adversary.danger_effective`, unchanged
    (FR-004). Never rejects any party size (FR-005)."""
    return adversary.danger_effective(record["danger"], party, record["written_for"])


def _check_list(needed: list[str], available: list[str]) -> dict:
    available_set = set(available)
    met = [item for item in needed if item in available_set]
    unmet = [item for item in needed if item not in available_set]
    return {"met": met, "unmet": unmet}


def check_requirements(
    record: dict, available_access: list[str], available_capability: list[str]
) -> dict:
    """Report each of `record`'s `needs_access`/`needs_capability` as met or unmet against
    what's currently available -- never filters the record out (FR-006)."""
    return {
        "access": _check_list(record.get("needs_access", []), available_access),
        "capability": _check_list(record.get("needs_capability", []), available_capability),
    }


def check_helped_by(record: dict, available: list[str]) -> dict:
    """Report which of `record`'s `helped_by` entries are currently available -- informational
    only, never a filter (FR-007)."""
    return _check_list(record.get("helped_by", []), available)


def is_eligible_for_setting(record: dict, setting: str) -> bool:
    """`setting` is in `record`'s `settings` list -- the one genuine hard gate (FR-008)."""
    return setting in record.get("settings", [])
