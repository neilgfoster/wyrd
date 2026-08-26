#!/usr/bin/env python3
"""Compute Stamina recovery and the Mend ladder, at the values a real character has.

CLAUDE.md: where a claim can be checked by a script, check it. The rule this settles had no
numbers at all -- nothing in design/ restored Stamina, and doc/design/09-aftermath.md declined the
question outright -- so every figure below has to be computed before it can be written down.

Everything here is derived from numbers already merged, not invented:

1. **A starting character has Stamina 6**, and a completed career grants +1 -- the only durable
   toughening (doc/design/05-character-creation.md, doc/design/03-rules.md section 6).
2. **Armour subtracts dice** -- light 1d3, modest 1d6, heavy 2d6, minimum 1 always through
   (doc/design/03-rules.md section 2).
3. **The ordinary pairing** is a mid-band weapon against modest armour: 1.56 points through,
   4.5 hits to drop a starting character (specs/013-the-mob-rule/check_mobs.py, #44).
4. **A critical happens below 0 Stamina**, and the dropped combatant rolls on the Aftermath table
   at +5 per point below zero (doc/design/09-aftermath.md).
5. **The Aftermath table's own weights**: a lasting mark 71%, death 23%, unweighted across drops
   of one to twelve (doc/design/09-aftermath.md).
6. **Strain recovers 1 at a Rally** (doc/design/03-rules.md section 5) -- the rate this rule borrows.
7. **The recorded player-facing mapping** is effective% = 50 + (player - opponent), clipped to
   5-95 (specs/012-combat-sequencing). Every claim is computed under BOTH today's opposed test
   and that mapping, because the rule must survive the conversion (#69).

Run: python3 specs/014-stamina-recovery/check_recovery.py

It takes several minutes: every fight is resolved exactly, round by round, in Fraction arithmetic
over the full damage distribution, with no sampling anywhere. That is the point -- the probability
claims in this ruleset have been wrong before and were caught only by computing them exactly -- and
nothing here is on a CI path, so the cost is paid once by whoever changes a number.
"""

from fractions import Fraction
from itertools import product

# ---------------------------------------------------------------------------
# Numbers from merged design documents. None of these is chosen here.
# ---------------------------------------------------------------------------

ARMOUR = {"none": [], "light": [3], "modest": [6], "heavy": [6, 6]}
MIN_THROUGH = 1
WEAPON_BAND = [("1d3", [3]), ("1d6", [6]), ("1d8", [8]), ("2d6", [6, 6])]
ORDINARY_WEAPON = [6]
ORDINARY_ARMOUR = "modest"

UNTRAINED = 10
STARTING_STAMINA = 6
CAREER_STAMINA = 7          # after one completed career
REAL_SKILLS = [25, 35, 45, 55]

# Beats -- and therefore Rallies -- a real session produces. doc/design/16-session.md: a single beat
# is the default shape, an extended session is several. Not a midpoint.
RALLIES_PER_SESSION = [1, 2, 3]

# Aftermath rows that leave a wound record, and the effect each carries. Rows whose effect the
# table leaves open are modelled as uniform over the closed effect set, because that set is
# closed: doc/design/09-aftermath.md makes anything outside it a load error.
CLOSED_EFFECTS = ["stamina_max", "skill", "dread"]

# ---------------------------------------------------------------------------
# The rule this script is testing, stated as constants so it can be falsified.
# ---------------------------------------------------------------------------

RALLY_RECOVERY = 1          # Stamina restored at each Rally -- Strain's rate, at Strain's trigger
DOWNTIME_RESTORES_FULL = True   # a downtime phase returns Stamina to maximum, automatically
DROPPED_WAKES_AT = 0        # a combatant who went below 0 restarts the track here
MEND_STEPS_PER_DOWNTIME = 1     # one named wound, one grade

# The ladder, per effect. Every rung is a value the closed effect set already permits: -10 and -5
# are the difficulty table's own rungs (doc/design/03-rules.md section 1), and "closed" is the record
# kept and marked, never deleted (doc/design/22-evolution.md).
MEND_LADDER = {
    "skill": [-10, -5, None],
    "stamina_max": [-1, None],
    "dread": [+1, None],
}
RECURRING_CLOSES = False    # a recurring wound is what a spent Fate point bought (ADR 0009)


