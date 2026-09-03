"""Verify the GM-followable per-roll procedure for a telling blow landed via a failed defence
roll reproduces exactly the aggregate rate check_conversion.py's own damage-multiplier modelling
(ADR 0028) already assumed via telling_rate(100 - eff_def, threshold).

Per-roll procedure (03-rules.md sec2, this issue's resolution): a failed defence roll r (r >
eff_def) is read as a virtual attack success -- virtual_eff = 100 - eff_def, virtual_roll = 101
- r -- and degrees are read from that virtual roll exactly as sec1 already does: tens(virtual_eff)
- tens(virtual_roll). Telling blow triggers at degrees >= threshold, the same threshold as
everywhere else (ADR 0028).
"""

import sys
from fractions import Fraction

sys.path.insert(0, "specs/018-player-facing-combat")
from check_conversion import degrees, find_threshold, telling_rate  # noqa: F401

THRESHOLD = find_threshold()


def per_roll_defence_telling_rate(eff_def: int, threshold: int) -> Fraction:
    """The per-roll GM procedure, computed roll by roll over every failed defence roll."""
    hits = 0
    telling = 0
    for r in range(1, 101):
        if r <= eff_def:
            continue  # defence succeeded, no blow lands
        hits += 1
        virtual_eff = 100 - eff_def
        virtual_roll = 101 - r
        d = degrees(virtual_eff, virtual_roll)
        if d >= threshold:
            telling += 1
    return Fraction(telling, hits) if hits else Fraction(0)


def check(claim: str, ok: bool) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {claim}")
    if not ok:
        raise SystemExit(1)


def main() -> int:
    print(f"Telling-blow threshold (reused from check_conversion.py): {THRESHOLD}")
    print(
        "\nPer-roll procedure vs. check_conversion.py's own aggregate modelling"
        " (telling_rate(100 - eff_def, threshold)):\n"
    )
    for eff_def in range(5, 96, 5):
        per_roll = per_roll_defence_telling_rate(eff_def, THRESHOLD)
        aggregate = telling_rate(100 - eff_def, THRESHOLD)
        print(
            f"  eff_def {eff_def:>3}%  per-roll {float(per_roll):.4f}  "
            f"aggregate {float(aggregate):.4f}"
        )
        check(
            f"eff_def={eff_def}: per-roll procedure matches check_conversion.py's own "
            f"aggregate modelling exactly",
            per_roll == aggregate,
        )
    print(
        "\nAll checks passed: the per-roll procedure this ADR states reproduces exactly the "
        "aggregate rate ADR 0028's own damage-multiplier figures already assumed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
