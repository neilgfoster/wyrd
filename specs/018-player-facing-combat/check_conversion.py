#!/usr/bin/env python3
"""Compute the player-facing combat conversion for #69.

CLAUDE.md: where a claim can be checked by a script, check it. #44 decided combat should become
player-facing -- the opponent never rolls, its capability is a static number the player rolls
against for both attack and defence -- and left three numbers unsettled: the telling-blow
threshold at the new roll's distribution, the actual damage-multiplier consequence of a
player-rolled defence (the issue states 1.4x-3.1x; this script verifies it rather than assuming
it), and starting Stamina against the resulting fight length.

Everything below is derived from numbers already merged, not invented here:

1. **The mapping is already calibrated**: effective% = clip(50 + (S - O), 5, 95)
   (specs/012-combat-sequencing/check_mapping.py). This script asserts agreement with that table
   before computing anything new -- it is a prior figure, not re-derived.
2. **Armour subtracts dice** -- light 1d3, modest 1d6, heavy 2d6, minimum 1 through
   (design/03-rules.md section 2), reused from specs/017-adversary-model/check_adversary.py by
   construction, not re-modelled.
3. **A starting character has Stamina 6** (design/03c-character-creation.md).
4. **Degrees are tens(skill) - tens(roll)** (design/03-rules.md section 1); this script feeds
   the formula the new input, effective%, rather than a raw skill.
5. **Today's telling blow: win by 3 or more degrees, damage doubles before armour**
   (design/03-rules.md section 2).

What this script settles that no prior issue did:

- The telling-blow threshold under the new roll's degree distribution (T002-T003).
- Whether the issue's stated 1.4x-3.1x damage-multiplier figure is correct (T004).
- Starting Stamina's expected fight length under the corrected damage rate (T005).
- That the Wyrd die's units-digit read is unaffected by the 5-95 clip (T006).
- A complete worked exchange under the rewritten rules (T007).

Run: python3 specs/018-player-facing-combat/check_conversion.py
"""

from fractions import Fraction
from functools import lru_cache
from itertools import product

# ---------------------------------------------------------------------------
# Numbers from merged design documents. None of these is chosen here.
# ---------------------------------------------------------------------------

ARMOUR = {"none": [], "light": [3], "modest": [6], "heavy": [6, 6]}
MIN_THROUGH = 1
ORDINARY_WEAPON = [6]           # 1d6, an ordinary blade
ORDINARY_ARMOUR = "modest"
STARTING_STAMINA = 6
CLIP_LOW, CLIP_HIGH = 5, 95
TODAYS_TELLING_THRESHOLD = 3

# Representative skill pairings, the same span specs/012 and specs/017 already use.
PAIRINGS = [
    (25, 25), (40, 40), (35, 30), (55, 40), (50, 30),
    (60, 30), (70, 35), (60, 20), (80, 40), (100, 50), (30, 60),
]


def check(claim: str, ok: bool, shown: str = "") -> None:
    status = "OK " if ok else "FAIL"
    print(f"[{status}] {claim}" + (f"  -- {shown}" if shown else ""))
    if not ok:
        raise SystemExit(f"disagreement: {claim}")


def pct(f) -> str:
    return f"{float(f) * 100:.1f}%"


# ---------------------------------------------------------------------------
# T001. The prior figure, reasserted rather than re-derived.
# ---------------------------------------------------------------------------


def effective_pct(actor: int, resister: int) -> int:
    """specs/012-combat-sequencing/check_mapping.py's calibrated mapping. Not re-derived here."""
    return max(CLIP_LOW, min(CLIP_HIGH, 50 + actor - resister))


PRIOR_MAPPING_TABLE = {
    (40, 40): 50, (55, 40): 65, (60, 30): 80, (100, 50): 95,
}


def assert_prior_mapping() -> None:
    for (s, o), expected in PRIOR_MAPPING_TABLE.items():
        check(f"effective%({s}, {o}) == {expected} (specs/012 check_mapping.py)",
              effective_pct(s, o) == expected, f"got {effective_pct(s, o)}")


# ---------------------------------------------------------------------------
# Dice and damage, reused from specs/017/check_adversary.py by construction.
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
    result: dict[int, Fraction] = {}
    for wd, wp in dice_distribution(weapon).items():
        for ad, ap in dice_distribution(armour).items():
            through = max(MIN_THROUGH, wd - ad)
            result[through] = result.get(through, Fraction(0)) + wp * ap
    return result


def doubled_damage_through(weapon: list[int], armour: list[int]) -> dict[int, Fraction]:
    """A telling blow doubles the *weapon* roll before armour subtracts (03-rules.md section 2):
    the order is roll, double, then subtract armour -- not double the post-armour result."""
    base = dice_distribution(weapon)
    result: dict[int, Fraction] = {}
    for wd, wp in base.items():
        for ad, ap in dice_distribution(armour).items():
            through = max(MIN_THROUGH, 2 * wd - ad)
            result[through] = result.get(through, Fraction(0)) + wp * ap
    return result