def dice_distribution(faces):
    if not faces:
        return {0: Fraction(1)}
    outcomes = list(product(*[range(1, f + 1) for f in faces]))
    weight = Fraction(1, len(outcomes))
    dist = {}
    for roll in outcomes:
        dist[sum(roll)] = dist.get(sum(roll), Fraction(0)) + weight
    return dist


def damage_through(weapon, armour):
    """Damage reaching Stamina after armour, with the minimum-1 floor. One ordinary hit."""
    result = {}
    for wd, wp in dice_distribution(weapon).items():
        for ad, ap in dice_distribution(armour).items():
            through = max(MIN_THROUGH, wd - ad)
            result[through] = result.get(through, Fraction(0)) + wp * ap
    return result


ORDINARY_HIT = damage_through(ORDINARY_WEAPON, ARMOUR[ORDINARY_ARMOUR])
ORDINARY_MEAN = sum((k * v for k, v in ORDINARY_HIT.items()), Fraction(0))


def degrees(skill, roll):
    return skill // 10 - roll // 10


def p_opposed_win(actor, resister):
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


def p_mapped(player, opponent):
    """The recorded player-facing mapping: slope 1, clipped to 5-95."""
    return Fraction(max(5, min(95, 50 + player - opponent)), 100)


HIT_MODELS = [("opposed", p_opposed_win), ("mapped", p_mapped)]


# ---------------------------------------------------------------------------
# 1. Rallies to full. The whole of the recovery rule, read as a road back.
# ---------------------------------------------------------------------------


def rallies_to_full(current, maximum):
    """Rallies to return to maximum at the borrowed rate. A dropped combatant starts at
    DROPPED_WAKES_AT, so the dropped case is rallies_to_full(0, maximum)."""
    missing = maximum - current
    return -(-missing // RALLY_RECOVERY)   # ceiling division; the rate is an integer


def sessions_for(rallies, rallies_per_session):
    return Fraction(rallies, rallies_per_session)


# ---------------------------------------------------------------------------
# 2-4. What a fight costs, and where recovery stops keeping up.
# ---------------------------------------------------------------------------


def fight_outcome(player_stamina, player_skill, opponent_skill, model,
                  opponent_stamina=STARTING_STAMINA, max_rounds=60):
    """Exact round-by-round resolution of one fight, both sides at the ordinary pairing.

    Returns (p_player_dropped, expected_Rallies_owed_by_player).

    Rallies owed is capped at the wake point, not the raw damage taken: a combatant who dropped
    wakes at 0 whatever they dropped by, so overkill below zero costs no further recovery. Counting
    it would publish a road back longer than the rule produces.

    Under the mapping the player rolls once per exchange: success is their blow landing, failure
    is the opponent's. Under today's opposed test both sides act, so each rolls its own attack.
    """
    if model is p_mapped:
        p_hit = p_mapped(player_skill, opponent_skill)
        p_taken = 1 - p_hit
        independent = False
    else:
        p_hit = p_opposed_win(player_skill, opponent_skill)
        p_taken = p_opposed_win(opponent_skill, player_skill)
        independent = True

    # state: (player current stamina, opponent current stamina) -> probability
    state = {(player_stamina, opponent_stamina): Fraction(1)}
    dropped = Fraction(0)
    lost = Fraction(0)
    for _ in range(max_rounds):
        nxt = {}
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
                           for d, dp in ORDINARY_HIT.items()}
                if opponent_lands:
                    sub = {(a - d, b): q * dp
                           for (a, b), q in sub.items()
                           for d, dp in ORDINARY_HIT.items()}
                for (a, b), q in sub.items():
                    if a < 0:
                        dropped += q
                        lost += q * (player_stamina - DROPPED_WAKES_AT)
                        continue
                    if b < 0:
                        lost += q * (player_stamina - a)
                        continue
                    nxt[(a, b)] = nxt.get((a, b), Fraction(0)) + q
        state = nxt
        if not state:
            break
    for (a, _b), q in state.items():          # fights still running at the cap
        lost += q * (player_stamina - a)
    return dropped, lost


LIKELY_LOSS = Fraction(3, 4)


def entry_curve(player_skill, opponent_skill, model, maximum=STARTING_STAMINA):
    """P(dropped) as a function of the Stamina the character walks in with."""
    return [(s, fight_outcome(s, player_skill, opponent_skill, model)[0])
            for s in range(0, maximum + 1)]


