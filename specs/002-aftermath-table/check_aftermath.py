#!/usr/bin/env python3
"""Check the Aftermath table's ranges and distribution against the rows as written.

CLAUDE.md: where a claim can be checked by a script, check it. Probability claims in this
repository have been wrong twice, and both were only caught by computing them.

Two things are verified here:

1. **Structure.** Ranges are contiguous, non-overlapping, start at the family's lowest
   possible total, and the last row is open at the top -- so every total the roll can
   produce lands on exactly one row (design/03a-tables.md).
2. **Weighting.** design/03-rules.md already claims "most results are a lasting mark rather
   than death". That has to be true of the rows as written, across the range of modifiers a
   character actually experiences -- not only at the midpoint.

Run: python3 specs/002-aftermath-table/check_aftermath.py
"""

from fractions import Fraction

# The family's roll: d100 + (5 x points below zero). Nothing else modifies the total.
#
# The tone contract's `mortality` knob deliberately does NOT modify the roll. An earlier
# draft had it as a +/-10 adjustment and this script rejected it: at mortality: low the
# lowest possible total became -4 rather than 6, so the first row no longer sat at the
# family's lowest total, and at mortality: high a combatant dropped by only 1 could reach
# the death row -- which is precisely what deferred death exists to prevent. `mortality`
# is an application rule instead (see MORTALITY_CLOSES_DEATH_ROWS below), which is also
# what design/01-principles.md literally says: it governs "how the Aftermath table is
# applied", not what is rolled.
DIE_FACES = 100
PER_POINT_BELOW_ZERO = 5

# At mortality: low the death rows are closed and re-read as the worst non-death row --
# the same mechanism a spent Fate point uses. No new machinery, and the roll is untouched.
MORTALITY_CLOSES_DEATH_ROWS = {"low": True, "standard": False, "high": False}

# Rows as written in design/03a-2-aftermath.md.
# (low, high or None for open-topped, key, is_death, is_lasting_mark)
ROWS = [
    (6, 30, "out-of-action", False, False),
    (31, 52, "lasting-wound", False, True),
    (53, 66, "left-for-dead", False, True),
    (67, 78, "new-enemy", False, True),
    (79, 88, "taken", False, True),
    (89, 98, "disfigured", False, True),
    (99, 110, "recurring-wound", False, True),
    (111, None, "death", True, False),
]

# The lowest total the family can produce: lowest die face (1), plus the smallest legal
# modifier. A critical happens when damage takes a combatant below 0 Stamina, so points
# below zero is at least 1.
MIN_POINTS_BELOW_ZERO = 1
LOWEST_POSSIBLE_TOTAL = 1 + PER_POINT_BELOW_ZERO * MIN_POINTS_BELOW_ZERO

# Points below zero seen in play. Stamina is small and damage is doubled by a telling blow,
# so a drop of 1-3 is ordinary and a drop past 8 means something went badly wrong.
REALISTIC_POINTS_BELOW_ZERO = range(1, 13)


def check_structure() -> list[str]:
    """Ranges contiguous, non-overlapping, correctly anchored, open at the top."""
    problems = []

    if ROWS[0][0] != LOWEST_POSSIBLE_TOTAL:
        problems.append(
            f"first row starts at {ROWS[0][0]}, but the lowest possible total is "
            f"{LOWEST_POSSIBLE_TOTAL} -- totals below the first row would be unanswered"
        )

    for i, (low, high, key, _, _) in enumerate(ROWS):
        if high is not None and high < low:
            problems.append(f"row {key}: range {low}-{high} is inverted")
        if i + 1 < len(ROWS):
            if high is None:
                problems.append(f"row {key} is open at the top but is not the last row")
                continue
            next_low = ROWS[i + 1][0]
            if next_low != high + 1:
                gap = "gap" if next_low > high + 1 else "overlap"
                problems.append(
                    f"{gap} between {key} (ends {high}) and {ROWS[i + 1][2]} "
                    f"(starts {next_low})"
                )

    if ROWS[-1][1] is not None:
        problems.append(
            f"last row {ROWS[-1][2]} ends at {ROWS[-1][1]}; it must be open at the top, "
            "because the modifier is unbounded"
        )

    return problems


def row_for(total: int) -> str:
    for low, high, key, _, _ in ROWS:
        if total >= low and (high is None or total <= high):
            return key
    raise AssertionError(f"total {total} landed on no row")


WORST_NON_DEATH_ROW = [key for _, _, key, is_death, _ in ROWS if not is_death][-1]


def distribution(points_below_zero: int, mortality: str = "standard"):
    """Exact probability of each row's key at this modifier. d100 is uniform."""
    modifier = PER_POINT_BELOW_ZERO * points_below_zero
    closes_death = MORTALITY_CLOSES_DEATH_ROWS[mortality]
    counts: dict[str, int] = {}
    for face in range(1, DIE_FACES + 1):
        key = row_for(face + modifier)
        if closes_death and key == "death":
            key = WORST_NON_DEATH_ROW
        counts[key] = counts.get(key, 0) + 1
    return {k: Fraction(v, DIE_FACES) for k, v in counts.items()}


