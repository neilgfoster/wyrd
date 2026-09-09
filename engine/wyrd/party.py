"""Companions and the NPC-played party: validation, Tension/Bond arithmetic, Loyalty gating.

docs/design/10-the-character.md §4 (person-first companion model) and docs/design/16-session.md
(the two-layer split, Party Tension, Loyalty) specify the rules this module implements; ADR 0034
settles Bond as the positive party track. Companions are `character` entities
(`wyrd.state`/`wyrd.character`'s existing shape); this module holds party-level concerns --
Tension, Bond offset, Loyalty gating, roster assembly -- that have no player-character analogue,
the same way `wyrd.adversary` sits alongside `wyrd.character` rather than inside it.

As with `wyrd.career`, setting-supplied data (here, the Loyalty relation table) is passed in as a
plain parameter -- the engine fixes nothing about what Loyalties exist or how they relate
(docs/design/16-session.md).

Python 3.11+, standard library only.
"""

from __future__ import annotations

#: The mechanical layer is closed at exactly these five fields (docs/design/16-session.md,
#: ADR 0034). `tools/check_companion_layers.py` asserts this set against the design document
#: itself, so it must never drift from what's declared there.
MECHANICAL_FIELDS = {"career", "bond", "taint", "strain", "wounds"}

#: The narrative layer -- prose only, never read by a resolution rule.
NARRATIVE_FIELDS = {"objective", "flaw", "secret", "arc"}

#: Fields a companion record carries besides the two layers -- identity and status, never read
#: by a resolution rule any more than the narrative layer is.
NON_LAYER_FIELDS = {"id", "type", "role", "status"}

#: The largest party the design's own effective-size table counts (docs/design/16-session.md).
MAX_PARTY_SIZE = 5

#: Party Tension's ceiling; reaching or exceeding it resolves as a single break and resets to 0.
TENSION_BREAK = 6


def validate_companion(companion: dict) -> dict:
    """Check a companion record's mechanical layer against the closed five-field set.

    Returns `{"valid": True}`, or `{"valid": False, "error": "..."}` naming the specific problem.
    Any key outside `MECHANICAL_FIELDS | NARRATIVE_FIELDS | NON_LAYER_FIELDS` is treated as an
    unexpected mechanical field -- the mechanical layer is the only one this feature closes, and
    an unrecognized field is the sixth-field case the design forbids, not a silently-accepted
    extension.
    """
    known = MECHANICAL_FIELDS | NARRATIVE_FIELDS | NON_LAYER_FIELDS
    unexpected = set(companion) - known
    if unexpected:
        return {"valid": False, "error": f"unexpected mechanical field: {sorted(unexpected)[0]}"}

    missing = MECHANICAL_FIELDS - set(companion)
    if missing:
        return {"valid": False, "error": f"missing mechanical field: {sorted(missing)[0]}"}

    bond = companion["bond"]
    if not isinstance(bond, int) or isinstance(bond, bool) or not (-3 <= bond <= 3):
        return {"valid": False, "error": "bond must be an integer in [-3, 3]"}

    return {"valid": True}


def tension_delta(base_delta: int, *, bond: int | None, strained_pairing: bool) -> int:
    """The actual Tension change for an event, per docs/design/16-session.md and ADR 0034.

    `bond` is the named companion's Bond (-3..+3), or `None` if the event names no companion --
    an unnamed event is unaffected by any one companion's Bond. `strained_pairing` doubles the
    rate (before any Bond offset) while the party holds a strained Loyalty pairing. The result is
    never negative.
    """
    delta = base_delta * 2 if strained_pairing else base_delta
    if bond is None:
        return delta
    return max(0, delta - bond)


def apply_tension(current: int, delta: int) -> dict:
    """Apply a computed delta to the current Tension (0-6).

    Returns `{"tension": <new value>, "broke": <bool>}`. Reaching or exceeding `TENSION_BREAK`
    resolves as a single break, however much the increment overshot it, and resets to 0.
    """
    new_value = current + delta
    if new_value >= TENSION_BREAK:
        return {"tension": 0, "broke": True}
    return {"tension": new_value, "broke": False}


def apply_tension_decrement(current: int) -> int:
    """Tension falls by 1 (downtime, or a beat spent on a companion's problem), floored at 0."""
    return max(0, current - 1)


def loyalty_relation(a: str, b: str, relations: dict[tuple[str, str], str]) -> str:
    """ "strained", "irreconcilable", or "undeclared" for the pair, symmetric in `a`/`b`."""
    return relations.get((a, b)) or relations.get((b, a)) or "undeclared"


def can_join(
    candidate_loyalty: str,
    party_loyalties: list[str],
    relations: dict[tuple[str, str], str],
    party_size: int,
) -> dict:
    """Whether a candidate with this Loyalty may join.

    Returns `{"allowed": True}` or `{"allowed": False, "reason": "..."}`.
    """
    if party_size >= MAX_PARTY_SIZE:
        return {"allowed": False, "reason": f"party is full (max {MAX_PARTY_SIZE} companions)"}

    for other in party_loyalties:
        if loyalty_relation(candidate_loyalty, other, relations) == "irreconcilable":
            return {
                "allowed": False,
                "reason": f"irreconcilable Loyalty pairing: {candidate_loyalty} / {other}",
            }

    return {"allowed": True}


def recheck_loyalty_change(
    party_loyalties: list[str], relations: dict[tuple[str, str], str]
) -> bool:
    """Whether the party, as it stands, now holds an irreconcilable pairing.

    Called after any character's Loyalty changes (docs/design/16-session.md); the caller applies
    the immediate Tension break (via `apply_tension`) when this returns `True`.
    """
    for i, a in enumerate(party_loyalties):
        for b in party_loyalties[i + 1 :]:
            if loyalty_relation(a, b, relations) == "irreconcilable":
                return True
    return False


def has_strained_pairing(party_loyalties: list[str], relations: dict[tuple[str, str], str]) -> bool:
    """Whether the party currently holds a strained Loyalty pairing (doubles Tension gain)."""
    for i, a in enumerate(party_loyalties):
        for b in party_loyalties[i + 1 :]:
            if loyalty_relation(a, b, relations) == "strained":
                return True
    return False


def roster(companions: list[dict]) -> list[dict]:
    """The full party roster: each companion's narrative and mechanical layers together.

    A pure pass-through -- no narrative content is generated or altered (FR-013;
    docs/design/16-session.md: "the GM never asks the player to decide for a companion").
    """
    return list(companions)