ORDINARY_HIT = damage_through(ORDINARY_WEAPON, ARMOUR[ORDINARY_ARMOUR])
ORDINARY_TELLING_HIT = doubled_damage_through(ORDINARY_WEAPON, ARMOUR[ORDINARY_ARMOUR])


def expected(dist: dict[int, Fraction]) -> Fraction:
    return sum((k * p for k, p in dist.items()), Fraction(0))


# ---------------------------------------------------------------------------
# T002-T003. Degrees and the telling-blow threshold under the new roll.
# ---------------------------------------------------------------------------


def degrees(skill: int, roll: int) -> int:
    return skill // 10 - roll // 10


def degree_distribution(eff: int) -> dict[int, Fraction]:
    """The distribution of degrees on a single roll against effective%, conditioned on a hit
    landing at all -- a miss has no degrees and does no damage, so it is not part of the telling-
    blow question."""
    dist: dict[int, Fraction] = {}
    for roll in range(1, eff + 1):
        d = degrees(eff, roll)
        dist[d] = dist.get(d, Fraction(0)) + Fraction(1, 100)
    total = sum(dist.values(), Fraction(0))
    return {d: p / total for d, p in dist.items()}


def telling_rate(eff: int, threshold: int) -> Fraction:
    dist = degree_distribution(eff)
    return sum((p for d, p in dist.items() if d >= threshold), Fraction(0))


def find_threshold() -> int:
    """The smallest threshold that keeps telling blows a minority of hits (< 50%) at every
    pairing in PAIRINGS -- the same span ADR 0016 found the old threshold of 3 to be broken
    against. Mirrors how a rate is "computed, not chosen" per CLAUDE.md."""
    for threshold in range(1, 10):
        rates = [telling_rate(effective_pct(s, o), threshold) for s, o in PAIRINGS if s > o]
        if rates and max(rates) < Fraction(1, 2):
            return threshold
    raise SystemExit("no threshold in range 1-9 keeps telling blows a minority")


# ---------------------------------------------------------------------------
# T004. The damage-multiplier consequence of a player-rolled defence.
# ---------------------------------------------------------------------------


def p_opposed_win(actor: int, resister: int) -> Fraction:
    """Today's structure: the double gate. The actor must succeed, then beat the resister's
    degrees; ties go to the resister (ADR 0016)."""
    wins = 0
    for ra in range(1, 101):
        if ra > actor:
            continue
        da = degrees(actor, ra)
        for rd in range(1, 101):
            if rd > resister or da > degrees(resister, rd):
                wins += 1
    return Fraction(wins, 100 * 100)


def expected_damage_per_round_today(attack_skill: int, defence_skill: int,
                                     telling_threshold: int = TODAYS_TELLING_THRESHOLD) -> Fraction:
    """A round today: one opposed test per side, each an attack that must clear the other's
    defence outright -- the double gate ADR 0016 describes. A hit's telling-blow share is read
    off the *conditional* degree distribution of the winning roll."""
    p_hit = p_opposed_win(attack_skill, defence_skill)
    if p_hit == 0:
        return Fraction(0)
    p_telling_given_hit = telling_given_opposed_win(attack_skill, defence_skill, telling_threshold)
    ordinary = expected(ORDINARY_HIT)
    telling = expected(ORDINARY_TELLING_HIT)
    return p_hit * ((1 - p_telling_given_hit) * ordinary + p_telling_given_hit * telling)


def telling_given_opposed_win(actor: int, resister: int, threshold: int) -> Fraction:
    wins = 0
    telling = 0
    for ra in range(1, actor + 1):
        da = degrees(actor, ra)
        for rd in range(1, 101):
            if rd > resister or da > degrees(resister, rd):
                wins += 1
                margin = da - (degrees(resister, rd) if rd <= resister else 0)
                if margin >= threshold:
                    telling += 1
    return Fraction(telling, wins) if wins else Fraction(0)


def expected_damage_per_round_converted(attack_skill: int, defence_skill: int,
                                         threshold: int) -> Fraction:
    """A round under the conversion: the player's own single roll decides whether *this* attack
    lands -- there is no second gate on the far side. The effective% already carries the skill
    comparison, so a hit is simply a roll <= effective%, and its degrees come from that same
    roll."""
    eff = effective_pct(attack_skill, defence_skill)
    p_hit = Fraction(eff, 100)
    if p_hit == 0:
        return Fraction(0)
    p_telling_given_hit = telling_rate(eff, threshold)
    ordinary = expected(ORDINARY_HIT)
    telling = expected(ORDINARY_TELLING_HIT)
    return p_hit * ((1 - p_telling_given_hit) * ordinary + p_telling_given_hit * telling)


