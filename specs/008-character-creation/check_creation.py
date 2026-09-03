#!/usr/bin/env python3
"""Derive the starting values for a new character, by computing rather than picking.

CLAUDE.md: where a claim can be checked by a script, check it -- probability claims in this
repository have been wrong twice, and both were only caught by computing them. Starting
Stamina in particular is not a taste decision: four things already merged constrain it, and
this script finds the values that satisfy all four.

The constraints, none of them invented here:

1. **A completed career grants +1 maximum Stamina** and that is "the only durable toughening"
   (docs/design/03-rules.md section 6). If starting Stamina were 20, +1 would be noise and the
   sentence would be false.
2. **"A character ten years in is not harder to kill"** (same section). Stamina barely grows,
   so its starting value is close to its lifetime value.
3. **A drop of 1-3 below zero is ordinary; past 8 means something went badly wrong.**
   Asserted by specs/002-aftermath-table/check_aftermath.py, which is merged and whose
   distribution table is built on it. Overshoot is bounded by how much damage exceeds
   remaining Stamina, so this is really a statement about Stamina's size.
4. **Armour subtracts dice** -- light 1d3, modest 1d6, heavy 2d6, minimum 1 always through
   (docs/design/03-rules.md section 2). These are engine numbers and fix the scale that weapon
   damage must live on.

Weapon damage is *setting* data (docs/design/24-authoring-a-setting.md), so it is modelled across
a band rather than assumed. A starting Stamina worth shipping has to hold across the whole
band, not at one convenient point.

Run: python3 specs/008-character-creation/check_creation.py
"""

from fractions import Fraction
from itertools import product

# Armour, as docs/design/03-rules.md section 2 defines it. (label, dice) where dice is a list of
# face counts: modest 1d6 is [6], heavy 2d6 is [6, 6].
ARMOUR = [("none", []), ("light", [3]), ("modest", [6]), ("heavy", [6, 6])]

# A minimum of 1 always gets through, whatever the armour rolls.
MIN_THROUGH = 1

# Weapon damage is a setting's business. This is the plausible band an engine-scale weapon
# sits in, given armour subtracts 1d3 to 2d6: a weapon that could not beat modest armour
# would make armour pointless, and one that ignored heavy armour would make it decorative.
WEAPON_BAND = [("1d3", [3]), ("1d6", [6]), ("1d8", [8]), ("2d6", [6, 6])]

# Candidate starting values to test. Deliberately wide, so the answer is found rather than
# confirmed.
CANDIDATE_STAMINA = range(3, 13)

# A telling blow -- win by 3+ degrees -- doubles the damage (section 2).
TELLING_BLOW_MULTIPLIER = 2


def dice_distribution(faces: list[int]) -> dict[int, Fraction]:
    """Exact distribution of a pool of dice. Empty pool always rolls 0."""
    if not faces:
        return {0: Fraction(1)}
    outcomes = list(product(*[range(1, f + 1) for f in faces]))
    weight = Fraction(1, len(outcomes))
    dist: dict[int, Fraction] = {}
    for roll in outcomes:
        dist[sum(roll)] = dist.get(sum(roll), Fraction(0)) + weight
    return dist


def damage_through(weapon: list[int], armour: list[int], telling: bool) -> dict[int, Fraction]:
    """Damage reaching Stamina, after armour, with the minimum-1 floor.

    Armour subtracts dice from the damage, not from the roll -- so a telling blow doubles
    what the weapon did, and armour then eats what it can.
    """
    result: dict[int, Fraction] = {}
    for wd, wp in dice_distribution(weapon).items():
        rolled = wd * (TELLING_BLOW_MULTIPLIER if telling else 1)
        for ad, ap in dice_distribution(armour).items():
            through = max(MIN_THROUGH, rolled - ad)
            result[through] = result.get(through, Fraction(0)) + wp * ap
    return result


def mean(dist: dict[int, Fraction]) -> Fraction:
    return sum((k * v for k, v in dist.items()), Fraction(0))


def hits_to_drop(stamina: int, dist: dict[int, Fraction]) -> Fraction:
    """Expected hits to take a character from full Stamina to below zero."""
    return Fraction(stamina + 1, 1) / mean(dist)


