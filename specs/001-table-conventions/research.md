# Research: Table conventions and the tables index

**Feature**: `001-table-conventions` | **Date**: 2026-08-22

Phase 0 output. Each decision below is settled here so `design/03a-tables.md` can state it as
present-tense fact rather than argue for it. Three of these were settled by the operator during
clarification and are marked as such.

---

## R1. Does the engine fix one die for all tables, or does each family declare its own?

**Decision**: Each family declares its own roll — a die expression and a modifier source. The
engine fixes the *row schema* and the *lookup rule*, not the die.

**Rationale**: `design/03-rules.md:114` already commits to `1d6 + points below zero` for criticals.
That modifier is meaningless to an aftermath roll and to an oracle, so a universal die would either
have to be the union of every family's needs or would force three families to fake a modifier they
do not have. Fixing the schema rather than the die is also what makes the index a genuine contract:
a reader can validate any family's file without knowing what it rolls.

**Alternatives considered**:

- *One universal die (`d100`) for every table.* Consistent with resolution, and the tempting answer
  because the engine is already percentile. Rejected: it silently discards the critical table's
  `points below zero` modifier, which is the mechanic that makes a critical scale with how hard you
  were hit. Replacing it with a percentile roll would make every critical equally severe.
- *One universal die per *kind* of table (harm vs. narrative).* A two-way split. Rejected as a
  distinction with no second member yet — three of the five families would be in one bucket, and the
  split would need re-litigating the moment a sixth family appears.

**Consequence for the document**: the conventions state that die and modifier are family properties,
declared in the family's own file, and that the index records each family's roll so all five are
comparable at a glance.

---

## R2. What happens above the highest row and below the lowest?

**Decision**: Clamp at both ends. A modified roll above the highest row's range reads the highest
row; below the lowest, the lowest. A table's ranges must be contiguous, so there is no gap to fall
into between them.

**Rationale**: The critical roll is `1d6 + points below zero`, and points below zero is unbounded —
a large enough blow will always exceed any finite table. `design/03-rules.md:115` says "high results
are lethal", which means the top row is already the worst outcome the family has; clamping to it is
the behaviour the rules already assume. The alternative, an error, would make the engine fail
precisely at the most dramatic moment in a fight.

**Alternatives considered**:

- *Extrapolate beyond the top row* (each point over adds some further effect). Rejected: it invents
  an effect the table never states, and it makes the worst outcome unbounded, which no family's rows
  can describe.
- *Roll again and combine.* Rejected as a stacking mechanic the ruleset does not have, and one that
  would make the very worst blows slower to resolve rather than more decisive.

**Consequence**: the conventions state clamping once, and state that contiguity is a load-time
requirement on every table including an overriding one — which is what makes clamping the *only*
out-of-range case.

---

## R3. What must every row carry?

**Decision**: Three fields, no more:

| Field | Purpose |
|---|---|
| range | the rolled values this row answers to |
| effect | the mechanical consequence, in a form the engine can apply without reading the prose |
| description | the words shown at the table, replaceable by a setting |

A family may declare additional fields, named in its own file. Severity is one such field, not a
shared one (R4).

**Rationale**: These three are the minimum for the document's own goal — a row must be findable
(range), actionable (effect), and sayable (description). Anything further is family business.
Keeping the shared schema at three fields is also what makes SC-003 achievable: a sibling adds one
index row and declares its own extras, touching nothing shared.

The split between `effect` and `description` is the load-bearing one. It is what lets a setting
replace the words without replacing the mechanics, and it is what keeps a rename presentation-only —
the effect is what reaches state, the description never does.

**Alternatives considered**:

- *A single free-text row.* Simplest to author. Rejected: the engine could not apply the result, so
  every table would need an AI to interpret it — the exact inference `design/07-tooling.md` and
  ADR 0005 rule out for anything with a correct answer.
- *A rich shared schema* carrying severity, tags, duration and dread. Rejected: four of those are
  needed by one or two families each, so most rows would carry fields nothing reads. Tables are
  where staleness hides, and an unread field is the ideal hiding place.

---

## R4. Is severity general or family-specific?

**Decision**: Family-specific. Only the families whose rules consume a severity carry one.

**Settled by**: operator, clarification session 2026-08-22.

**Rationale**: `design/03-rules.md:205` has a transformation consume Taint equal to its severity, so
transformations need it and afflictions plausibly do. Criticals, aftermath and oracles have no rule
that reads a severity. A required-everywhere severity would put an unread number on the majority of
rows.

**Alternatives considered**: required on every row (rejected: meaningless values on three families);
optional on every row (rejected: in practice identical to family-specific, but phrased so that each
family still decides — the shared schema would gain a field and lose nothing).

---

## R5. What does the engine do when an already-held result comes up again?

**Decision**: Each family declares itself unique-per-character or repeatable. A unique family
rerolls when the character already holds the result. A repeatable family does not.

**Settled by**: operator, clarification session 2026-08-22.

**Rationale**: The two cases are genuinely different. A character cannot take the same permanent
transformation twice; a character can perfectly well take the same wound twice. A single rule for
both would be wrong for one of them, and rerolling criticals would quietly bias that table away from
its most common results.

**Exhaustion** (FR-004a): when a unique family's table holds no result the character lacks,
rerolling cannot terminate. The conventions state that the engine stops rerolling and applies the
family's declared exhaustion outcome — for transformations, `design/03-rules.md:213` already supplies
one: the character is lost. A family that declares itself unique must therefore also declare what
exhaustion means for it; the conventions require the declaration rather than inventing a general
answer.

