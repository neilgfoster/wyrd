# ADR 0020 — Stamina recovers on the clocks the engine already has

**Date:** 2026-08-25
**Status:** Accepted

## Context

Nothing in the engine restored Stamina. Every other track had an answer — Strain recovers 1 at a
Rally, Taint and Strain both have the **Recover** undertaking, Trauma sawtooths through Afflictions
— and the resource the whole of [`03-rules.md`](../03-rules.md) §2 spends had none.
[`03a-2-aftermath.md`](../03a-2-aftermath.md) declined the question explicitly, which was correct
scoping there and left it homeless.

The consequence was not small. A starting character has Stamina **6**, an ordinary telling blow
drops one outright, and without a recovery rule that character is at 0 for the rest of the
chronicle. The combat loop had no bottom half, and two later requirements were blocked outright by
its absence.

Three pressures pulled against each other, and each has a failure mode that is invisible in prose.

**Recovery must not undo the fight.** A rule that returns a character to full between beats makes
Stamina a per-scene resource and leaves the Aftermath table as the only thing combat ever costs.

**Recovery must not stall the chronicle.** A character who cannot get back to fighting shape
without a season will spend the chronicle avoiding the engine's own combat rules.

**No new cadence.** The engine has exactly two clocks that restore anything: the Rally, and
downtime. A third would be a parallel mechanic, and two clocks describing one thing is the fault
class this repo keeps being corrected for.

## Decision

**At each Rally, recover 1 Stamina. At the end of a downtime phase, Stamina returns to maximum. A
combatant who dropped below 0 wakes at 0 and recovers from there.**

The Rally rate is **Strain's rate at Strain's trigger**. It is copied rather than chosen: the engine
already spends a reader's attention on "1 per Rally", and a second restoration rate at the same
pause would be two numbers doing one job.

**Downtime costs no undertaking.** It restores whether or not the period is spent on it.

## Why

The numbers, computed at the values a real character has rather than at a midpoint
([`check_recovery.py`](../../specs/014-stamina-recovery/check_recovery.py)):

- A dropped starting character is **6 Rallies** from full; **7** after a completed career.
- One ordinary fight against an **even** opponent owes **4.6 to 4.9** Rallies of rest — most of the
  track — and drops the character about half the time whatever they walked in with.
- The same fight at a **20-point advantage** owes **2.2 to 3.3**.

Those are Rallies *owed*, capped at the wake point: a combatant who dropped by six points and one
who dropped by one both wake at 0, so overkill costs no further recovery. Counting the raw damage
instead published a road back longer than the rule produces, and the first draft did exactly that.

So the rule lands exactly where it was asked to. A character who fights an equal every beat never
sees full Stamina again before a downtime; one who picks their fights recovers between them. The
fight is remembered for the rest of the session and forgotten by the next season, which is what an
attritional register wants and what a paralytic one does not do.

**Downtime is off the undertaking list because the trade is the point.** Downtime's one-undertaking
constraint exists so that recovering from taint means *not* pursuing the thing that corrupted you
([`04-session.md`](../04-session.md)). Put Stamina on that list and every downtime after a real
fight resolves to the same choice, and the trade becomes a formality. There is also nothing to
explain: **Stamina is not meat** (`03-rules.md` §2), and weeks of rest mending cuts and bruises
needs no mechanic. What a season cannot mend is a lasting wound, and that is what **Mend** is for
([ADR 0021](0021-mending-steps-and-the-recurring-wound-does-not.md)).

**Waking at 0 keeps dropping priced in one place.** The Aftermath table has already said what the
fight cost; the recovery rule says only where the track restarts.

## Alternatives rejected

**Full Stamina at every Rally.** Simplest possible rule, and it makes combat a per-scene resource:
nothing accumulates across a session, so the only durable consequence of dropping is the Aftermath
row. That deletes attrition as a pressure, and attrition is most of what makes a fight a decision
rather than a scene.

**Downtime only, nothing at a Rally.** The strongest register, and it stalls play. At the computed
figures a character leaving an even fight is 5 or 6 Stamina down, which under this alternative means
the rest of the arc spent declining the engine's own combat rules. The rule would be obeyed by
avoiding it.

**Stamina as a Recover undertaking.** Puts the restore on a clock the engine already has, so it
passes the no-new-cadence test — and it fails the trade test, as above. It also charges a season's
one decision for something a season would do anyway.

**Waking at a fraction of maximum** — half, or 1. Softens dropping in a second place, on top of the
Aftermath table which already prices it. Two rules softening one event will eventually disagree
about how bad the event was, and the disagreement will not look like a fault in either of them.

**A recovery test — a roll to recover, at a skill or against a track.** Rejected on two counts: the
engine names no skill ([ADR 0013](0013-the-engine-names-no-skill.md)), so there is nothing to roll
against without inventing an attribute for the purpose; and it puts a roll in the pause whose whole
function is to be a clean stopping point.

## Consequences

- The Rally gains a second line, and remains one pause with one rate.
- Downtime gains an automatic restore that is explicitly *not* an undertaking, stated where the
  undertaking list is, so the omission cannot read as an oversight.
- A character's Stamina is now a state the chronicle carries between sessions and is meaningful to
  render diegetically ([`10-diegesis.md`](../10-diegesis.md)).
- Nothing here depends on the opponent rolling dice, so the rule survives the player-facing
  conversion unchanged.
