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


#: docs/design/03-rules.md "Declaration" subsection. `None` is the sentinel for "so
#: well-judged it removes the risk" -- not a numeric bonus, a signal to skip the roll entirely.
DECLARATION_BONUSES = {
    "specific": 10,
    "specific_leveraging": 20,
    "brief": 0,
    "against_nature": -20,
    "removes_risk": None,
}


def declaration_bonus(category: str) -> int | None:
    """Look up a declaration category's fixed point value (or `None` for "no roll").

    Never derives a value from length -- the caller (GM/model) judges which category a
    declared action falls into; this function only holds the closed table of point values
    (docs/design/27-tooling.md's deterministic-over-inference split).
    """
    if category not in DECLARATION_BONUSES:
        raise ValueError(f"no such category: {category}")
    return DECLARATION_BONUSES[category]


def assistance_bonus(helper_skill: int, can_attempt: bool = True) -> int:
    """A helper's contribution: a tenth of their own skill, rounded down, capped at +10.

    Zero if they could not attempt the task alone (docs/design/03-rules.md "Assistance":
    "someone who could not attempt it alone cannot improve someone who is attempting it").
    Whether they could attempt it is supplied by the caller, not derived here.
    """
    if not can_attempt:
        return 0
    return min(helper_skill // 10, 10)


def opposed_test(
    skill: int,
    opponent: int,
    seed: int | None = None,
    declaration: str | None = None,
    helper_skill: int | None = None,
    helper_can_attempt: bool = True,
) -> dict:
    """Resolve a single player-facing opposed test (docs/design/03-rules.md "Opposed tests").

    One roll, on the acting side only -- the opponent's dice are never consulted. Degrees of
    success are reported only when the roll succeeds; a failure "simply fails the action"
    with no degrees comparison performed. The Wyrd die is read independently of success.

    `declaration` and `helper_skill` are optional modifiers (specs/077-declaration-assistance)
    added to `skill` before `effective_pct` is computed. Calling with neither is identical to
    calling this function before those modifiers existed -- no default behavior change.
    `declaration == "removes_risk"` skips the roll entirely and reports automatic success.
    """
    bonus_from_declaration = declaration_bonus(declaration) if declaration is not None else 0
    if bonus_from_declaration is None:  # "removes_risk"
        return {
            "verb": "opposed-test",
            "skill": skill,
            "opponent": opponent,
            "declaration": declaration,
            "helper_skill": helper_skill,
            "effective_pct": None,
            "roll": None,
            "success": True,
            "degrees": None,
            "wyrd": "none",
            "no_roll": True,
            "seed": seed,
        }

    bonus_from_assistance = (
        assistance_bonus(helper_skill, helper_can_attempt) if helper_skill is not None else 0
    )
    effective_skill = skill + bonus_from_declaration + bonus_from_assistance
    effective_pct = max(5, min(95, 50 + (effective_skill - opponent)))
    roll = roll_d100(sides=100, seed=seed)
    wyrd = _wyrd_die(roll)
    success = roll <= effective_pct
    degrees = _tens(effective_pct) - _tens(roll) if success else None
    return {
        "verb": "opposed-test",
        "skill": skill,
        "opponent": opponent,
        "declaration": declaration,
        "helper_skill": helper_skill,
        "effective_pct": effective_pct,
        "roll": roll,
        "success": success,
        "degrees": degrees,
        "wyrd": wyrd,
        "no_roll": False,
        "seed": seed,
    }
