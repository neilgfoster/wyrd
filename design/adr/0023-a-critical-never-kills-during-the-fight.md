# ADR 0023 — A critical never kills during the fight

**Date:** 2026-08-25
**Status:** Accepted

## Context

Two tables answer one blow, and both can be fatal.

[`03-rules.md`](../03-rules.md) says of criticals that **high results are lethal**.
[`03a-2-aftermath.md`](../03a-2-aftermath.md) says that **death is deferred** — nothing resolves while
the fight is running, and what dropping cost is settled when it is over. Deferred death is not a
detail: it is how a single-character chronicle survives lethal combat at all, and
[ADR 0009](0009-fate-closes-the-death-rows.md) hangs a spent Fate point's entire promise on the
Aftermath death rows being the place death happens.

Writing the critical tables forced the question the ruleset had left open: when the worst row of a
critical table comes up mid-fight, **who has the killing blow?**

Left unstated, the GM decides — and the two answers are not close. One of them quietly repeals
deferred death.

## Decision

**A critical never kills during the fight.** The worst row of every table marks the blow **mortal**,
and:

> A combatant carrying a mortal blow has their Aftermath result read on the `death` row, whatever the
> dice said.

This is the exact mirror of the re-read [ADR 0009](0009-fate-closes-the-death-rows.md) already
publishes in the other direction, where a spent Fate point re-reads a `death` result onto the worst
non-death row. One mechanism, running both ways.

Everything that closes a death still closes this one: a spent Fate point, and `mortality: low`.

## Rejected

**The critical kills outright.** The obvious reading of *high results are lethal*, and the reason
this record exists. It creates a second way to die, in the one place the ruleset had promised there
was none — a character could be killed mid-fight without ever reaching the table that was supposed to
decide it, and Fate would have nothing to be spent against, because there would be no `death` result
to re-read. It repeals deferred death by accident, in a table nobody would think to check.

**Criticals never kill at all**, topping out at a severe wound. Coherent, and it makes the tables
simpler. Rejected because it makes [`03-rules.md`](../03-rules.md) false and the family's open top
pointless: an unbounded modifier that tops out at a limp is a ladder with nothing at the top of it,
and the worst blow the rules can produce would be indistinguishable from a moderately bad one.

**A bonus to the Aftermath total** — a mortal blow adds, say, +20. Rejected twice over. Aftermath
declares exactly one modifier and [`03a-tables.md`](../03a-tables.md) forbids a family carrying a
second; and it makes a mortal blow *probably* fatal rather than fatal, which is a different rule
wearing the same name. It also reintroduces the failure mode
[ADR 0009](0009-fate-closes-the-death-rows.md) already diagnosed for `mortality`: adjusting the total
rather than the reading is how a light knockdown ends up reaching the death row.

## Consequences

- The mortal row is rare by construction. Computed at the modifiers that actually occur, it is
  between **0.5%** (blunt) and **3.6%** (piercing) of criticals, and the whole family moves the
  chance a drop ends in death by **under one percentage point**
  ([`check_criticals.py`](../../specs/015-damage-type-criticals/check_criticals.py)).
- A combatant dropped by a single point cannot be killed by any critical table: the highest total
  they can reach is 7, and the earliest mortal row begins at 19.
- Companions remain the chronicle's reliable source of loss for the reason they already were — they
  have no Fate of their own — rather than because a new rule weights the dice against them.
- A setting may not move the composition. It is a mechanism Fate depends on; lethality is already a
  setting's to set, through `mortality`.
