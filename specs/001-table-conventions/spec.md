# Feature Specification: Table conventions and the tables index

**Feature Branch**: `001-table-conventions`

**Created**: 2026-08-22

**Status**: Draft

**Input**: GitHub issue #15 — "Table conventions and the tables index". Create `docs/design/04-tables.md`
as the engine's table index and the shared conventions every table family must satisfy: how a table
is rolled and read, the row schema, the override contract, the index, and versioning. Out of scope:
the contents of any actual table, and implementing `tables.py`.

## Context

The ruleset in `docs/design/03-rules.md` names five table families — criticals, aftermath,
transformations, afflictions, oracles — and defines none of them. `docs/design/02-architecture.md` and
`docs/design/27-tooling.md` both promise a `tables/` directory holding them as pure, setting-neutral,
overridable data, but nothing in the repository states the shape of a row, how a result is looked
up, or what a setting may replace.

This feature is the gate for issue #15's four sibling children (one per table family). Without an
agreed structural answer first, four siblings write four dialects.

## Clarifications

### Session 2026-08-22

- Q: When a table result comes up that this character has already taken, what does the engine do? →
  A: Each family declares whether its results are unique-per-character or repeatable; a unique
  family rerolls on a duplicate, a repeatable family does not.
- Q: Should severity be a field every table row carries, or only the families that need it? →
  A: Family-specific. Severity belongs to the families whose rules consume it; other families omit
  it from their rows.
- Q: How should a table be pinned so recorded outcomes stay interpretable when the table changes? →
  A: Reuse the existing version stamps. Tables ship with the engine or the setting, both already
  versioned in `chronicle.yaml`, and every outcome already records the engine that produced it;
  the outcome additionally records the table key. No per-table version is introduced.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An author writes a new table family (Priority: P1)

Someone picking up one of the sibling issues opens `docs/design/04-tables.md` and can write their
family's file without inventing any structural decision: the die, the modifier, the out-of-range
behaviour, the required row fields and the file's location are all already settled and stated in one
place.

**Why this priority**: This is the whole reason the document exists. Every other benefit is
downstream of four authors reading the same conventions.

**Independent Test**: Give the document to a reader who has not seen the sibling issues and ask them
to state, without guessing, what fields a critical-hit row must carry and what happens on a roll
above the highest row. Both answers are found in the document.

**Acceptance Scenarios**:

1. **Given** `docs/design/04-tables.md` exists, **When** an author needs to know what die a table is
   rolled on and where its modifier comes from, **Then** the document states both, and states them
   once rather than per family.
2. **Given** a roll resolves above the highest row or below the lowest, **When** the author consults
   the conventions, **Then** the document states that this cannot happen and why, without leaving
   it to the family.
3. **Given** a family needs a field the shared schema does not define, **When** the author consults
   the conventions, **Then** the document states whether family-specific fields are permitted and
   how they are declared.

---

### User Story 2 - A setting author replaces a table (Priority: P2)

Someone writing a `wyrd-<setting>` repository wants a table whose results fit their world. They need
to know exactly what `overrides.tables:` lets them replace, what it does not, and how their renamed
vocabulary stays presentation-only.

**Why this priority**: `docs/design/24-authoring-a-setting.md:157` already presumes this contract exists
and is the only evidence in the repo of either a naming scheme or a per-table file. Leaving it
undefined means the one published example is unbacked.

**Independent Test**: A setting author can determine, from this document alone, whether a proposed
override is legal, and can name the file path their replacement must live at.

**Acceptance Scenarios**:

1. **Given** a setting wishes to replace a table's rows, **When** it declares the table under
   `overrides.tables:`, **Then** the document states this is permitted and states the key naming
   scheme used to address a table.
2. **Given** a setting wishes to change a table's die, its modifier, or its row schema, **When** it
   attempts to do so, **Then** the document states this is a new mechanism, forbidden by
   `docs/design/24-authoring-a-setting.md`, and is a load error.
3. **Given** a setting renames a mechanic that a table's rows refer to, **When** a result is
   recorded to state, **Then** the document states that the rename is presentation-only and the
   engine's own label is what reaches state.

