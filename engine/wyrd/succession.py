"""Succession: passing through the thread, not the bloodline (#340).

docs/design/19-campaign.md, "Succession": a chronicle running years may outlast the character who
began it. The successor is selected by how strongly the predecessor's own history entangles them
-- never affection -- and inherits the unresolved situation, not the sheet: threads, enemies,
active Threats and what the world believes, never skills, Stamina, Fate, Taint or an assumption
of goodwill. The predecessor themselves does not simply vanish: lost, died, or retired each leave
a different, queryable trace.

Four pure functions, no I/O, matching the epic's existing division of labour:

- `rank_candidates` -- the six-category, closed-vocabulary priority order (FR-001, FR-002).
- `propose_successors` -- "the GM proposes two or three candidates" (FR-003).
- `inherit` -- the inherited/excluded field table exactly; holdings only when explicitly passed
  (FR-004, FR-005, FR-006).
- `record_predecessor` -- the three post-succession outcomes (FR-007).

Python 3.11+, standard library only.
"""

from __future__ import annotations

_ENTANGLEMENT_PRIORITY = (
    "wronged",
    "investigating",
    "bystander",
    "rival",
    "found_evidence",
    "companion",
)

_INHERITED_FIELDS = ("threads", "enemies", "active_threats", "world_belief")

_PREDECESSOR_OUTCOMES = frozenset({"lost", "died", "retired"})
_OUTCOME_STATUS = {"lost": "gm-controlled", "died": "died", "retired": "findable"}


def rank_candidates(candidates: list[dict]) -> list[dict]:
    """`candidates` sorted by entanglement priority, stable on ties (FR-001, FR-002).

    Raises `ValueError` naming the offending candidate if any `entanglement` value is outside
    the six-member closed vocabulary.
    """
    for candidate in candidates:
        if candidate.get("entanglement") not in _ENTANGLEMENT_PRIORITY:
            raise ValueError(
                f"candidate {candidate.get('id', candidate)!r} has an unrecognised "
                f"entanglement {candidate.get('entanglement')!r}; must be one of "
                f"{_ENTANGLEMENT_PRIORITY}"
            )
    return sorted(candidates, key=lambda c: _ENTANGLEMENT_PRIORITY.index(c["entanglement"]))


def propose_successors(ranked: list[dict], limit: int = 3) -> list[dict]:
    """The first `limit` of `ranked` (FR-003) -- fewer if `ranked` has fewer."""
    return list(ranked[:limit])


def inherit(predecessor: dict, inherited_holding: dict | None = None) -> dict:
    """The successor's inherited state from `predecessor` (FR-004, FR-005, FR-006).

    Copies `threads`/`enemies`/`active_threats`/`world_belief` when present on `predecessor`
    (absent from the result when the predecessor didn't have them). Never includes `skills`,
    `careers`, `advances`, `stamina`, `fate`, `taint`, `transformations`, `afflictions`, or
    `holdings` -- excluded outright, not merely emptied. `predecessor`'s `reputation`, if
    present, is carried as `predecessor_reputation`, kept separate from the successor's own
    (fresh/absent) reputation. `inherited_holding`, when given, is the only way a holding
    reaches the result -- always marked `encumbered: True`.
    """
    result = {field: predecessor[field] for field in _INHERITED_FIELDS if field in predecessor}
    if "reputation" in predecessor:
        result["predecessor_reputation"] = predecessor["reputation"]
    if inherited_holding is not None:
        result["holding"] = {**inherited_holding, "encumbered": True}
    return result


def record_predecessor(outcome: str, *, fact: str | None = None, rumour: str | None = None) -> dict:
    """Record the predecessor's post-succession state for `outcome` (FR-007).

    `outcome` is one of `"lost" | "died" | "retired"`; any other value raises `ValueError`.
    `fact`/`rumour` are only carried for `died`, and are permitted to differ.
    """
    if outcome not in _PREDECESSOR_OUTCOMES:
        raise ValueError(f"outcome must be one of {sorted(_PREDECESSOR_OUTCOMES)}, got {outcome!r}")
    result = {"status": _OUTCOME_STATUS[outcome]}
    if outcome == "died":
        result["fact"] = fact
        result["rumour"] = rumour
    return result
