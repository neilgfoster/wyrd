---
description: "Task list for Chronicle.yaml schema, load/save and versioning"
---

# Tasks: Chronicle.yaml schema, load/save and versioning

**Input**: Design documents from `specs/122-chronicle-yaml-schema/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/state_module.md,
quickstart.md

**Tests**: Included — CLAUDE.md expects the repo to stay ruff-clean and this feature's own
acceptance scenarios are directly testable; `tests/engine/test_state.py` already exists and is
extended in place.

**Organization**: All work lands in one existing module (`engine/wyrd/state.py`) and one existing
test module (`tests/engine/test_state.py`) — there is no multi-file parallelism to exploit within
a story, but stories remain independently testable functions/assertions.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Confirm `PYTHONPATH=engine` test invocation still passes before any change:
      `python3 -m unittest tests.engine.test_state -v`

## Phase 2: Foundational (blocking prerequisites for all user stories)

**Purpose**: the chronicle-schema constants and shape every user story's tasks build on.

- [ ] T002 Add `DEFAULT_CHRONICLE_PATH`, `_MIGRATION_CLASSES` (the frozenset of
      `additive`/`tuning`/`structural`/`behavioural`), and the `_INTENT_DEFAULTS` mapping
      (`about: None`, `avoid: []`, `session_length: 20`, `lethality: "standard"`,
      `world_acts_offstage: True`) to `engine/wyrd/state.py`, per data-model.md.

**Checkpoint**: constants exist; user story implementation can begin.

---

## Phase 3: User Story 1 - Round-trip a chronicle's full identity (Priority: P1) 🎯 MVP

**Goal**: `default_chronicle_state()`, `save_chronicle()`, `load_chronicle()` round-trip a fully
populated chronicle with zero field loss, defaulting absent optional fields, and rejecting a
state missing a required field.

**Independent Test**: build a state with every field, save+load it, assert equality; save+load a
state missing an optional field and confirm the default is filled; attempt to load a state
missing a required field and confirm `StateError` names it.

### Tests for User Story 1

- [ ] T003 [P] [US1] Test: `default_chronicle_state()` returns the documented shape, in
      `tests/engine/test_state.py`
- [ ] T004 [P] [US1] Test: save then load a fully-populated chronicle state returns an equal
      mapping, in `tests/engine/test_state.py`
- [ ] T005 [P] [US1] Test: loading a state missing `era`/`pending`/an `intent` sub-field fills
      each documented default, in `tests/engine/test_state.py`
- [ ] T006 [P] [US1] Test: loading a state missing a required field (e.g. no `schema_version`,
      no `name`) raises `StateError` naming that field, in `tests/engine/test_state.py`
- [ ] T007 [P] [US1] Test: saving a state with a negative `sessions` or `danger_rating` raises
      `StateError` before writing anything (file on disk unchanged), in
      `tests/engine/test_state.py`

### Implementation for User Story 1

- [ ] T008 [US1] Implement `default_chronicle_state(name, engine_repo, engine_version,
      setting_repo, setting_version) -> dict` in `engine/wyrd/state.py`, per
      contracts/state_module.md (depends on T002)
- [ ] T009 [US1] Implement `validate_chronicle(state, previous_migrations=None) -> dict` in
      `engine/wyrd/state.py`: required-field check (FR-008), default-filling for optional
      fields (FR-009), non-negative `sessions`/`danger_rating` check (FR-010) — migration-class
      and immutability checks land in User Story 3's tasks, this task's version raises nothing
      for either yet (depends on T002, T008)
- [ ] T010 [US1] Implement `load_chronicle(path=DEFAULT_CHRONICLE_PATH) -> dict` in
      `engine/wyrd/state.py`: read via existing `load()`, raise `StateError` naming the path if
      it does not exist, then `validate_chronicle()` the result (depends on T009)
- [ ] T011 [US1] Implement `save_chronicle(state, path=DEFAULT_CHRONICLE_PATH) -> None` in
      `engine/wyrd/state.py`: `validate_chronicle()` first (no write on failure), then write via
      the existing atomic `save()` (depends on T009)

**Checkpoint**: User Story 1 fully functional and testable independently — a chronicle can be
created, saved, and loaded with its complete schema.

---

## Phase 4: User Story 2 - Distinguish current version from originating version (Priority: P1)

**Goal**: `engine.version`/`engine.created_under` and `setting.version`/`setting.created_under`
survive independently across a save/load cycle that changes only `version`.

**Independent Test**: load a chronicle, mutate only `engine.version`, save, reload, confirm
`created_under` is untouched for both engine and setting.

### Tests for User Story 2

- [ ] T012 [P] [US2] Test: mutating only `engine.version` and saving/reloading leaves
      `engine.created_under` unchanged, in `tests/engine/test_state.py`
- [ ] T013 [P] [US2] Test: the same independence holds for `setting.version` /
      `setting.created_under`, in `tests/engine/test_state.py`

### Implementation for User Story 2

- [ ] T014 [US2] Confirm (and if needed adjust) `validate_chronicle()` so it never derives or
      overwrites `created_under` from `version` for either version pin — this should already
      hold from T009's straight field pass-through; this task exists to make the guarantee
      explicit and tested, in `engine/wyrd/state.py` (depends on T009)

**Checkpoint**: User Stories 1 and 2 both independently functional.

---

## Phase 5: User Story 3 - Append a migration record without disturbing history (Priority: P1)

**Goal**: `append_migration()` adds an entry without touching prior entries; an illegal edit or
reorder of an already-saved entry is rejected at `save_chronicle()` time; an invalid `class` is
rejected.

**Independent Test**: start from a state with two migration entries, append a third, confirm the
first two are unchanged and in order; attempt to save a state with an altered prior entry and
confirm rejection; attempt to append/save an entry with an invalid `class`.

### Tests for User Story 3

- [ ] T015 [P] [US3] Test: `append_migration()` adds an entry after two existing ones, leaving
      both unchanged and in order, in `tests/engine/test_state.py`
- [ ] T016 [P] [US3] Test: `append_migration()` and `validate_chronicle()` both raise
      `StateError` for a `class` outside the four allowed values, in `tests/engine/test_state.py`
- [ ] T017 [P] [US3] Test: `save_chronicle()` rejects a state whose `migrations` list edits or
      reorders an entry already present in the file on disk, leaving the file unchanged, in
      `tests/engine/test_state.py`

### Implementation for User Story 3

- [ ] T018 [US3] Implement `append_migration(state, entry) -> dict` in `engine/wyrd/state.py`:
      validates `entry["class"]`, returns a new state with `entry` appended to a copied
      `migrations` list (depends on T002, T009)
- [ ] T019 [US3] Extend `validate_chronicle()` to check every `migrations[i].class` against
      `_MIGRATION_CLASSES`, and — when `previous_migrations` is given — that the new list's
      leading entries equal `previous_migrations` exactly, in `engine/wyrd/state.py` (depends
      on T009, T018)
- [ ] T020 [US3] Extend `save_chronicle()` to read the file's currently-saved state (if it
      exists) via `load()` and pass its `migrations` as `previous_migrations` to
      `validate_chronicle()`, in `engine/wyrd/state.py` (depends on T011, T019)

**Checkpoint**: User Stories 1-3 all independently functional — the append-only migrations
guarantee is enforced end-to-end.

---

## Phase 6: User Story 4 - Carry an opaque interrupted-session marker (Priority: P2)

**Goal**: `pending` round-trips exactly, whatever mapping (or `null`) it holds, with no
interpretation by this feature.

**Independent Test**: save a chronicle with a populated `pending` block, reload, confirm exact
equality; save with `pending: null`, reload, confirm `null`.

### Tests for User Story 4

- [ ] T021 [P] [US4] Test: a populated `pending` mapping round-trips unchanged through
      save/load, in `tests/engine/test_state.py`
- [ ] T022 [P] [US4] Test: `pending: None` round-trips as `None`, in `tests/engine/test_state.py`

### Implementation for User Story 4

- [ ] T023 [US4] Confirm `validate_chronicle()` treats `pending` as opaque (default `None` when
      absent per T009, no further validation of its contents) — this should already hold from
      the generic `dump_yaml`/`parse_yaml` round-trip; this task exists to make the guarantee
      explicit and tested, in `engine/wyrd/state.py` (depends on T009)

**Checkpoint**: all four user stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T024 Run `python3 -m ruff check . && python3 -m ruff format --check .` and fix any finding
- [ ] T025 Run the quickstart.md validation scenarios by hand (or as a scratch script) to confirm
      the documented shell/Python snippets behave as written
- [ ] T026 [P] Update `engine/wyrd/state.py`'s module docstring to note the chronicle schema is
      now implemented (it currently says "Later features extend the schema")

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup — blocks every user story
- **User Story 1 (Phase 3)**: depends on Foundational; no dependency on other stories
- **User Story 2 (Phase 4)**: depends on Foundational and on US1's `validate_chronicle` (T009)
  existing — not a functional dependency, just the same function being extended
- **User Story 3 (Phase 5)**: depends on Foundational and on US1's `validate_chronicle`/
  `save_chronicle` (T009/T011)
- **User Story 4 (Phase 6)**: depends on Foundational and on US1's `validate_chronicle` (T009)
- **Polish (Phase 7)**: depends on all four user stories

### Within Each User Story

- Tests are written first per story and should fail before that story's implementation tasks
  land
- Implementation tasks within a story are sequenced by their stated `(depends on ...)` note

### Parallel Opportunities

- All tests within one story phase (marked `[P]`) touch the same test file but assert
  independent behavior — write them together, run once
- T003-T007, T012-T013, T015-T017, and T021-T022 are each internally parallelizable within their
  own story phase
- Because every implementation task touches the single `engine/wyrd/state.py` module, US2/US3/US4
  implementation tasks are sequenced after US1's T009, not run in parallel with it

## Implementation Strategy

### MVP First (User Story 1 only)

Complete Phases 1-3, then stop and validate: a chronicle round-trips its full schema. This alone
unblocks #326/#327/#328 reading and writing chronicle.yaml, even before migrations or `pending`
semantics land.

### Incremental Delivery

1. Setup + Foundational → constants ready
2. US1 → round-trip works (MVP)
3. US2 → version-pin independence confirmed
4. US3 → append-only migrations enforced
5. US4 → `pending` round-trips opaquely
6. Polish → ruff-clean, quickstart validated, docstring updated
