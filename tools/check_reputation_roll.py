#!/usr/bin/env python3
"""Verify `roll_standing`'s band-width maths (#280).

Computes, for a swept range of Standing scores, the (favourable, neutral, unfavourable) row
widths `economy.standing_bands` returns and asserts they sum to exactly 100 and cover 1-100 with
no gaps or overlaps -- the same shape `check_oracle_answers.py` already asserts for the oracle
table (CLAUDE.md: "check the maths"). Run directly; exits non-zero on any mismatch.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "engine"))

from wyrd import economy

#: Sweeps well past the ±9 point where each band caps at 45 (5 + 5*9 = 50, clamped to 45), so the
#: cap itself is exercised alongside the unclamped middle.
STANDING_SCORES = list(range(-15, 16))


def rows_for(favourable: int, neutral: int, unfavourable: int) -> tuple[range, range, range]:
    """The three row ranges (1-indexed, inclusive) a band-width triple produces."""
    fav = range(1, favourable + 1)
    neu = range(favourable + 1, favourable + neutral + 1)
    unfav = range(favourable + neutral + 1, 101)
    return fav, neu, unfav


def main() -> int:
    failures = []

    for standing in STANDING_SCORES:
        favourable, neutral, unfavourable = economy.standing_bands(standing)
        total = favourable + neutral + unfavourable
        if total != 100:
            failures.append(
                f"standing={standing}: widths ({favourable}, {neutral}, {unfavourable}) "
                f"sum to {total}, not 100"
            )
            continue

        ranges = rows_for(favourable, neutral, unfavourable)
        covered = sorted(v for r in ranges for v in r)
        if covered != list(range(1, 101)):
            failures.append(f"standing={standing}: rows do not exactly cover 1-100")

        if neutral < 50:
            failures.append(f"standing={standing}: neutral width {neutral} fell below the 50 floor")

        print(
            f"standing={standing:3d}  favourable={favourable:2d}%  "
            f"neutral={neutral:2d}%  unfavourable={unfavourable:2d}%"
        )

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f" - {f}")
        return 1

    print("\nAll bands check out: row widths cover 1-100 exactly for every Standing score tried.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
