# ADR 0027 — Combat rolls belong to the player; the opponent's dice are gone

**Date:** 2026-08-25
**Status:** Accepted
**Supersedes:** [ADR 0016](0016-opposed-tests-need-a-successful-actor.md), for combat only

## Context

Combat resolved as an opposed test — the attacker rolls and must succeed, then the defender rolls
and the higher degrees win, ties to the defender ([ADR 0016](0016-opposed-tests-need-a-successful-actor.md)).
That is a double gate, and no skill escapes it: computed across realistic pairings, **61-84% of the
player's rolls did nothing at all** — a miss on the attacker's own roll, most of the time, with the
defender never getting to roll at all.

#44 (Stage 5 — Conflict) decided the direction in a review comment and left it unowned: combat
should become **player-facing** — the opponent's capability becomes a static number, and the player
rolls against it for both attack and defence. Two children of #44 touched combat since (#11
sequencing, #13 the mob rule) and neither performed the conversion.

The mapping that turns two skills into one roll is calibrated separately
([`specs/012-combat-sequencing/check_mapping.py`](../../specs/012-combat-sequencing/check_mapping.py)):

```
effective% = clip(50 + (attacker_skill - defender_skill_or_baseline), 5, 95)
```

checked against a margin contest and a degrees contest with no linearity assumed, worst deviation
8.3 points against either. This record is about what that mapping replaces, not the mapping's shape.

## Decision

**An attack in combat is one roll, by the attacker, against `effective%`. A defence against an
attack on a player character or companion is one roll, by the player, against `effective%`
computed the other way round. The opponent's dice are never consulted, in either direction.**

1. **Attack**: the attacker (a player character or companion) rolls once against
   `effective%(attack_skill, defender_skill_or_baseline)`.
2. **Defence**: when the target of an attack is a player character or companion, the player rolls
   once against `effective%(defence_skill, attacker_skill_or_baseline)` — never a second roll for
   the opponent, and never the opponent's own attack roll.
3. **Degrees** are computed exactly as before — `tens(effective%) − tens(roll)` — fed the new
   input. The telling-blow threshold this produces is a separate finding
   ([ADR 0028](0028-the-telling-blow-threshold-and-the-damage-finding.md)).
4. **The Wyrd die is always read from the player's own roll** — attack or defence — because there
   is no longer a roll on the opponent's side for it to belong to instead.
5. **Assistance** (`03-rules.md` §1) applies identically to both rolls; nothing in its wording was
   attack-specific, and combat is not made the one place it behaves differently by which roll a
   player is making.

**Outside combat, two-sided opposed tests still exist, and ADR 0016 still governs them.** A contest
where both parties genuinely act on the fiction — a tug-of-war of wills, a race for the same
outcome named by the GM as two actors — is not converted. Combat is the only place a static
opponent number stands in for a roll, because combat is the only place the opponent side already
had a schema for that number ([`06-the-adversary.md`](../design/06-the-adversary.md)). This record
narrows ADR 0016's remaining scope; it does not retire it.

## Consequences

**The share of a player's combat rolls that do nothing drops sharply.** Every attack roll is now a
single roll against a single, meaningful percentage — no roll is spent only to discover the other
side also had to be beaten. A defence roll is likewise decisive on its own.

**The double-gate structure is gone from combat**, and with it the case ADR 0016 corrected —
because there is no longer a second roll on either side of an exchange for a failure's degrees to
inflate a margin against. ADR 0016's five provisions describe a shape combat no longer has.

**Fight length holds close to what the design already accepted.** Computed
([`specs/018-player-facing-combat/check_conversion.py`](../../specs/018-player-facing-combat/check_conversion.py)),
expected Stamina lost by the time the player wins an even fight is **4.0** (was 4.6-4.9 under the
opposed test), and **2.1** at a 20-point advantage (was 2.2-3.3) — both close enough to the
published figures that **starting Stamina is reaffirmed at 6**, not changed. The conversion removes
wasted rolls without shortening the fight enough that Stamina needs to move.

**A named antagonist is unaffected structurally.** [ADR 0025](0025-an-adversary-is-a-thin-block.md)
already made a nemesis a `character` entity carrying an adversary block; this record changes who
rolls against that block, not what the block contains.

## Alternatives rejected

**Keep the opposed test, give the defender a static number instead of a roll.** Shaves one roll off
the defender's side and leaves the attacker's own roll as the first gate — most of the 61-84% comes
from that gate alone, so this halves the waste rather than removing it, and it leaves the two rolls
asymmetric in a way that is hard to explain to a player: your attack still needs luck twice, your
defence needs it once.

**Give the defender a resource cost instead of a static number.** Same shape as above with a
different currency; it still leaves most rolls doing nothing, and it adds an economy (what the
resource is, how it recovers) to answer a structural problem a roll-count fix does not need.

**Leave combat as a fully two-sided opposed test and accept the roll-waste as flavour.** The
option before #44's review comment. Rejected there on the numbers above, and not re-litigated by
this record — see #44's thread for the original finding.
