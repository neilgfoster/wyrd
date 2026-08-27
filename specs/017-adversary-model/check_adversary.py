#!/usr/bin/env python3
"""Compute the adversary model: what an opponent carries, and how danger reaches it.

CLAUDE.md: where a claim can be checked by a script, check it. Nothing in design/ said how an
opponent was represented, while five separate rules had been reading fields off one for four
stages -- most sharply ADR 0019's crowd rule, which calls itself "a lookup, and nothing else"
over three fields that belonged to no schema.

Everything below is derived from numbers already merged, not invented here:

1. **Armour subtracts dice** -- light 1d3, modest 1d6, heavy 2d6, minimum 1 always through
   (docs/design/03-rules.md section 2).
2. **A starting character has Stamina 6** (docs/design/11-character-creation.md), and a critical
   happens when damage takes a combatant below 0 (docs/design/05-criticals.md).
3. **Untrained is a flat 10%**, a skill opens at 25% and rises by 5 (docs/design/03-rules.md section 1,
   docs/design/10-the-character.md).
4. **An attack is an opposed test** with the successful-actor gate and ties to the resisting side
   (docs/design/03-rules.md section 1, ADR 0016).
5. **The k-th body is worth 1/k**, so a party of p bodies has effective size H(p), and both sides
   of the danger ratio are read through that function (docs/design/03-rules.md section 7, ADR 0024).
6. **The difficulty ladder** runs +20 to -40 in rungs of 10 (docs/design/03-rules.md section 1).
7. **The recorded player-facing mapping** is effective% = 50 + (player_skill - opponent_skill),
   clipped to 5-95 (specs/012-combat-sequencing, for #69 to adopt). Every claim here is computed
   under BOTH the opposed test as it stands today and that mapping, because the adversary block
   must survive the conversion.

The one thing this script DERIVES rather than reuses is the skill adjustment: the points added to
an opponent's percentage when content is prepared for a party other than the one it was written
for. docs/design/03-rules.md section 7 has always claimed that danger scales "enemy counts and skill
values"; the count half was settled by #8, and the skill half was never evaluable because a
percentage cannot be multiplied by a ratio. The coefficient is fitted from the achievable ratio
range, not chosen -- see section T005/T006 below.

Fight resolution is the expensive part, so the exchange table is memoised up front and every
figure is read from it. Each corrected figure is otherwise a full re-run.

Run: python3 specs/017-adversary-model/check_adversary.py
"""

import math
from fractions import Fraction
from functools import lru_cache
from itertools import product

# ---------------------------------------------------------------------------
# Numbers from merged design documents. None of these is chosen here.
# ---------------------------------------------------------------------------

ARMOUR = {"none": [], "light": [3], "modest": [6], "heavy": [6, 6]}
ARMOUR_RANKS = ["none", "light", "modest", "heavy"]      # docs/design/03-rules.md section 2
MIN_THROUGH = 1
WEAPON_BAND = [("1d3", [3]), ("1d6", [6]), ("1d8", [8]), ("2d6", [6, 6])]
ORDINARY_WEAPON = [6]
ORDINARY_ARMOUR = "modest"

DAMAGE_TYPES = ["slashing", "piercing", "blunt", "searing"]   # ADR 0022, closed
UNTRAINED = 10
SKILL_OPENS_AT = 25
SKILL_STEP = 5                     # docs/design/03-rules.md section 6: an advance is +5
STARTING_STAMINA = 6

LADDER = [20, 0, -10, -20, -30, -40]     # docs/design/03-rules.md section 1
LADDER_TOP = max(LADDER)                 # +20, the ladder's whole positive extent

REAL_SKILLS = [25, 35, 45, 55]
# Party sizes and written_for values a chronicle actually produces. A solo engine's party is the
# player character plus companions; published content is written for four to six.
REAL_PARTIES = [1, 2, 3, 4, 5]
REAL_WRITTEN_FOR = [4, 6]
MAX_BODIES = 6                     # the domain the published table covers
DANGERS = [1, 2, 3, 4, 5, 6]

# The crowd rule's own three constants (ADR 0019), restated so this script can falsify them
# against the block rather than trusting that they still line up.
CROWD_MAX_STAMINA = 1
CROWD_MAX_ARMOUR = "none"
CROWD_SKILL_GAP = 20

