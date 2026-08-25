# Implementation Plan: Stamina recovery and the fate of lasting wounds

**Branch**: `014-stamina-recovery` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Give Stamina the bottom half of its loop — 1 at a Rally, full at a downtime, a dropped combatant
restarting at 0 — and turn `04-session.md`'s undefined **Mend** undertaking into a rule that steps
one wound's effect one grade per season, with the recurring wound exempt. Compute the attrition
before writing any of it, play a two-fight arc by hand before settling it, and record both decisions
as ADRs.

## The load-bearing decisions

**The rate is copied, not chosen.** Strain recovers 1 at a Rally; Stamina recovers 1 at a Rally.
That is deliberate: the engine already spends a reader's attention on "1 per Rally", and a second
restoration rate at the same trigger would be two numbers where one does the work. What has to be
*checked* is that the borrowed rate produces a sane road back at the values a character actually has
— Stamina 6, or 7 after a completed career — not that it is elegant.

**Downtime restores without spending the undertaking, and that is the whole reason the undertaking
choice survives.** `04-session.md` makes the one-undertaking constraint the point of downtime
("Recovering from taint means *not* pursuing the thing that corrupted you"). If Stamina were also on
that list, every downtime after a real fight would resolve to the same choice, and the trade would
be a formality. Weeks of rest mending cuts and bruises needs no mechanic; **Stamina is not meat**
(`03-rules.md` §2), and what it models is exactly the thing a season fixes.

**A drop restarts at 0, not at a fraction.** The Aftermath table has already priced dropping; the
recovery rule's job is to say where the track resumes, not to re-price it. Restarting anywhere above
0 would be a second, quieter softening of the same event, and the two would eventually disagree
about how bad dropping is.

**Mend steps rather than closes, and the step is constrained by the closed effect set.**
`03a-2-aftermath.md` declares three legal effects and makes anything else a load error, so a mending
rule cannot invent an intermediate value. It may only move an effect to another legal value or to
closed: `skill: -10 → -5 → closed`, `stamina_max: -1 → closed`, `dread: +1 → closed`. That the
`skill` effect is the only one with a middle rung is a property of the merged numbers, not a choice
made here — `-10` and `-5` are the difficulty table's own rungs.

**The recurring wound is exempt, and that exemption is what makes Fate mechanical.**
`03a-2-aftermath.md` closes the death rows by re-reading onto the recurring wound; a spent Fate point
buys survival plus that wound for life. If one downtime removed it, Fate's promise would cost a
season, and the ADR 0009 argument would quietly stop holding. This is the "unless a later rule says
otherwise" clause being answered *no*, on purpose.

**A closed wound's record is kept.** History is never recomputed (`09-evolution.md`). Closing is a
new field on an existing record, additive, and `06-state.md` holds it.

## What the check script has to settle

`check_recovery.py`, stdlib only, exact arithmetic (`Fraction`), no sampling:

1. **Rallies to full** from every reachable state, at Stamina 6 and 7 — and from 0, the dropped case
   — read against how many Rallies a real session actually produces.
2. **Whether the borrowed rate keeps up with the damage the engine deals**: at the ordinary pairing
   (1.56 through modest armour), how many Rallies one fight's worth of damage costs, and therefore
   whether a chronicle of ordinary fights converges or spirals.
3. **The spiral bound explicitly**: the Stamina at which entering a fight means dropping in it, and
   how many Rallies of rest that threshold demands — so "long enough to be remembered, short enough
   to continue" is a computation and not a hope.
4. **What downtime is worth**, in Rallies, so the two clocks can be compared on one axis.
5. **The Mend ladder**: how many downtimes a full set of wounds takes to clear at the accumulation
   rate the Aftermath table's own weights imply (71% a lasting mark per drop), and the assertion that
   a recurring wound never reaches closed however many are spent.
6. **Agreement with the figures merged issues computed** — 1.56 through modest armour, 4.5 hits to
   drop (`specs/013-the-mob-rule/check_mobs.py`), and the Aftermath weights of 71% / 23%. A private
   damage model would make everything above internally tidy and wrong.
7. **Every figure the design documents publish**, asserted against the model, so drift fails loudly.

## Where the rules land

| Document | Change |
|---|---|
| `03-rules.md` §2 | the recovery rule itself, next to the harm that spends it |
| `03a-2-aftermath.md` | replace "not this table's business" with the pointer, and answer the wound record's deferred healing question |
| `04-session.md` | the Rally gains its Stamina line; downtime gains the automatic restore; **Mend** gains its effect |
| `06-state.md` | the wound record's closing field, additively |
| `03b-the-character.md` | the character's Stamina row points at the recovery rule |

## The order of work

The computation comes first and is allowed to reject the clarified rate; if six Rallies from zero
turns out to spiral at real values, that is a finding, not a rounding error. The playtest comes
second — a two-fight arc with a downtime between them — and is allowed to add rules the computation
cannot see. The design documents are written last, from what survived. Two ADRs record what was
rejected.
