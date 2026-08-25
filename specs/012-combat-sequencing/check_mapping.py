"""Calibrating the player-facing skill mapping.

A finding for #44, computed here because #11 is where the question surfaced.

Direction set on #44: combat moves to player-facing rolls, the opponent's capability becoming a
static number rather than a roll, mapped so an even match is a coin flip:

    effective% = 50 + (player_skill - opponent_skill)

The open question is the *slope*. A half-difference variant, 50 + (S - O) / 2, reads as the more
cautious choice. It is not: it is flat everywhere except an even match, and it needs a 90-point
skill gap to reach the top of the scale at all -- a master against a competent professional still
loses one contest in four.

This script answers the slope question by computing two independent contest models that assume no
linearity at all, and comparing both candidate mappings against them. Exact arithmetic throughout;
no sampling.

Run: python3 specs/012-combat-sequencing/check_mapping.py
"""

from fractions import Fraction

DIE = 100
CLIP_LOW, CLIP_HIGH = 5, 95


def degrees(skill: int, roll: int) -> int:
    """Degrees of success: tens digit of skill minus tens digit of roll (03-rules.md 1)."""
    return skill // 10 - roll // 10


def opposed_adr0016(actor: int, resister: int) -> Fraction:
    """Today's rule. The actor must succeed first; ties go to the resister (ADR 0016)."""
    wins = 0
    for a in range(1, DIE + 1):
        if a > actor:
            continue  # a failed roll has no degrees, and the action simply fails
        da = degrees(actor, a)
        for d in range(1, DIE + 1):
            if d > resister or da > degrees(resister, d):
                wins += 1
    return Fraction(wins, DIE * DIE)


def margin_contest(actor: int, resister: int) -> Fraction:
    """Model A: both roll, higher (skill - roll) wins, ties to the resister. No success gate."""
    wins = sum(
        1
        for a in range(1, DIE + 1)
        for d in range(1, DIE + 1)
        if actor - a > resister - d
    )
    return Fraction(wins, DIE * DIE)


def degrees_contest(actor: int, resister: int) -> Fraction:
    """Model B: both must succeed, higher degrees wins; ties and double failures rerolled.

    Rerolling to exhaustion is the conditional probability given a decisive outcome, so this
    needs no loop -- it is wins over decisive outcomes.
    """
    wins = decisive = 0
    for a in range(1, DIE + 1):
        for d in range(1, DIE + 1):
            hit_a, hit_d = a <= actor, d <= resister
            if hit_a != hit_d:
                decisive += 1
                wins += hit_a
            elif hit_a and hit_d:
                da, dd = degrees(actor, a), degrees(resister, d)
                if da != dd:
                    decisive += 1
                    wins += da > dd
    return Fraction(wins, decisive)


def linear(actor: int, resister: int) -> int:
    """50 + (S - O), clipped so neither certainty nor impossibility is ever reached."""
    return max(CLIP_LOW, min(CLIP_HIGH, 50 + actor - resister))


def half(actor: int, resister: int) -> int:
    """50 + (S - O) / 2, clipped the same way."""
    return max(CLIP_LOW, min(CLIP_HIGH, 50 + (actor - resister) // 2))


PAIRINGS = [
    (25, 25), (40, 40), (35, 30), (55, 40), (50, 30),
    (60, 30), (70, 35), (60, 20), (80, 40), (100, 50), (30, 60),
]


def pct(f: Fraction) -> str:
    return f"{float(f) * 100:.1f}%"


def main() -> None:
    print("Calibrating the player-facing mapping (a finding for #44)\n")
    print(f"{'S':>4} {'O':>4} | {'margin':>7} {'degrees':>8} | {'50+(S-O)':>9} {'50+(S-O)/2':>11}"
          f" | {'opposed today':>13}")
    print("-" * 72)
    worst_linear = worst_half = Fraction(0)
    for actor, resister in PAIRINGS:
        a = margin_contest(actor, resister)
        b = degrees_contest(actor, resister)
        lin, hlf = linear(actor, resister), half(actor, resister)
        print(f"{actor:>4} {resister:>4} | {pct(a):>7} {pct(b):>8} |"
              f" {lin:>8}% {hlf:>10}% | {pct(opposed_adr0016(actor, resister)):>13}")
        for model in (a, b):
            worst_linear = max(worst_linear, abs(Fraction(lin, 100) - model))
            worst_half = max(worst_half, abs(Fraction(hlf, 100) - model))

    print(f"\nWorst deviation from either contest model:")
    print(f"  50 + (S - O)      {float(worst_linear) * 100:.1f} points")
    print(f"  50 + (S - O) / 2  {float(worst_half) * 100:.1f} points")

    # The half-difference mapping's structural fault: it needs an implausible gap to reach the
    # clip at all. A 50-point advantage -- a master against a competent professional -- still
    # loses one contest in four.
    print("\nHow wide a gap each mapping needs to reach the 95% clip:")
    for name, fn in (("50 + (S - O)", linear), ("50 + (S - O) / 2", half)):
        gap = next(g for g in range(0, 201) if fn(g, 0) >= CLIP_HIGH)
        print(f"  {name:<17} {gap} points")
    print("\nA master against a competent professional (100 v 50):")
    print(f"  50 + (S - O)      {linear(100, 50)}%")
    print(f"  50 + (S - O) / 2  {half(100, 50)}%   -- and the contest models say ~87-89%")

    assert worst_linear < worst_half, "slope 1 should track the contest models more closely"
    assert half(100, 50) < 80, "the half-difference mapping is flat where play actually happens"
    assert linear(100, 0) == CLIP_HIGH and linear(0, 100) == CLIP_LOW, "the clip must bind"
    assert linear(40, 40) == 50, "an even match must be a coin flip"
    print("\nAll assertions passed.")


if __name__ == "__main__":
    main()