# The closed trait vocabulary. Every effect names a mechanism that already exists; a setting may
# retune through these and may never add one (docs/design/24-authoring-a-setting.md).
TRAIT_EFFECTS = {
    "difficulty": "shifts the difficulty of a named class of test, in ladder rungs",
    "damage": "adds or removes damage dice on this opponent's blows",
    "damage_type": "fixes the damage type of this opponent's blows",
    "stamina_max": "raises or lowers maximum Stamina",
    "armour_rank": "raises or lowers the armour rank by whole ranks",
    "wyrd": "widens the Ill Omen or Fair Omen band on tests against this opponent",
}

failures: list[str] = []


def check(claim: str, ok: bool, shown: str = "") -> None:
    if not ok:
        failures.append(f"{claim}" + (f"  [{shown}]" if shown else ""))


def pct(f) -> str:
    return f"{float(f) * 100:5.1f}%"


def num(f, dp: int = 2) -> str:
    return f"{float(f):.{dp}f}"


# ---------------------------------------------------------------------------
# Dice, damage and the opposed test. Identical to specs/013 and specs/014 by construction --
# a second model of the same rules is the two-documents fault class in code.
# ---------------------------------------------------------------------------


def dice_distribution(faces: list[int]) -> dict[int, Fraction]:
    if not faces:
        return {0: Fraction(1)}
    outcomes = list(product(*[range(1, f + 1) for f in faces]))
    weight = Fraction(1, len(outcomes))
    dist: dict[int, Fraction] = {}
    for roll in outcomes:
        dist[sum(roll)] = dist.get(sum(roll), Fraction(0)) + weight
    return dist


def damage_through(weapon: list[int], armour: list[int]) -> dict[int, Fraction]:
    """Damage reaching Stamina after armour, with the minimum-1 floor. One ordinary hit."""
    result: dict[int, Fraction] = {}
    for wd, wp in dice_distribution(weapon).items():
        for ad, ap in dice_distribution(armour).items():
            through = max(MIN_THROUGH, wd - ad)
            result[through] = result.get(through, Fraction(0)) + wp * ap
    return result


def p_dropped_by_one_hit(stamina: int, weapon: list[int], armour: list[int]) -> Fraction:
    return sum(
        (p for through, p in damage_through(weapon, armour).items() if through > stamina),
        Fraction(0),
    )


def worst_and_mean_drop(stamina: int, armour_label: str) -> tuple[Fraction, Fraction]:
    armour = ARMOUR[armour_label]
    ps = [p_dropped_by_one_hit(stamina, w, armour) for _, w in WEAPON_BAND]
    return min(ps), sum(ps, Fraction(0)) / len(ps)


def degrees(skill: int, roll: int) -> int:
    return skill // 10 - roll // 10


@lru_cache(maxsize=None)
def p_opposed_win(actor: int, resister: int) -> Fraction:
    """ADR 0016's successful-actor gate, ties to the resisting side."""
    wins = 0
    for ra in range(1, 101):
        if ra > actor:
            continue
        da = degrees(actor, ra)
        for rd in range(1, 101):
            if rd > resister or da > degrees(resister, rd):
                wins += 1
    return Fraction(wins, 100 * 100)


def p_mapped(player: int, opponent: int) -> Fraction:
    return Fraction(max(5, min(95, 50 + player - opponent)), 100)


HIT_MODELS = [("opposed", p_opposed_win), ("mapped", p_mapped)]

ORDINARY_HIT = damage_through(ORDINARY_WEAPON, ARMOUR[ORDINARY_ARMOUR])

# The critical table rows run from 2 (1d6 plus at least 1 point below zero) to 22+
# (docs/design/05-criticals.md). One table per damage type; the block picks which.
CRITICAL_FIRST_ROW = 2
CRITICAL_DIE = 6


def parse_damage(expr: str) -> list[int]:
    """'1d6' -> [6], '2d6' -> [6, 6]. The block writes what its blows roll, and the fight has
    to read it -- otherwise the damage field is decoration and the exchange proves nothing
    about it."""
    count, _, faces = expr.partition("d")
    return [int(faces)] * int(count or 1)