---

### User Story 3 - A chronicle replays years later (Priority: P3)

A chronicle that recorded a table result under one version of a table is loaded after the table has
changed. The recorded outcome must remain interpretable, and the history must not be recomputed.

**Why this priority**: Required by `docs/design/29-evolution.md`, but only bites once tables exist and
change. It must be settled now because it constrains what a row carries.

**Independent Test**: Given a recorded table outcome from an earlier version, a reader can determine
which table produced it and that it will not be recomputed.

**Acceptance Scenarios**:

1. **Given** a table changes, **When** a chronicle that rolled on the older version is loaded,
   **Then** the document states that the recorded outcome stands unchanged and the new table applies
   forward only.
2. **Given** a recorded table outcome, **When** a reader inspects it, **Then** the document states
   what pinning information identifies the table and version that produced it.

---

### Edge Cases

- A modified roll lands above the highest row, or below the lowest.
- A unique-per-character family rolls a result the character already holds, and rerolls.
- A unique-per-character family's table is exhausted — the character holds every result in it — so
  rerolling cannot terminate.
- A setting override supplies a table with gaps or overlaps in its ranges, or whose ranges do not
  span the rollable span.
- A setting override names a table key the engine does not publish.
- A transformation's severity would consume more Taint than the character holds.
- A family that has no natural severity concept.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST contain `docs/design/04-tables.md`, a design document in the present
  tense describing the engine's table conventions and indexing every table family.
- **FR-002**: The document MUST state how a table is rolled: the die used, where the modifier comes
  from, and that the die and modifier are properties of the family rather than of an individual row.
- **FR-003**: The document MUST state that there is no out-of-range case and why — that ranges are
  contiguous, start at the family's lowest possible total, and end in a row open at the top, all
  required at load — so no total can fall above the highest row or below the lowest.
- **FR-004**: The document MUST state that each family declares whether its results are
  unique-per-character or repeatable, that a unique family rerolls when an already-held result comes
  up, and that a repeatable family does not.
- **FR-004a**: The document MUST state what a unique family does when rerolling cannot terminate —
  when every result in the table is already held.
- **FR-005**: The document MUST define the row schema every family satisfies, carrying at minimum a
  range, a mechanical effect the engine can apply, and a description slot.
- **FR-006**: The document MUST state that severity is family-specific rather than a shared row
  field — carried only by the families whose rules consume it, omitted by the rest — and MUST be
  consistent with `docs/design/03-rules.md`'s statement that a transformation consumes Taint equal to its
  severity.
- **FR-007**: The document MUST state whether and how a family may add fields beyond the shared
  schema.
- **FR-008**: The document MUST state the table naming scheme and the file layout — one file per
  table, at a stated path — consistent with the `critical-slashing` example already published in
  `docs/design/24-authoring-a-setting.md`.
- **FR-009**: The document MUST define the override contract: that a setting replaces a table's rows
  via `overrides.tables:`, that it may not change the roll or the row schema, and that an override
  naming an unpublished table key is a load error.
- **FR-010**: The document MUST state that renames are presentation-only and never reach state, for
  table rows as for everything else.
- **FR-011**: The document MUST state what an overriding table must satisfy to load — at minimum,
  that its ranges cover the rollable span without gaps or overlaps.
- **FR-012**: The document MUST contain an index with one row per table family, linking to that
  family's own file, structured so a sibling change appends exactly one row.
- **FR-013**: The document MUST state that a table is pinned by the version stamps that already
  exist — the engine and setting versions in `chronicle.yaml` and the engine stamped on every
  recorded outcome — plus the table key recorded with the outcome, and MUST state that no per-table
  version is introduced.
- **FR-013a**: The document MUST state that a changed table applies forward only and that recorded
  outcomes stand unchanged, consistent with `docs/design/29-evolution.md`; and MUST state which change
  class a table change falls into, so the `migrations[]` entry in `docs/design/22-state.md` is
  determinable.
