# Feature Specification: Chronicle.yaml schema, load/save and versioning

**Feature Branch**: `122-chronicle-yaml-schema`

**Created**: 2026-09-10

**Status**: Draft

**Input**: User description: "Chronicle.yaml schema, load/save and versioning (closes #325)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Round-trip a chronicle's full identity (Priority: P1)

A chronicle exists as a directory of entity files plus exactly one non-entity file,
`chronicle.yaml`, which pins the chronicle's own identity: what engine and setting it runs
under, its calendar, its danger rating, and the intent recorded at bootstrap. The engine must
be able to write that file, and later read it back, with every field intact and nothing
silently dropped or reordered.

**Why this priority**: Nothing else in this epic (load-tier resolution, invariants, the
transaction lifecycle) has anywhere to read or write its own state without this. It is the
foundation the rest of #300 builds on.

**Independent Test**: Construct a chronicle.yaml mapping covering every field in the schema,
save it, load it back, and confirm the loaded mapping equals the original.

**Acceptance Scenarios**:

1. **Given** a fully-populated chronicle state (name, engine/setting version pins, calendar,
   era, sessions, danger rating, intent, an empty migrations log), **When** it is saved and
   then loaded, **Then** the loaded mapping is identical to the original.
2. **Given** a chronicle.yaml on disk with fields in a different order than the schema
   documents them, **When** it is loaded, **Then** every field is read correctly regardless of
   its position in the file.
3. **Given** a chronicle.yaml missing an optional field (e.g. `era: null`, `pending: null`),
   **When** it is loaded, **Then** the missing field reads back as its documented default
   rather than raising an error.

---

### User Story 2 - Distinguish current version from originating version (Priority: P1)

A chronicle's engine and setting each carry two separate values: the version they run under
*now*, and the version they began under. A reader years later — human or engine — must be able
to tell these apart, because an apparent oddity in old recorded state may be explained by what
the rules were when it was written, not by what they are today.

**Why this priority**: This is the specific guarantee docs/design/22-state.md calls out as
mattering "as much as `version`" — without it, an early oddity is unattributable, which is
exactly the failure the design doc names as unacceptable.

**Independent Test**: Save a chronicle with `engine.version` and `engine.created_under` set to
different values, load it back, and confirm both survive distinctly (i.e. bumping `version`
alone must never overwrite or infer `created_under`).

**Acceptance Scenarios**:

1. **Given** a chronicle created under engine version 0.1.0 and later saved again after the
   engine version advanced to 0.4.0, **When** it is loaded, **Then** `engine.created_under`
   still reads `0.1.0` and `engine.version` reads `0.4.0`.
2. **Given** the same chronicle for `setting.version` / `setting.created_under`, **When**
   loaded, **Then** the same distinction holds independently of the engine's.

---

### User Story 3 - Append a migration record without disturbing history (Priority: P1)

When a chronicle's engine or setting version changes, that change is recorded as an entry
appended to the chronicle's migrations log: what changed, what class of change it was, when it
applied, and a human-readable note. Once written, an entry is never edited or reordered — the
log is the append-only history a decade-old chronicle depends on to explain itself.

**Why this priority**: This is the specific mechanism docs/design/29-evolution.md and
docs/design/22-state.md both rely on for explaining drift over a chronicle's life; getting the
append-only guarantee wrong (allowing an edit, a reorder, or a silent overwrite) breaks that
guarantee for good, because "the history you would want to describe has already happened."

**Independent Test**: Start from a chronicle with two prior migration entries, append a third,
and confirm the first two are byte-for-byte unchanged and still in original order, with the new
entry appended after them.

**Acceptance Scenarios**:

1. **Given** a chronicle with an existing migrations log of two entries, **When** a third entry
   is appended, **Then** the log contains all three entries, the first two unchanged, and the
   new entry last.
2. **Given** an attempt to modify an already-appended migration entry's fields, **When** the
   chronicle is next saved, **Then** the write is rejected rather than silently accepted — an
   entry, once appended, is immutable through this feature's own save path.
3. **Given** a migration entry, **When** it is written, **Then** its `class` is one of
   `additive`, `tuning`, `structural`, or `behavioural` — any other value is rejected at write
   time.

---

### User Story 4 - Carry an opaque interrupted-session marker (Priority: P2)

A session may stop mid-beat, in which case chronicle.yaml records a `pending` block describing
where play stopped. This feature does not implement what `pending` *means* (a later feature in
this epic does), but it must round-trip whatever is written there without corrupting or
dropping it, since a later feature will depend on this one having preserved it faithfully.

**Why this priority**: Lower than the other three because this feature does not act on
`pending`'s semantics at all — it only must not lose the field. Still P2, not P3, because a
later child issue in this epic depends on this round-trip being reliable from day one.

**Independent Test**: Save a chronicle with an arbitrary `pending` mapping (beat, awaiting text,
and a nested `rolled` value), load it back, and confirm the mapping is unchanged; separately
confirm a chronicle with `pending: null` round-trips as `null`.

**Acceptance Scenarios**:

1. **Given** a chronicle with a populated `pending` block, **When** saved and reloaded, **Then**
   every field of `pending` is preserved unchanged.
2. **Given** a chronicle with no interrupted session (`pending: null`), **When** saved and
   reloaded, **Then** `pending` reads back as `null`.

### Edge Cases

