#!/usr/bin/env python3
"""Compute the critical tables: the modifier that actually occurs, and what each table weighs.

CLAUDE.md: where a claim can be checked by a script, check it. Probability claims in this repo
have been wrong twice and both were caught only by computing them. Every figure
doc/design/08-criticals.md publishes is asserted here, so a change to either fails loudly rather
than reading as authoritative and being wrong.

Nothing about the damage scale is invented here. It is the model specs/013-the-mob-rule already
merged, and this script asserts agreement with the two figures that repo published -- 1.56 points
through modest armour and 4.5 hits to drop a starting character -- because a private damage model
would make everything below internally tidy and wrong.

From merged design documents:

1. Armour subtracts dice -- light 1d3, modest 1d6, heavy 2d6, a minimum of 1 always through
   (doc/design/03-rules.md section 2).
2. A telling blow doubles the damage rolled, before armour subtracts (doc/design/03-rules.md
   section 2).
3. A critical happens when damage takes a combatant below 0 Stamina, and reads 1d6 + points
   below zero (doc/design/03-rules.md section 2, doc/design/07-tables.md).
4. Aftermath reads d100 + 5 x points below zero, and death begins at 111
   (doc/design/09-aftermath.md).
5. A starting character has Stamina 6, 7 after a completed career
   (doc/design/05-character-creation.md, doc/design/03-rules.md section 5).

Weapon damage is setting data (doc/design/26-authoring-a-setting.md), so it is modelled across the
same plausible band the merged scripts used, and no conclusion is allowed to hold at only one
point of it.

Run: python3 specs/015-damage-type-criticals/check_criticals.py
"""

from fractions import Fraction
from functools import lru_cache
from itertools import product

# ---------------------------------------------------------------------------
# Numbers from merged design documents. None of these is chosen here.
# ---------------------------------------------------------------------------

ARMOUR = {"none": [], "light": [3], "modest": [6], "heavy": [6, 6]}
MIN_THROUGH = 1
WEAPON_BAND = [("1d3", [3]), ("1d6", [6]), ("1d8", [8]), ("2d6", [6, 6])]
ORDINARY_WEAPON = [6]          # the mid-band weapon specs/013 calibrated on
STARTING_STAMINA = 6
CAREER_STAMINA = 7
CRITICAL_DIE = 6               # 1d6
AFTERMATH_DEATH_FROM = 111     # doc/design/09-aftermath.md
AFTERMATH_PER_POINT = 5

# The Stamina a combatant actually has left when the blow lands. A fight is not fought at full
# Stamina -- CLAUDE.md is explicit that the numbers get run at real values, not at a midpoint.
REAL_REMAINING = list(range(0, CAREER_STAMINA + 1))

# ---------------------------------------------------------------------------
# The tables this script is testing, stated as data so they can be falsified.
#
# The four share the die, the modifier and the schema. They differ in where each becomes mortal
# and in what each leaves behind: a puncture kills more readily than a bruise and cripples less.
# If they did not differ, damage type would be a rename wearing a mechanic's costume.
# ---------------------------------------------------------------------------

LEGAL_EFFECTS = {"none", "stamina_max", "skill", "dread", "mortal"}

TABLES = {
    "critical-slashing": [
        ((2, 5),   "slashing-glancing",  {"none": True}),
        ((6, 9),   "slashing-scored",    {"dread": 1}),
        ((10, 13), "slashing-opened",    {"skill": -5}),
        ((14, 17), "slashing-hamstrung", {"skill": -10}),
        ((18, 20), "slashing-maimed",    {"stamina_max": -1, "dread": 1}),
        ((21, None), "slashing-mortal",  {"mortal": True}),
    ],
    "critical-piercing": [
        ((2, 4),   "piercing-grazed",     {"none": True}),
        ((5, 8),   "piercing-punctured",  {"skill": -5}),
        ((9, 12),  "piercing-transfixed", {"stamina_max": -1}),
        ((13, 15), "piercing-organ",      {"stamina_max": -1, "skill": -5}),
        ((16, 18), "piercing-collapsed",  {"stamina_max": -2}),
        ((19, None), "piercing-mortal",   {"mortal": True}),
    ],
    "critical-blunt": [
        ((2, 6),   "blunt-winded",      {"none": True}),
        ((7, 11),  "blunt-cracked",     {"skill": -5}),
        ((12, 15), "blunt-broken",      {"skill": -10}),
        ((16, 19), "blunt-shattered",   {"stamina_max": -1, "skill": -5}),
        ((20, 23), "blunt-concussed",   {"stamina_max": -2}),
        ((24, None), "blunt-mortal",    {"mortal": True}),
    ],
    "critical-searing": [
        ((2, 5),   "searing-scorched",  {"none": True}),
        ((6, 9),   "searing-blistered", {"dread": 1}),
        ((10, 13), "searing-seared",    {"skill": -5}),
        ((14, 17), "searing-scarred",   {"dread": 2}),
        ((18, 21), "searing-charred",   {"stamina_max": -1, "dread": 1}),
        ((22, None), "searing-mortal",  {"mortal": True}),
    ],
}