**Alternatives considered**: always reroll (wrong for criticals and aftermath); never reroll, deepen
instead (invents a stacking mechanic the ruleset lacks).

---

## R6. How is a table addressed and where does it live?

**Decision**: A table is addressed by a lowercase hyphenated key, `<family>` where the family holds
one table and `<family>-<variant>` where it holds several. One table per file.

**Rationale**: `design/13-authoring-a-setting.md:157` already publishes
`tables: {critical-slashing: setting/rules/tables/critical-slashing.yaml}`. That single line is the
only evidence in the repository of either a naming scheme or a per-table file, and it is consistent:
`critical` is the family, `slashing` the variant, the file is named for the key. Inventing a
different scheme now would make the one published example wrong.

**Alternatives considered**: a nested key (`critical.slashing`) — rejected because the published
example is flat and flat keys survive being used as filenames; one file per family holding all its
variants — rejected because it makes a setting override all-or-nothing when the natural unit of
replacement is one damage type.

**Engine path**: `engine/tables/<key>.yaml`, mirroring the setting path the published example uses.
`design/02-architecture.md:91` says `tables/` without a filename convention; this fills that in
rather than contradicting it.

---

## R7. How is a table pinned?

**Decision**: By the version stamps that already exist. A table ships with the engine or with a
setting; `chronicle.yaml` already records both versions, and every recorded outcome already records
the engine that produced it (`design/09-evolution.md:105`). The outcome additionally records the
table key it rolled on. No per-table version is introduced.

**Settled by**: operator, clarification session 2026-08-22.

**Rationale**: `design/06-state.md:29` is explicit that four things carry versions and enumerates
them. A fifth would have to be bumped by hand every time a row changed, and a version nobody bumps
reliably is worse than no version — it reads as authoritative and is not, which is fault class 4 in
`CLAUDE.md`. Engine version plus table key already resolves an outcome to exactly one table.

**Change class**: a table change is *tuning* under `design/09-evolution.md:37` when it alters
numbers, ranges or effects within an existing family, and *additive* when it adds a table or a row
without changing existing ranges. Neither is retroactive; both are forward-only, so no recorded
outcome is ever recomputed.

**Alternatives considered**: a per-table version field (rejected above); a content hash (cannot
drift, but is unreadable to a human auditing the log, which is the stated purpose of provenance).

---

## R8. What may a setting override, and what makes an override load?

**Decision**: A setting replaces a table's **rows** — their ranges, effects and descriptions — via
`overrides.tables:`. It may not change the family's die, its modifier source, its row schema, its
uniqueness declaration, or the set of published table keys.

**Rationale**: `design/13-authoring-a-setting.md` already draws exactly this line: content is a
setting's business, mechanism is the engine's, and a setting that needs a mechanism the engine lacks
files an engine gap instead. Changing the die or the schema is changing the mechanism.

**Load-time requirements on an overriding table**, all mechanical and therefore checkable rather
than asserted (ADR 0005):

1. The key is one the engine publishes; an unknown key is a load error
   (`design/13-authoring-a-setting.md`: the overridable set is closed).
2. The ranges are contiguous and non-overlapping, and span the family's rollable minimum upward.
3. Every row carries the three shared fields and whatever the family additionally declares.
4. Every `effect` names a mechanic the engine knows; an effect naming an unknown mechanic is a load
   error, not a silently ignored row.

**Renames**: presentation-only, per `design/13-authoring-a-setting.md` and ADR 0004. A rename
changes what a description says; the `effect` and the table key are what reach state, and they are
never renamed. This is why the row schema separates the two.

---

## R9. Does this feature earn a decision record?

**Decision**: Yes — one, covering R1 together with R3: the engine fixes the row schema and the
lookup rule, and lets each family declare its own roll.

**Rationale**: `design/README.md`'s two-part test. A real alternative was rejected — one universal
table format, rolled the same way across every family, which is a workable engine and a smaller one.
And someone would plausibly propose it again: "why does every table roll differently?" is the
obvious first question a reader asks of the finished document, and the answer is not visible from
the document itself.

The other decisions do not earn their own records. R2, R6 and R8 follow from documents that already
exist rather than choosing against them. R4, R5 and R7 each rejected a real alternative, but all
three are stated in `design/03a-tables.md` itself and their rejected alternatives are recorded here
in this committed spec — which is what `CLAUDE.md` says a spec is for. Writing four records where
one is load-bearing is the noise `design/README.md` warns turns records into something nobody reads.

---

## R10. What in the existing design set has to change?

Found by reading the referenced documents against each other (fault class 3 in `CLAUDE.md`), not by
grep:

| Document | Line | Problem | Action |
|---|---|---|---|
| `design/07-tooling.md` | 84 | Lists "criticals, aftermath, transformations, oracles" — omits afflictions, which `design/02-architecture.md:91` includes and `design/03-rules.md:229` requires | Add afflictions, so the two lists match |
| `design/02-architecture.md` | 91 | Names the families but nothing points to where they are defined | Link to `design/03a-tables.md` |
| `design/03-rules.md` | 115, 123, 205, 229 | Names four table families without resolving any of them | Link each to `design/03a-tables.md` |
| `design/13-authoring-a-setting.md` | 157 | The `overrides.tables:` example is the only statement of the contract and states none of its rules | Link to the override contract in `design/03a-tables.md` |
| `design/README.md` | Index | Will not list the new ADR | Add its row |

`design/09-evolution.md` and `design/06-state.md` need no change: the conventions were chosen to fit
what they already say, which is the point of R7.