def entry_threshold(player_skill, opponent_skill, model, maximum=STARTING_STAMINA):
    """The highest starting Stamina at which this fight is one the character is likely to lose
    -- P(dropped) at or above LIKELY_LOSS. This is not a spiral threshold: an even fight is
    close to a coin flip even at full Stamina, which is a property of the damage scale and not
    of the recovery rule. What the recovery rule owes is that entering short is materially
    worse, and this is where materially worse becomes likely."""
    worst = None
    for s, p in entry_curve(player_skill, opponent_skill, model, maximum):
        if p >= LIKELY_LOSS:
            worst = s
    return worst


# ---------------------------------------------------------------------------
# 5. The Aftermath table, so the Mend ladder is fed by the real accumulation rate.
# ---------------------------------------------------------------------------

AFTERMATH_ROWS = [
    (6, 30, "out-of-action", None, False),
    (31, 52, "lasting-wound", "open", False),
    (53, 66, "left-for-dead", "open", False),
    (67, 78, "new-enemy", "open", False),
    (79, 88, "taken", None, False),
    (89, 98, "disfigured", "dread", False),
    (99, 110, "recurring-wound", "skill", True),
    (111, None, "death", None, False),
]


def aftermath_distribution(points_below):
    """Row probabilities for a drop of this many points below zero: d100 + 5 x points."""
    dist = {}
    mod = 5 * points_below
    for roll in range(1, 101):
        total = roll + mod
        for lo, hi, key, _effect, _rec in AFTERMATH_ROWS:
            if total >= lo and (hi is None or total <= hi):
                dist[key] = dist.get(key, Fraction(0)) + Fraction(1, 100)
                break
    return dist


MARK_ROWS = {"lasting-wound", "left-for-dead", "new-enemy", "taken", "disfigured",
             "recurring-wound"}


def aftermath_weights(drops=range(1, 13)):
    """Unweighted across a range of drops: chance of a lasting mark, and of death."""
    marks, deaths, n = Fraction(0), Fraction(0), 0
    for d in drops:
        dist = aftermath_distribution(d)
        marks += sum((p for k, p in dist.items() if k in MARK_ROWS), Fraction(0))
        deaths += dist.get("death", Fraction(0))
        n += 1
    return marks / n, deaths / n


def wound_rows_per_drop(drops=range(1, 13)):
    """Expected wound records left per drop, and the share of them that recur."""
    total, recurring, n = Fraction(0), Fraction(0), 0
    for d in drops:
        dist = aftermath_distribution(d)
        for lo, hi, key, effect, rec in AFTERMATH_ROWS:
            if effect is None:
                continue
            p = dist.get(key, Fraction(0))
            total += p
            if rec:
                recurring += p
        n += 1
    return total / n, recurring / n


def mend_steps(effect):
    """Downtimes to close a wound of this effect. A recurring wound never closes."""
    return (len(MEND_LADDER[effect]) - 1) * MEND_STEPS_PER_DOWNTIME


def expected_downtimes_per_drop(drops=range(1, 13)):
    """Downtimes of Mend a single drop's wounds cost, ignoring recurring wounds (they never
    close, so they are never a cost that can be paid)."""
    total, n = Fraction(0), 0
    open_mean = Fraction(sum(mend_steps(e) for e in CLOSED_EFFECTS), len(CLOSED_EFFECTS))
    for d in drops:
        dist = aftermath_distribution(d)
        for lo, hi, key, effect, rec in AFTERMATH_ROWS:
            if effect is None or rec:
                continue
            p = dist.get(key, Fraction(0))
            total += p * (open_mean if effect == "open" else mend_steps(effect))
        n += 1
    return total / n


def pct(f):
    return f"{float(f) * 100:5.1f}%"


def num(f, places=2):
    return f"{float(f):.{places}f}"