def overshoot_from_full(stamina: int, dist: dict[int, Fraction]) -> Fraction:
    """Expected points below zero when a single telling blow drops a full-Stamina character.

    This is the quantity constraint 3 is about: check_aftermath.py's realistic range, and the
    argument that a light knockdown must stay survivable.
    """
    total, weight = Fraction(0), Fraction(0)
    for through, p in dist.items():
        if through > stamina:
            total += (through - stamina) * p
            weight += p
    return total / weight if weight else Fraction(0)


def p_dropped_from_full(stamina: int, dist: dict[int, Fraction]) -> Fraction:
    return sum((p for through, p in dist.items() if through > stamina), Fraction(0))


def pct(f: Fraction) -> str:
    return f"{float(f) * 100:5.1f}%"


def num(f: Fraction) -> str:
    return f"{float(f):5.2f}"


def main() -> int:
    failures: list[str] = []

    print("Damage through armour, by weapon (expected value)")
    print("-" * 64)
    print("  weapon " + "".join(f"{label:>10}" for label, _ in ARMOUR))
    for wlabel, weapon in WEAPON_BAND:
        row = "".join(
            num(mean(damage_through(weapon, armour, False))).rjust(10) for _, armour in ARMOUR
        )
        print(f"  {wlabel:>6} {row}")

    print()
    print("Constraint 1 — a completed career's +1 Stamina must be a real gain")
    print("-" * 64)
    print("  stamina   +1 is")
    for stamina in CANDIDATE_STAMINA:
        share = Fraction(1, stamina)
        verdict = "noise" if share < Fraction(1, 10) else "meaningful"
        print(f"  {stamina:>7}   {pct(share)}  {verdict}")

    print()
    print("Constraint 3 — overshoot when a telling blow drops a character from full")
    print("-" * 64)
    print("  ORDINARY means a mid-band weapon against modest armour. check_aftermath.py")
    print("  calls a drop of 1-3 ordinary and past 8 badly wrong -- but it models 1-12, so")
    print("  the worst case is meant to be grim, not impossible. Judging the worst case by")
    print("  the ordinary threshold was this script's first mistake and it caught it.")
    print()
    print("  stamina   ordinary(1d6/modest)   worst(2d6/none)")
    for stamina in CANDIDATE_STAMINA:
        ordinary = overshoot_from_full(stamina, damage_through([6], [6], True))
        worst = overshoot_from_full(stamina, damage_through([6, 6], [], True))
        flag = "ok" if 0 < ordinary <= 3 and worst <= 12 else "--"
        print(f"  {stamina:>7}   {num(ordinary):>14}       {num(worst):>10}   {flag}")

    print()
    print("Hits to drop an unarmoured and a modest-armoured character (1d6 weapon)")
    print("-" * 64)
    print("  stamina   unarmoured   modest armour")
    for stamina in CANDIDATE_STAMINA:
        bare = hits_to_drop(stamina, damage_through([6], [], False))
        armoured = hits_to_drop(stamina, damage_through([6], [6], False))
        print(f"  {stamina:>7}   {num(bare)}       {num(armoured)}")

    print()
    print("Chance a single telling blow drops a character from FULL Stamina")
    print("-" * 64)
    print("  stamina" + "".join(f"{w:>9}" for w, _ in WEAPON_BAND))
    for stamina in CANDIDATE_STAMINA:
        row = "".join(
            pct(p_dropped_from_full(stamina, damage_through(weapon, [], True))).rjust(9)
            for _, weapon in WEAPON_BAND
        )
        print(f"  {stamina:>7}{row}")

    print()
    print("The passing band, and the tiebreak")
    print("-" * 64)
    print("  Stamina 5-10 all satisfy the overshoot constraint, so it does not pick a single")
    print("  value on its own. Two further constraints narrow it, and both favour the low end:")
    print()
    print("  stamina   +1 career gain   armoured fight length")
    for stamina in range(5, 11):
        share = Fraction(1, stamina)
        length = hits_to_drop(stamina, damage_through([6], [6], False))
        note = []
        if share < Fraction(15, 100):
            note.append("+1 thinning")
        if length > 5:
            note.append("fight too long for a 20-minute session")
        print(f"  {stamina:>7}   {pct(share):>13}   {num(length):>10} hits   {'; '.join(note)}")
    print()
    print("  Success criterion 5 (docs/design/01-principles.md) requires a session to be playable")
    print("  in twenty minutes on a phone, and a fight running 7+ exchanges does not fit.")
    print("  6 is the largest value where +1 is unambiguously meaningful and an armoured")
    print("  exchange still resolves quickly.")

    print()
    print("Luck — a percentage that erodes 1 per test, for the rest of the arc")
    print("-" * 64)
    print("  docs/design/03-rules.md section 1. Starting value must survive an arc's worth of")
    print("  testing while the erosion stays visible.")
    print()
    print("  start   after 5 tests   after 10 tests   expected passes in 10 tests")
    for start in (25, 30, 40, 50):
        after5, after10 = start - 5, start - 10
        # Each test is against the eroded value, so successes compound downward.
        expected = sum(Fraction(start - i, 100) for i in range(10))
        print(f"  {start:>5}   {after5:>12}   {after10:>13}   {num(expected):>10}")
    print()
    print("  40 keeps a test a genuine gamble (it fails more often than not) and leaves")
    print("  something to lose after a heavy arc. 25 is exhausted by one bad arc; 50 makes")
    print("  testing near-automatic early on.")

    print()
    print("Creation spends advances; it does not open skills for free")
    print("-" * 64)
    print("  docs/design/03-rules.md section 6 has exactly three doors: open a career skill at")
    print("  25%, raise one by +5%, or change career. Opening every career skill for free is")
    print("  not one of them, and doing so left a starting character holding 5-9 skills at")
    print("  25% -- which docs/design/13-diegesis.md calls 'never really done this'. A character")
    print("  guessing at their own profession. Creation uses the same doors play uses.")
    print()
    RAISE, OPENS_AT_PCT = 5, 25
    print("  pool   opened   resulting values                 lowest band")
    for pool in (6, 8, 10, 12):
        for k in (2, 3, 4):
            if k > pool:
                continue
            vals = [OPENS_AT_PCT] * k
            for i in range(pool - k):
                vals[i % k] += RAISE
            vals.sort(reverse=True)
            worst = min(vals)
            b = (
                "guessing"
                if worst <= 25
                else "trained"
                if worst <= 40
                else "practised"
                if worst <= 55
                else "expert"
            )
            mark = "  <-- chosen" if pool == 8 and k == 3 else ""
            print(f"  {pool:>4}   {k:>6}   {', '.join(f'{v}%' for v in vals):<32} {b}{mark}")
        print()
    print("  A pool of 8 puts every opened skill in the trained band at every spread from 2")
    print("  to 4 skills, and leaves everything else honestly untrained at 10%.")
    print()
    print("  At least two skills must be opened. Without that floor, 8 advances on a single")
    print("  skill opens at 60% -- expert, before the chronicle has begun. A career is not")
    print("  one skill, so the floor costs nothing a character would plausibly want.")

    print()
    print("Free advances at creation — how far into the first career a character starts")
    print("-" * 64)
    print("  Every career-granted skill opens at 25%. A pool of free advances is then spent")
    print("  inside that career, and how it is spent IS the character's background. Bounded")
    print("  by the skill bands in docs/design/13-diegesis.md:")
    print()
    print("    <=25 guessing | 30-40 trained | 45-55 practised | 60-70 expert | 75+ definitive")
    print()
    print("  A new character should be able to reach TRAINED broadly or PRACTISED narrowly,")
    print("  and must not begin EXPERT in anything -- that is what a chronicle is for.")
    print()
    print("  pool   all on one skill   spread over 3   spread over 6   verdict")
    ADVANCE = 5
    OPEN = 25
    best_n = None
    for pool in range(2, 13):
        one = OPEN + ADVANCE * pool
        three = OPEN + ADVANCE * (pool // 3)
        six = OPEN + ADVANCE * (pool // 6)
        # Must not reach expert (60) even if entirely dumped on one skill...
        no_expert = one < 60
        # ...but must be able to clear "guessing" on at least three skills.
        trains_broadly = three >= 30
        ok = no_expert and trains_broadly
        if ok:
            best_n = pool
        print(
            f"  {pool:>4}   {one:>13}%   {three:>11}%   {six:>11}%   "
            f"{'ok' if ok else ('expert too early' if not no_expert else 'too thin')}"
        )
    print()
    print(f"  The band is satisfied by pools up to {best_n}. The largest passing value is taken:")
    print("  a smaller pool makes the choice trivial and the background faint, and the whole")
    print("  point is that how it is spent distinguishes two characters of one career.")

    print()
    print("The untrained base — a skill the character does not have")
    print("-" * 64)
    print("  There are no characteristics to fall back on (ADR 0013), so the engine states a")
    print("  flat base. It has to sit below the 25% a skill opens at, stay inside the")
    print("  guessing band, and still let a well-judged easy attempt be worth making.")
    print()
    DIFFICULTY = [
        ("easy", 20),
        ("average", 0),
        ("challenging", -10),
        ("difficult", -20),
        ("hard", -30),
        ("very hard", -40),
    ]
    DECLARATION = [("brief", 0), ("specific", 10), ("leveraging", 20)]
    print("  base   " + "".join(f"{d:>12}" for d, _ in DIFFICULTY))
    for base in (5, 10, 15, 20):
        row = "".join(f"{max(0, base + m):>12}" for _, m in DIFFICULTY)
        print(f"  {base:>4}   {row}")
    print()
    print("  At base 10, with declaration (easy difficulty):")
    for label, bonus in DECLARATION:
        print(f"    {label:<12} {10 + 20 + bonus:>3}%")

    UNTRAINED = 10
    OPENS_AT = 25
    GUESSING_TOP = 25
    if UNTRAINED >= OPENS_AT:
        failures.append(
            f"untrained {UNTRAINED}% is not below the {OPENS_AT}% a skill opens at — "
            "having the skill would buy nothing"
        )
    if UNTRAINED > GUESSING_TOP:
        failures.append(
            f"untrained {UNTRAINED}% is outside the <={GUESSING_TOP}% guessing band in "
            "docs/design/13-diegesis.md"
        )
    if UNTRAINED + (-30) > 0:
        failures.append(
            f"untrained {UNTRAINED}% remains possible at hard difficulty; an untrained "
            "attempt at something hard should not be"
        )
    if UNTRAINED + 20 + 20 < 40:
        failures.append(
            f"untrained {UNTRAINED}% with an easy task and a good declaration is still not "
            "worth attempting, which makes the base decorative"
        )

    # ---- the decision, stated as checks rather than as a preference ----
    print()
    print("Verdict")
    print("-" * 64)

    chosen = 6

    share = Fraction(1, chosen)
    if share < Fraction(1, 10):
        failures.append(
            f"at starting Stamina {chosen}, a completed career's +1 is {pct(share)} — "
            "docs/design/03-rules.md calls it the only durable toughening, which would be false"
        )
    print(
        f"  +1 from a completed career is {pct(share)} of a new character   "
        f"[{'ok' if share >= Fraction(1, 10) else 'FAIL'}]"
    )

    # The ORDINARY case -- a mid-band weapon against modest armour -- must land in the 1-3
    # that check_aftermath.py calls ordinary. That is what makes deferred death routinely
    # survivable rather than a formality.
    ordinary_overshoot = overshoot_from_full(chosen, damage_through([6], [6], True))
    if not 0 < ordinary_overshoot <= 3:
        failures.append(
            f"at starting Stamina {chosen}, an ordinary telling blow overshoots by "
            f"{num(ordinary_overshoot)}, outside the 1-3 check_aftermath.py treats as ordinary"
        )
    print(
        f"  ordinary telling blow overshoots by {num(ordinary_overshoot)} points        "
        f"[{'ok' if 0 < ordinary_overshoot <= 3 else 'FAIL'}]"
    )

    # The WORST case -- a martial weapon, telling blow, no armour -- must stay inside the
    # range check_aftermath.py actually models. It is allowed to be grim: a martial weapon is
    # illegal in most civilised places precisely because of what it does to an unarmoured
    # person (docs/design/03-rules.md section 2).
    worst = overshoot_from_full(chosen, damage_through([6, 6], [], True))
    if worst > 12:
        failures.append(
            f"at starting Stamina {chosen}, the worst case overshoots by {num(worst)}, past "
            "the 1-12 range check_aftermath.py models -- the Aftermath table has no rows for it"
        )
    print(
        f"  worst case (martial, unarmoured) overshoots by {num(worst)}     "
        f"[{'ok' if worst <= 12 else 'FAIL'}]"
    )

    # An ordinary exchange must not be decided by one hit, or there is no fight.
    ordinary = hits_to_drop(chosen, damage_through([6], [6], False))
    if ordinary < 2:
        failures.append(
            f"at starting Stamina {chosen}, a modest-armoured character drops in "
            f"{num(ordinary)} ordinary hits — a fight would not last a round"
        )
    print(
        f"  a modest-armoured character takes {num(ordinary)} ordinary hits to drop  "
        f"[{'ok' if ordinary >= 2 else 'FAIL'}]"
    )

    # ...and an unarmoured one must be in real danger, or armour means nothing.
    bare = hits_to_drop(chosen, damage_through([6], [], False))
    if bare > ordinary:
        failures.append("armour is not reducing the number of hits needed")
    print(
        f"  unarmoured drops in {num(bare)}, so armour roughly doubles endurance  "
        f"[{'ok' if bare < ordinary else 'FAIL'}]"
    )

    # Free advances: the pool must not make a starting character expert at anything, and
    # must let them read as trained across a few skills.
    pool = 8
    MIN_OPENED = 2
    # Two advances open two skills; the remaining pool-2 can all pile onto one of them.
    # A career is not one skill -- someone who has soldiered knows more than one soldierly
    # thing -- and without the minimum, 8 advances on a single skill opens at 60%, which
    # docs/design/13-diegesis.md calls expert. Beginning expert is what a chronicle is for.
    peak = 25 + 5 * (pool - MIN_OPENED)
    if peak >= 60:
        failures.append(
            f"a pool of {pool} advances peaks at {peak}%, which docs/design/13-diegesis.md "
            "calls expert — a chronicle should be what gets you there"
        )
    print(
        f"  {pool} advances, {MIN_OPENED} skills minimum, peak {peak}% — practised   "
        f"[{'ok' if peak < 60 else 'FAIL'}]"
    )

    # Opening 3 skills costs 3; the remaining 5 raise them. The weakest must clear "guessing".
    three = [25, 25, 25]
    for i in range(pool - 3):
        three[i % 3] += 5
    if min(three) <= 25:
        failures.append(
            f"a pool of {pool} leaves a skill at {min(three)}% when three are opened — "
            "docs/design/13-diegesis.md calls that guessing, in the character's own career"
        )
    print(
        f"  opening 3, the weakest sits at {min(three)}% — trained, not guessing  "
        f"[{'ok' if min(three) > 25 else 'FAIL'}]"
    )

    # CORRECTED. This was labelled "exchanges" and is HITS -- it ignores the miss rate
    # entirely, so it understated fight length by a factor of three or more. Turning hits
    # into exchanges needs the opposed-test hit probability, which is specs/010-opposed-tests.
    # Stamina is not the lever on fight length; the hit rate is, and that is Stage 5's (#44).
    # Reported rather than asserted, because creation cannot fix it.
    length = hits_to_drop(chosen, damage_through([6], [6], False))
    print(f"  a modest-armoured character absorbs {num(length)} hits before dropping")
    print("  (NOT exchanges -- at starting skills most attacks miss, so a fight runs three")
    print("   to six times longer than this. See specs/010-opposed-tests/check_opposed.py")
    print("   and the fight-length finding raised against Stage 5.)")

    print(
        f"  untrained {UNTRAINED}% sits below the {OPENS_AT}% a skill opens at        "
        f"[{'ok' if UNTRAINED < OPENS_AT else 'FAIL'}]"
    )
    print(
        f"  untrained is impossible at hard difficulty ({UNTRAINED - 30}%)         "
        f"[{'ok' if UNTRAINED - 30 <= 0 else 'FAIL'}]"
    )
    print(
        f"  a well-judged easy untrained attempt reaches {UNTRAINED + 40}%         "
        f"[{'ok' if UNTRAINED + 40 >= 40 else 'FAIL'}]"
    )

    print()
    if failures:
        print(f"FAILED: {len(failures)} problem(s)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"All checks passed. Starting Stamina {chosen} satisfies every stated constraint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
