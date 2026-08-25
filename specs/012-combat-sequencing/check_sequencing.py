"""What combat sequencing actually costs.

Five questions this feature is not allowed to answer from intuition (spec FR-14):

  1. How long is a fight, in rounds, at the skills characters actually have?
  2. What is acting first worth?               -- the value of FR-2's turn order
  3. What is a *free* round worth?             -- the gate on FR-8's surprise rule
  4. What rung should the ambush bonus be?     -- chosen, not picked
  5. What does fleeing cost?                   -- FR-7's "never free", as a quantity

A fight is a small absorbing Markov chain over (stamina_a, stamina_b, side_to_act). It is solved
exactly by Gaussian elimination over Fractions -- not sampled and not propagated round by round,
both of which trade an exact answer for an approximate one (ADR 0005). Surprise is applied as an
explicit first move onto the solved chain, so a free round costs the surprised side a whole round
rather than a single attack -- the modelling error the plan flags as the likely one.

Run: python3 specs/012-combat-sequencing/check_sequencing.py
"""

from fractions import Fraction
from functools import lru_cache

DIE = 100
STAMINA = 6      # starting Stamina (03b-the-character.md)
BASE_DAMAGE = 2  # see calibration below


# BASE_DAMAGE is calibrated, not chosen. Issue #44 corrected an earlier claim in this repo and
# established that a combatant takes about 4.5 hits to drop. At Stamina 6 that means a mean of
# roughly 1.5 points getting through per hit; 2 is the nearest value that keeps the state space
# exact, and it yields 4 hits to drop -- close enough to 4.5 to reason with, and stated rather than
# assumed. The earlier draft of this script used 4, which drops a combatant in two hits and made
# every fight three times too short: the same fault #44 caught, reintroduced.
HITS_TO_DROP = STAMINA // BASE_DAMAGE + 1


def degrees(skill: int, roll: int) -> int:
    return skill // 10 - roll // 10


@lru_cache(maxsize=None)
def attack_outcomes(attacker: int, defender: int) -> tuple[tuple[int, Fraction], ...]:
    """((damage, probability), ...) for one attack under today's opposed rule (ADR 0016).

    The attacker must succeed first; ties go to the defender. A telling blow -- a win by 3 or more
    degrees -- doubles the damage. Damage is its mean rather than its distribution: this script
    measures fight *length* and win rates, which the miss rate dominates by an order of magnitude.
    Stated here rather than buried, because the last combat number in this repo went wrong by
    measuring hits when it meant exchanges (issue #44).
    """
    attacker = max(1, min(99, attacker))
    counts: dict[int, int] = {}
    for a in range(1, DIE + 1):
        if a > attacker:
            continue
        da = degrees(attacker, a)
        for d in range(1, DIE + 1):
            if d <= defender and da <= degrees(defender, d):
                continue  # defended
            dmg = BASE_DAMAGE * 2 if da >= 3 else BASE_DAMAGE
            counts[dmg] = counts.get(dmg, 0) + 1
    total = DIE * DIE
    hit = sum(counts.values())
    out = [(d, Fraction(c, total)) for d, c in sorted(counts.items())]
    out.append((0, Fraction(total - hit, total)))  # a miss
    return tuple(out)


def _levels() -> list[int]:
    """Reachable non-negative Stamina values, given a fixed damage size."""
    seen, s = [], STAMINA
    while s >= 0:
        seen.append(s)
        s -= BASE_DAMAGE
    return seen


def _solve(matrix: list[list[Fraction]]) -> list[Fraction]:
    """Exact Gaussian elimination. matrix is augmented, n rows by n+1 columns."""
    n = len(matrix)
    for col in range(n):
        piv = next(r for r in range(col, n) if matrix[r][col] != 0)
        matrix[col], matrix[piv] = matrix[piv], matrix[col]
        inv = matrix[col][col]
        matrix[col] = [v / inv for v in matrix[col]]
        for r in range(n):
            if r != col and matrix[r][col] != 0:
                f = matrix[r][col]
                matrix[r] = [v - f * w for v, w in zip(matrix[r], matrix[col])]
    return [matrix[r][n] for r in range(n)]


@lru_cache(maxsize=None)
def chain(skill_a: int, skill_b: int) -> tuple[dict, dict]:
    """Solve the fight exactly. Returns (P(a wins) by state, expected actions by state)."""
    levels = _levels()
    states = [(sa, sb, side) for sa in levels for sb in levels for side in ("a", "b")]
    index = {s: i for i, s in enumerate(states)}
    n = len(states)

    win = [[Fraction(0)] * (n + 1) for _ in range(n)]
    dur = [[Fraction(0)] * (n + 1) for _ in range(n)]
    for i, (sa, sb, side) in enumerate(states):
        win[i][i] = dur[i][i] = Fraction(1)
        dur[i][n] = Fraction(1)  # this action counts, whatever happens next
        other = "b" if side == "a" else "a"
        atk, dfn = (skill_a, skill_b) if side == "a" else (skill_b, skill_a)
        for dmg, p in attack_outcomes(atk, dfn):
            if side == "a":
                ns, nxt = sb - dmg, (sa, sb - dmg, other)
            else:
                ns, nxt = sa - dmg, (sa - dmg, sb, other)
            if ns < 0:  # absorbed: the defender is out of action
                if side == "a":
                    win[i][n] += p
                continue
            j = index[nxt]
            win[i][j] -= p
            dur[i][j] -= p
    return (
        dict(zip(states, _solve(win))),
        dict(zip(states, _solve(dur))),
    )


