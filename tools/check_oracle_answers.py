#!/usr/bin/env python3
"""Verify the oracle-answer table's probabilities.

Computes, for every likelihood band, the exact d100 row widths and resulting
outcome probabilities, and asserts them against the numbers claimed in
research.md and docs/design/12-oracle-answers.md. Run directly; exits non-zero
on any mismatch (CLAUDE.md: "check the maths").
"""

from __future__ import annotations

BANDS: dict[str, int] = {
    "Near Certain": 90,
    "Likely": 70,
    "Even": 50,
    "Unlikely": 30,
    "Near Impossible": 10,
}

# (band, exceptional_yes%, yes%, no%, exceptional_no%, total_yes%, total_no%)
CLAIMED = {
    "Near Certain": (5, 85, 5, 5, 90, 10),
    "Likely": (5, 65, 25, 5, 70, 30),
    "Even": (5, 45, 45, 5, 50, 50),
    "Unlikely": (5, 25, 65, 5, 30, 70),
    "Near Impossible": (5, 5, 85, 5, 10, 90),
}


def rows_for(threshold: int) -> tuple[range, range, range, range]:
    """The four row ranges (1-indexed, inclusive) a threshold T produces."""
    exceptional_yes = range(1, 6)
    yes = range(6, threshold + 1)
    no = range(threshold + 1, 96)
    exceptional_no = range(96, 101)
    return exceptional_yes, yes, no, exceptional_no


def widths(ranges: tuple[range, ...]) -> tuple[int, ...]:
    return tuple(len(r) for r in ranges)


def main() -> int:
    failures = []

    for band, threshold in BANDS.items():
        if not (5 <= threshold <= 90):
            failures.append(f"{band}: threshold {threshold} out of the 5-90 safe range")
            continue

        ranges = rows_for(threshold)
        w = widths(ranges)
        total = sum(w)
        if total != 100:
            failures.append(f"{band}: row widths {w} sum to {total}, not 100")

        # Contiguity and coverage of the whole 1-100 space, no gaps or overlaps.
        covered = sorted(v for r in ranges for v in r)
        if covered != list(range(1, 101)):
            failures.append(f"{band}: rows do not exactly cover 1-100")

        exc_yes, yes, no, exc_no = w
        total_yes = exc_yes + yes
        total_no = no + exc_no

        claimed = CLAIMED[band]
        computed = (exc_yes, yes, no, exc_no, total_yes, total_no)
        if computed != claimed:
            failures.append(f"{band}: computed {computed} != claimed {claimed}")

        print(
            f"{band:16s} T={threshold:2d}  "
            f"exc-yes={exc_yes:2d}%  yes={yes:2d}%  no={no:2d}%  exc-no={exc_no:2d}%  "
            f"| total yes={total_yes:2d}%  total no={total_no:2d}%"
        )

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f" - {f}")
        return 1

    print(
        "\nAll bands check out: row widths cover 1-100 exactly, and match the claimed odds."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
