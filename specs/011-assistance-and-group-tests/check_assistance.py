#!/usr/bin/env python3
"""Check the three shapes of test added in specs/011, at the skills characters really have.

Two numbers in this feature cannot be chosen by taste, and both are invisible in prose:

1. **The assistance divisor.** A helper's bonus derives from the helper's own skill. Too small
   and nobody bothers to help; too large and one companion moves a test a full rung down the
   difficulty ladder, which makes the ladder decorative. There is also a subtler failure: a cap
   that binds at skills characters actually have collapses a scaled bonus back into a flat one,
   silently undoing the decision it was meant to implement.

2. **The extended-task target scale.** A target is a count of accumulated degrees, and degrees
   are tens(skill) - tens(roll), so the expected gain per interval is around one at average
   skill. A target of 10 is therefore ten rolls -- "only roll when it is dramatic" turned into
   a chore. The scale has to come from the expected gain, not from a tidy-looking number.

CLAUDE.md: probability claims in this repository have been wrong twice, and both were only
caught by computing them.

Run: python3 specs/011-assistance-and-group-tests/check_assistance.py
"""

from fractions import Fraction

FACES = 100

# Skill values a character actually has. Creation produces 25-40% (design/03c-creation.md) and a
# career cap is not yet set (#12, Stage 9), so the upper end is a practised character.
REALISTIC = [25, 30, 35, 40, 45, 55, 65]

# design/03-rules.md section 1. The rungs, as modifiers to the skill.
LADDER = [("Easy", 20), ("Average", 0), ("Challenging", -10),
          ("Difficult", -20), ("Hard", -30), ("Very Hard", -40)]

# The smallest gap between adjacent rungs. A helper may be worth at most this much, or one
# companion silently rewrites the difficulty the GM set.
SMALLEST_RUNG = 10

CANDIDATE_DIVISORS = [2, 3, 5, 10]
CANDIDATE_CAPS = [10, 20]

TARGETS = {"a night's work": 2, "a season's work": 4, "a great labour": 6}
MAX_INTERVALS = 8   # more than this and a long task stops being a handful of beats


def degrees(skill: int, roll: int) -> int:
    """Tens digit of the skill minus tens digit of the roll (design/03-rules.md section 1)."""
    return skill // 10 - roll // 10


def success_rate(effective: int) -> Fraction:
    """d100 at or under the effective skill, which cannot go below 0 or above 100."""
    return Fraction(max(0, min(FACES, effective)), FACES)