def every_total_lands_on_a_row() -> list[str]:
    """The claim that no total is unanswered, checked rather than assumed."""
    problems = []
    for pbz in REALISTIC_POINTS_BELOW_ZERO:
        modifier = PER_POINT_BELOW_ZERO * pbz
        for face in range(1, DIE_FACES + 1):
            total = face + modifier
            if total < ROWS[0][0]:
                problems.append(
                    f"dropped by {pbz}, die {face}: total {total} falls below the "
                    f"first row ({ROWS[0][0]})"
                )
                break
            try:
                row_for(total)
            except AssertionError as exc:
                problems.append(str(exc))
                break
    return problems


def pct(fraction: Fraction) -> str:
    return f"{float(fraction) * 100:5.1f}%"


def main() -> int:
    failures = []

    print("Structure")
    print("---------")
    problems = check_structure()
    problems += every_total_lands_on_a_row()
    if problems:
        failures += problems
        for p in problems:
            print(f"  FAIL  {p}")
    else:
        print(f"  ok    ranges contiguous from {LOWEST_POSSIBLE_TOTAL}, open at the top")
        print("  ok    every reachable total lands on exactly one row")

    print()
    print("Distribution by how hard the combatant dropped (mortality: standard)")
    print("-------------------------------------------------------------------")
    keys = [r[2] for r in ROWS]
    header = "  drop  " + "".join(f"{k[:9]:>10}" for k in keys)
    print(header)
    for pbz in REALISTIC_POINTS_BELOW_ZERO:
        dist = distribution(pbz)
        line = f"  {pbz:>4}  " + "".join(
            f"{pct(dist.get(k, Fraction(0))):>10}" for k in keys
        )
        print(line)

    print()
    print("The ruleset's own claim: most results are a lasting mark rather than death")
    print("--------------------------------------------------------------------------")
    print("  drop     mark     death   nothing")
    for pbz in REALISTIC_POINTS_BELOW_ZERO:
        dist = distribution(pbz)
        mark = sum(
            (dist.get(k, Fraction(0)) for _, _, k, _, lasting in ROWS if lasting),
            Fraction(0),
        )
        death = sum(
            (dist.get(k, Fraction(0)) for _, _, k, d, _ in ROWS if d), Fraction(0)
        )
        nothing = Fraction(1) - mark - death
        print(f"  {pbz:>4}  {pct(mark)}  {pct(death)}  {pct(nothing)}")

    # The claim has to hold across the realistic range, not at a chosen point.
    print()
    marks, deaths = [], []
    for pbz in REALISTIC_POINTS_BELOW_ZERO:
        dist = distribution(pbz)
        marks.append(
            sum(
                (dist.get(k, Fraction(0)) for _, _, k, _, lst in ROWS if lst),
                Fraction(0),
            )
        )
        deaths.append(
            sum((dist.get(k, Fraction(0)) for _, _, k, d, _ in ROWS if d), Fraction(0))
        )

    mean_mark = sum(marks, Fraction(0)) / len(marks)
    mean_death = sum(deaths, Fraction(0)) / len(deaths)
    print(f"  Across drops of 1-12, unweighted: mark {pct(mean_mark)}, "
          f"death {pct(mean_death)}")

    if mean_mark <= mean_death:
        failures.append(
            "the ruleset claims most results are a lasting mark rather than death, but "
            f"across the realistic range death ({pct(mean_death)}) is not the minority "
            f"outcome against marks ({pct(mean_mark)})"
        )

    # A soft knockdown must not be able to kill: that is what deferred death is for.
    soft_knockdown_fatal = [
        pbz
        for pbz in (1, 2)
        for m in MORTALITY_CLOSES_DEATH_ROWS
        if distribution(pbz, m).get("death", Fraction(0)) != 0
    ]
    if soft_knockdown_fatal:
        failures.append(
            f"a combatant dropped by only {sorted(set(soft_knockdown_fatal))} can reach "
            "the death row; deferred death is supposed to make a light knockdown "
            "survivable"
        )
    print(
        "  A drop of 1-2 cannot reach the death row, at any mortality      "
        f"[{'FAIL' if soft_knockdown_fatal else 'ok'}]"
    )

    # At mortality: low nobody dies on the table at all -- Fate's mechanism, applied by
    # the setting. Checked, because it is the whole content of the `mortality` claim.
    low_deaths = [
        pbz
        for pbz in REALISTIC_POINTS_BELOW_ZERO
        if distribution(pbz, "low").get("death", Fraction(0)) != 0
    ]
    if low_deaths:
        failures.append(
            f"mortality: low still produces death results at drops {low_deaths}; it is "
            "supposed to close the death rows entirely"
        )
    print(
        "  mortality: low closes the death rows entirely                   "
        f"[{'FAIL' if low_deaths else 'ok'}]"
    )

    print()
    if failures:
        print(f"FAILED: {len(failures)} problem(s)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