def fight(skill_a: int, skill_b: int, first: str = "a") -> tuple[Fraction, Fraction]:
    """(P(a wins), expected rounds) from a standing start."""
    w, d = chain(skill_a, skill_b)
    start = (STAMINA, STAMINA, first)
    return w[start], d[start] / 2  # two actions to a round, one per side


def fight_with_surprise(skill_a: int, skill_b: int, ambush_bonus: int = 0) -> Fraction:
    """P(a wins) when a surprises b: b loses the whole first round (FR-8).

    a acts; b does not act at all; then the ordinary chain resumes with a to act again.
    """
    w, _ = chain(skill_a, skill_b)
    total = Fraction(0)
    for dmg, p in attack_outcomes(skill_a + ambush_bonus, skill_b):
        remaining = STAMINA - dmg
        if remaining < 0:
            total += p  # dropped before ever acting
        else:
            total += p * w[(STAMINA, remaining, "a")]
    return total


def pct(f: Fraction) -> str:
    return f"{float(f) * 100:.1f}%"


PAIRINGS = [(25, 25), (35, 35), (40, 40), (45, 45), (55, 55), (55, 40), (40, 55)]


def main() -> None:
    print(f"Calibration: Stamina {STAMINA}, {BASE_DAMAGE} points through per hit,"
          f" {HITS_TO_DROP} hits to drop (issue #44 computed 4.5).\n")
    print("1-2. Fight length, and what acting first is worth\n")
    print(f"{'A':>4} {'B':>4} | {'rounds':>7} | {'A first':>8} {'B first':>8} | {'edge':>6}")
    print("-" * 52)
    edges = []
    for a, b in PAIRINGS:
        pa_first, rounds = fight(a, b, first="a")
        pa_second, _ = fight(a, b, first="b")
        edges.append(pa_first - pa_second)
        print(f"{a:>4} {b:>4} | {float(rounds):6.1f} | {pct(pa_first):>8} {pct(pa_second):>8}"
              f" | {float(edges[-1]) * 100:+5.1f}")
    print(f"\n  Acting first is worth {float(min(edges)) * 100:+.1f} to"
          f" {float(max(edges)) * 100:+.1f} points of win rate.")

    print("\n\n3. The surprise gate -- what a FREE round is worth\n")
    print(f"{'A':>4} {'B':>4} | {'no surprise':>12} {'A surprises B':>14} | {'gain':>6}")
    print("-" * 48)
    gains, worst = [], Fraction(0)
    for a, b in PAIRINGS:
        base, _ = fight(a, b, first="a")
        surp = fight_with_surprise(a, b)
        gains.append(surp - base)
        worst = max(worst, surp)
        print(f"{a:>4} {b:>4} | {pct(base):>12} {pct(surp):>14} | {float(surp - base) * 100:+5.1f}")
    print(f"\n  A free round is worth {float(min(gains)) * 100:+.1f} to"
          f" {float(max(gains)) * 100:+.1f} points.")
    print(f"  Highest win rate it produces anywhere: {pct(worst)}")
    gate = worst <= Fraction(9, 10)
    print(f"  GATE {'PASSED' if gate else 'FAILED'}: a free round must not make the fight a"
          " formality (FR-8).")

    print("\n\n4. The ambush rung -- eases the free round's attacks only\n")
    header = "  ".join(f"{a}v{b}" for a, b in PAIRINGS[:5])
    print(f"{'rung':>6} | {header}")
    print("-" * (9 + len(header)))
    for rung in (0, 10, 20, 30):
        row = "  ".join(f"{pct(fight_with_surprise(a, b, rung)):>5}" for a, b in PAIRINGS[:5])
        label = f"+{rung}" if rung else "0"
        print(f"{label:>6} | {row}")
    print("\n  +10 and +20 are rungs of the existing difficulty ladder (03-rules.md 1).")
    print("  +30 exceeds the largest declaration bonus in the engine, so an ambush should not")
    print("  reach it -- a prepared ambush is not worth more than a perfectly judged action.")

    print("\n\n5. What fleeing costs -- parting blows on breaking engagement\n")
    print(f"{'opponents':>10} | " + "  ".join(f"{s}%" for s in (25, 40, 55)))
    print("-" * 34)
    for n in (1, 2, 3):
        row = []
        for opp in (25, 40, 55):
            mean = sum(d * p for d, p in attack_outcomes(opp, 40)) * n
            row.append(f"{float(mean):4.2f}")
        print(f"{n:>10} | " + "  ".join(row))
    print(f"\n  Starting Stamina is {STAMINA}. Breaking engagement with three opponents costs a")
    print("  real fraction of it before the group test to get away is even rolled. Flight is")
    print("  never free, and this is how much.")

    # --- assertions: only what this feature owns ---
    assert 4 <= HITS_TO_DROP <= 5, "damage must stay calibrated to issue #44's corrected 4.5 hits"
    assert all(e > 0 for e in edges), "acting first must be an advantage, or FR-2 buys nothing"
    assert max(edges) < Fraction(1, 2), "acting first must not decide the fight on its own"
    assert all(g > 0 for g in gains), "a free round must matter, or surprise is dead text"
    assert gate, "FR-8 gate: a free round must not make the fight a formality"
    print("\n\nAll assertions passed.")


if __name__ == "__main__":
    main()