# ---------------------------------------------------------------------------
# T004. The memoised exchange table, built once, before any figure is read from it.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def fight_outcome(player_stamina: int, player_skill: int, opponent_skill: int,
                  model_name: str, opponent_stamina: int = STARTING_STAMINA,
                  opponent_armour: str = ORDINARY_ARMOUR,
                  opponent_damage: str = "1d6",
                  max_rounds: int = 60):
    """Exact round-by-round resolution of one fight.

    Returns (p_player_dropped, p_opponent_dropped, expected_rounds, below_zero), where
    below_zero maps points-below-zero to probability for the opponent -- which is what the
    critical rule reads.

    Each side's incoming damage is read through its own armour, and the opponent's blows roll
    the dice its own block declares. Both are fields the fight actually consumes.
    """
    model = p_opposed_win if model_name == "opposed" else p_mapped
    if model_name == "mapped":
        p_hit = p_mapped(player_skill, opponent_skill)
        p_taken = 1 - p_hit
        independent = False
    else:
        p_hit = model(player_skill, opponent_skill)
        p_taken = model(opponent_skill, player_skill)
        independent = True

    to_opponent = damage_through(ORDINARY_WEAPON, ARMOUR[opponent_armour])
    to_player = damage_through(parse_damage(opponent_damage), ARMOUR[ORDINARY_ARMOUR])

    state = {(player_stamina, opponent_stamina): Fraction(1)}
    player_dropped = Fraction(0)
    opponent_dropped = Fraction(0)
    rounds = Fraction(0)
    below_zero: dict[int, Fraction] = {}
    for r in range(1, max_rounds + 1):
        nxt: dict[tuple[int, int], Fraction] = {}
        for (ps, os_), p in state.items():
            branches = []
            if independent:
                for a, pa in ((True, p_hit), (False, 1 - p_hit)):
                    for b, pb in ((True, p_taken), (False, 1 - p_taken)):
                        branches.append((a, b, pa * pb))
            else:
                branches.append((True, False, p_hit))
                branches.append((False, True, p_taken))
            for player_lands, opponent_lands, pb in branches:
                if pb == 0:
                    continue
                sub = {(ps, os_): p * pb}
                if player_lands:
                    sub = {(a, b - d): q * dp
                           for (a, b), q in sub.items()
                           for d, dp in to_opponent.items()}
                if opponent_lands:
                    sub = {(a - d, b): q * dp
                           for (a, b), q in sub.items()
                           for d, dp in to_player.items()}
                for (a, b), q in sub.items():
                    if a < 0:
                        player_dropped += q
                        rounds += q * r
                        continue
                    if b < 0:
                        opponent_dropped += q
                        rounds += q * r
                        below_zero[-b] = below_zero.get(-b, Fraction(0)) + q
                        continue
                    nxt[(a, b)] = nxt.get((a, b), Fraction(0)) + q
        state = nxt
        if not state:
            break
    for _, q in state.items():
        rounds += q * max_rounds
    return player_dropped, opponent_dropped, rounds, below_zero


# ---------------------------------------------------------------------------
# T005-T010. The skill adjustment, derived.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def H(p: int) -> Fraction:
    """Effective size of a party of p bodies: the k-th body is worth 1/k (ADR 0024)."""
    return sum((Fraction(1, k) for k in range(1, p + 1)), Fraction(0))


def ratio(party: int, written_for: int) -> Fraction:
    """Both sides read through the same function, or the identity case never lands."""
    if written_for <= 0:
        return Fraction(1)
    return H(party) / H(written_for)


def achievable_ratio_range(max_bodies: int = MAX_BODIES) -> tuple[Fraction, Fraction]:
    """The curve's input domain, computed before the curve is fitted to it."""
    values = [ratio(p, w)
              for p in range(1, max_bodies + 1)
              for w in range(1, max_bodies + 1)]
    return min(values), max(values)


def fit_coefficient(max_bodies: int = MAX_BODIES) -> float:
    """The coefficient is not chosen. It is whatever makes the extreme of the achievable
    range land exactly on the ladder's top rung."""
    _, r_max = achievable_ratio_range(max_bodies)
    return LADDER_TOP / math.log2(float(r_max))


COEFFICIENT = fit_coefficient()

# What docs/design/03-rules.md section 7 actually prints. A GM reads the published number, not the
# fitted one, so the published number is what has to reproduce the published table -- otherwise
# the document carries a plausible round figure that nothing checks, which is the fault class
# CLAUDE.md lists fourth.
PUBLISHED_COEFFICIENT = 15.5


def round_to(x: float, step: int) -> int:
    """Round half up, the rule docs/design/03-rules.md section 7 already applies everywhere."""
    return int(math.floor(x / step + 0.5)) * step


def raw_adjustment(party: int, written_for: int) -> float:
    r = float(ratio(party, written_for))
    return COEFFICIENT * math.log2(r)


def adjustment(party: int, written_for: int, step: int = SKILL_STEP) -> int:
    """Points added to an opponent's percentage, clipped inside the ladder."""
    return max(-LADDER_TOP, min(LADDER_TOP, round_to(raw_adjustment(party, written_for), step)))