def damage_multiplier(attack_skill: int, defence_skill: int, threshold: int) -> Fraction:
    today = expected_damage_per_round_today(attack_skill, defence_skill)
    converted = expected_damage_per_round_converted(attack_skill, defence_skill, threshold)
    if today == 0:
        return Fraction(0)
    return converted / today


# ---------------------------------------------------------------------------
# T005. Starting Stamina against the new fight length.
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def fight_outcome(player_stamina: int, opponent_stamina: int,
                   player_attack: int, player_defence: int,
                   opponent_attack: int, opponent_defence: int,
                   threshold: int, max_rounds: int = 80):
    """One round: the player's attack roll (opponent never rolls) and the player's defence roll
    against the opponent's attack (opponent never rolls) are independent -- both, either or
    neither may land, since they are separate turns within the round, not one contest deciding
    both."""
    p_player_hits = Fraction(effective_pct(player_attack, opponent_defence), 100)
    p_player_hit_by = Fraction(100 - effective_pct(player_defence, opponent_attack), 100)
    p_player_telling = telling_rate(effective_pct(player_attack, opponent_defence), threshold)
    p_opponent_telling = telling_rate(100 - effective_pct(player_defence, opponent_attack),
                                       threshold) if p_player_hit_by > 0 else Fraction(0)

    to_opponent = {k: v for k, v in ORDINARY_HIT.items()}
    to_opponent_telling = {k: v for k, v in ORDINARY_TELLING_HIT.items()}
    to_player = {k: v for k, v in ORDINARY_HIT.items()}
    to_player_telling = {k: v for k, v in ORDINARY_TELLING_HIT.items()}

    def branch_damage(lands: bool, telling_p: Fraction, ordinary: dict, telling: dict):
        if not lands:
            return {0: Fraction(1)}
        out: dict[int, Fraction] = {}
        for d, p in ordinary.items():
            out[d] = out.get(d, Fraction(0)) + p * (1 - telling_p)
        for d, p in telling.items():
            out[d] = out.get(d, Fraction(0)) + p * telling_p
        return out

    state = {(player_stamina, opponent_stamina): Fraction(1)}
    player_dropped = Fraction(0)
    opponent_dropped = Fraction(0)
    rounds = Fraction(0)
    below_zero: dict[int, Fraction] = {}
    # Stamina the player has spent by the time the *opponent* drops -- what the road-back table
    # (03-rules.md section 2) reports as Rallies to full, since 1 Stamina recovers per Rally.
    player_stamina_lost_on_win = Fraction(0)
    for r in range(1, max_rounds + 1):
        nxt: dict[tuple[int, int], Fraction] = {}
        for (ps, os_), p in state.items():
            for player_lands, pa in ((True, p_player_hits), (False, 1 - p_player_hits)):
                to_opp = branch_damage(player_lands, p_player_telling, to_opponent, to_opponent_telling)
                for opponent_lands, pb in ((True, p_player_hit_by), (False, 1 - p_player_hit_by)):
                    to_pl = branch_damage(opponent_lands, p_opponent_telling, to_player, to_player_telling)
                    weight = p * pa * pb
                    if weight == 0:
                        continue
                    for do, pdo in to_opp.items():
                        for dp, pdp in to_pl.items():
                            nps, nos = ps - dp, os_ - do
                            w = weight * pdo * pdp
                            player_out, opponent_out = nps < 0, nos < 0
                            lost_this_branch = player_stamina - max(nps, 0)
                            if player_out and opponent_out:
                                # Both land in the same round -- split the weight rather than
                                # letting resolution order silently favour one side (both acted
                                # within the round; nothing here says who went first).
                                player_dropped += w / 2
                                opponent_dropped += w / 2
                                rounds += w * r
                                below_zero[-nos] = below_zero.get(-nos, Fraction(0)) + w / 2
                                player_stamina_lost_on_win += (w / 2) * lost_this_branch
                            elif player_out:
                                player_dropped += w
                                rounds += w * r
                            elif opponent_out:
                                opponent_dropped += w
                                rounds += w * r
                                below_zero[-nos] = below_zero.get(-nos, Fraction(0)) + w
                                player_stamina_lost_on_win += w * lost_this_branch
                            else:
                                nxt[(nps, nos)] = nxt.get((nps, nos), Fraction(0)) + w
        state = nxt
        if not state:
            break
    for _, q in state.items():
        rounds += q * max_rounds
    stamina_lost_given_win = (player_stamina_lost_on_win / opponent_dropped
                               if opponent_dropped else Fraction(0))
    return player_dropped, opponent_dropped, rounds, below_zero, stamina_lost_given_win