LOWEST_TOTAL = 2   # the die's lowest face is 1, and a critical means at least 1 below zero

# Every figure doc/design/08-criticals.md publishes, asserted below. A table is where staleness
# hides: each row reads as a small factual claim, and nothing about a wrong one looks wrong.
PUBLISHED_MODIFIER_SHARE = {1: 23.3, 2: 12.9, 4: 9.4, 8: 4.6, 12: 2.2}
PUBLISHED_WEIGHTS = {                     # nothing lasting, a lasting mark, mortal
    "critical-piercing": (17.8, 78.6, 3.6),
    "critical-slashing": (27.2, 70.9, 1.8),
    "critical-searing":  (27.2, 71.5, 1.3),
    "critical-blunt":    (38.0, 61.5, 0.5),
}
PUBLISHED_COMPOSED_DEATH = {"critical-blunt": 16.3, "critical-piercing": 17.2}
# specs/015-damage-type-criticals/worked-criticals.md quotes this one, and a figure quoted in a
# playtest note goes stale exactly as readily as one quoted in a design document.
PUBLISHED_MODIFIER_AT_LEAST_15 = 3.8
PUBLISHED_AFTERMATH_ALONE = 16.3
TOLERANCE = 0.05                          # a published figure is quoted to one decimal place


# ---------------------------------------------------------------------------
# The damage model, memoized: every figure correction is a full re-run.
# ---------------------------------------------------------------------------

def _key(faces: list[int]) -> tuple[int, ...]:
    return tuple(faces)


@lru_cache(maxsize=None)
def dice_distribution(faces: tuple[int, ...]) -> tuple[tuple[int, Fraction], ...]:
    if not faces:
        return ((0, Fraction(1)),)
    outcomes = list(product(*[range(1, f + 1) for f in faces]))
    weight = Fraction(1, len(outcomes))
    dist: dict[int, Fraction] = {}
    for roll in outcomes:
        dist[sum(roll)] = dist.get(sum(roll), Fraction(0)) + weight
    return tuple(sorted(dist.items()))


@lru_cache(maxsize=None)
def damage_through(weapon: tuple[int, ...], armour: tuple[int, ...],
                   telling: bool) -> tuple[tuple[int, Fraction], ...]:
    """Damage reaching Stamina after armour, with the minimum-1 floor. One hit."""
    result: dict[int, Fraction] = {}
    for wd, wp in dice_distribution(weapon):
        rolled = wd * 2 if telling else wd
        for ad, ap in dice_distribution(armour):
            t = max(MIN_THROUGH, rolled - ad)
            result[t] = result.get(t, Fraction(0)) + wp * ap
    return tuple(sorted(result.items()))


def mean(dist: tuple[tuple[int, Fraction], ...]) -> Fraction:
    return sum((v * p for v, p in dist), Fraction(0))


def below_zero_distribution(weapon, armour, telling, remaining):
    """Points below zero, given this blow lands on a combatant with this Stamina left.

    Returns (unconditional weight of a drop, {points below zero: weight})."""
    out: dict[int, Fraction] = {}
    dropped = Fraction(0)
    for t, p in damage_through(_key(weapon), _key(armour), telling):
        below = t - remaining
        if below > 0:
            out[below] = out.get(below, Fraction(0)) + p
            dropped += p
    return dropped, out


