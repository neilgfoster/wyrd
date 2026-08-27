#!/usr/bin/env python3
"""Compute whether a +/-10 combat-Omen roll modifier meaningfully shifts expected damage per
round and fight length, against the figures ADR 0028/check_conversion.py already published
without it.

CLAUDE.md: where a claim can be checked by a script, check it. #159 proposes that a combat Ill
Omen applies -10 to the roller's own next roll in the same fight, and a Fair Omen +10 -- the
roller being the player, since the opponent never rolls (ADR 0027) and the Wyrd die "always
belongs to the player making the roll, attack or defence" (03-rules.md sec2). Because the
opponent never rolls, every Omen in a fight belongs to the player, and "the roller's own next
roll" is simply the player's next roll of any kind (attack or defence), in chronological order.

This reuses specs/018-player-facing-combat/check_conversion.py's own numbers (armour, weapon,
telling threshold, PAIRINGS) rather than re-deriving them, and extends its per-round Markov model
with one extra state dimension: the pending modifier (-10, 0, +10) on the player's next roll.

Rolls are grouped into probability buckets (miss/ordinary-hit/telling-hit x omen face) rather
than enumerated one natural roll at a time, since the branching factor of 100 raw rolls per roll,
two rolls per round, times a growing (stamina x stamina x pending) state space, is what made the
first version of this script too slow to finish -- CLAUDE.md's own recorded fault ("exact
arithmetic scripts are slow; memoize... up front").

Run: python3 specs/049-combat-omen-mechanical-effect/check_omen_effect.py
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache

CLIP_LOW, CLIP_HIGH = 5, 95
ARMOUR = {"none": [], "light": [3], "modest": [6], "heavy": [6, 6]}
ORDINARY_WEAPON = [6]  # 1d6
ORDINARY_ARMOUR = "modest"
TELLING_THRESHOLD = 6  # ADR 0028's accepted threshold
STARTING_STAMINA = 6

PAIRINGS = [
    (25, 25), (40, 40), (35, 30), (55, 40), (50, 30),
    (60, 30), (70, 35), (60, 20), (80, 40), (100, 50),
]


def effective_pct(actor: int, resister: int) -> int:
    return max(CLIP_LOW, min(CLIP_HIGH, 50 + actor - resister))


def clip(x: int) -> int:
    return max(CLIP_LOW, min(CLIP_HIGH, x))


def dist_of(dice: list[int]) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {0: Fraction(1)}
    for sides in dice:
        new: dict[int, Fraction] = {}
        for total, p in out.items():
            for face in range(1, sides + 1):
                new[total + face] = new.get(total + face, Fraction(0)) + p * Fraction(1, sides)
        out = new
    return out


def subtract_and_floor(dmg_dist: dict[int, Fraction], armour_dist: dict[int, Fraction],
                        floor: int) -> dict[int, Fraction]:
    out: dict[int, Fraction] = {}
    for d, pd in dmg_dist.items():
        for a, pa in armour_dist.items():
            through = max(floor, d - a)
            out[through] = out.get(through, Fraction(0)) + pd * pa
    return out


WEAPON_DIST = dist_of(ORDINARY_WEAPON)
ARMOUR_DIST = dist_of(ARMOUR[ORDINARY_ARMOUR])
ORDINARY_HIT = subtract_and_floor(WEAPON_DIST, ARMOUR_DIST, 1)
DOUBLED_WEAPON_DIST = {k * 2: v for k, v in WEAPON_DIST.items()}
ORDINARY_TELLING_HIT = subtract_and_floor(DOUBLED_WEAPON_DIST, ARMOUR_DIST, 1)


def expected(dist: dict[int, Fraction]) -> Fraction:
    return sum((d * p for d, p in dist.items()), Fraction(0))


EXP_ORDINARY = expected(ORDINARY_HIT)
EXP_TELLING = expected(ORDINARY_TELLING_HIT)


def degrees(skill: int, roll: int) -> int:
    return skill // 10 - roll // 10


def omen_of(roll: int) -> int:
    u = roll % 10
    if u == 9:
        return 1
    if u == 0:
        return -1
    return 0


@lru_cache(maxsize=None)
def attack_buckets(eff: int) -> tuple:
    """For an attack roll against effective% `eff`: group the 100 natural rolls by
    (hits, telling, omen) so identical combinations merge into one Fraction(n, 100)."""
    grouped: dict[tuple[bool, bool, int], int] = {}
    for roll in range(1, 101):
        hits = roll <= eff
        telling = hits and degrees(eff, roll) >= TELLING_THRESHOLD
        omen = omen_of(roll)
        key = (hits, telling, omen)
        grouped[key] = grouped.get(key, 0) + 1
    return tuple((Fraction(count, 100), hits, telling, omen) for (hits, telling, omen), count in grouped.items())


@lru_cache(maxsize=None)
def defence_buckets(eff_def: int) -> tuple:
    """For a defence roll against effective% `eff_def`: "failure means the blow lands" (roll >
    eff_def). The Omen is read from the roll as it actually fell (natural-roll rule,
    03-rules.md sec1) -- NOT from any transformed/virtual roll, so this groups the 100 real
    natural rolls directly by (lands, omen), rather than reusing attack_buckets' complementary
    distribution (which would read the Omen off the wrong roll value)."""
    grouped: dict[tuple[bool, int], int] = {}
    for roll in range(1, 101):
        lands = roll > eff_def
        omen = omen_of(roll)
        key = (lands, omen)
        grouped[key] = grouped.get(key, 0) + 1
    return tuple((Fraction(count, 100), lands, omen) for (lands, omen), count in grouped.items())


@lru_cache(maxsize=None)
def outcome_no_omen(player_attack: int, player_defence: int, opponent_attack: int,
                     opponent_defence: int, max_rounds: int = 30):
    eff_atk = effective_pct(player_attack, opponent_defence)
    eff_def = effective_pct(player_defence, opponent_attack)
    p_hit = Fraction(eff_atk, 100)
    p_hit_by = Fraction(100 - eff_def, 100)

    def telling_rate(eff: int) -> Fraction:
        hits = tellings = 0
        for roll in range(1, eff + 1):
            hits += 1
            if degrees(eff, roll) >= TELLING_THRESHOLD:
                tellings += 1
        return Fraction(tellings, hits) if hits else Fraction(0)

    p_tell_atk = telling_rate(eff_atk)
    p_tell_def = telling_rate(100 - eff_def) if p_hit_by > 0 else Fraction(0)

    def branch(p_lands, telling_p):
        out: dict[int, Fraction] = {0: Fraction(1) - p_lands}
        for d, p in ORDINARY_HIT.items():
            out[d] = out.get(d, Fraction(0)) + p_lands * p * (1 - telling_p)
        for d, p in ORDINARY_TELLING_HIT.items():
            out[d] = out.get(d, Fraction(0)) + p_lands * p * telling_p
        return out

    dmg_by_player = branch(p_hit, p_tell_atk)
    dmg_to_player = branch(p_hit_by, p_tell_def)

    state = {(STARTING_STAMINA, STARTING_STAMINA): Fraction(1)}
    dealt = taken = rounds = Fraction(0)
    for _ in range(max_rounds):
        nxt: dict[tuple[int, int], Fraction] = {}
        for (ps, os_), p in state.items():
            rounds += p
            for dp, pdp in dmg_by_player.items():
                nos = os_ - dp
                dealt += p * pdp * dp
                if nos <= 0:
                    continue
                for dt, pdt in dmg_to_player.items():
                    prob = p * pdp * pdt
                    taken += prob * dt
                    nps = ps - dt
                    if nps <= 0:
                        continue
                    nxt[(nps, nos)] = nxt.get((nps, nos), Fraction(0)) + prob
        state = nxt
        if not state:
            break
    return {"rounds": rounds, "dealt": dealt, "taken": taken}


@lru_cache(maxsize=None)
def outcome_with_omen(player_attack: int, player_defence: int, opponent_attack: int,
                       opponent_defence: int, max_rounds: int = 30):
    state: dict[tuple[int, int, int], Fraction] = {(STARTING_STAMINA, STARTING_STAMINA, 0): Fraction(1)}
    dealt = taken = rounds = Fraction(0)

    for _ in range(max_rounds):
        nxt: dict[tuple[int, int, int], Fraction] = {}
        for (ps, os_, pending), p in state.items():
            rounds += p
            eff_atk = clip(effective_pct(player_attack, opponent_defence) + pending * 10)
            for p_atk, hits, telling, omen_atk in attack_buckets(eff_atk):
                p1 = p * p_atk
                dmg_dist = {0: Fraction(1)}
                if hits:
                    dmg_dist = ORDINARY_TELLING_HIT if telling else ORDINARY_HIT
                for dp, pdp in dmg_dist.items():
                    p2 = p1 * pdp
                    nos = os_ - dp
                    dealt += p2 * dp
                    if nos <= 0:
                        continue  # opponent dropped -- no defence roll this round
                    eff_def = clip(effective_pct(player_defence, opponent_attack) + omen_atk * 10)
                    for p_def, blow_lands, omen_def in defence_buckets(eff_def):
                        p3 = p2 * p_def
                        dt_dist = {0: Fraction(1)}
                        if blow_lands:
                            # Conservative reading of #155: no telling blow via a failed defence.
                            dt_dist = ORDINARY_HIT
                        for dt, pdt in dt_dist.items():
                            p4 = p3 * pdt
                            taken += p4 * dt
                            nps = ps - dt
                            if nps <= 0:
                                continue
                            new_pending = omen_def
                            nxt[(nps, nos, new_pending)] = nxt.get((nps, nos, new_pending), Fraction(0)) + p4
        state = nxt
        if not state:
            break
    return {"rounds": rounds, "dealt": dealt, "taken": taken}


def main() -> int:
    print(f"{'pairing':>10}  {'dealt/rd base':>14}  {'dealt/rd omen':>14}  {'delta':>9}  "
          f"{'taken/rd base':>14}  {'taken/rd omen':>14}  {'delta':>9}")
    max_abs_delta = Fraction(0)
    for atk, dfc in PAIRINGS:
        # PAIRINGS entries are (player_skill, opponent_skill) -- one flat skill per side, used
        # for both attack and defence, matching check_conversion.py's own rounds_summary() call
        # convention exactly (its own PAIRINGS usage: fight_outcome(..., player_skill,
        # player_skill, opponent_skill, opponent_skill, ...)). An earlier version of this script
        # mismapped this to (attack, defence) for one side, which made effective_pct(atk, atk)
        # always evaluate to 50 regardless of the pairing -- caught because every row printed an
        # identical delta, which is itself the kind of self-check CLAUDE.md's own "check the
        # maths" principle is for.
        base = outcome_no_omen(atk, atk, dfc, dfc)
        omen = outcome_with_omen(atk, atk, dfc, dfc)
        base_dealt_rd = base["dealt"] / base["rounds"] if base["rounds"] else Fraction(0)
        omen_dealt_rd = omen["dealt"] / omen["rounds"] if omen["rounds"] else Fraction(0)
        base_taken_rd = base["taken"] / base["rounds"] if base["rounds"] else Fraction(0)
        omen_taken_rd = omen["taken"] / omen["rounds"] if omen["rounds"] else Fraction(0)
        d_dealt = omen_dealt_rd - base_dealt_rd
        d_taken = omen_taken_rd - base_taken_rd
        max_abs_delta = max(max_abs_delta, abs(d_dealt), abs(d_taken))
        print(f"{f'{atk}v{dfc}':>10}  {float(base_dealt_rd):>14.3f}  {float(omen_dealt_rd):>14.3f}  "
              f"{float(d_dealt):>+9.3f}  {float(base_taken_rd):>14.3f}  {float(omen_taken_rd):>14.3f}  "
              f"{float(d_taken):>+9.3f}")

    print()
    print(f"Largest |delta| in expected damage per round across every pairing: {float(max_abs_delta):.3f}")
    threshold = Fraction(1, 10)
    if max_abs_delta < threshold:
        print(f"Below the {float(threshold)} damage/round materiality threshold: ADR 0028's "
              "published figures do not need re-deriving.")
        return 0
    print(f"At or above the {float(threshold)} damage/round materiality threshold: ADR 0028's "
          "figures should be re-checked against this mechanic.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
