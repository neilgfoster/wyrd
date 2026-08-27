#!/usr/bin/env python3
"""Compute the mob rule: which opponents can be cleared without a roll, and how many.

CLAUDE.md: where a claim can be checked by a script, check it. The rule this replaces was one
sentence -- "each round a character also clears petty opponents weaker than themselves" -- and it
carried no numbers at all. Neither *petty* nor *weaker* was defined, so whether the rule applied
was a judgement call, which is exactly what docs/design/27-tooling.md exists to prevent.

Everything below is derived from numbers already merged, not invented here:

1. **Armour subtracts dice** -- light 1d3, modest 1d6, heavy 2d6, minimum 1 always through
   (docs/design/03-rules.md section 2).
2. **A starting character has Stamina 6** (docs/design/11-character-creation.md), and a critical
   happens when damage takes a combatant below 0.
3. **Untrained is a flat 10%**, a skill opens at 25% and rises by 5 (docs/design/03-rules.md section 1,
   docs/design/10-the-character.md).
4. **An attack is an opposed test** with the successful-actor gate and ties to the resisting side
   (docs/design/03-rules.md section 1, ADR 0016).
5. **The recorded player-facing mapping** is effective% = 50 + (player_skill - opponent_skill),
   clipped to 5-95 (specs/012-combat-sequencing, for #44 to adopt). Every claim here is computed
   under BOTH the opposed test as it stands today and that mapping, because the rule must survive
   the conversion.

Weapon damage is setting data (docs/design/24-authoring-a-setting.md), so it is modelled across the
same plausible band specs/008-character-creation/check_creation.py used, and no conclusion is
allowed to hold at only one point of it.

Run: python3 specs/013-the-mob-rule/check_mobs.py
"""

from fractions import Fraction
from itertools import product

# ---------------------------------------------------------------------------
# Numbers from merged design documents. None of these is chosen here.
# ---------------------------------------------------------------------------

ARMOUR = {"none": [], "light": [3], "modest": [6], "heavy": [6, 6]}
MIN_THROUGH = 1
WEAPON_BAND = [("1d3", [3]), ("1d6", [6]), ("1d8", [8]), ("2d6", [6, 6])]

# The ORDINARY pairing, in the sense docs/design/11-character-creation.md already uses: a mid-band
# weapon against modest armour. It is 1.56 points through and 4.5 hits to drop a starting
# character -- the figures #44 corrected this repo to and specs/012 is calibrated against. A
# crowd's blows are modelled on it rather than on the band mean, because the band mean includes
# a martial weapon in every hand, which is not what a crowd is.
ORDINARY_WEAPON = [6]

UNTRAINED = 10          # docs/design/03-rules.md section 1
SKILL_OPENS_AT = 25     # docs/design/10-the-character.md section 2
STARTING_STAMINA = 6    # docs/design/11-character-creation.md section 2

# The skills a character actually has in a real fight: newly opened, a few advances in,
# competent, and practised. Not a midpoint -- CLAUDE.md is explicit about that.
REAL_SKILLS = [25, 35, 45, 55]

# Real crowd sizes. A crowd is not two people and it is not an army.
REAL_CROWDS = [4, 6, 8, 12, 20]

# Real party sizes: the player's character plus companions.
REAL_PARTIES = [1, 2, 3, 4]

# ---------------------------------------------------------------------------
# The rule this script is testing, stated as constants so it can be falsified.
# ---------------------------------------------------------------------------

CROWD_MAX_STAMINA = 1      # a crowd member's own maximum Stamina, at or below this
CROWD_MAX_ARMOUR = "none"  # and no armour at all
CROWD_SKILL_GAP = 20       # the character's skill must exceed theirs by at least this
CLEARED_PER_ROUND = 1      # bodies removed per character per round, no roll, no action
WEIGHT_OF_NUMBERS = 10     # eased per extra body engaged with the same target
WEIGHT_CAP = 20            # ...to a ceiling of Easy on the ladder


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


def p_dropped(stamina: int, weapon: list[int], armour: list[int]) -> Fraction:
    """Chance one ordinary hit takes a body of this Stamina below 0."""
    return sum(
        (p for through, p in damage_through(weapon, armour).items() if through > stamina),
        Fraction(0),
    )


