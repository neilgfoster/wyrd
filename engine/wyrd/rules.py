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


def _wyrd_die(natural_roll: int, omen_width: int = 0) -> str:
    """Read the Wyrd die from the units digit of the natural (unmodified) roll.

    Computed as a single shared step, before any success/failure branch, so the reading is
    structurally independent of the outcome axis (docs/design/03-rules.md: "the units digit
    is uniform within both the success and failure sets") rather than merely tested to be.

    `omen_width` widens the band read as an Omen at each end (docs/design/12-the-adversary.md
    section 5's `wyrd` trait, specs/096-adversary-trait-effects): units `0..omen_width` read
    Ill Omen, units `(9-omen_width)..9` read Fair Omen. Defaults to 0, reproducing exactly the
    single-value bands every existing caller already relies on.
    """
    units = natural_roll % 10
    if units <= omen_width:
        return "ill_omen"
    if units >= 9 - omen_width:
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


#: docs/design/15-oracle-prompts.md "The tables": four families, each ten rows of equal width
#: (1-10, 11-20, ... 91-100) covering 1d100 exactly with no modifier. Transcribed verbatim from
#: the design document; `tools/check_oracle_prompts.py` verifies this table stays in sync with it.
ORACLE_PROMPT_TABLES: dict[str, list[tuple[range, str, str]]] = {
    "oracle-prompt-npc-objective": [
        (
            range(1, 11),
            "protect_someone",
            "Wants someone or something specific protected, and will do whatever it takes.",
        ),
        (
            range(11, 21),
            "escape_a_debt",
            "Wants out from under a debt or obligation, without anyone noticing until it's done.",
        ),
        (
            range(21, 31),
            "prove_worth",
            "Wants to prove their worth to someone whose opinion matters more than they'll admit.",
        ),
        (
            range(31, 41),
            "recover_something_taken",
            "Wants something taken from them recovered, by whatever means are still open.",
        ),
        (
            range(41, 51),
            "preserve_the_status_quo",
            "Wants things to stay exactly as they are -- believes they're the last one holding "
            "it together.",
        ),
        (
            range(51, 61),
            "gain_advantage_over_a_rival",
            "Wants an advantage over a named rival, and sees this as the opening.",
        ),
        (
            range(61, 71),
            "keep_a_secret_buried",
            "Wants a specific secret to stay buried, whatever the immediate cost.",
        ),
        (
            range(71, 81),
            "be_free_of_an_arrangement",
            "Wants free of an arrangement they no longer chose, but can't simply walk away from.",
        ),
        (
            range(81, 91),
            "settle_an_old_grievance",
            "Wants an old grievance settled that the record has forgotten but they haven't.",
        ),
        (
            range(91, 101),
            "survive_at_any_cost",
            "Wants, above everything else, to survive whatever's coming -- at nearly any expense "
            "to others.",
        ),
    ],
    "oracle-prompt-situation-truth": [
        (
            range(1, 11),
            "deliberate_front",
            "What's presented is a deliberate front; the truth is hidden nearby, not far.",
        ),
        (
            range(11, 21),
            "no_longer_true",
            "What's presented used to be true and no longer is -- nobody has updated it.",
        ),
        (
            range(21, 31),
            "true_but_changing",
            "What's presented is true, but only for now -- it's actively changing.",
        ),
        (
            range(31, 41),
            "true_for_most_not_all",
            "What's presented is true for most people here, but not for the one who matters.",
        ),
        (
            range(41, 51),
            "missing_one_fact",
            "What's presented is missing one crucial fact that changes its meaning entirely.",
        ),
        (
            range(51, 61),
            "true_and_that_is_the_danger",
            "What's presented is true, and the danger is precisely that it looks safe.",
        ),
        (
            range(61, 71),
            "staged_for_someone_else",
            "What's presented was staged for someone specific, not for whoever's here now.",
        ),
        (
            range(71, 81),
            "true_on_the_surface_only",
            "What's presented is true on the surface, false in the details underneath.",
        ),
        (
            range(81, 91),
            "an_honest_mistake",
            "What's presented is a mistake, not a lie -- whoever set it up believed it.",
        ),
        (
            range(91, 101),
            "true_for_the_wrong_reason",
            "What's presented is true, but the reason it's true is not what anyone assumes.",
        ),
    ],
    "oracle-prompt-thread-turn": [
        (
            range(1, 11),
            "someone_switches_sides",
            "Someone involved switches sides, for reasons that make sense to them.",
        ),
        (
            range(11, 21),
            "new_information_reframes_it",
            "New information surfaces that changes what the thread is actually about.",
        ),
        (
            range(21, 31),
            "a_deadline_moves_closer",
            "A deadline moves closer, forced by someone else's unrelated action.",
        ),
        (
            range(31, 41),
            "an_ally_becomes_a_liability",
            "An ally becomes a liability, through no fault of their own.",
        ),
        (
            range(41, 51),
            "the_opposition_escalates",
            "The opposition escalates, using a method not seen from them before.",
        ),
        (
            range(51, 61),
            "an_assumed_resource_is_gone",
            "A resource everyone assumed was available turns out not to be.",
        ),
        (
            range(61, 71),
            "the_goal_was_a_means_to_another",
            "The thread's apparent goal turns out to be a means to a different one.",
        ),
        (
            range(71, 81),
            "an_outsider_intervenes",
            "Someone outside the thread notices it and moves to intervene.",
        ),
        (
            range(81, 91),
            "two_threads_collide",
            "Two threads intersect, and progress on one now costs progress on the other.",
        ),
        (
            range(91, 101),
            "the_thread_stalls",
            "The thread stalls, and staying still becomes its own kind of danger.",
        ),
    ],
    "oracle-prompt-complication": [
        (
            range(1, 11),
            "an_uninvited_party_arrives",
            "An unexpected party arrives, with their own agenda.",
        ),
        (
            range(11, 21),
            "a_resource_fails",
            "A resource runs out or fails at the worst possible moment.",
        ),
        (
            range(21, 31),
            "the_wrong_person_overhears",
            "Something said is overheard by someone who shouldn't have heard it.",
        ),
        (
            range(31, 41),
            "the_environment_turns",
            "The environment itself turns hostile or unstable.",
        ),
        (
            range(41, 51),
            "an_old_debt_comes_due",
            "An old promise or debt comes due, right now.",
        ),
        (
            range(51, 61),
            "a_misunderstanding_compounds",
            "A misunderstanding compounds, and correcting it costs time nobody has.",
        ),
        (
            range(61, 71),
            "help_arrives_at_a_cost",
            "Help arrives, but at a cost nobody agreed to.",
        ),
        (
            range(71, 81),
            "the_plan_works_and_backfires",
            "The plan works, but produces a consequence nobody anticipated.",
        ),
        (
            range(81, 91),
            "an_earlier_choice_catches_up",
            "A choice made earlier in the chronicle catches up here.",
        ),
        (
            range(91, 101),
            "someone_is_not_who_they_seem",
            "Someone present is not who they appear to be.",
        ),
    ],
}