def adjusted_skill(skill: int, party: int, written_for: int) -> int:
    """The opponent's percentage as it is actually tested. Floored at 0: a percentage is not a
    negative number, and docs/design/03-rules.md section 1 already says what a test at or below zero
    is -- it is not attempted. Flooring states where the track stops; it adds no rule."""
    return max(0, skill + adjustment(party, written_for))


def danger_effective(danger: int, party: int, written_for: int) -> Fraction:
    return danger * ratio(party, written_for)


def scaled_count(written_count: int, danger: int, party: int, written_for: int) -> int:
    """Round half up at the point of use, never below 1 where the written quantity was."""
    exact = Fraction(written_count) * danger_effective(danger, party, written_for) / danger
    scaled = int(math.floor(float(exact) + 0.5))
    return max(1, scaled) if written_count >= 1 else scaled


# ---------------------------------------------------------------------------
# The block itself, as a data shape this script can exercise.
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = ["id", "name", "baseline", "stamina_max", "armour", "skills"]
OPTIONAL_FIELDS = ["damage", "damage_type", "ranged", "traits", "notes"]


def opponent_skill(block: dict, skill: str) -> int:
    """What an opponent tests. A skill it does not list is tested at its baseline -- not at the
    untrained 10%, which is a rule about people who never learned a thing."""
    return block["skills"].get(skill, block["baseline"])


def qualifies_as_crowd(block: dict, character_skill: int, skill: str) -> tuple[bool, str]:
    """ADR 0019's three-test lookup, resolved entirely from declared fields."""
    if block["stamina_max"] > CROWD_MAX_STAMINA:
        return False, f"stamina_max {block['stamina_max']} > {CROWD_MAX_STAMINA}"
    if block["armour"] != CROWD_MAX_ARMOUR:
        return False, f"armour {block['armour']!r} is not {CROWD_MAX_ARMOUR!r}"
    theirs = opponent_skill(block, skill)
    if character_skill - theirs < CROWD_SKILL_GAP:
        return False, f"skill gap {character_skill - theirs} < {CROWD_SKILL_GAP}"
    return True, f"stamina_max 1, no armour, gap {character_skill - theirs}"


MOB_BODY = {
    "id": "mob-body", "name": "a body in the crowd",
    "baseline": 10, "stamina_max": 1, "armour": "none",
    "skills": {"brawl": 20}, "damage": "1d3", "damage_type": "blunt", "ranged": False,
}

NEMESIS = {
    "id": "the-hunter", "name": "a named antagonist",
    "baseline": 35, "stamina_max": 7, "armour": "modest",
    "skills": {"blade": 55}, "damage": "1d6", "damage_type": "slashing", "ranged": False,
    "traits": [{"name": "Unhurried", "effect": {"difficulty": -10}}],
}


