# An arc played across the recovery rule

Run against the drafted rule before it was settled. The engine has been playtested once, and that
session corrected the resolution mechanic three times inside two rolls; the sequencing and crowd
features each found three or four missing rules the same way. This is the same exercise for
recovery.

**Not a probability check.** The numbers live in [`check_recovery.py`](check_recovery.py). This is
here to find the questions the rule does not answer, and it found four.

## The arc

Three beats, a downtime, and a second fight. One character, one companion.

| | Skill | Stamina | Armour |
|---|---|---|---|
| **The player's character** | 45% | 6 | modest |
| **The companion** | 35% | 6 | light |

## Beat one — the fight that hurts

An even fight, 45% against 45%. It runs eight rounds and the character takes three blows: 2, 1 and
4 through modest armour. That is 7 against a track of 6, so they **drop by 1**.

The companion, at 35% against a 25% opponent, ends on **3**.

Aftermath, once, for the character who dropped: `d100` + 5 × 1 = 5. Rolls 48, total 53 —
`left-for-dead`. One wound record, and they wake elsewhere without what they carried.

**Question one the rule did not answer: what Stamina do they wake at, and when?** The rule says 0,
and the fight is over, so the answer is: 0, at the moment the fight ends, before any Rally. The
Aftermath row moved them across the map; it did not move them up the track. *Folded back: the rule
says a dropped combatant wakes at 0, and the Rally that follows is the first point of recovery.*

## Beats two and three — the Rallies

Two beats pass. Nothing violent: a conversation, a road, a locked door.

| | After the fight | Rally 1 | Rally 2 |
|---|---|---|---|
| the character | 0 | 1 | 2 |
| the companion | 3 | 4 | 5 |

At the third Rally the character is on 3, half a track, two beats after being left for dead. That
felt right at the table in a way an argument on paper had not settled: they are up and moving and
they are visibly not fit for another fight.

**Question two: does the companion recover on the same rule?** Nothing said. They roll on the same
Aftermath table and have no separate rate for anything else, so: yes, the same. *Folded back: no
companion-specific rate is introduced; the rule is written for combatants, not for the player's
character.*

**Question three: what does the GM say?** "You are on 3 Stamina" is engine scaffolding
([`10-diegesis.md`](../../doc/design/23-diegesis.md)). What was actually said was that the character
could walk without the wall now, and still would not want to run. That is the existing diegesis rule
applying unchanged, which is the correct outcome — no new rendering rule was needed, and one was
nearly written.

## The downtime

A season at a friendly holding. Upkeep paid, one advance spent.

Stamina returns to maximum for both, automatically, and **the undertaking is still unspent** — which
is the whole argument for keeping it off the list, felt rather than reasoned about. The undertaking
went on **Mend**, naming the wound from the fight: `skill: -10` bearing on the character's fighting
skill, stepped to `-5`.

**Question four: what happens to a wound whose effect is halved — is it still the same wound?**
Yes: same `id`, same `from`, same description at the table. The knee that never set right is still
the knee; it simply troubles them less. *Folded back: Mend moves the `effect` and touches nothing
else on the record, so a wound keeps its identity across mending and a later rule can still name it.*

## The second fight, entered short

A month later, another even fight — but the wound is still at `-5`, so the character fights at 40%,
not 45%. They are at full Stamina and one rung down the difficulty ladder, and they lose the
exchange more often than the sheet suggests.

That is the rule doing what it is for. **Stamina came back; the fight did not go away.** The
character is whole and slightly worse, which is the distinction the whole feature exists to draw —
and it is the distinction that a rule restoring everything at a downtime, or a rule closing a wound
outright, would have collapsed.

## What the play changed

1. A dropped combatant wakes at 0 **when the fight ends**, not at the next Rally — stated, because
   the gap between those two is a whole beat.
2. Companions recover on the same rule, stated once rather than left to be inferred.
3. Mend moves the `effect` and nothing else, so a mended wound keeps its identity.
4. No new diegesis rule: the existing one already covers a half-recovered character, and writing a
   second would have been the parallel-mechanic fault in a new place.