def oracle_prompt(family: str, roll: int) -> tuple[str, str]:
    """Look up a natural 1d100 roll against one of the four oracle-prompt tables.

    docs/design/15-oracle-prompts.md: repeatable, no modifier, ten equal-width rows per
    family. An unrecognized family or an out-of-range roll is a load error, not a table
    quietly skipped (matching `resolution.py`'s `_critical_band` convention).
    """
    if family not in ORACLE_PROMPT_TABLES:
        raise ValueError(
            f"no such oracle prompt family: {family!r} (valid: {sorted(ORACLE_PROMPT_TABLES)})"
        )
    if not isinstance(roll, int) or not (1 <= roll <= 100):
        raise ValueError(f"roll must be an integer 1-100, got {roll!r}")
    for row_range, effect, description in ORACLE_PROMPT_TABLES[family]:
        if roll in row_range:
            return effect, description
    raise AssertionError(f"unreachable: {family} table does not cover roll {roll}")


#: docs/design/14-oracle-answers.md: five fixed likelihood bands, each a Yes-threshold `T` over
#: 1d100. Transcribed verbatim from the design document; `tools/check_oracle_answers.py` verifies
#: these thresholds stay in sync with it.
ORACLE_ANSWER_THRESHOLDS: dict[str, int] = {
    "Near Certain": 90,
    "Likely": 70,
    "Even": 50,
    "Unlikely": 30,
    "Near Impossible": 10,
}


def _oracle_answer_rows(threshold: int) -> list[tuple[range, str]]:
    """The four (range, outcome) rows a Yes-threshold `T` produces (docs/design/14-oracle-
    answers.md): 1-5 exceptional yes, 6-T yes, T+1-95 no, 96-100 exceptional no. Derived from `T`
    rather than hand-transcribed per band, since the shape is a deterministic function of `T`
    alone and `tools/check_oracle_answers.py` already treats it that way.
    """
    return [
        (range(1, 6), "exceptional_yes"),
        (range(6, threshold + 1), "yes"),
        (range(threshold + 1, 96), "no"),
        (range(96, 101), "exceptional_no"),
    ]