def main() -> int:
    print("=" * 78)
    print("T004  The exchange table, memoised before anything reads from it")
    print("=" * 78)
    for model_name, _ in HIT_MODELS:
        for skill in REAL_SKILLS:
            fight_outcome(STARTING_STAMINA, skill, skill, model_name)
            fight_outcome(STARTING_STAMINA, skill, max(1, skill - 20), model_name)
    info = fight_outcome.cache_info()
    print(f"  fights resolved: {info.currsize}   (hits {info.hits}, misses {info.misses})")
    check("the exchange table was built before it was read", info.currsize > 0)
    print()

    # -- T005 ---------------------------------------------------------------
    print("=" * 78)
    print("T005  The achievable ratio range -- the curve's input domain")
    print("=" * 78)
    r_min, r_max = achievable_ratio_range()
    print(f"  bodies 1..{MAX_BODIES} against written_for 1..{MAX_BODIES}")
    print(f"  ratio runs {num(r_min, 4)} .. {num(r_max, 4)}")
    print(f"  log2 runs  {math.log2(float(r_min)):+.4f} .. {math.log2(float(r_max)):+.4f}")
    check("the range is symmetric in log space", abs(math.log2(float(r_min))
                                                     + math.log2(float(r_max))) < 1e-12,
          f"{math.log2(float(r_min)):+.6f} vs {math.log2(float(r_max)):+.6f}")
    print("  The range is exactly antisymmetric, because swapping party and written_for inverts")
    print("  the ratio. That is what lets one coefficient serve both directions.")
    print()

    # -- T006 ---------------------------------------------------------------
    print("=" * 78)
    print("T006  The coefficient, fitted rather than chosen")
    print("=" * 78)
    print(f"  Require the extreme of the computed range to land on the ladder's top rung:")
    print(f"    coefficient = {LADDER_TOP} / log2({num(r_max, 4)}) = {COEFFICIENT:.4f}")
    print(f"  At the extreme: {COEFFICIENT * math.log2(float(r_max)):+.4f} -> "
          f"{adjustment(MAX_BODIES, 1):+d}")
    check("the fitted coefficient lands the extreme exactly on the ladder top",
          adjustment(MAX_BODIES, 1) == LADDER_TOP, str(adjustment(MAX_BODIES, 1)))
    check("and its mirror on the bottom of the same span",
          adjustment(1, MAX_BODIES) == -LADDER_TOP, str(adjustment(1, MAX_BODIES)))

    print()
    print(f"  The design document prints {PUBLISHED_COEFFICIENT}, not {COEFFICIENT:.4f}. A GM")
    print("  applies the printed number, so the printed number must reproduce the printed table.")
    mismatches = [
        (p_, w, adjustment(p_, w),
         max(-LADDER_TOP, min(LADDER_TOP,
             round_to(PUBLISHED_COEFFICIENT * math.log2(float(ratio(p_, w))), SKILL_STEP))))
        for p_ in range(1, MAX_BODIES + 1) for w in range(1, MAX_BODIES + 1)
    ]
    differing = [m for m in mismatches if m[2] != m[3]]
    print(f"  cells where they differ: {len(differing)}")
    check("the published coefficient reproduces the published table exactly",
          not differing, str(differing[:3]))
    # And it must still land the extreme on the rung, or the fit was rounded away.
    published_extreme = round_to(
        PUBLISHED_COEFFICIENT * math.log2(float(r_max)), SKILL_STEP)
    check("the published coefficient still lands the extreme on the ladder top",
          min(LADDER_TOP, published_extreme) == LADDER_TOP, str(published_extreme))
    print()

    # -- T008: granularity --------------------------------------------------
    print("=" * 78)
    print("T008  Rounding granularity: the advance step against the ladder step")
    print("=" * 78)
    for step in (SKILL_STEP, 10):
        table = {(p, w): adjustment(p, w, step)
                 for p in range(1, MAX_BODIES + 1) for w in range(1, MAX_BODIES + 1)}
        identity_ok = all(table[(p, p)] == 0 for p in range(1, MAX_BODIES + 1))
        monotone_ok = all(table[(p, w)] <= table[(p + 1, w)]
                          for p in range(1, MAX_BODIES) for w in range(1, MAX_BODIES + 1))
        antisym_ok = all(table[(p, w)] == -table[(w, p)]
                         for p in range(1, MAX_BODIES + 1) for w in range(1, MAX_BODIES + 1))
        distinct = len(set(table.values()))
        print(f"  step {step:>2}: identity {identity_ok}, monotone {monotone_ok}, "
              f"antisymmetric {antisym_ok}, distinct values {distinct}")
    print()
    print("  Both preserve the identity case and monotonicity. The advance step wins on")
    print("  resolution -- 5 is the finest unit the engine moves a skill by at all, so an")
    print("  adjustment in 5s says nothing the engine cannot already express, and an")
    print("  adjustment in 10s throws away a rung the difficulty ladder itself uses.")
    table = {(p, w): adjustment(p, w) for p in range(1, MAX_BODIES + 1)
             for w in range(1, MAX_BODIES + 1)}
    check("the published step preserves the identity case",
          all(table[(p, p)] == 0 for p in range(1, MAX_BODIES + 1)))
    check("the adjustment never rises as the party shrinks",
          all(table[(p, w)] <= table[(p + 1, w)]
              for p in range(1, MAX_BODIES) for w in range(1, MAX_BODIES + 1)))
    check("the adjustment is antisymmetric under swapping party and written_for",
          all(table[(p, w)] == -table[(w, p)]
              for p in range(1, MAX_BODIES + 1) for w in range(1, MAX_BODIES + 1)))

    # -- T007 / the published table ----------------------------------------
    print("=" * 78)
    print("T007  The published table, and the identity case exactly")
    print("=" * 78)
    print("   party \\ written_for" + "".join(f"{w:>7}" for w in range(1, MAX_BODIES + 1)))
    for p in range(1, MAX_BODIES + 1):
        row = "".join(f"{adjustment(p, w):>+7d}" for w in range(1, MAX_BODIES + 1))
        print(f"   {p:>19}{row}")
    for p in range(1, MAX_BODIES + 1):
        check(f"identity at {p} bodies is exactly +0", adjustment(p, p) == 0,
              str(adjustment(p, p)))
        check(f"identity at {p} bodies scales danger by exactly 1",
              danger_effective(3, p, p) == 3, str(danger_effective(3, p, p)))
    print()
    print("  The diagonal is +0 all the way down: content written for four, run by four bodies,")
    print("  meets opponents at their written percentages. That is the identity case ADR 0024")
    print("  exists to protect, holding on the second of the two quantities section 7 scales.")
    print()

    # -- T009 / T010: the bound --------------------------------------------
    print("=" * 78)
    print("T009  The bound at both ends, and past it")
    print("=" * 78)
    for party, wf in ((10, 1), (20, 1), (1, 10), (1, 20)):
        raw = raw_adjustment(party, wf)
        print(f"  {party:>2} bodies vs written_for {wf:>2}: raw {raw:+6.2f} -> "
              f"clipped {adjustment(party, wf):+d}")
        check(f"the adjustment is clipped inside the ladder at {party} vs {wf}",
              abs(adjustment(party, wf)) <= LADDER_TOP, str(adjustment(party, wf)))
    print()
    print("  Outside the published table the raw value runs past the ladder, and it clips. The")
    print("  clip is symmetric at +/-20 rather than reaching the ladder's -40, because the")
    print("  adjustment must negate when party and written_for swap; a -40 floor against a +20")
    print("  ceiling would break exactly that.")
    print()
    print("T010  Nothing leaves the ladder, across every realistic combination")
    print("-" * 78)
    worst_low = None
    worst_high = None
    for p in range(1, MAX_BODIES + 1):
        for w in range(1, MAX_BODIES + 1):
            adj = adjustment(p, w)
            for skill in REAL_SKILLS + [UNTRAINED, 10, 20, 70]:
                got = adjusted_skill(skill, p, w)
                if worst_low is None or got < worst_low:
                    worst_low = got
                if worst_high is None or got > worst_high:
                    worst_high = got
    print(f"  adjusted skills across the domain run {worst_low} .. {worst_high}")
    check("no adjusted skill falls below 0", worst_low >= 0, str(worst_low))
    check("no adjusted skill exceeds 100", worst_high <= 100, str(worst_high))
    unfloored = min(skill + adjustment(p, w)
                    for p in range(1, MAX_BODIES + 1) for w in range(1, MAX_BODIES + 1)
                    for skill in REAL_SKILLS + [UNTRAINED, 10, 20, 70])
    print(f"  before the floor they would run as low as {unfloored}")
    check("the floor is load-bearing rather than decorative", unfloored < 0, str(unfloored))
    print("  The floor is the live edge, and it is doing real work: an opponent already at the")
    print("  untrained 10, in content written for six, met by a lone character, goes 20 points")
    print("  below its own percentage and lands under zero. A percentage is not a negative")
    print("  number, so it floors at 0 -- and section 1 already says what a test at or below zero")
    print("  is. It is not attempted. No new rule is needed for it.")
    print()

    # -- The count half, for completeness -----------------------------------
    print("=" * 78)
    print("Both halves together: what section 7 does to one written encounter")
    print("=" * 78)
    print("  written: 6 opponents at 45%, danger 3, written_for 4")
    print("  party  bodies   ratio  danger_eff   count   skill")
    for p in REAL_PARTIES:
        r = ratio(p, 4)
        print(f"  {p:>5}  {p:>6}  {num(r):>6}  {num(danger_effective(3, p, 4)):>10}"
              f"  {scaled_count(6, 3, p, 4):>6}  {adjusted_skill(45, p, 4):>5}")
    check("the identity party runs the encounter exactly as written",
          scaled_count(6, 3, 4, 4) == 6 and adjustment(4, 4) == 0)
    check("a count of at least 1 never scales to 0",
          all(scaled_count(1, d, p, w) >= 1
              for d in DANGERS for p in REAL_PARTIES for w in REAL_WRITTEN_FOR))
    print()

    # -- T012: the crowd lookup against the block ---------------------------
    print("=" * 78)
    print("T012  The crowd lookup, resolved from declared fields alone")
    print("=" * 78)
    for block, character_skill, skill, expected in (
        (MOB_BODY, 45, "brawl", True),
        (MOB_BODY, 45, "guile", True),
        (NEMESIS, 45, "blade", False),
        (NEMESIS, 75, "blade", False),
        (MOB_BODY, 35, "brawl", False),
        (MOB_BODY, 40, "brawl", True),
    ):
        got, why = qualifies_as_crowd(block, character_skill, skill)
        mark = "crowd" if got else "rolled"
        print(f"  {block['id']:>10} vs {character_skill:>3}% on {skill:<6} -> {mark:<6} ({why})")
        check(f"{block['id']} vs {character_skill} on {skill} lands as expected",
              got == expected, f"got {got}")
    print()
    print("  The nemesis fails on stamina_max, the first test, before skill is even consulted --")
    print("  so the rule stays a lookup and never becomes a judgement about what an opponent is")
    print("  worth. The gap boundary is exact: 40% clears a 20% body, 35% does not.")
    print()
    print("  And the baseline is what makes the second row work. Asked for a skill the block")
    print("  does not list, the body tests at 10, not at some absent value the GM invents.")
    check("an unlisted skill resolves to the baseline",
          opponent_skill(MOB_BODY, "guile") == MOB_BODY["baseline"])
    check("a listed skill is unaffected by the baseline",
          opponent_skill(NEMESIS, "blade") == 55)
    check("the baseline is not a floor under a listed skill",
          opponent_skill(MOB_BODY, "brawl") == 20 and MOB_BODY["baseline"] == 10)
    print()

    # -- T011: a full exchange ----------------------------------------------
    print("=" * 78)
    print("T011  A complete exchange against a written opponent")
    print("=" * 78)
    print(f"  {NEMESIS['name']}: baseline {NEMESIS['baseline']}%, blade "
          f"{NEMESIS['skills']['blade']}%, Stamina {NEMESIS['stamina_max']}, "
          f"{NEMESIS['armour']} armour, {NEMESIS['damage']} {NEMESIS['damage_type']}")
    print()
    print("  model     character   p(character drops)  p(opponent drops)   rounds")
    for model_name, _ in HIT_MODELS:
        for skill in REAL_SKILLS:
            pd, od, rounds, _ = fight_outcome(STARTING_STAMINA, skill,
                                              NEMESIS["skills"]["blade"], model_name,
                                              NEMESIS["stamina_max"], NEMESIS["armour"],
                                              NEMESIS["damage"])
            print(f"  {model_name:<9} {skill:>7}%  {pct(pd):>18}  {pct(od):>17}"
                  f"  {num(rounds):>7}")
            check(f"the exchange resolves under {model_name} at {skill}",
                  pd + od > Fraction(99, 100), num(pd + od, 4))
    print()
    print("  Every field the exchange consumed came off the block: the skill it resisted with,")
    print("  the armour that subtracted, the Stamina it had to lose, and the dice its own blows")
    print("  roll. Nothing was invented at the table.")
    print()

    # The damage field has to change the answer, or the fight is not reading it.
    base = fight_outcome(STARTING_STAMINA, 45, NEMESIS["skills"]["blade"], "mapped",
                         NEMESIS["stamina_max"], NEMESIS["armour"], "1d6")
    heavier = fight_outcome(STARTING_STAMINA, 45, NEMESIS["skills"]["blade"], "mapped",
                            NEMESIS["stamina_max"], NEMESIS["armour"], "2d6")
    print(f"  the same opponent swinging 1d6: character drops {pct(base[0]).strip()}")
    print(f"                        and 2d6: character drops {pct(heavier[0]).strip()}")
    check("the block's declared damage changes the outcome", heavier[0] > base[0],
          f"{pct(base[0]).strip()} vs {pct(heavier[0]).strip()}")
    print()

    # -- The critical the damage type selects -------------------------------
    print("  The critical, when the character wins: 1d6 + points below zero, on the table for")
    print(f"  the block's damage type ({NEMESIS['damage_type']}).")
    _, od, _, below = fight_outcome(STARTING_STAMINA, 55, NEMESIS["skills"]["blade"],
                                    "mapped", NEMESIS["stamina_max"], NEMESIS["armour"],
                                    NEMESIS["damage"])
    totals: dict[int, Fraction] = {}
    for points, p_points in below.items():
        for die in range(1, CRITICAL_DIE + 1):
            total = die + points
            totals[total] = totals.get(total, Fraction(0)) + p_points / CRITICAL_DIE
    mass = sum(totals.values(), Fraction(0))
    expected = sum((k * v for k, v in totals.items()), Fraction(0)) / mass
    print(f"  totals run {min(totals)} to {max(totals)}, mean {num(expected)}")
    check("every critical total reaches the table's first row",
          min(totals) >= CRITICAL_FIRST_ROW, str(min(totals)))
    check("the critical mass equals the chance the opponent dropped",
          mass == od, f"{num(mass, 4)} vs {num(od, 4)}")
    check("the damage type names a table that exists",
          NEMESIS["damage_type"] in DAMAGE_TYPES, NEMESIS["damage_type"])
    print("  The lowest reachable total is the table's own first row, which is why that row")
    print("  starts at 2 rather than 1: a blow that drops someone is at least 1 point below")
    print("  zero, and the die adds at least 1 more.")
    print()
    print("  The Aftermath table is NOT rolled here. It is rolled once per character or")
    print("  companion who dropped (03-rules.md section 2), and an adversary is neither --")
    print("  which is the same rule section 2 already states for a crowd.")
    print()

    # -- T013: the published figures ----------------------------------------
    print("=" * 78)
    print("T013  Figures earlier issues published, asserted against this model")
    print("=" * 78)
    band = [p_dropped_by_one_hit(1, w, ARMOUR["none"]) for _, w in WEAPON_BAND]
    light_worst, _ = worst_and_mean_drop(1, "light")
    s2_worst, _ = worst_and_mean_drop(2, "none")
    discounts = []
    for skill in REAL_SKILLS:
        _, mean_drop = worst_and_mean_drop(CROWD_MAX_STAMINA, CROWD_MAX_ARMOUR)
        rolled = p_mapped(skill, UNTRAINED) * mean_drop
        discounts.append(1 / float(rolled))
    # These two were published by specs/014 under the player-facing mapping, not the opposed
    # test. Asserting them against the opposed model instead reads plausible and is wrong -- it
    # gives 11.0% and 46.1%. The model has to match the one the figure was computed under.
    adv_full = fight_outcome(STARTING_STAMINA, 45, 25, "mapped")[0]
    adv_low = fight_outcome(2, 45, 25, "mapped")[0]

    published = {
        "one blow drops a Stamina-1 unarmoured body 67% to 100% of the time":
            (pct(min(band)).strip(), pct(max(band)).strip()) == ("66.7%", "100.0%"),
        "the same body in the lightest armour drops as low as 11%":
            pct(light_worst).strip() == " 11.1%".strip(),
        "a body of Stamina 2 drops as low as 33%":
            pct(s2_worst).strip() == " 33.3%".strip(),
        "the free clear is worth 1.25x to 1.82x rolling it out":
            (f"{min(discounts):.2f}", f"{max(discounts):.2f}") == ("1.25", "1.82"),
        "a character drops 14.8% of the time at full Stamina against a 20-point advantage":
            pct(adv_full).strip() == "14.8%",
        "and 48.6% at Stamina 2":
            pct(adv_low).strip() == "48.6%",
    }
    for claim, ok in published.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {claim}")
        check(f"published: {claim}", ok)
    print()
    print(f"  (band {pct(min(band)).strip()}..{pct(max(band)).strip()}, "
          f"light {pct(light_worst).strip()}, stamina-2 {pct(s2_worst).strip()}, "
          f"discount {min(discounts):.2f}x..{max(discounts):.2f}x, "
          f"drops {pct(adv_full).strip()}/{pct(adv_low).strip()})")
    print()

    # -- The block's own closure --------------------------------------------
    print("=" * 78)
    print("The block is closed, and so is every set it draws on")
    print("=" * 78)
    for block in (MOB_BODY, NEMESIS):
        unknown = set(block) - set(REQUIRED_FIELDS) - set(OPTIONAL_FIELDS)
        missing = set(REQUIRED_FIELDS) - set(block)
        check(f"{block['id']} carries every required field", not missing, str(missing))
        check(f"{block['id']} carries no undefined field", not unknown, str(unknown))
        check(f"{block['id']} armour is a published rank", block["armour"] in ARMOUR_RANKS)
        check(f"{block['id']} damage type is one of the closed four",
              block.get("damage_type") in DAMAGE_TYPES)
        for trait in block.get("traits", []):
            for effect in trait["effect"]:
                check(f"{block['id']} trait effect {effect!r} is in the vocabulary",
                      effect in TRAIT_EFFECTS, effect)
    print(f"  required fields: {', '.join(REQUIRED_FIELDS)}")
    print(f"  optional fields: {', '.join(OPTIONAL_FIELDS)}")
    print(f"  trait effects:   {', '.join(TRAIT_EFFECTS)}")
    check("the trait vocabulary touches only mechanisms that already exist",
          set(TRAIT_EFFECTS) == {"difficulty", "damage", "damage_type", "stamina_max",
                                 "armour_rank", "wyrd"})
    print()

    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("All assertions hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
