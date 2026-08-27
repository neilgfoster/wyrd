# ADR 0022 — Four damage types, named for the shape of the wound

**Date:** 2026-08-25
**Status:** Accepted

## Context

[`03-rules.md`](../design/03-rules.md) has instructed the GM to roll a critical "on the table for the damage
type" since the ruleset was written. There were no such tables, and — worse — **the engine had never
enumerated its damage types at all**. Two fragments were the entire evidence anywhere in the repo:
`critical-slashing`, used as an override example in
[`24-authoring-a-setting.md`](../design/24-authoring-a-setting.md), and "he is Blunt 5" in
[`13-diegesis.md`](../design/13-diegesis.md). Neither is a statement of the set.

So the tables could not be written without first deciding a thing the engine had been assuming for
its whole existence. The decision is constrained twice over. The set is **closed** — a weapon
declaring a type the engine does not publish is a load error, not a table quietly skipped — so
whatever is chosen has to serve every setting the engine will ever hold. And no label may only make
sense to someone who has read a particular book ([`CLAUDE.md`](../../CLAUDE.md)).

## Decision

**Four types, named for the shape of the wound:** `slashing`, `piercing`, `blunt`, `searing`.

The naming axis is the load-bearing part. A damage type names **what happened to the body**, not what
was swung and not what element was involved. `searing` is deliberately the widest of the four — fire,
a beam weapon, acid, cold, a current — and a setting that has none of them renames it or declares no
weapon of that type.

## Rejected

**A taxonomy of weapons** — blade, spear, club, bow, flame. Rejected because it is unbounded: every
setting's armoury adds a shape, the set is closed, and the engine would be answering a request for a
fifth type every time a setting shipped. It also mistakes the instrument for the injury, which is
what the table is actually describing.

**A taxonomy of elements** — fire, lightning, cold, acid, and physical as a single lump. Rejected
because it smuggles a genre in. A setting with no supernatural or energetic harm at all would carry
four types it never rolls and one that does all the work, and the engine would have taken a position
on what kind of world it is running — which [ADR 0004](0004-tone-belongs-to-the-setting.md) says it
does not get to do.

**Three physical types with no fourth.** Genuinely tempting: `slashing`, `piercing`, `blunt` covers
every setting whose fights are fought with hands and steel, and it keeps both surviving fragments in
the repo true. Rejected because burning is not one of the three and never has been — a burn parts
nothing and crushes nothing — so a setting with a torch in it would have to file an engine gap
before it could resolve a critical. The engine would be shipping a hole in a common case to save one
row.

**A single, undifferentiated critical table.** The leanest option, and it was rejected on the
strength of what it would make the rest mean. If one table answered every blow, the damage type would
be a label with no mechanical consequence — a rename wearing a mechanic's costume — and the
ruleset's own instruction to roll *on the table for the damage type* would be describing something
that does not exist. Four tables are only worth their length if they differ, so they do: computed at
the modifiers that actually occur, piercing is **seven times** likelier to be mortal than blunt, and
blunt is more than twice as likely to leave nothing behind
([`check_criticals.py`](../../specs/015-damage-type-criticals/check_criticals.py)).

**Renaming the first three to plainer English** — cutting, crushing. Rejected because it buys nothing
and costs two documents their accuracy: `critical-slashing` and "Blunt 5" are already written down,
and both are descriptive English by the standard [`CLAUDE.md`](../../CLAUDE.md) sets.

## Consequences

- The overridable table keys are `critical-slashing`, `critical-piercing`, `critical-blunt` and
  `critical-searing`. The set is closed and published.
- A setting renames a type whose fiction it lacks; the rename is presentation-only and never reaches
  state.
- The two fragments that were the only prior evidence stay true, so nothing in the repo goes stale as
  a result of this decision.
- Adding a fifth type later is an engine change, deliberately — it changes a closed set every setting
  loads against.
