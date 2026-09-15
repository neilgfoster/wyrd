# Feature Specification: Per-type entity status vocabulary

**Feature Branch**: `155-per-type-entity-status-vocabulary`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "entity.py's validate() enforces one global STATUSES vocabulary, rejecting companion and thread entities' own documented status values (#408)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A companion entity file loads with its documented status (Priority: P1)

Someone (the engine itself, at bootstrap or during play) writes a `character` entity with
`role: companion` and a status value from the vocabulary `docs/design/22-state.md` documents for
companions (`with-party | away | dead | lost | departed`). Loading that file must succeed.

**Why this priority**: this is the exact defect reported in #408 — it currently fails outright,
and it blocks every downstream feature that seeds or updates a real companion file (`/wyrd-bootstrap`,
a real chronicle).

**Independent Test**: write a companion entity file to disk with `status: with-party` and call
`validate()` on its loaded frontmatter; it must report valid.

**Acceptance Scenarios**:

1. **Given** a `character` entity with `role: companion` and `status: with-party` saved to disk,
   **When** the entity file is loaded and validated, **Then** validation succeeds.
2. **Given** the same entity with `status: departed`, **When** validated, **Then** validation
   succeeds (every value in the companion vocabulary is accepted, not just one).
3. **Given** a companion entity with `status: complete` (a value from the old global vocabulary,
   not the companion vocabulary), **When** validated, **Then** validation fails — the companion
   vocabulary replaces the default for companions, it does not add to it.

---

### User Story 2 - A thread entity file loads with its documented status (Priority: P1)

Someone writes a `thread` entity with a status value from the vocabulary `docs/design/22-state.md`
documents for threads (`open | resolved | cold | never-answered`). Loading that file must succeed.

**Why this priority**: the same defect as User Story 1, for the other entity type #408 names by
name, and equally blocking for real chronicle state.

**Independent Test**: write a thread entity file to disk with `status: open` and call `validate()`
on its loaded frontmatter; it must report valid.

**Acceptance Scenarios**:

1. **Given** a `thread` entity with `status: open` saved to disk, **When** the entity file is
   loaded and validated, **Then** validation succeeds.
2. **Given** the same entity with `status: never-answered`, **When** validated, **Then** validation
   succeeds.
3. **Given** a thread entity with `status: stub` (a value from the old global vocabulary, not the
   thread vocabulary), **When** validated, **Then** validation fails.

---

### User Story 3 - Every other entity type keeps working exactly as before (Priority: P2)

`docs/design/25-entities.md`'s common schema documents `status: stub | drafted | complete` for
every entity, and `docs/design/22-state.md` only calls out a different vocabulary for companion
characters and for threads. A `place`, `organisation`, `arc`, `beat`, `creature`, `item`,
`tracker`, `lore` entity, and a `character` that is not a companion (the player, a nemesis, a
bystander), must keep validating against `stub | drafted | complete` exactly as they do today —
correcting the companion/thread gap must not narrow or change validation for anything else.

**Why this priority**: the fix is scoped to two documented exceptions, not a redesign of status
validation; regressing an unrelated entity type would trade one bug for another.

**Independent Test**: validate an existing fixture of each other entity type with each of
`stub`, `drafted`, `complete` and confirm all three still succeed, and that an invented value
(e.g. `active`) still fails.

**Acceptance Scenarios**:

1. **Given** a `place` (or any non-companion, non-thread type) entity with `status: drafted`,
   **When** validated, **Then** validation succeeds.
2. **Given** a `character` entity with `role: player` (or no `role`, or `role: nemesis`) and
   `status: complete`, **When** validated, **Then** validation succeeds.
3. **Given** any of these entities with an unrecognised status value, **When** validated, **Then**
   validation fails with the existing "invalid status" error.

### Edge Cases

- A `character` entity with no `role` field at all (the schema does not require `role`): treated
  as a non-companion character, validated against the default `stub | drafted | complete`
  vocabulary — only `role: companion` opts into the companion vocabulary.
- A `thread` entity is never anything other than a thread — `type` alone selects its vocabulary,
  with no further branching.
- An entity whose `type`/`role` combination has no documented override falls back to the default
  vocabulary rather than being rejected outright, since only two overrides are documented today.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `validate()` MUST accept `status: with-party`, `status: away`, `status: dead`,
  `status: lost`, or `status: departed` for a `character` entity whose `role` is `companion`, and
  MUST reject any other status value for such an entity.
- **FR-002**: `validate()` MUST accept `status: open`, `status: resolved`, `status: cold`, or
  `status: never-answered` for a `thread` entity, and MUST reject any other status value for such
  an entity.
- **FR-003**: `validate()` MUST continue to accept only `status: stub`, `status: drafted`, or
  `status: complete` for every entity that is neither a companion character nor a thread —
  `place`, `organisation`, `arc`, `beat`, `creature`, `item`, `tracker`, `lore`, and `character`
  entities whose `role` is not `companion`.
- **FR-004**: The error message for an invalid status MUST continue to name the offending value,
  and SHOULD make clear which vocabulary it was checked against, so a rejection is diagnosable
  without reading `entity.py`'s source.
- **FR-005**: A real, on-disk companion entity file and a real, on-disk thread entity file, each
  carrying one of their own documented status values, MUST both pass validation end-to-end
  (frontmatter parsed from the file, not constructed as an in-memory dict in the test).

### Key Entities

- **Entity status vocabulary**: the closed set of legal `status` values for a given entity
  shape. Selected by `type` alone for most types, and additionally by `role` for `character`
  entities (companion vs. everything else).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A real companion entity file with `status: with-party` and a real thread entity
  file with `status: open`, both loaded from disk, pass validation — zero exceptions, zero
  false rejections.
- **SC-002**: Every entity type's status vocabulary matches what `docs/design/22-state.md` and
  `docs/design/25-entities.md` document for it, verified type by type rather than assumed.
- **SC-003**: No existing passing test regresses — every entity type that validated successfully
  before this change continues to validate successfully after it.

## Assumptions

- The two documented overrides (companion characters, threads) are the only ones that exist
  today; every other type shares the one default vocabulary the common schema documents. This is
  confirmed by reading `docs/design/22-state.md` and `docs/design/25-entities.md` in full rather
  than assumed, per the issue's own instruction.
- "Companion" is identified by `role: companion` on a `character` entity, per `22-state.md`'s own
  `role: companion` + `status` example — not by any other signal (e.g. a separate `is_companion`
  field, which does not exist).
- This is a validation-logic fix, not a schema or data-migration change: no existing entity file
  needs rewriting, since the defect only ever caused correct files to be wrongly rejected.