def helper_bonus(helper_skill: int, divisor: int, cap: int) -> int:
    return min(helper_skill // divisor, cap)


def expected_gain(effective: int) -> Fraction:
    """Degrees accumulated per interval of an extended task.

    A success adds its degrees, minimum 1 -- otherwise a bare success (roll in the same tens as
    the skill) advances the work by nothing, and a run of them stalls it while still costing
    intervals of fiction. A failure adds nothing.
    """
    eff = max(0, min(FACES, effective))
    total = 0
    for roll in range(1, FACES + 1):
        if roll <= eff:
            total += max(1, degrees(eff, roll))
    return Fraction(total, FACES)


def pct(f: Fraction) -> str:
    return f"{float(f) * 100:5.1f}%"


def main() -> int:
    failures = []

    print("1. How large may a helper's bonus be?")
    print("=" * 74)
    print("A helper's bonus is helper_skill // divisor, capped. Two duties compete: the bonus")
    print("must be worth asking for, and it must never be worth a whole rung of the ladder.")
    print()
    print("  divisor  cap    bonus at helper skill 25 / 40 / 65 / 100   cap binds at")
    for divisor in CANDIDATE_DIVISORS:
        for cap in CANDIDATE_CAPS:
            bonuses = [helper_bonus(s, divisor, cap) for s in (25, 40, 65, 100)]
            binds_at = next((s for s in range(1, 101)
                             if s // divisor >= cap), None)
            binds = f"{binds_at}%" if binds_at else "never"
            print(f"    // {divisor:<3}  +{cap:<3}   "
                  f"{bonuses[0]:>3} /{bonuses[1]:>3} /{bonuses[2]:>3} /{bonuses[3]:>4}"
                  f"                {binds:>6}")

    print()
    print("Rejecting a candidate needs both tests:")
    print(f"  (a) at no realistic helper skill (<= {max(REALISTIC)}%) may the bonus reach "
          f"{SMALLEST_RUNG}")
    print("  (b) the cap must not bind at a realistic helper skill, or the bonus is flat in")
    print("      every case that matters and the helper's own skill has stopped setting it")
    print()
    survivors = []
    for divisor in CANDIDATE_DIVISORS:
        for cap in CANDIDATE_CAPS:
            worst = max(helper_bonus(s, divisor, cap) for s in REALISTIC)
            binds = any(s // divisor >= cap for s in REALISTIC)
            ok_a = worst < SMALLEST_RUNG
            ok_b = not binds
            verdict = "kept" if (ok_a and ok_b) else "rejected"
            why = []
            if not ok_a:
                why.append(f"worth +{worst}, a whole rung")
            if not ok_b:
                why.append("cap binds at realistic skill; scaling is decorative")
            print(f"  // {divisor}, cap +{cap:<3} {verdict:<9} {'; '.join(why)}")
            if ok_a and ok_b:
                survivors.append((divisor, cap))

    if not survivors:
        failures.append("no assistance rule survives both tests")
    print()
    print(f"  surviving: {survivors}")

    divisor, cap = survivors[0] if survivors else (10, 10)

    print()
    print("2. Is the surviving rule worth asking for?")
    print("=" * 74)
    print("  actor  rung          alone    + helper 30%   + helper 65%")
    for actor in (35, 45, 55):
        for rung, mod in LADDER[2:5]:
            alone = success_rate(actor + mod)
            weak = success_rate(actor + mod + helper_bonus(30, divisor, cap))
            strong = success_rate(actor + mod + helper_bonus(65, divisor, cap))
            print(f"   {actor:>3}%  {rung:<12} {pct(alone)}       {pct(weak)}        "
                  f"{pct(strong)}")

    lift = success_rate(45 + helper_bonus(65, divisor, cap)) - success_rate(45)
    if lift <= 0:
        failures.append("a skilled helper does not improve the test at all")
    print()
    print(f"  a 65% helper lifts a 45% actor by {pct(lift)} in absolute terms -- real, and")
    print("  nowhere near a rung. A 30% helper is nearly worthless, which is the point: help")
    print("  from someone who cannot do the task is not assistance.")

    print()
    print("3. What no-stacking is buying")
    print("=" * 74)
    print("If every willing companion added a flat +10 instead, at a Hard test:")
    print("  actor   alone   +1 helper  +2  +3  +4")
    for actor in (35, 45, 55):
        row = [pct(success_rate(actor - 30 + 10 * n)) for n in range(5)]
        print(f"   {actor:>3}%   {row[0]}   {row[1]}  {row[2]}  {row[3]}  {row[4]}")
    naive = success_rate(45 - 30 + 40)
    chosen = success_rate(45 - 30 + helper_bonus(65, divisor, cap))
    if naive <= chosen:
        failures.append("naive stacking is no worse than the chosen rule; FR-2 buys nothing")
    print()
    print(f"  A party of five turns a Hard test at 45% from {pct(success_rate(15))} into "
          f"{pct(naive)}.")
    print("  That is the rung the GM chose, deleted by turning up with friends.")

    print()
    print("4. The extended-task target scale")
    print("=" * 74)
    print("Expected degrees gained per interval (a success adds its degrees, minimum 1):")
    print("  effective skill   gain/interval   intervals for a target of 2 / 4 / 6")
    for eff in (25, 35, 45, 55, 65, 75):
        gain = expected_gain(eff)
        if gain == 0:
            continue
        cols = "  ".join(f"{float(t / gain):5.1f}" for t in TARGETS.values())
        print(f"       {eff:>3}%          {float(gain):5.2f}            {cols}")

    competent = 45
    gain = expected_gain(competent)
    worst_target = max(TARGETS.values())
    intervals = worst_target / gain
    ok = intervals <= MAX_INTERVALS
    if not ok:
        failures.append(
            f"the largest target takes {float(intervals):.1f} intervals at {competent}% -- "
            f"more than the {MAX_INTERVALS} that keeps a long task a handful of beats"
        )
    print()
    print(f"  At a competent {competent}%, the largest target takes "
          f"{float(intervals):.1f} intervals   "
          f"[{'ok' if ok else 'FAIL'}]")
    print("  At 25% it takes far longer, and the rule says so rather than hiding it: an")
    print("  extended task at a skill you barely have is not a long task, it is a wall. Bring")
    print("  a helper, or the GM lowers the difficulty, or it is not attempted.")

    print()
    print("5. The minimum-1 rule is load-bearing")
    print("=" * 74)
    print("Without it, a success whose roll falls in the same tens as the skill advances the")
    print("work by nothing while still spending an interval.")
    print("  effective skill   gain with min-1   gain without")
    for eff in (25, 35, 45, 55, 65):
        with_min = expected_gain(eff)
        without = Fraction(sum(max(0, degrees(eff, r)) for r in range(1, eff + 1)), FACES)
        print(f"       {eff:>3}%           {float(with_min):5.2f}            {float(without):5.2f}")
    stall = Fraction(sum(1 for r in range(1, 26) if degrees(25, r) == 0), 25)
    print()
    print(f"  At 25% skill, {pct(stall)} of successes would gain nothing at all.")
    if stall <= 0:
        failures.append("the minimum-1 rule protects against nothing")

    print()
    print("Verdict")
    print("-" * 74)
    print(f"  assistance: helper_skill // {divisor}, capped at +{cap}")
    print(f"  extended tasks: targets of {', '.join(str(v) for v in TARGETS.values())} degrees")
    print()
    print("FINDING FOR STAGE 5 -- not asserted here. Assistance applies to attacks, which are")
    print("opposed tests, and a helper is worth a few points of skill on both sides. Whether")
    print("companions may assist an attack at all, and whether the telling-blow margin should")
    print("see an assisted actor's degrees, is combat's to settle (#44).")

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