def modifier_distribution() -> tuple[dict[int, Fraction], int]:
    """Points below zero across every configuration the rules can produce, conditioned on a drop.

    Every weapon in the band, every armour rank, telling and ordinary, every remaining Stamina a
    real character has. Weighted equally across configurations -- this is the span of what occurs,
    not a prediction of one fight.
    """
    agg: dict[int, Fraction] = {}
    total = Fraction(0)
    for _, weapon in WEAPON_BAND:
        for armour in ARMOUR.values():
            for telling in (False, True):
                for remaining in REAL_REMAINING:
                    _, dist = below_zero_distribution(weapon, armour, telling, remaining)
                    for below, p in dist.items():
                        agg[below] = agg.get(below, Fraction(0)) + p
                        total += p
    return {k: v / total for k, v in sorted(agg.items())}, max(agg)


def total_distribution(mod_dist: dict[int, Fraction]) -> dict[int, Fraction]:
    """1d6 + points below zero, over the modifier distribution."""
    out: dict[int, Fraction] = {}
    face = Fraction(1, CRITICAL_DIE)
    for below, p in mod_dist.items():
        for d in range(1, CRITICAL_DIE + 1):
            out[d + below] = out.get(d + below, Fraction(0)) + p * face
    return out


def row_for(table: str, total: int):
    for (lo, hi), key, effect in TABLES[table]:
        if total >= lo and (hi is None or total <= hi):
            return key, effect
    raise AssertionError(f"{table} answers nothing at total {total}")


def aftermath_death_chance(below: int) -> Fraction:
    """P(d100 + 5*below >= 111), the death rows as doc/design/09-aftermath.md publishes them."""
    need = AFTERMATH_DEATH_FROM - AFTERMATH_PER_POINT * below
    if need <= 1:
        return Fraction(1)
    if need > 100:
        return Fraction(0)
    return Fraction(101 - need, 100)


def pct(f: Fraction) -> str:
    return f"{float(f) * 100:.1f}%"


FAILURES: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)


