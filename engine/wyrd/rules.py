"""Resolution primitives: pure functions, no I/O, no state.

docs/design/01-principles.md principle 1: the dice bind the GM. This is the only place a
random result comes from -- the model narrates from what this module returns and never
recomputes it (docs/design/27-tooling.md section 3).

Python 3.11+, standard library only.
"""

from __future__ import annotations

import random


def roll_d100(sides: int = 100, seed: int | None = None) -> int:
    """Roll one die of the given number of sides (default: d100).

    A locally-seeded `random.Random` instance is used rather than the module-level
    `random` global, so one call's seed can never leak into an unrelated call in the same
    process. Given the same seed, the result is always identical; with no seed, the result
    is drawn from the platform's default randomness (not reproducible).
    """
    if not isinstance(sides, int) or sides <= 0:
        raise ValueError(f"sides must be a positive integer, got {sides!r}")
    rng = random.Random(seed)
    return rng.randint(1, sides)


def _tens(value: int) -> int:
    return value // 10


def _wyrd_die(natural_roll: int) -> str:
    """Read the Wyrd die from the units digit of the natural (unmodified) roll.

    Computed as a single shared step, before any success/failure branch, so the reading is
    structurally independent of the outcome axis (docs/design/03-rules.md: "the units digit
    is uniform within both the success and failure sets") rather than merely tested to be.
    """
    units = natural_roll % 10
    if units == 0:
        return "ill_omen"
    if units == 9:
        return "fair_omen"
    return "none"


def opposed_test(skill: int, opponent: int, seed: int | None = None) -> dict:
    """Resolve a single player-facing opposed test (docs/design/03-rules.md "Opposed tests").

    One roll, on the acting side only -- the opponent's dice are never consulted. Degrees of
    success are reported only when the roll succeeds; a failure "simply fails the action"
    with no degrees comparison performed. The Wyrd die is read independently of success.
    """
    effective_pct = max(5, min(95, 50 + (skill - opponent)))
    roll = roll_d100(sides=100, seed=seed)
    wyrd = _wyrd_die(roll)
    success = roll <= effective_pct
    degrees = _tens(effective_pct) - _tens(roll) if success else None
    return {
        "verb": "opposed-test",
        "skill": skill,
        "opponent": opponent,
        "effective_pct": effective_pct,
        "roll": roll,
        "success": success,
        "degrees": degrees,
        "wyrd": wyrd,
        "seed": seed,
    }