def oracle_answer(band: str, roll: int) -> tuple[str, str]:
    """Look up a natural 1d100 roll against one of the five oracle-answer bands.

    docs/design/14-oracle-answers.md: repeatable, no modifier, the band selects which row set
    is read. An unrecognized band or an out-of-range roll is a load error, not a table quietly
    skipped (matching `oracle_prompt`'s convention). Returns `(outcome, wyrd)` -- the outcome key
    and the Wyrd die reading for that same roll, read via this module's own `_wyrd_die` helper:
    "an oracle roll reads the same Wyrd die as every other d100 roll, with no separate mechanism."
    """
    if band not in ORACLE_ANSWER_THRESHOLDS:
        raise ValueError(
            f"no such oracle answer band: {band!r} (valid: {sorted(ORACLE_ANSWER_THRESHOLDS)})"
        )
    if not isinstance(roll, int) or not (1 <= roll <= 100):
        raise ValueError(f"roll must be an integer 1-100, got {roll!r}")
    for row_range, outcome in _oracle_answer_rows(ORACLE_ANSWER_THRESHOLDS[band]):
        if roll in row_range:
            return outcome, _wyrd_die(roll)
    raise AssertionError(f"unreachable: {band} table does not cover roll {roll}")


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
    omen_width: int = 0,
) -> dict:
    """Resolve a single player-facing opposed test (docs/design/03-rules.md "Opposed tests").

    One roll, on the acting side only -- the opponent's dice are never consulted. Degrees of
    success are reported only when the roll succeeds; a failure "simply fails the action"
    with no degrees comparison performed. The Wyrd die is read independently of success.

    `declaration` and `helper_skill` are optional modifiers (specs/077-declaration-assistance)
    added to `skill` before `effective_pct` is computed. Calling with neither is identical to
    calling this function before those modifiers existed -- no default behavior change.
    `declaration == "removes_risk"` skips the roll entirely and reports automatic success.

    `omen_width` passes straight through to `_wyrd_die` (docs/design/12-the-adversary.md
    section 5's `wyrd` trait, specs/096-adversary-trait-effects) -- defaults to 0, no change to
    existing behavior.
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
    wyrd = _wyrd_die(roll, omen_width=omen_width)
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


#: A member with no relevant skill at all is tested at this flat rate (docs/design/03-rules.md
#: "Group tests"), same as the untrained rate for any other test.
UNTRAINED_SKILL = 10

#: docs/design/10-the-character.md section 2, "The scale": a skill opens at this value when an
#: advance grants it, and rises by this amount per further advance. Career-cap enforcement is
#: out of scope here -- no career graph exists in the engine yet (#210).
SKILL_OPEN_VALUE = 25
SKILL_ADVANCE_STEP = 5

GROUP_TEST_MODES = ("most_capable", "least_capable")


def select_group_skill(member_skills: list[int | None], mode: str) -> int:
    """Select which member's skill a group test is actually rolled against.

    `None` in `member_skills` means "no relevant skill at all" and is substituted with the
    untrained rate before selection -- never excluded, per docs/design/03-rules.md: "Leaving
    them behind is a decision available to the party," not something this function decides.
    """
    if not member_skills:
        raise ValueError("member_skills must not be empty")
    if mode not in GROUP_TEST_MODES:
        raise ValueError(f"no such mode: {mode}")
    effective_skills = [UNTRAINED_SKILL if skill is None else skill for skill in member_skills]
    return max(effective_skills) if mode == "most_capable" else min(effective_skills)


def group_test(
    member_skills: list[int | None],
    mode: str,
    opponent: int,
    seed: int | None = None,
    **opposed_test_kwargs,
) -> dict:
    """Resolve a group test: one selection, one roll (docs/design/03-rules.md "Group tests").

    "The party's composition shows in the skill tested, never in the number of dice" -- this
    delegates entirely to `opposed_test` for the actual roll, so a group test can never
    accidentally roll more than once regardless of how many members are listed.
    """
    selected_skill = select_group_skill(member_skills, mode)
    result = opposed_test(selected_skill, opponent, seed=seed, **opposed_test_kwargs)
    return {
        **result,
        "verb": "group-test",
        "member_skills": member_skills,
        "mode": mode,
        "selected_skill": selected_skill,
    }


def resolve_extended_interval(
    skill: int,
    opponent: int,
    progress: int,
    target: int,
    seed: int | None = None,
    **opposed_test_kwargs,
) -> dict:
    """Resolve one interval of an extended task (docs/design/03-rules.md "Extended tasks").

    One test per interval. A success adds its degrees, minimum 1 -- a bare success never
    stalls the work. A failed interval is spent and gains nothing. Progress is not persisted
    here; the caller carries it into the next interval's call.
    """
    result = opposed_test(skill, opponent, seed=seed, **opposed_test_kwargs)
    if result["no_roll"]:
        # No numeric degrees exists for a no-roll declaration; the minimum-1 floor is the
        # closest documented rule for "a success adds its degrees, minimum 1"
        # (specs/078-group-tests-extended-tasks/research.md's Assumption).
        gained = 1
    elif result["success"]:
        gained = max(1, result["degrees"])
    else:
        gained = 0
    new_progress = progress + gained
    return {
        **result,
        "verb": "extended-task-interval",
        "progress": new_progress,
        "target": target,
        "gained": gained,
        "done": new_progress >= target,
    }
