# ADR 0009 — Fate closes the death rows rather than suppressing the roll

**Date:** 2026-08-22
**Status:** Accepted

## Context

Two mechanics claim the same moment, and until now neither described it.

[`03-rules.md`](../03-rules.md) says a spent Fate point means the character **survives and is not
better off** — the blow was glancing, everything goes black, they wake later, and the GM chooses
where. It also says that when a combatant drops, death is deferred to the Aftermath table.

So when a character rolls a death result and the player spends Fate, two rules both have an answer,
and the ruleset never said which one runs. A reader can construct two coherent readings and neither
looks wrong from inside itself.

The same moment is claimed a third time by the tone contract. [`01-principles.md`](../01-principles.md)
says a setting's `mortality` value governs "how the Aftermath table is applied", without saying what
it changes.

## Decision

**A death result that is closed to a character is re-read on the worst non-death row, and that row's
effect is applied.** The roll still happens; the character still takes a result; the result is not
death.

Two things close the death rows, and both use this one mechanism:

- a **spent Fate point** — the player's, for themselves or for a companion they are present for
- **`mortality: low`** in the setting's tone contract, which closes them for everyone, always

`mortality` therefore modifies **how the table is applied**, never what is rolled.

Fate may be spent only against a `death` result. It does not improve any other row.

## Consequences

**Fate's existing promise becomes mechanical.** "Survives and is not better off" is now a row rather
than a sentence: in practice the worst non-death row is the recurring wound, so a spent Fate point
reliably leaves something that wakes before every future fight. The cost of the chronicle's scarcest
resource is visible for the rest of the character's life.

**One mechanism serves two rules.** `mortality: low` needs no machinery of its own, and there is no
second way for death to be taken off the table that could drift from the first.

**The natural roll rule is untouched.** Fate changes which row is applied and never what was rolled,
which is why the log records `fate_spent` alongside the total. *You can change what happened. You
cannot change what it cost.*

**Companions inherit the boundary for free.** They have no Fate, so the death rows are open to them
unless the player spends against a death they are present for — already the rule in
[`03-rules.md`](../03-rules.md), now with a mechanical consequence rather than a narrated one.

## Alternatives rejected

**Fate suppresses the Aftermath roll entirely.** The obvious reading, and the one that hollows out
the rule it is trying to serve: a spent Fate point would cost the character nothing lasting, so
"not better off" would be prose with no mechanism under it. That is a specification that reads as
authoritative and is not — the fault class this repository has been corrected for most often.

**Fate is declared before the roll.** More tense, and it changes what Fate is. The ruleset says Fate
is spent *to avoid death*, which presupposes knowing that death is what is on the table. Declaring
blind converts a death valve into a gamble.

**`mortality` as a `±10` adjustment to the total.** This was the first design, and it was rejected by
computing it rather than by reading it. Two faults, neither visible in prose:

1. At `mortality: low` the lowest possible total becomes `1 + 5 − 10 = −4`, below the table's first
   row. [`03a-tables.md`](../03a-tables.md) requires a family's ranges to start at its lowest
   possible total, so the table would not load at one of its three legal settings.
2. At `mortality: high` a combatant who dropped by a single point can reach the death row —
   destroying the property deferred death exists to provide, that a light knockdown is survivable.

**A separate table per `mortality` value.** Three tables to keep in step, each of whose rows reads as
a small factual claim rather than an argument. Tables are where staleness hides; three copies of one
table is how it gets in.
