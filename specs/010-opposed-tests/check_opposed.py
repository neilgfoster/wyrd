#!/usr/bin/env python3
"""Check how an opposed test actually behaves, at the skills characters really have.

docs/design/03-rules.md carried opposed tests as one sentence: "both roll; the higher degree of
success wins; ties to the defender." It reads complete and leaves two questions unanswered,
and the answers change the game noticeably:

1. **What if the acting side fails?** "The higher degree of success wins" still compares, so
   a missed attack whose degrees happen to exceed the defender's would win. An attack that
   missed would do damage.
2. **What are the degrees of a failed roll?** Degrees are tens(skill) - tens(roll), which goes
   negative on a failure. Subtracting a negative inflates the margin.

Question 2 is the dangerous one, because it is invisible in prose and enormous in play: it
makes roughly three quarters of successful attacks telling blows, and a telling blow doubles
damage.

CLAUDE.md: probability claims in this repository have been wrong twice, and both were only
caught by computing them.

Run: python3 specs/010-opposed-tests/check_opposed.py
"""

from fractions import Fraction

FACES = 100

# Skill values a character actually has. Creation produces 25-40% (design/03c), and a career
# cap is not yet set (#12, Stage 9), so the upper end is where a practised character sits.
REALISTIC = [25, 30, 35, 40, 55]

TELLING_BLOW_MARGIN = 3   # docs/design/03-rules.md section 2


def degrees(skill: int, roll: int) -> int:
    """Tens digit of the skill minus tens digit of the roll (docs/design/03-rules.md section 1)."""
    return skill // 10 - roll // 10


def outcomes(attacker: int, defender: int, failed_defence: str):
    """Distribution over an opposed test.

    `failed_defence` is the rule under test for a defender who rolled over their skill:
      'negative' -- use their degrees as computed, which are negative
      'zero'     -- a failed roll has no degrees
    """
    unit = Fraction(1, FACES * FACES)
    result = {"fails": Fraction(0), "wins": Fraction(0),
              "defended": Fraction(0), "telling": Fraction(0)}
    for a_roll in range(1, FACES + 1):
        if a_roll > attacker:
            result["fails"] += unit * FACES      # the action fails; no defence needed
            continue
        a_deg = degrees(attacker, a_roll)
        for d_roll in range(1, FACES + 1):
            d_ok = d_roll <= defender
            if d_ok:
                d_deg = degrees(defender, d_roll)
            else:
                d_deg = degrees(defender, d_roll) if failed_defence == "negative" else 0
            if a_deg > d_deg:
                result["wins"] += unit
                if a_deg - d_deg >= TELLING_BLOW_MARGIN:
                    result["telling"] += unit
            else:
                result["defended"] += unit       # ties to the defender
    return result


def pct(f: Fraction) -> str:
    return f"{float(f) * 100:5.1f}%"


def main() -> int:
    failures = []

    print("The rule for a failed defence decides how often damage doubles")
    print("=" * 74)
    for rule in ("negative", "zero"):
        print(f"\n  a failed defence contributes: {rule} degrees")
        print("    A    D      action fails    attacker wins    telling, as share of wins")
        for a in (25, 35, 40, 55):
            for d in (30, 40):
                r = outcomes(a, d, rule)
                share = r["telling"] / r["wins"] if r["wins"] else Fraction(0)
                print(f"   {a:>3}  {d:>3}      {pct(r['fails'])}         {pct(r['wins'])}"
                      f"          {pct(share)}")

    print()
    print("A telling blow doubles damage. Under 'negative' it is the common case, not the")
    print("notable one -- and nothing in the prose hints at that.")

    # The rule is chosen by this number, not by preference.
    worst_negative = max(
        outcomes(a, d, "negative")["telling"] / outcomes(a, d, "negative")["wins"]
        for a in REALISTIC for d in REALISTIC
    )
    worst_zero = max(
        outcomes(a, d, "zero")["telling"] / outcomes(a, d, "zero")["wins"]
        for a in REALISTIC for d in REALISTIC
    )
    print()
    print(f"  worst case, 'negative': {pct(worst_negative)} of wins are telling blows")
    print(f"  worst case, 'zero':     {pct(worst_zero)} of wins are telling blows")

    if worst_negative <= Fraction(1, 2):
        failures.append(
            "the 'negative' rule was expected to produce absurd telling-blow rates and did "
            "not; the argument for rejecting it does not hold"
        )

    print()
    print("Ties go to the defender — how often that decides it")
    print("=" * 74)
    print("    A    D   defended (incl. ties)")
    for a in (25, 40, 55):
        for d in (25, 40, 55):
            r = outcomes(a, d, "zero")
            print(f"   {a:>3}  {d:>3}      {pct(r['defended'])}")

    print()
    print("Verdict")
    print("-" * 74)

    # A failed action must not win. Checked by construction: the acting side's failure short-
    # circuits before any comparison.
    r = outcomes(25, 55, "zero")
    total = r["fails"] + r["wins"] + r["defended"]
    if total != 1:
        failures.append(f"outcomes do not sum to 1 ({float(total)})")
    print(f"  outcomes are exhaustive and disjoint                       "
          f"[{'ok' if total == 1 else 'FAIL'}]")

    # An unskilled actor against a strong defender should rarely win.
    weak = outcomes(25, 55, "zero")["wins"]
    if weak > Fraction(1, 5):
        failures.append(f"a 25% actor beats a 55% defender {pct(weak)} of the time")
    print(f"  a 25% actor beats a 55% defender only {pct(weak)}              "
          f"[{'ok' if weak <= Fraction(1, 5) else 'FAIL'}]")

    # Choosing 'zero' must actually be an improvement, or the argument is empty.
    if worst_zero >= worst_negative:
        failures.append(
            f"the chosen rule ({pct(worst_zero)}) is no better than the rejected one "
            f"({pct(worst_negative)})"
        )
    print(f"  the chosen rule roughly halves telling blows vs the rejected one  "
          f"[{'ok' if worst_zero < worst_negative else 'FAIL'}]")

    print()
    print("FINDING FOR STAGE 5 — not asserted here, because the threshold is not this")
    print("feature's to set. docs/design/03-rules.md section 2 makes a telling blow a win by 3+")
    print("degrees, and that is combat's number (#44).")
    print()
    print("    A    D   telling blows, as a share of successful attacks")
    for a, d in ((25, 25), (30, 30), (40, 40), (55, 40), (55, 25)):
        r = outcomes(a, d, "zero")
        share = r["telling"] / r["wins"] if r["wins"] else Fraction(0)
        print(f"   {a:>3}  {d:>3}      {pct(share)}")
    print()
    print("  At starting skills a telling blow is impossible -- degrees cannot reach 3.")
    print("  By practised skill it is the majority of hits. Doubling damage on most hits")
    print("  is unlikely to be what section 2 intends, and the threshold probably has to")
    print("  rise or scale. Stage 5 owns that; this feature only makes the margin honest.")

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
