# Implementation Plan: The crowd rule

**Branch**: `013-the-mob-rule` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Replace one undefined sentence in `03-rules.md` §2 with a rule that can be looked up: who qualifies,
how many are cleared, what it costs, and what the crowd does back. Compute every number before
writing any of it, play a crowd fight by hand before settling it, and record the decision — including
the naming decision — in one ADR.

## The load-bearing decisions

**The qualifying threshold is found, not chosen.** The mechanic *petty* was standing in for is "a
body one blow removes", so the threshold belongs wherever one blow stops removing them. That is a
computable point, and it has to hold across the whole plausible weapon band rather than at one
convenient weapon — a threshold that works only against a mid-band blade is a threshold that fails
in any setting whose weapons sit elsewhere. The first drafted answer (Stamina 3, light armour) was
put into the script and rejected, which is the plan working rather than the plan failing.

**The free clear is generous by construction, so what is checkable is the size of the discount.**
The rule buys out a `d100` per body; it cannot also be neutral. The bound that matters is that the
shortcut must never beat taking a real action, and it is checked under the **mapping**, because that
is the resolution combat is moving to. Today's opposed test is reported and not designed around: it
has a competent character missing an untrained one two times in three, which is the fault #44 exists
to correct and not a fault this rule should absorb.

**The crowd's side of the roll budget is half the feature.** A rule that spares the player sixty
rolls and hands the GM sixty has moved the cost, not removed it. So the crowd answers once per
engaged character, and extra bodies convert into the existing difficulty ladder — capped at its top
rung, because going further would invent one and would let numbers alone make a roll certain.

**The rule must not make crowds safe.** The check is not "does the party win" but "is there a real
crowd that beats a real character": if a lone unarmoured character can grind down any number of
bodies, the rule has deleted a category of danger the engine wanted. This is asserted, not hoped.

**The adversary model is not decided here.** #54 owns it. This rule may *require* an adversary to
state a maximum Stamina and an armour rating; it may not say how an adversary is represented.

## What the check script has to settle

`check_mobs.py`, stdlib only, exact arithmetic (`Fraction`), no sampling:

1. **Where one blow stops being enough**, across the whole weapon band, by Stamina and armour — and
   the assertion that the body one step up *fails* the same bar, so the line is not arbitrary.
2. **The rolled-out clear rate** at real skills, under both resolution models, against the free rate
   of 1 — reporting the discount rather than assuming it.
3. **What the crowd does back**: rounds to put a starting character below zero, at real body counts,
   armoured and not, under both models.
4. **Where weight of numbers saturates**, and whether the largest real crowd can reach that ceiling
   against the largest real party — otherwise the rule never fires at the sizes play uses.
5. **Rounds to clear at real party and crowd sizes**, read against 3, so the "not a way to win
   alone" claim is a computation.
6. **Agreement with the damage scale #44 established** — 1.56 through modest armour, 4.5 hits to
   drop. A private damage model would make everything above internally tidy and wrong.
7. **Every figure the design document publishes**, asserted against the model, so drift fails loudly.

## The order of work

The computation comes first and is allowed to reject the drafted rule; it did. The playtest comes
second and is allowed to add rules the computation cannot see; it did, three of them. The design
document is written last, from what survived. The ADR records what was rejected, because the
rejected reasoning is as useful as the winning reasoning.
