# ADR 0008 — The engine fixes the row schema; each table family declares its own roll

**Status:** accepted 2026-08-22

## Context

[`../03-rules.md`](../03-rules.md) names five kinds of table — criticals, aftermath,
transformations, afflictions, oracles — and defines none of them. [`../02-architecture.md`](../02-architecture.md)
and [`../07-tooling.md`](../07-tooling.md) both promise them as pure, setting-neutral, overridable
data. Nothing stated the shape of a row, how a result was looked up, or what a setting was allowed
to replace.

Five families were about to be written by five separate pieces of work. Without a structural answer
first, they would have produced five dialects — each internally coherent, which is the kind of
disagreement that is only found by reading two documents against each other.

So the question was not *what should the tables contain*. It was: **how much does the engine fix?**

## Decision

The engine fixes **the row schema and the lookup rule**. Every row in every family carries a range,
an effect and a description; every lookup rolls, applies a modifier, finds the containing row, and
clamps at both ends.

The engine does **not** fix the die. Each family declares its own roll, its own modifier source, and
whether its results repeat or are unique to a character. Those declarations live in the family's own
file and are summarised in the index in [`../03a-tables.md`](../03a-tables.md).

A setting replaces rows. It cannot replace a declaration, because a declaration is a mechanism.

## Alternatives rejected

**One universal table format, rolled the same way everywhere.** The obvious answer, and a smaller
engine: one die, one modifier rule, five sets of rows. Rejected because [`../03-rules.md`](../03-rules.md)
already commits to `1d6 + points below zero` for criticals, and that modifier is what makes a
critical scale with how hard you were hit. A universal percentile roll would have made every
critical equally severe regardless of the blow — discarding a mechanic the ruleset had already
chosen, in order to gain a uniformity nothing needed. The same modifier is meaningless to an oracle,
so the universal rule would have been a rule three families ignored.

**A universal roll per *kind* of table** — one for harm, one for narrative. A two-way split.
Rejected as a distinction with no second member: four of the five families fall on one side of it,
and the split would need re-litigating the moment a sixth family appeared.

**A rich shared row schema**, carrying severity, duration, tags and Dread on every row. Rejected
because each of those is read by one or two families, so most rows would carry fields nothing reads.
Severity in particular is consumed by transformations and afflictions and by nothing else, so it is
a family field. An unread field on a table row is the ideal place for a wrong value to hide.

**A per-table version, so a chronicle could pin exactly the rows it rolled on.** Rejected because
[`../06-state.md`](../06-state.md) already versions four things, and the engine and setting versions
plus the table key already resolve an outcome to one table. A fifth version would have to be bumped
by hand on every row change, and a version nobody bumps reliably is worse than none — it reads as
authoritative and is not.

## Consequences

- The index in [`../03a-tables.md`](../03a-tables.md) has to carry each family's roll and
  uniqueness, because those now vary. It is the only place all five are comparable.
- The **effect/description split** becomes load-bearing rather than tidy. The effect is what reaches
  state; the description is what a setting rewrites. Without the split, a rename could not be
  presentation-only in practice, only in principle ([ADR 0004](0004-tone-belongs-to-the-setting.md)).
- Validating a table file is entirely mechanical — contiguous ranges, known key, known effect,
  required fields present — so it is checked rather than asserted
  ([ADR 0005](0005-deterministic-over-inference.md)). One rule is not mechanical, that no borrowed
  system vocabulary enters an engine table, and it stays a review obligation.
- A family that declares itself unique per character must also declare what happens when a character
  holds every result in its table, because rerolling can no longer terminate. The ruleset already
  answers this for transformations: the character is lost.
- `tables.py` has a specification to implement before it is written, rather than a shape inferred
  from whichever family happened to be written first.