def worst_and_mean_drop(stamina: int, armour_label: str) -> tuple[Fraction, Fraction]:
    """Across the weapon band: the worst weapon's drop chance, and the band's mean."""
    armour = ARMOUR[armour_label]
    ps = [p_dropped(stamina, w, armour) for _, w in WEAPON_BAND]
    return min(ps), sum(ps, Fraction(0)) / len(ps)


# ---------------------------------------------------------------------------
# Hit chances, under both resolution models.
# ---------------------------------------------------------------------------


def degrees(skill: int, roll: int) -> int:
    return skill // 10 - roll // 10


def p_opposed_win(actor: int, resister: int) -> Fraction:
    """Actor's chance to win an opposed test: ADR 0016's successful-actor gate, ties to the
    resisting side, degrees compared only when both succeed."""
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
    """The recorded player-facing mapping: slope 1, clipped to 5-95."""
    return Fraction(max(5, min(95, 50 + player - opponent)), 100)


HIT_MODELS = [("opposed", p_opposed_win), ("mapped", p_mapped)]


# ---------------------------------------------------------------------------
# What rolling it out body by body would actually average.
# ---------------------------------------------------------------------------


def rolled_clear_rate(skill: int, model, armour_label: str, stamina: int) -> Fraction:
    """Bodies a character removes per round if they attacked the crowd and rolled for it:
    the chance the attack lands, times the chance the damage drops that body."""
    _, mean_drop = worst_and_mean_drop(stamina, armour_label)
    return model(skill, UNTRAINED) * mean_drop


# ---------------------------------------------------------------------------
# What the crowd does back.
# ---------------------------------------------------------------------------


def crowd_attack_skill(bodies_on_target: int) -> int:
    """A crowd attacks at the untrained 10%, eased by weight of numbers to a ceiling."""
    extra = max(0, bodies_on_target - 1)
    return UNTRAINED + min(WEIGHT_CAP, WEIGHT_OF_NUMBERS * extra)


def p_crowd_lands(bodies_on_target: int, defender_skill: int, model) -> Fraction:
    """The crowd's single attack against one defender, under either model.

    Under the opposed test the crowd is the acting side and the defender resists. Under the
    mapping the player still rolls, so the defender's chance to avoid it is the mapped value
    and the crowd lands on the complement.
    """
    if model is p_mapped:
        return 1 - p_mapped(defender_skill, crowd_attack_skill(bodies_on_target))
    return p_opposed_win(crowd_attack_skill(bodies_on_target), defender_skill)


def expected_damage_to_character(armour_label: str) -> Fraction:
    """Mean damage a landed crowd blow does to an armoured character, ordinary weapon."""
    dist = damage_through(ORDINARY_WEAPON, ARMOUR[armour_label])
    return sum((k * v for k, v in dist.items()), Fraction(0))


def rounds_to_drop_character(bodies_on_target: int, defender_skill: int, model,
                             armour_label: str) -> Fraction:
    """Expected rounds for a crowd to put a starting character below 0 Stamina."""
    per_round = p_crowd_lands(bodies_on_target, defender_skill, model) * \
        expected_damage_to_character(armour_label)
    if per_round == 0:
        return Fraction(10**6)
    return Fraction(STARTING_STAMINA + 1, 1) / per_round


def rounds_to_clear(crowd: int, party: int) -> Fraction:
    """Rounds for a party to clear a crowd at the free rate, ignoring their own actions."""
    return Fraction(crowd, party * CLEARED_PER_ROUND)


def pct(f: Fraction) -> str:
    return f"{float(f) * 100:5.1f}%"


def num(f: Fraction) -> str:
    return f"{float(f):5.2f}"


