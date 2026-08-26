# ADR 0021 — Mending steps one grade a season, and the recurring wound never closes

**Date:** 2026-08-25
**Status:** Accepted

## Context

Two documents had been left pointing at each other with nothing in between.

[`09-aftermath.md`](../design/09-aftermath.md) hands out a wound record on five of its eight rows,
and said outright that a wound record "carries no healing field, no duration and no severity —
whether a wound ever mends is not settled here". Deferring it was right at the time: a field shaped
for one answer would have prejudged the question.

Meanwhile [`16-session.md`](../design/16-session.md) already listed **Mend** — "treat a lasting wound" — as
one of the downtime undertakings a player may choose. So the engine had an undertaking whose effect
was undefined, pointing at a record deliberately shaped to refuse the question. A player could spend
a season on it and the engine could not resolve what happened.

One of the two had to move, and the Aftermath table's own weights make the choice consequential
rather than tidy: across drops of one to twelve points below zero, a drop leaves **0.61** wound
records on average. Over a long chronicle that accumulates, and whether it accumulates without limit
is a design decision, not an implementation detail.

## Decision

**Mend names one wound by its `id` and moves that wound's effect one grade toward nothing**, at the
cost of the downtime's one undertaking:

| Effect | Ladder |
|---|---|
| `skill: -N` | `-10` → `-5` → closed |
| `stamina_max: -N` | `-1` → closed |
| `dread: +N` | `+1` → closed |

A wound whose effect reaches nothing is **closed, not deleted** — the record is kept and marked with
the beat that closed it.

**A recurring wound never closes.** Mend cannot reach it, whatever is spent.

## Why

**The ladder is constrained, not chosen.** `09-aftermath.md` declares a closed set of wound
effects and makes anything outside it a load error, so a mending rule cannot invent an intermediate
value. That the `skill` effect is the only one with a middle rung is a property of merged numbers:
`−10` and `−5` are the difficulty ladder's own rungs (`03-rules.md` §1), so a half-mended wound
introduces no number anyone has to learn.

**Stepping rather than closing outright is what makes the season worth spending twice.** At the
Aftermath table's own accumulation rate, one drop costs **0.62** downtimes of Mend to clear
([`check_recovery.py`](../../specs/014-stamina-recovery/check_recovery.py)). A character who fights
hard about as often as they rest keeps pace; one who fights harder than that accumulates. The rule
is a valve, not a reset — which is the shape the rest of the engine's recovery rules already have.

**Keeping the closed record is not sentimentality.** History is never recomputed
([`22-evolution.md`](../design/22-evolution.md)). A character who limped for two years limped for two
years, and a chronicle that deletes the record loses the ability to answer why a roll two years ago
went the way it did.

**The recurring wound's exemption is what keeps Fate's promise mechanical.**
`09-aftermath.md` closes the death rows by re-reading a `death` result onto the worst non-death
row — in practice the recurring wound. A spent Fate point therefore buys survival *plus* a wound
that wakes before every fight for the rest of the character's life, and
[ADR 0009](0009-fate-closes-the-death-rows.md) rests on that being a real price. If one season of
Mend erased it, the price would be one season, and the argument would quietly stop holding without
anything in either document looking wrong. The table's own "unless a later rule says otherwise"
clause is hereby answered **no**, deliberately.

## Alternatives rejected

**Mend closes one wound outright, recurring included.** Simpler to state and to apply, and it prices
the worst survivable Aftermath result — the one a Fate point was spent to reach — at a single
undertaking. It also makes Mend strictly better than every other undertaking for anyone carrying a
recurring wound, which is a choice that is not a choice.

**Wounds never mend; remove Mend from the undertaking list.** The cleanest rule available, with no
new state at all, and it was seriously considered. It fails on the accumulation figure: at 0.61
wound records per drop and no valve whatever, a long chronicle converges on a character who is a
list of penalties. The engine's stated ambition is that a character ten years in is *harder to
replace*, not unplayable.

**A healing test, or a rate in weeks.** Rejected twice over: the engine names no skill
([ADR 0013](0013-the-engine-names-no-skill.md)), so there is nothing to roll; and a duration in
weeks would need a second clock beside downtime, which is the parallel-mechanic fault
[ADR 0020](0020-stamina-recovers-on-the-clocks-the-engine-has.md) declined for Stamina.

**A `severity` field on the wound record, mended down.** Would give every effect the same ladder
length regardless of what it does, and would be a number no other rule reads — which is exactly how
`09-aftermath.md` argued its way out of a severity field in the first place.

## Consequences

- The wound record gains `closed:`, additively ([`19-state.md`](../design/19-state.md)). Writing it on a
  recurring wound is a load error rather than a quietly ignored field.
- Mend is now resolvable, and the undertaking list is a list of things the engine can actually do.
- A setting may still replace the Aftermath rows, and this rule holds for whatever effects those
  rows produce, because the effects are the same closed set.