- What happens when chronicle.yaml exists on disk but is missing a required field entirely
  (e.g. no `schema_version`)? Loading it must fail with an error naming the missing field,
  rather than silently defaulting a value that changes the chronicle's recorded identity.
- What happens when a load or save is interrupted mid-write (process killed, disk full)? The
  file on disk must remain either the old, fully-valid state or the new, fully-valid state —
  never a partially-written, unparseable file (docs/design/27-tooling.md, "persist before
  narrate").
- What happens when `danger_rating` or `sessions` is given a negative value? The write is
  rejected — both are non-negative by definition.
- What happens when the migrations log already exists but the file predates this feature (i.e.
  was written by the current minimal `schema_version: 1` + `last_roll` scaffold)? Loading it
  must either upgrade it to the full schema with sensible defaults for the new fields, or fail
  clearly naming what's missing — never silently misread old data as if it already matched the
  new shape.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST be able to save a chronicle's full state — `schema_version`,
  `name`, `engine` (`repo`, `version`, `created_under`), `setting` (`repo`, `version`,
  `created_under`), `calendar` (`year`, `month`, `day`), `era`, `sessions`, `danger_rating`,
  `migrations` (a list), `intent` (`about`, `avoid`, `session_length`, `lethality`,
  `world_acts_offstage`), and `pending` — to `chronicle.yaml`, and load it back with every
  field intact, per docs/design/22-state.md § `chronicle.yaml`.
- **FR-002**: The engine MUST preserve `engine.version`/`engine.created_under` and
  `setting.version`/`setting.created_under` as four independently-settable values; saving with
  an updated `version` MUST NOT alter `created_under`.
- **FR-003**: The engine MUST support appending an entry to `migrations` (fields: `from`, `to`,
  `class`, `applied`, `note`) such that every previously-written entry is preserved unchanged
  and in its original order, and the new entry is added after them.
- **FR-004**: The engine MUST reject any write that would edit or reorder an already-appended
  `migrations` entry — appending is the only mutation this feature's save path permits on that
  list.
- **FR-005**: The engine MUST reject a `migrations` entry whose `class` is not one of
  `additive`, `tuning`, `structural`, `behavioural`.
- **FR-006**: The engine MUST round-trip the `pending` field's contents opaquely (whatever
  mapping or `null` is given) without interpreting or validating its internal semantics — that
  belongs to a later feature in this epic.
- **FR-007**: The engine MUST perform every write via an atomic replace (write to a temp file,
  then rename), matching the crash-safety guarantee `engine/wyrd/state.py`'s existing scaffold
  already provides, so a chronicle.yaml on disk is always either the fully-old or fully-new
  valid state, never a partial write.
- **FR-008**: The engine MUST reject loading a chronicle.yaml that is missing a required field,
  naming the specific missing field, rather than substituting a silent default for it.
- **FR-009**: The engine MUST default an absent optional field (`era`, `pending`, and any
  `intent` sub-field not given) to its documented default value on load.
- **FR-010**: The engine MUST reject a negative `sessions` or `danger_rating` value at write
  time.
- **FR-011**: The engine MUST use only the standard library, matching the rest of `engine/`
  (docs/design/27-tooling.md), and extend `engine/wyrd/state.py`'s existing restricted-YAML
  reader/writer rather than introduce a second implementation.

### Key Entities

- **Chronicle state**: The single mapping persisted in `chronicle.yaml` — a chronicle's own
  identity, distinct from any entity file. Holds engine/setting version pins, calendar, era,
  session count, danger rating, the append-only migrations log, the bootstrap `intent` block,
  and the current interrupted-session marker (`pending`), per docs/design/22-state.md.
- **Migration entry**: One record in the `migrations` list — `from`, `to` (each a partial
  version pin, e.g. `{engine: 0.1.0}`), `class` (one of the four defined values), `applied`
  (date), and `note`. Immutable once appended.
- **Intent**: The bootstrap-interview record — `about`, `avoid`, `session_length`, `lethality`,
  `world_acts_offstage` — read every session per docs/design/22-state.md.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A chronicle's full state round-trips through save and load with zero field loss
  or reordering, verified by an automated round-trip test covering every field in the schema.
- **SC-002**: A chronicle's recorded history (its migrations log) is provably append-only: no
  code path this feature introduces can alter or reorder an already-written entry.
- **SC-003**: A chronicle.yaml written by this feature can still be read correctly after an
  engine/setting version bump is recorded, distinguishing `version` from `created_under` with
  no ambiguity.
- **SC-004**: `ruff check .` and `ruff format --check .` both report clean across the whole
  repository after this feature lands.

## Assumptions

- This feature covers chronicle.yaml's own schema only. It does not implement entity
  load-tier resolution, invariant enforcement, or `pending`'s transaction-lifecycle semantics —
  those are separate, dependent features in the same parent epic (#300), tracked as #326, #327,
  #328.
- `engine/wyrd/state.py`'s existing atomic-write and restricted-YAML-subset machinery
  (from specs/075-engine-scaffolding) is extended in place, not replaced or duplicated.
- A chronicle.yaml with no recognizable `schema_version` is treated as the pre-existing minimal
  scaffold and is either upgraded on load with documented defaults, or rejected naming what's
  missing — never silently misread.
- "The intent block from the bootstrap interview" refers to the fields docs/design/22-state.md
  already names (`about`, `avoid`, `session_length`, `lethality`, `world_acts_offstage`); this
  feature persists that shape, it does not design the bootstrap interview itself.