def main() -> int:
    print("=" * 78)
    print("1. Agreement with the damage scale merged issues already computed")
    print("=" * 78)

    ordinary = damage_through(_key(ORDINARY_WEAPON), _key(ARMOUR["modest"]), False)
    through = mean(ordinary)
    hits = Fraction(STARTING_STAMINA + 1) / through
    print(f"  Mean through modest armour, ordinary weapon: {float(through):.2f} per landed blow")
    print(f"  Hits to take a starting character below 0:   {float(hits):.1f}")
    check(abs(float(through) - 1.56) < 0.01,
          f"Mean through modest armour is {float(through):.2f}, against the 1.56 "
          "specs/013-the-mob-rule computed. The damage scale under these tables is not the "
          "merged one.")
    check(abs(float(hits) - 4.5) < 0.05,
          f"Hits to drop is {float(hits):.2f}, against the 4.5 specs/013-the-mob-rule computed.")

    print()
    print("=" * 78)
    print("2. The modifier that actually occurs")
    print("=" * 78)
    mod_dist, max_below = modifier_distribution()
    cum = Fraction(0)
    print("  below zero   share      cumulative   1d6 + it reads")
    for below, p in sorted(mod_dist.items()):
        cum += p
        if below <= 14 or below == max_below:
            print(f"  {below:>9}   {pct(p):>7}   {pct(cum):>10}   {1 + below}-{6 + below}")
    print(f"\n  Largest modifier the rules can produce: {max_below} "
          f"(a doubled telling blow from the heaviest weapon in the band, unarmoured, at 0 left)")
    check(max_below == 24, f"Largest modifier is {max_below}, not the 24 the document publishes.")

    median = min(b for b in sorted(mod_dist) if sum(
        (p for k, p in mod_dist.items() if k <= b), Fraction(0)) >= Fraction(1, 2))
    print(f"  Median modifier: {median}")
    check(median == 4, f"Median modifier is {median}, not the 4 the document publishes.")

    for below, published in PUBLISHED_MODIFIER_SHARE.items():
        got = float(mod_dist[below]) * 100
        check(abs(got - published) < TOLERANCE,
              f"A modifier of {below} occurs {got:.1f}% of the time; the document publishes "
              f"{published}%.")

    tail_15 = sum((p for b, p in mod_dist.items() if b >= 15), Fraction(0))
    print(f"  Share of criticals with a modifier of 15 or more: {pct(tail_15)}")
    check(abs(float(tail_15) * 100 - PUBLISHED_MODIFIER_AT_LEAST_15) < TOLERANCE,
          f"A modifier of 15 or more occurs {float(tail_15) * 100:.1f}% of the time; "
          f"worked-criticals.md quotes {PUBLISHED_MODIFIER_AT_LEAST_15}%.")

    tail_20 = sum((p for b, p in mod_dist.items() if b >= 20), Fraction(0))
    print(f"  Share of criticals with a modifier of 20 or more: {pct(tail_20)}")
    check(tail_20 < Fraction(1, 100),
          "The far tail is no longer under 1%, so the open top is doing more work than stated.")

    print()
    print("=" * 78)
    print("3. Every range is whole")
    print("=" * 78)
    for table, rows in TABLES.items():
        lows = [lo for (lo, _), _, _ in rows]
        check(lows[0] == LOWEST_TOTAL,
              f"{table} starts at {lows[0]}, not at the family's lowest possible total "
              f"{LOWEST_TOTAL}.")
        for i, ((lo, hi), _, _) in enumerate(rows):
            if i + 1 < len(rows):
                check(hi is not None and rows[i + 1][0][0] == hi + 1,
                      f"{table} is not contiguous between rows {i} and {i + 1}.")
            else:
                check(hi is None, f"{table}'s last row is not open at the top.")
        # every total from the lowest to well past the extreme lands on exactly one row
        for total in range(LOWEST_TOTAL, CRITICAL_DIE + max_below + 50):
            hits_rows = [k for (lo, hi), k, _ in rows
                         if total >= lo and (hi is None or total <= hi)]
            check(len(hits_rows) == 1,
                  f"{table} answers total {total} with {len(hits_rows)} rows, not exactly one.")
        for _, key, effect in rows:
            for name in effect:
                check(name in LEGAL_EFFECTS,
                      f"{table} row {key} names effect '{name}', which is not one the engine "
                      "knows.")
            check("trauma" not in effect,
                  f"{table} row {key} charges Trauma, which doc/design/03-rules.md section 5 already "
                  "charges once per critical taken.")
        print(f"  {table:<20} {len(rows)} rows, {lows[0]}-open, every total answered once")

    print()
    print("=" * 78)
    print("4. What each table weighs, at the modifiers that actually occur")
    print("=" * 78)
    totals = total_distribution(mod_dist)
    weights = {}
    print("  table                 nothing lasting   a lasting mark   mortal")
    for table in TABLES:
        nothing = Fraction(0)
        mark = Fraction(0)
        mortal = Fraction(0)
        for total, p in totals.items():
            _, effect = row_for(table, total)
            if effect.get("none"):
                nothing += p
            elif effect.get("mortal"):
                mortal += p
            else:
                mark += p
        weights[table] = (nothing, mark, mortal)
        print(f"  {table:<20}  {pct(nothing):>14}   {pct(mark):>14}   {pct(mortal):>6}")

    for table, (nothing, mark, mortal) in weights.items():
        for got, published, what in (
            (float(nothing) * 100, PUBLISHED_WEIGHTS[table][0], "nothing lasting"),
            (float(mark) * 100, PUBLISHED_WEIGHTS[table][1], "a lasting mark"),
            (float(mortal) * 100, PUBLISHED_WEIGHTS[table][2], "mortal"),
        ):
            check(abs(got - published) < TOLERANCE,
                  f"{table} is {what} {got:.1f}% of the time; the document publishes "
                  f"{published}%.")

    mortals = {t: w[2] for t, w in weights.items()}
    check(max(mortals.values()) - min(mortals.values()) > Fraction(1, 100),
          "The four tables do not differ measurably in lethality, so the damage type is a rename "
          "wearing a mechanic's costume.")
    check(mortals["critical-piercing"] > mortals["critical-blunt"],
          "Piercing is no longer readier to kill than blunt, which is the distinction the four "
          "tables exist to draw.")
    for table, (nothing, mark, mortal) in weights.items():
        check(mortal < Fraction(1, 10),
              f"{table} is mortal {pct(mortal)} of the time -- a critical is meant to be a wound "
              "far more often than a killing.")
        check(nothing > Fraction(15, 100),
              f"{table} leaves nothing lasting only {pct(nothing)} of the time -- a critical that "
              "is always a lasting mark makes the first row decorative.")
    check(max(weights, key=lambda t: weights[t][0]) == "critical-blunt",
          "Blunt is no longer the likeliest to leave nothing lasting, which is the other half of "
          "the distinction the four tables draw.")

    print()
    print("=" * 78)
    print("5. Death, composed through both tables")
    print("=" * 78)
    print("  A mortal critical is read on Aftermath's death row. Everything else rolls Aftermath")
    print("  as published. Both are answered by a spent Fate point.")
    print()
    print("  table                 death, composed   Aftermath alone")
    aftermath_alone = sum(
        (p * aftermath_death_chance(below) for below, p in mod_dist.items()), Fraction(0))
    face = Fraction(1, CRITICAL_DIE)
    for table in TABLES:
        composed = Fraction(0)
        for below, p in mod_dist.items():
            for d in range(1, CRITICAL_DIE + 1):
                _, effect = row_for(table, d + below)
                if effect.get("mortal"):
                    composed += p * face
                else:
                    composed += p * face * aftermath_death_chance(below)
        print(f"  {table:<20}  {pct(composed):>15}   {pct(aftermath_alone):>15}")
        if table in PUBLISHED_COMPOSED_DEATH:
            got = float(composed) * 100
            check(abs(got - PUBLISHED_COMPOSED_DEATH[table]) < TOLERANCE,
                  f"Composed death with {table} is {got:.1f}%; the document publishes "
                  f"{PUBLISHED_COMPOSED_DEATH[table]}%.")
        check(composed - aftermath_alone < Fraction(1, 10),
              f"{table} adds {pct(composed - aftermath_alone)} to the chance a drop ends in "
              "death. Criticals are meant to sharpen deferred death, not to replace it.")

    print(f"\n  Aftermath alone, over the modifiers that occur: {pct(aftermath_alone)}")
    check(abs(float(aftermath_alone) * 100 - PUBLISHED_AFTERMATH_ALONE) < TOLERANCE,
          f"Aftermath alone over the modifiers that occur is {float(aftermath_alone) * 100:.1f}%; "
          f"the document publishes {PUBLISHED_AFTERMATH_ALONE}%.")

    # doc/design/09-aftermath.md publishes 23%, UNWEIGHTED across drops of one to twelve. This
    # script weights by how often each modifier actually occurs, and low modifiers dominate, so
    # the two figures are different questions about the same table. Both are asserted, because
    # taking one for the other is exactly how a stale-but-plausible number survives.
    unweighted = sum((aftermath_death_chance(b) for b in range(1, 13)), Fraction(0)) / 12
    print(f"  Aftermath alone, unweighted across drops of one to twelve: {pct(unweighted)}")
    check(abs(float(unweighted) - 0.23) < 0.01,
          f"Unweighted Aftermath death computes to {pct(unweighted)}, against the 23% "
          "doc/design/09-aftermath.md publishes. One of the two models is wrong.")
    check(aftermath_alone < unweighted,
          "Weighting by the modifiers that actually occur no longer lowers the death rate, which "
          "would mean the modifier distribution has stopped concentrating on light drops.")

    print()
    print("=" * 78)
    print("6. The light blow")
    print("=" * 78)
    earliest_mortal = min(lo for rows in TABLES.values() for (lo, hi), _, e in rows
                          if e.get("mortal"))
    print(f"  Highest total a drop of one point can reach: {CRITICAL_DIE + 1}")
    print(f"  Earliest mortal row on any table begins at:  {earliest_mortal}")
    check(earliest_mortal == 19,
          f"The earliest mortal row begins at {earliest_mortal}, not the 19 the document "
          "publishes.")
    for table in TABLES:
        worst_at_one = row_for(table, CRITICAL_DIE + 1)
        print(f"  {table:<20} dropped by 1, worst possible: {worst_at_one[0]}")
        check(not worst_at_one[1].get("mortal"),
              f"{table} can be mortal on a drop of one point. A light knockdown is meant to be "
              "survivable by construction rather than by luck.")

    print()
    if FAILURES:
        print("FAILED:")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("All checks pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
