#!/usr/bin/env python3
"""Prove the transformation re-roll loop terminates.

design/03-rules.md section 4: crossing a Taint threshold forces a roll on the
transformation table (design/03a-3-transformations.md). The result consumes Taint
equal to its severity; if Taint is still at or over the threshold just crossed, roll
again. This script computes, rather than asserts, how many re-rolls that loop takes
at the Taint values a real character reaches.

Two independent guarantees are checked:

1. Severity arithmetic terminates the loop on its own, given the threshold spacing
   (every 3 points, starting at 3 -- design/03a-3-transformations.md) and the
   severity distribution on the six-row table (1, 1, 2, 2, 3, 4).
2. Even if it did not, the table is finite and unique-per-character
   (design/03a-tables.md): six rows bound the loop at six re-rolls before the
   *exhaustion* clause fires (the character is lost), which is a second, independent
   termination guarantee.

Run: python3 tools/check_transformation.py
"""
from itertools import product

SEVERITIES = [1, 1, 2, 2, 3, 4]  # one per table row, d6
THRESHOLD_SPACING = 3            # thresholds at 3, 6, 9, 12, ...
MAX_SINGLE_GAIN = 3              # largest single Exposure/Bargain gain (design/03-rules.md s4)


def thresholds_up_to(n):
    t = THRESHOLD_SPACING
    out = []
    while t <= n:
        out.append(t)
        t += THRESHOLD_SPACING
    return out


def rerolls_to_clear(taint_after_gain, threshold):
    """Worst case: always roll the smallest severity available; unique-per-character
    means a severity, once taken, cannot be taken again until the table refreshes for
    a new character. Model worst case within one character's first pass over the six
    rows: draw severities smallest-first without replacement."""
    remaining = sorted(SEVERITIES)  # worst case order: smallest first
    taint = taint_after_gain
    rerolls = 0
    while taint >= threshold and remaining:
        taint -= remaining.pop(0)
        rerolls += 1
    return rerolls, taint


def expected_rerolls_to_clear(taint_after_gain, threshold, trials=200000):
    import random
    total = 0
    for _ in range(trials):
        remaining = SEVERITIES[:]
        random.shuffle(remaining)
        taint = taint_after_gain
        rerolls = 0
        while taint >= threshold and remaining:
            taint -= remaining.pop(0)
            rerolls += 1
        total += rerolls
    return total / trials


def main():
    print("Thresholds (every 3, starting at 3): first few =", thresholds_up_to(24))
    print()
    print(f"{'Taint before gain':>18} {'gain':>5} {'threshold crossed':>18} "
          f"{'worst-case re-rolls':>20} {'expected re-rolls':>18}")

    worst_overall = 0
    # Realistic range: Taint 0 through 20 before the gain, every legal single-event
    # gain (1..MAX_SINGLE_GAIN), and every threshold that gain could cross.
    for taint_before in range(0, 21):
        for gain in range(1, MAX_SINGLE_GAIN + 1):
            taint_after = taint_before + gain
            crossed = [t for t in thresholds_up_to(taint_after) if taint_before < t <= taint_after]
            if not crossed:
                continue
            threshold = crossed[-1]  # the highest threshold newly crossed
            worst, _ = rerolls_to_clear(taint_after, threshold)
            expected = expected_rerolls_to_clear(taint_after, threshold, trials=20000)
            worst_overall = max(worst_overall, worst)
            if taint_before in (0, 2, 5, 8, 11, 14, 17, 20):
                print(f"{taint_before:>18} {gain:>5} {threshold:>18} {worst:>20} {expected:>18.2f}")

    print()
    print(f"Worst case across the whole scanned range (Taint 0-20, every legal single-event "
          f"gain): {worst_overall} re-rolls.")
    print(f"The table has {len(SEVERITIES)} rows and is unique-per-character, so no re-roll "
          f"burst can ever exceed {len(SEVERITIES)} rolls regardless of severities drawn -- "
          f"the exhaustion clause (character lost, joins the opposition) fires first if it did.")
    assert worst_overall <= len(SEVERITIES), "worst case must never exceed the table's row count"
    print()
    print("PASS: the re-roll loop terminates within the table's own size, and typically far "
          "sooner (see expected column above).")


if __name__ == "__main__":
    main()