- **FR-014**: The document MUST NOT contain the contents of any actual table beyond whatever minimal
  illustration the conventions require, and MUST NOT specify the implementation of `tables.py`.
- **FR-015**: Existing design documents that reference tables MUST agree with the new document —
  where `docs/design/02-architecture.md`, `docs/design/27-tooling.md` or `docs/design/24-authoring-a-setting.md`
  state something the conventions contradict or leave dangling, those documents are updated in place
  rather than left to drift.
- **FR-016**: No setting name, system name, or term borrowed from a source system may appear in the
  document, in prose, in examples, or in a table row; and no tonal register may be baked into a
  convention or its examples.
- **FR-017**: `docs/README.md`'s index MUST reflect any decision record this feature produces, and
  the document MUST be reachable from the design set the same way its siblings are.

### Key Entities

- **Table family**: A named category of outcome the rules roll for — criticals, aftermath,
  transformations, afflictions, oracles. Carries a die, a modifier source, whether its results are
  unique-per-character or repeatable, and a set of rows.
- **Table**: One concrete rollable list within a family, addressed by a key and held in its own
  file. A family may hold several (one critical table per damage type).
- **Row**: One entry in a table — a range, a mechanical effect, a description slot, and whatever the
  family additionally requires.
- **Override**: A setting's declaration under `overrides.tables:` replacing a named table's rows
  with a file of its own.
- **Pin**: The information identifying which table produced a recorded outcome — the table key on
  the outcome, resolved against the engine and setting versions the chronicle already records. Not a
  new version of its own.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who has seen none of the sibling issues can, from `docs/design/04-tables.md`
  alone, answer all five structural questions — die, modifier, out-of-range, row fields, file path —
  without guessing.
- **SC-002**: Every table family named in `docs/design/02-architecture.md` and `docs/design/27-tooling.md`
  appears in the index, and every family in the index appears in those documents. The two sets match
  exactly.
- **SC-003**: Adding one sibling family to the index is a one-row change to `docs/design/04-tables.md`
  and touches no other line of it.
- **SC-004**: A grep for setting and system vocabulary across `design/` returns nothing new.
- **SC-005**: Every table reference in `docs/design/03-rules.md` resolves to a family present in the
  index — no rule names a table the index does not know about.
- **SC-007**: The conventions introduce no version, no storage location and no override key beyond
  those `docs/design/22-state.md` and `docs/design/24-authoring-a-setting.md` already define.
- **SC-006**: No statement in the new document contradicts `docs/design/02-architecture.md`,
  `docs/design/27-tooling.md`, `docs/design/29-evolution.md` or `docs/design/24-authoring-a-setting.md`; where one
  did, that document was updated in the same change.

## Assumptions

- The conventions document is prose design, not schema code. Any YAML shown is illustrative of the
  contract, not a specification of a parser — `tables.py` is R4 of epic #1 and out of scope here.
- The five families named in `docs/design/02-architecture.md` are the complete current set. Oracles are
  included even though `docs/design/27-tooling.md`'s list omits afflictions; that omission is treated as
  the stale one and is corrected under FR-015.
- Each family lands in its own `design/03a-N-*.md` file, per issue #15's stated deviation from epic
  #6's "one new file" deliverable. This document indexes rather than contains them.
- Existing engine conventions are reused rather than re-invented: the version-pinning shape comes
  from `docs/design/22-state.md`, the forward-only rule from `docs/design/29-evolution.md`, the closed
  overridable set from `docs/design/24-authoring-a-setting.md`.
- The `critical-slashing` key in `docs/design/24-authoring-a-setting.md:157` is authoritative for the
  naming scheme: lowercase, hyphenated, `<family>-<variant>`.
- Whether this feature also earns an ADR is decided during planning against `docs/README.md`'s
  two-part test; the spec does not presume one either way.

## Dependencies

- Blocks: issue #15's four sibling children (#2–#7's table-family work), each of which appends one
  row to this document's index.
- Depended on by: R4 of epic #1 (`tables.py`), which implements what this document specifies.
- Parent epic #6; grandparent epic #1.