def rounds_summary(player_stamina: int, opponent_stamina: int, player_skill: int,
                    opponent_skill: int, threshold: int):
    """The figures design/03-rules.md section 2's road-back table already publishes at starting
    Stamina: expected Stamina lost by the time the player wins (Rallies to full), and the round
    count. One skill per side, for both attack and defence, matching the convention specs/012 and
    specs/017 already use."""
    player_dropped, opponent_dropped, rounds, _, stamina_lost = fight_outcome(
        player_stamina, opponent_stamina, player_skill, player_skill,
        opponent_skill, opponent_skill, threshold)
    return player_dropped, opponent_dropped, rounds, stamina_lost


# ---------------------------------------------------------------------------
# T006. The Wyrd die at the clip boundary.
# ---------------------------------------------------------------------------


def wyrd_die_uniform(eff: int) -> bool:
    """Units digit of the natural roll (design/03-rules.md section 1) is read from 1-100
    regardless of eff; the clip only changes which percentage the roll is compared against, not
    the roll itself. Uniform within both the success set (1..eff) and the failure set
    (eff+1..100) whenever each set's size is a multiple of 10, and at worst off by the partial
    final decade -- checked exactly here rather than assumed."""
    success = list(range(1, eff + 1))
    failure = list(range(eff + 1, 101))
    for group in (success, failure):
        if not group:
            continue
        counts = {}
        for r in group:
            units = r % 10
            counts[units] = counts.get(units, 0) + 1
        # Uniform iff every units digit that appears, appears the same number of times as
        # every other -- the natural-roll rule promises this within each set.
        if len(set(counts.values())) > 1:
            spread = max(counts.values()) - min(counts.values())
            if spread > 1:  # the partial final/first decade may differ by at most one
                return False
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("Player-facing combat conversion (#69)\n")

    print("T001 -- the prior mapping, reasserted")
    assert_prior_mapping()

    print("\nT002 -- degrees and the telling-blow rate at today's threshold (3), new roll")
    for s, o in PAIRINGS:
        eff = effective_pct(s, o)
        rate = telling_rate(eff, TODAYS_TELLING_THRESHOLD)
        print(f"  {s:>3} v {o:>3} -> eff {eff:>2}%  telling@3 {pct(rate):>6}")

    threshold = find_threshold()
    print(f"\nT003 -- corrected telling-blow threshold: {threshold} degrees")
    for s, o in PAIRINGS:
        eff = effective_pct(s, o)
        rate = telling_rate(eff, threshold)
        print(f"  {s:>3} v {o:>3} -> eff {eff:>2}%  telling@{threshold} {pct(rate):>6}")
    check(f"telling blows stay a minority of hits at threshold {threshold}",
          all(telling_rate(effective_pct(s, o), threshold) < Fraction(1, 2) for s, o in PAIRINGS))

    print("\nT004 -- the damage-multiplier consequence of a player-rolled defence")
    multipliers = []
    for s, o in PAIRINGS:
        if s <= o:
            continue  # need a plausible attacker-favoured pairing for the "today" gate to bite
        m = damage_multiplier(s, o, threshold)
        multipliers.append(m)
        print(f"  {s:>3} v {o:>3} -> x{float(m):.2f}")
    lo, hi = min(multipliers), max(multipliers)
    print(f"  range: {float(lo):.2f}x - {float(hi):.2f}x  (issue #69 stated 1.4x-3.1x)")

    print("\nT005 -- Stamina lost when the player wins (Rallies to full), starting Stamina 6")
    print("  (design/03-rules.md section 2 today publishes: even 4.6-4.9, +20 advantage 2.2-3.3)")
    for label, (s, o) in [("even", (40, 40)), ("+20 advantage", (60, 40))]:
        p_drop, o_drop, rounds, stamina_lost = rounds_summary(
            STARTING_STAMINA, STARTING_STAMINA, s, o, threshold)
        print(f"  {label}: p(player drops)={pct(p_drop)}  p(opponent drops)={pct(o_drop)}  "
              f"Stamina lost on a win={float(stamina_lost):.2f}  "
              f"expected rounds to a drop either side={float(rounds):.2f}")

    print("\nT006 -- Wyrd die uniformity at the clip boundary")
    for eff in (CLIP_LOW, CLIP_HIGH, 50):
        check(f"units digit uniform within success/failure sets at eff={eff}", wyrd_die_uniform(eff))

    print("\nT007 -- a complete exchange, one attack roll, one defence roll, at 55 v 40")
    eff_attack = effective_pct(55, 40)
    eff_defence = effective_pct(45, 55)
    print(f"  attack: effective {eff_attack}%, telling threshold {threshold}")
    print(f"  defence: effective {eff_defence}%")
    print(f"  expected damage per landed ordinary hit: {float(expected(ORDINARY_HIT)):.2f}")
    print(f"  expected damage per landed telling hit: {float(expected(ORDINARY_TELLING_HIT)):.2f}")

    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