def main() -> int:
    failures: list[str] = []

    # -- 1. Which bodies a hit actually removes ------------------------------
    print("A single ordinary hit: chance it takes a body below 0 Stamina")
    print("-" * 74)
    print("  stamina  armour" + "".join(f"{label:>9}" for label, _ in WEAPON_BAND) + "     worst")
    for stamina in range(1, 5):
        for armour_label in ("none", "light", "modest"):
            row = "".join(
                pct(p_dropped(stamina, w, ARMOUR[armour_label])).rjust(9)
                for _, w in WEAPON_BAND
            )
            worst, _ = worst_and_mean_drop(stamina, armour_label)
            print(f"  {stamina:>7}  {armour_label:>6}{row}{pct(worst).rjust(10)}")
    print()
    print("  This is why the threshold is a small number. A body with a starting character's")
    print("  Stamina is not cleared by one blow under any weapon in the band, so 'petty' can")
    print("  never mean 'ordinary person in armour'.")
    print()

    # The threshold has to hold across the whole weapon band, not at one convenient point:
    # the WORST weapon must still drop a qualifying body more often than not. Otherwise the
    # free clear is doing work the dice would not have done.
    worst_qualifying, _ = worst_and_mean_drop(CROWD_MAX_STAMINA, CROWD_MAX_ARMOUR)
    if worst_qualifying <= Fraction(1, 2):
        failures.append(
            f"A qualifying body (Stamina {CROWD_MAX_STAMINA}, {CROWD_MAX_ARMOUR} armour) is "
            f"dropped by the worst weapon in the band only {pct(worst_qualifying).strip()} of "
            "the time. One blow does not remove them, so the definition is wrong."
        )

    # And the next body up must FAIL that same bar, or the threshold is arbitrary. This is
    # what makes the definition a lookup: the line sits where one blow stops being enough.
    worst_next, _ = worst_and_mean_drop(CROWD_MAX_STAMINA + 1, CROWD_MAX_ARMOUR)
    if worst_next > Fraction(1, 2):
        failures.append(
            f"Stamina {CROWD_MAX_STAMINA + 1} also passes the one-blow bar "
            f"({pct(worst_next).strip()} on the worst weapon). The threshold is drawn in the "
            "wrong place and should be higher."
        )
    # Armour is the other half of the definition, and it must matter: the same body in the
    # lightest armour must fail the bar, or 'no armour' is decoration.
    worst_armoured, _ = worst_and_mean_drop(CROWD_MAX_STAMINA, "light")
    if worst_armoured > Fraction(1, 2):
        failures.append(
            "The same body in light armour still passes the one-blow bar "
            f"({pct(worst_armoured).strip()}). The armour clause is doing no work."
        )

    # -- 2. The free clear against what rolling would give -------------------
    print("Bodies cleared per round: the free rate against rolling it out")
    print("-" * 74)
    print("  A qualifying body has maximum Stamina %d, wears %s armour, untrained at %d%%."
          % (CROWD_MAX_STAMINA, CROWD_MAX_ARMOUR, UNTRAINED))
    print()
    print("   skill   model     hit    drop   rolled    free   generosity")
    generosities: list[Fraction] = []
    for skill in REAL_SKILLS:
        for label, model in HIT_MODELS:
            hit = model(skill, UNTRAINED)
            _, drop = worst_and_mean_drop(CROWD_MAX_STAMINA, CROWD_MAX_ARMOUR)
            rolled = rolled_clear_rate(skill, model, CROWD_MAX_ARMOUR, CROWD_MAX_STAMINA)
            factor = Fraction(CLEARED_PER_ROUND, 1) / rolled
            generosities.append(factor)
            print(f"  {skill:>5}%  {label:>7}{pct(hit).rjust(8)}{pct(drop).rjust(8)}"
                  f"{num(rolled).rjust(9)}{CLEARED_PER_ROUND:>8}{num(factor).rjust(13)}x")
    print()
    mapped_only = [
        Fraction(CLEARED_PER_ROUND, 1)
        / rolled_clear_rate(skill, p_mapped, CROWD_MAX_ARMOUR, CROWD_MAX_STAMINA)
        for skill in REAL_SKILLS
    ]
    print(f"  Under the mapping the free clear is {float(min(mapped_only)):.2f}x to "
          f"{float(max(mapped_only)):.2f}x what rolling body by body would average.")
    print(f"  Under today's opposed test it reads as high as {float(max(generosities)):.2f}x,")
    print("  because that test has a competent character missing an untrained one two times")
    print("  in three. That gap is #44's to close and is not this rule's to answer for.")
    print()

    # The shortcut is generous by construction -- that is what buying out a d100 per body
    # costs. What is checkable is the size of the discount, and it is checked under the
    # mapping, because that is the resolution this rule has to live under (#44). Today's
    # opposed test is reported alongside it and deliberately not gated on: it understates a
    # lopsided fight badly enough that a competent character whiffs two attacks in three
    # against an untrained one, which is the fault #44 exists to correct, not a fault here.
    mapped_factors = [
        Fraction(CLEARED_PER_ROUND, 1)
        / rolled_clear_rate(skill, p_mapped, CROWD_MAX_ARMOUR, CROWD_MAX_STAMINA)
        for skill in REAL_SKILLS
    ]
    if max(mapped_factors) > 2:
        failures.append(
            f"Under the mapping the free clear is {float(max(mapped_factors)):.2f}x the "
            "rolled-out rate. Past 2x the shortcut is not a shortcut, it is a better attack "
            "than attacking."
        )
    if min(mapped_factors) < 1:
        failures.append(
            "Rolling body by body clears faster than the free rate at some real skill. "
            "Nobody would ever use the rule."
        )
    # A free clear above 1 per round would exceed a character's own action, which is one
    # thing per turn (docs/design/03-rules.md section 2).
    if CLEARED_PER_ROUND > 1:
        failures.append(
            "A character does one thing on their turn. Clearing more than one body for free "
            "makes the crowd worth more than the fight."
        )

    # -- 3. What the crowd does back -----------------------------------------
    print("What the crowd does back: rounds to put a starting character below 0")
    print("-" * 74)
    print("  Defender at %d%%, Stamina %d. Weight of numbers eases the crowd's attack by +%d"
          % (REAL_SKILLS[2], STARTING_STAMINA, WEIGHT_OF_NUMBERS))
    print("  per extra body on the same target, to a ceiling of +%d." % WEIGHT_CAP)
    print()
    print("  bodies   crowd%   armour   opposed    mapped")
    for bodies in (1, 2, 3, 4, 6):
        row = []
        for armour_label in ("none", "modest"):
            for label, model in HIT_MODELS:
                row.append(rounds_to_drop_character(bodies, REAL_SKILLS[2], model, armour_label))
        print(f"  {bodies:>6}   {crowd_attack_skill(bodies):>5}%     none"
              f"{num(row[0]).rjust(10)}{num(row[1]).rjust(10)}")
        print(f"  {'':>6}   {'':>6}   modest{num(row[2]).rjust(10)}{num(row[3]).rjust(10)}")
    print()

    # A crowd that cannot hurt anyone is scenery; a crowd that drops a character in a round
    # is not a crowd of the weak. Both bounds are checked at the sizes play actually uses.
    for bodies in (1, 2, 3, 4, 6):
        for armour_label in ("none", "modest"):
            for label, model in HIT_MODELS:
                r = rounds_to_drop_character(bodies, REAL_SKILLS[2], model, armour_label)
                if r < 2:
                    failures.append(
                        f"{bodies} bodies drop a competent, {armour_label}-armoured character in "
                        f"{float(r):.2f} rounds ({label}). Weight of numbers is doing too much."
                    )
    unarmoured_worst = min(
        rounds_to_drop_character(6, REAL_SKILLS[2], model, "none") for _, model in HIT_MODELS
    )
    if unarmoured_worst > 12:
        failures.append(
            f"Six bodies need {float(unarmoured_worst):.1f} rounds to threaten an unarmoured "
            "competent character. A crowd is scenery and the rule protects nobody."
        )

    # -- 3a. Where numbers stop helping, and what they buy instead ------------
    saturates_at = 1 + WEIGHT_CAP // WEIGHT_OF_NUMBERS
    print("Bodies on one target, at real crowd and party sizes")
    print("-" * 74)
    print("  A crowd rolls once per character it is engaged with, never once per body. Weight")
    print("  of numbers reaches its ceiling at %d bodies on a target, so a crowd's numbers past"
          % saturates_at)
    print("  that buy nothing against one defender -- what they buy is more defenders engaged.")
    print()
    print("  party " + "".join(f"{c:>8}" for c in REAL_CROWDS))
    for party in REAL_PARTIES:
        print(f"  {party:>5} " + "".join(
            f"{Fraction(c, party).__float__():>8.1f}" for c in REAL_CROWDS
        ))
    print()
    print("  A party of four is at the ceiling from twelve bodies on. Below that, spreading")
    print("  out is worth something; above it, only the count of people who can be reached is.")
    print()

    if saturates_at * max(REAL_PARTIES) > max(REAL_CROWDS):
        failures.append(
            f"A crowd of {max(REAL_CROWDS)} cannot reach the ceiling against a party of "
            f"{max(REAL_PARTIES)}. The largest real crowd is not a full-strength crowd, so the "
            "weight-of-numbers rule never fires at the sizes play uses."
        )

    # -- 4. Real party sizes against real crowds ------------------------------
    print("Rounds to clear, at real party and crowd sizes")
    print("-" * 74)
    print("  party " + "".join(f"{c:>8}" for c in REAL_CROWDS))
    for party in REAL_PARTIES:
        print(f"  {party:>5} " + "".join(
            num(rounds_to_clear(c, party)).rjust(8) for c in REAL_CROWDS
        ))
    print()
    print("  Read against the rounds-to-drop table above: a lone character does not clear a")
    print("  crowd of twenty, and a party of four handles one in five rounds while still")
    print("  taking their own turns against whatever the crowd was protecting.")
    print()

    # The rule's stated purpose is that one character plus companions can face a crowd.
    # A party of four against the largest real crowd must finish inside a fight's length,
    # and a lone character against the same crowd must not.
    party_of_four = rounds_to_clear(max(REAL_CROWDS), 4)
    lone = rounds_to_clear(max(REAL_CROWDS), 1)
    if party_of_four > 8:
        failures.append(
            f"A party of four needs {float(party_of_four):.1f} rounds against {max(REAL_CROWDS)} "
            "bodies. The rule does not deliver what it exists for."
        )
    # And the rule must not make a crowd harmless. A lone competent character in no armour
    # is dropped by six bodies faster than they can clear six bodies -- so the answer to a
    # crowd is companions or armour, not the rule.
    lone_clears_six = rounds_to_clear(6, 1)
    lone_dropped_by_six = min(
        rounds_to_drop_character(6, REAL_SKILLS[2], model, "none") for _, model in HIT_MODELS
    )
    print(f"  A lone competent character in no armour clears six bodies in "
          f"{num(lone_clears_six).strip()} rounds and is dropped by them in "
          f"{num(lone_dropped_by_six).strip()}.")
    print("  The rule is not a way to win alone; it is a way to not roll sixty times.")
    print()
    if lone_dropped_by_six > lone_clears_six:
        failures.append(
            f"A lone character clears six bodies in {float(lone_clears_six):.1f} rounds and "
            f"survives {float(lone_dropped_by_six):.1f}. The rule wins the fight by itself."
        )

    if lone <= 8:
        failures.append(
            f"One character alone clears {max(REAL_CROWDS)} bodies in {float(lone):.1f} rounds. "
            "The rule makes a crowd harmless to a single character, which is not what it says."
        )

    # -- 5. The skill gap -----------------------------------------------------
    print("The skill gap: who the rule is available to")
    print("-" * 74)
    print("  A crowd member is untrained at %d%%. The rule needs a gap of %d or more."
          % (UNTRAINED, CROWD_SKILL_GAP))
    print()
    print("  A skill opens at %d%% and rises by 5, so the rule opens at %d%% -- one advance"
          % (SKILL_OPENS_AT, UNTRAINED + CROWD_SKILL_GAP))
    print("  past opening. An untrained character has no gap at all and clears nobody.")
    print()

    if UNTRAINED + CROWD_SKILL_GAP <= SKILL_OPENS_AT:
        failures.append(
            f"A gap of {CROWD_SKILL_GAP} is cleared by a skill on the day it opens "
            f"({SKILL_OPENS_AT}%). 'Weaker than themselves' would mean 'trained at all'."
        )
    if UNTRAINED + CROWD_SKILL_GAP > SKILL_OPENS_AT + 25:
        failures.append(
            f"A gap of {CROWD_SKILL_GAP} needs {UNTRAINED + CROWD_SKILL_GAP}%, five advances "
            "past opening. The rule would almost never be available."
        )

    # -- 6. Agreement with what earlier issues already computed ---------------
    print("Agreement with figures earlier issues computed")
    print("-" * 74)
    modest = expected_damage_to_character("modest")
    hits = Fraction(STARTING_STAMINA + 1, 1) / modest
    print(f"  Mean damage through modest armour: {num(modest)} per landed blow "
          "(mid-band weapon).")
    print(f"  Hits to drop a starting character: {num(hits)}.")
    print("  #44 corrected this repo to about 1.5 points through and 4.5 hits to drop, and")
    print("  specs/012 is calibrated to it. A mob rule computed on a different damage scale")
    print("  would be internally tidy and wrong, which is how two probability claims here")
    print("  have already been wrong.")
    print()
    if not Fraction(5, 4) <= modest <= Fraction(7, 4):
        failures.append(
            f"Mean damage through modest armour is {float(modest):.2f}, against the ~1.5 that "
            "#44 established and specs/012 is calibrated to. This script and that one disagree."
        )
    if not 4 <= float(hits) <= 5:
        failures.append(
            f"A starting character takes {float(hits):.2f} hits to drop here, against the 4.5 "
            "#44 computed. The damage scale underneath this rule is not the merged one."
        )
    # The player-facing mapping must be the one specs/012 recorded, not a re-derivation.
    if (p_mapped(40, 40), p_mapped(100, 0), p_mapped(0, 100)) != \
            (Fraction(1, 2), Fraction(95, 100), Fraction(5, 100)):
        failures.append(
            "The mapping used here is not slope 1 clipped to 5-95, which is what "
            "specs/012-combat-sequencing/check_mapping.py computed and recorded for #44."
        )

    # -- 7. The figures docs/design/03-rules.md publishes --------------------------
    # Tables are where staleness hides (CLAUDE.md): each row reads as a small factual claim
    # and nothing about a wrong one looks wrong. Every number the rule states in prose is
    # asserted here, so changing the model here fails rather than silently disagreeing with
    # the design document.
    published = [
        ("one blow, Stamina 1, no armour, worst weapon", worst_and_mean_drop(1, "none")[0],
         Fraction(2, 3)),
        ("one blow, Stamina 1, light armour, worst weapon", worst_and_mean_drop(1, "light")[0],
         Fraction(1, 9)),
        ("one blow, Stamina 2, no armour, worst weapon", worst_and_mean_drop(2, "none")[0],
         Fraction(1, 3)),
        ("rolled clear rate at 25%, mapped",
         rolled_clear_rate(25, p_mapped, CROWD_MAX_ARMOUR, CROWD_MAX_STAMINA), Fraction(55, 100)),
        ("rolled clear rate at 55%, mapped",
         rolled_clear_rate(55, p_mapped, CROWD_MAX_ARMOUR, CROWD_MAX_STAMINA), Fraction(80, 100)),
        ("six bodies drop an unarmoured character in",
         rounds_to_drop_character(6, REAL_SKILLS[2], p_mapped, "none"), Fraction(57, 10)),
        ("six bodies drop a modest-armoured character in",
         rounds_to_drop_character(6, REAL_SKILLS[2], p_mapped, "modest"), Fraction(129, 10)),
    ]
    print("The figures docs/design/03-rules.md publishes")
    print("-" * 74)
    for label, computed, stated in published:
        agrees = abs(computed - stated) <= abs(stated) / 100
        print(f"  {label:<48}{num(computed)}  vs {num(stated)}  "
              f"{'ok' if agrees else 'DRIFT'}")
        if not agrees:
            failures.append(
                f"docs/design/03-rules.md states {float(stated):.2f} for {label}; this script "
                f"computes {float(computed):.2f}. One of the two is stale."
            )
    print()

    print("=" * 74)
    if failures:
        for f in failures:
            print("FAIL: " + f)
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