def main():
    failures = []

    def check(label, condition, detail=""):
        if not condition:
            failures.append(f"{label}: {detail}")
        return condition

    print("=" * 78)
    print("T001  Agreement with the damage scale merged issues computed")
    print("=" * 78)
    hits_to_drop = Fraction(STARTING_STAMINA + 1, 1) / ORDINARY_MEAN
    print(f"  ordinary hit through modest armour   {num(ORDINARY_MEAN)}  (#44: 1.56)")
    print(f"  ordinary hits to drop Stamina 6      {num(hits_to_drop)}  (#44: 4.5)")
    check("ordinary damage through", num(ORDINARY_MEAN) == "1.56", num(ORDINARY_MEAN))
    check("hits to drop", num(hits_to_drop, 1) == "4.5", num(hits_to_drop))

    marks, deaths = aftermath_weights()
    print(f"  Aftermath: a lasting mark            {pct(marks)}  (03a-2: 71%)")
    print(f"  Aftermath: death                     {pct(deaths)}  (03a-2: 23%)")
    check("aftermath marks", round(float(marks) * 100) == 71, pct(marks))
    check("aftermath deaths", round(float(deaths) * 100) == 23, pct(deaths))

    print()
    print("=" * 78)
    print("T002  Rallies to full, at the Stamina a real character has")
    print("=" * 78)
    print("  max  current  Rallies   sessions at 1 / 2 / 3 Rallies each")
    for maximum in (STARTING_STAMINA, CAREER_STAMINA):
        for current in range(0, maximum + 1):
            r = rallies_to_full(current, maximum)
            spans = " / ".join(num(sessions_for(r, k), 1) for k in RALLIES_PER_SESSION)
            tag = "  <- dropped" if current == DROPPED_WAKES_AT else ""
            print(f"  {maximum:3d}  {current:7d}  {r:7d}   {spans}{tag}")
    dropped_road = rallies_to_full(DROPPED_WAKES_AT, STARTING_STAMINA)
    print(f"\n  A dropped starting character is {dropped_road} Rallies from full.")
    check("dropped road", dropped_road == 6, str(dropped_road))
    check("career road", rallies_to_full(0, CAREER_STAMINA) == 7,
          str(rallies_to_full(0, CAREER_STAMINA)))

    print()
    print("=" * 78)
    print("T003  What one ordinary fight costs, in Rallies, at real skills")
    print("=" * 78)
    print("  model     skill  vs     P(dropped)  Stamina lost  Rallies owed")
    worst_cost = Fraction(0)
    even_costs, advantage_costs = [], []
    for name, model in HIT_MODELS:
        for skill in REAL_SKILLS:
            for gap in (0, 10, 20):
                opponent = max(UNTRAINED, skill - gap)
                p, lost = fight_outcome(STARTING_STAMINA, skill, opponent, model)
                owed = lost / RALLY_RECOVERY
                worst_cost = max(worst_cost, owed)
                (even_costs if gap == 0 else
                 advantage_costs if gap == 20 else []).append(owed)
                print(f"  {name:8s}  {skill:5d}  {opponent:3d}    {pct(p)}      "
                      f"{num(lost)}         {num(owed)}")
    print(f"\n  Worst ordinary fight owes {num(worst_cost)} Rallies of rest.")
    even_lo, even_hi = min(even_costs), max(even_costs)
    adv_lo, adv_hi = min(advantage_costs), max(advantage_costs)
    print(f"  An even fight costs {num(even_lo, 1)} to {num(even_hi, 1)} Rallies; "
          f"a 20-point advantage costs {num(adv_lo, 1)} to {num(adv_hi, 1)}.")

    print()
    print("=" * 78)
    print("T004  What entering a fight short actually costs")
    print("=" * 78)
    print("  P(dropped) by the Stamina the character walks in with. An even fight is near a")
    print("  coin flip at FULL Stamina -- a property of the damage scale, not of this rule --")
    print("  so what matters is the gradient: how much worse each missing point makes it.")
    print("  model     skill  vs     P(dropped) at Stamina 6 / 4 / 2 / 0    likely-loss line")
    for name, model in HIT_MODELS:
        for skill in REAL_SKILLS:
            for gap in (0, 20):
                opponent = max(UNTRAINED, skill - gap)
                curve = dict(entry_curve(skill, opponent, model))
                t = entry_threshold(skill, opponent, model)
                line = "none" if t is None else f"at {t} or below"
                print(f"  {name:8s}  {skill:5d}  {opponent:3d}     "
                      f"{pct(curve[6])} / {pct(curve[4])} / {pct(curve[2])} / {pct(curve[0])}"
                      f"    {line}")
    full = dict(entry_curve(45, 25, p_mapped))
    full_even = dict(entry_curve(45, 45, p_mapped))
    print(f"\n  At a 20-point advantage, dropping runs {pct(full[6])} at full Stamina and "
          f"{pct(full[2])} at 2.")
    check("entering short is materially worse", full[2] > 2 * full[6],
          f"{pct(full[6])} -> {pct(full[2])}")
    check("full Stamina is not itself a likely loss at an advantage", full[6] < LIKELY_LOSS,
          pct(full[6]))

    print("=" * 78)
    print("T005  The two clocks on one axis")
    print("=" * 78)
    full_span = rallies_to_full(DROPPED_WAKES_AT, CAREER_STAMINA)
    print(f"  A downtime restores {'to maximum' if DOWNTIME_RESTORES_FULL else 'nothing'},")
    print(f"  which is worth up to {full_span} Rallies -- the longest road the Rally offers.")
    print(f"  In sessions of ordinary play that is {num(sessions_for(full_span, 1), 1)} to "
          f"{num(sessions_for(full_span, 3), 1)}.")
    check("downtime dominates the Rally", DOWNTIME_RESTORES_FULL and full_span >= 6,
          str(full_span))

    print()
    print("=" * 78)
    print("T006  The Mend ladder against the Aftermath table's own accumulation rate")
    print("=" * 78)
    per_drop, recurring = wound_rows_per_drop()
    cost = expected_downtimes_per_drop()
    print(f"  wound records left per drop          {num(per_drop)}")
    print(f"  ...of which recurring (never close)  {num(recurring)}")
    print(f"  downtimes of Mend one drop costs     {num(cost)}")
    print(f"  downtimes available per drop         {MEND_STEPS_PER_DOWNTIME}")
    verdict = "clears" if cost <= MEND_STEPS_PER_DOWNTIME else "accumulates"
    print(f"  => a character who drops once per downtime {verdict}")
    check("mend keeps pace with the closable wounds", cost <= MEND_STEPS_PER_DOWNTIME,
          num(cost))
    check("a recurring wound never closes",
          RECURRING_CLOSES is False and MEND_LADDER["skill"][0] == -10 and recurring > 0,
          num(recurring))

    print()
    print("=" * 78)
    print("T007  Every rung of the ladder is a value the closed effect set already permits")
    print("=" * 78)
    for effect, rungs in MEND_LADDER.items():
        shown = " -> ".join("closed" if r is None else f"{r:+d}" for r in rungs)
        print(f"  {effect:12s} {shown}    ({mend_steps(effect)} downtime(s))")
        check(f"{effect} rungs are legal",
              all(r is None or isinstance(r, int) for r in rungs) and rungs[-1] is None,
              str(rungs))
        check(f"{effect} is in the closed set", effect in CLOSED_EFFECTS, effect)
    check("the skill ladder uses the difficulty table's own rungs",
          MEND_LADDER["skill"][:2] == [-10, -5], str(MEND_LADDER["skill"]))

    print()
    print("=" * 78)
    print("T008  Figures the design documents publish, asserted against this model")
    print("=" * 78)
    published = {
        "1 Stamina restored at a Rally": RALLY_RECOVERY == 1,
        "a dropped combatant restarts at 0": DROPPED_WAKES_AT == 0,
        "six Rallies from dropped to full at Stamina 6": dropped_road == 6,
        "seven Rallies at Stamina 7": rallies_to_full(0, CAREER_STAMINA) == 7,
        "a downtime restores to maximum": DOWNTIME_RESTORES_FULL,
        "Mend steps one grade per downtime": MEND_STEPS_PER_DOWNTIME == 1,
        "skill -10 takes two downtimes to close": mend_steps("skill") == 2,
        "stamina_max and dread take one": mend_steps("stamina_max") == 1
                                          and mend_steps("dread") == 1,
        "a recurring wound never closes": RECURRING_CLOSES is False,
        "an even fight costs 4.6 to 4.9 Rallies":
            (num(even_lo, 1), num(even_hi, 1)) == ("4.6", "4.9"),
        "a 20-point advantage costs 2.2 to 3.3":
            (num(adv_lo, 1), num(adv_hi, 1)) == ("2.2", "3.3"),
        "dropping at a 20-point advantage runs 14.8% at full and 48.6% at 2":
            (pct(full[6]).strip(), pct(full[2]).strip()) == ("14.8%", "48.6%"),
        "an even fight is a coin flip at full Stamina": num(full_even[6] * 100, 0) == "50",
        "0.61 wound records per drop": num(per_drop) == "0.61",
        "0.62 downtimes of Mend per drop": num(cost) == "0.62",
    }
    for claim, ok in published.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {claim}")
        check(f"published: {claim}", ok)

    print()
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(1)
    print("All assertions hold.")


if __name__ == "__main__":
    main()
