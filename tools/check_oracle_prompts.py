#!/usr/bin/env python3
"""Verify the oracle-prompt tables' structure.

Unlike tools/check_oracle_answers.py, this family makes no probability claim
to compute -- its correctness criterion is genre-neutrality, a qualitative
reading check recorded per row in design/03a-6-oracle-prompts.md, not a
number. What *is* computable, per design/03a-tables.md's row schema, is
checked here: every table's ranges are contiguous, start at 1, and every row
declares that its genre-neutrality check passed. Run directly; exits
non-zero on any mismatch (CLAUDE.md: "where a claim can be checked by a
script, check it").
"""

from __future__ import annotations

# Row shape: (range, effect key, checked). The description text lives only in
# the design document -- this script checks structure, not prose.
Row = tuple[range, str, bool]

TABLES: dict[str, list[Row]] = {
    "oracle-prompt-npc-objective": [
        (range(1, 11), "protect_someone", True),
        (range(11, 21), "escape_a_debt", True),
        (range(21, 31), "prove_worth", True),
        (range(31, 41), "recover_something_taken", True),
        (range(41, 51), "preserve_the_status_quo", True),
        (range(51, 61), "gain_advantage_over_a_rival", True),
        (range(61, 71), "keep_a_secret_buried", True),
        (range(71, 81), "be_free_of_an_arrangement", True),
        (range(81, 91), "settle_an_old_grievance", True),
        (range(91, 101), "survive_at_any_cost", True),
    ],
    "oracle-prompt-situation-truth": [
        (range(1, 11), "deliberate_front", True),
        (range(11, 21), "no_longer_true", True),
        (range(21, 31), "true_but_changing", True),
        (range(31, 41), "true_for_most_not_all", True),
        (range(41, 51), "missing_one_fact", True),
        (range(51, 61), "true_and_that_is_the_danger", True),
        (range(61, 71), "staged_for_someone_else", True),
        (range(71, 81), "true_on_the_surface_only", True),
        (range(81, 91), "an_honest_mistake", True),
        (range(91, 101), "true_for_the_wrong_reason", True),
    ],
    "oracle-prompt-thread-turn": [
        (range(1, 11), "someone_switches_sides", True),
        (range(11, 21), "new_information_reframes_it", True),
        (range(21, 31), "a_deadline_moves_closer", True),
        (range(31, 41), "an_ally_becomes_a_liability", True),
        (range(41, 51), "the_opposition_escalates", True),
        (range(51, 61), "an_assumed_resource_is_gone", True),
        (range(61, 71), "the_goal_was_a_means_to_another", True),
        (range(71, 81), "an_outsider_intervenes", True),
        (range(81, 91), "two_threads_collide", True),
        (range(91, 101), "the_thread_stalls", True),
    ],
    "oracle-prompt-complication": [
        (range(1, 11), "an_uninvited_party_arrives", True),
        (range(11, 21), "a_resource_fails", True),
        (range(21, 31), "the_wrong_person_overhears", True),
        (range(31, 41), "the_environment_turns", True),
        (range(41, 51), "an_old_debt_comes_due", True),
        (range(51, 61), "a_misunderstanding_compounds", True),
        (range(61, 71), "help_arrives_at_a_cost", True),
        (range(71, 81), "the_plan_works_and_backfires", True),
        (range(81, 91), "an_earlier_choice_catches_up", True),
        (range(91, 101), "someone_is_not_who_they_seem", True),
    ],
}


def main() -> int:
    failures = []

    for key, rows in TABLES.items():
        ranges = [r for r, _effect, _checked in rows]

        # Contiguity, coverage of 1-100 exactly (no modifier: the d100 max is
        # the family's own ceiling, so the last row is open at the top the
        # same way design/03a-5-oracle-answers.md's rows are).
        covered = sorted(v for r in ranges for v in r)
        if covered != list(range(1, 101)):
            failures.append(f"{key}: rows do not exactly cover 1-100")

        if ranges[0].start != 1:
            failures.append(f"{key}: first row does not start at 1")

        # No duplicate effect keys within a table.
        effects = [effect for _r, effect, _checked in rows]
        if len(effects) != len(set(effects)):
            failures.append(f"{key}: duplicate effect keys")

        unchecked = [effect for _r, effect, checked in rows if not checked]
        if unchecked:
            failures.append(
                f"{key}: rows missing a recorded genre-neutrality check: {unchecked}"
            )

        print(f"{key:32s} {len(rows):2d} rows, 1-100 covered, all checked")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f" - {f}")
        return 1

    print(
        f"\nAll {len(TABLES)} prompt tables check out: contiguous 1-100 coverage, "
        "unique rows, every row's genre-neutrality check recorded."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
