---

description: "Task list template for feature implementation"
---

# Tasks: Per-type entity status vocabulary

**Input**: Design documents from `/specs/155-per-type-entity-status-vocabulary/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Explicitly required by the feature spec (FR-005) — the issue's own root cause is that
no prior test loaded a real on-disk companion/thread entity file, so this feature is incomplete
without that exact test.

**Organization**: Tasks are grouped by user story to enable independent implementation and
testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project (per plan.md): `engine/wyrd/` for source, `tests/engine/` for tests.

---

## Phase 1: Setup

No new project scaffolding is needed — `engine/wyrd/entity.py` and `tests/engine/test_entity.py`
already exist and this feature only edits them.

- [X] T001 Read `engine/wyrd/entity.py` in full (STATUSES, validate(), legal_transition(),
      status_counts(), `_TYPE_ENUM_FIELDS`) to confirm the exact current shape the fix edits, and
      `tests/engine/test_entity.py`'s existing fixtures/conventions (`_minimal()`, `unittest`,
      `PYTHONPATH=engine`) so new tests match the file's own style.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The one shared code change every user story's tests exercise — the per-type/role
status vocabulary lookup and `validate()`'s use of it.

**⚠️ CRITICAL**: No user story task can be verified until this phase is complete.

- [X] T002 In `engine/wyrd/entity.py`, add a `_STATUS_VOCABULARIES` (or equivalent) lookup that
      maps `type` to the vocabulary tuples researched in `research.md`'s Decision table:
      `character` maps to a nested lookup keyed on `role` (default `STATUSES` unless
      `role == "companion"`, which maps to `("with-party", "away", "dead", "lost", "departed")`);
      `thread` maps directly to `("open", "resolved", "cold", "never-answered")`; every other type
      has no entry and falls back to `STATUSES`. Follow the existing `_TYPE_ENUM_FIELDS` dict
      pattern already in this file (same file, same module) rather than a new shape.
- [X] T003 In `engine/wyrd/entity.py`, add a small helper (e.g. `_status_vocabulary(frontmatter)`)
      that, given an entity's frontmatter, returns the correct vocabulary tuple for its
      `type`/`role` using the lookup from T002. Depends on T002.
- [X] T004 In `engine/wyrd/entity.py`'s `validate()`, replace the flat `if status not in STATUSES`
      check with a call to the T003 helper, keeping the existing error shape
      (`{"valid": False, "error": f"invalid status '{status}'"}`) but naming which vocabulary it
      was checked against per FR-004 (e.g. include the entity's type/role or the vocabulary name
      in the message) so a rejection is diagnosable without reading the source. Depends on T003.
- [X] T005 Confirm (do not change) that `legal_transition()` and `status_counts()` are left
      operating only over the default `STATUSES` tuple, per plan.md's explicit scope decision —
      add a one-line comment near `STATUSES`/`legal_transition()` if none already explains why
      they are unaffected, so a future reader does not "fix" this as an oversight. Depends on T004.

**Checkpoint**: `validate()` now checks status against the correct per-type/role vocabulary;
every user story below just exercises this from different fixtures.

---

## Phase 3: User Story 1 - A companion entity file loads with its documented status (Priority: P1) 🎯 MVP

**Goal**: `validate()` accepts every documented companion status value, and rejects a value from
the old default vocabulary once it's a companion.

**Independent Test**: write a companion entity file to disk with `status: with-party`, load it via
`wyrd.state.load_entity`, and confirm `entity.validate()` on the loaded frontmatter reports valid.

### Tests for User Story 1

- [X] T006 [P] [US1] Add `EndToEndStatusVocabularyTest` (or extend an existing test class) in
      `tests/engine/test_entity.py`: write a real companion entity file to a `tempfile`
      directory (`type: character`, `role: companion`, `status: with-party`, plus the other
      required common fields), load it with `wyrd.state.load_entity`, and assert
      `entity.validate()` on the loaded frontmatter returns `{"valid": True}` — the exact
      end-to-end gap FR-005/the issue names. This is the primary acceptance test for US1.
- [X] T007 [P] [US1] In the same test class, parametrize (subTest) over every companion status
      value (`with-party`, `away`, `dead`, `lost`, `departed`) against an in-memory frontmatter
      dict (matching `_minimal()`'s convention) and assert each passes `entity.validate()`.
- [X] T008 [P] [US1] Add a test asserting a `role: companion` character with `status: complete`
      (a value from the *default* vocabulary, not the companion one) is rejected by
      `entity.validate()` — proves the companion vocabulary replaces the default rather than
      extending it (spec's Acceptance Scenario 3 for US1).

**Checkpoint**: User Story 1 is independently verifiable — run
`PYTHONPATH=engine python3 -m unittest tests.engine.test_entity -v` and see these three pass.

---

## Phase 4: User Story 2 - A thread entity file loads with its documented status (Priority: P1)

**Goal**: `validate()` accepts every documented thread status value, and rejects a value from the
old default vocabulary once it's a thread.

**Independent Test**: write a thread entity file to disk with `status: open`, load it via
`wyrd.state.load_entity`, and confirm `entity.validate()` on the loaded frontmatter reports valid.

### Tests for User Story 2

- [X] T009 [P] [US2] In `tests/engine/test_entity.py`, write a real thread entity file to a
      `tempfile` directory (`type: thread`, `status: open`, plus required common fields), load it
      with `wyrd.state.load_entity`, and assert `entity.validate()` on the loaded frontmatter
      returns `{"valid": True}` — the second end-to-end gap FR-005/the issue names.
- [X] T010 [P] [US2] In the same test class, parametrize (subTest) over every thread status value
      (`open`, `resolved`, `cold`, `never-answered`) against an in-memory frontmatter dict and
      assert each passes `entity.validate()`.
- [X] T011 [P] [US2] Add a test asserting a `thread` entity with `status: stub` (a default-
      vocabulary value, not a thread one) is rejected by `entity.validate()` (spec's Acceptance
      Scenario 3 for US2).

**Checkpoint**: User Stories 1 and 2 both independently verifiable via the same test run.

---

## Phase 5: User Story 3 - Every other entity type keeps working exactly as before (Priority: P2)

**Goal**: confirm the fix does not narrow or change validation for any type/role that was never
part of the reported bug.

**Independent Test**: validate an existing fixture of each other entity type with each of `stub`,
`drafted`, `complete`, confirm all three still succeed, and that an invented value still fails.

### Tests for User Story 3

- [X] T012 [P] [US3] In `tests/engine/test_entity.py`, extend or add a test that iterates
      `entity.ENTITY_TYPES` minus `thread` (companions are `type: character`, so this also
      needs `role` left unset/non-companion for `character`) and asserts each of `stub`,
      `drafted`, `complete` still passes `entity.validate()` via `_minimal()` — a regression
      guard for SC-003.
- [X] T013 [P] [US3] Add a test asserting a `character` entity with `role: player` (and, per the
      Edge Cases section, one with no `role` field at all) and `status: complete` still passes
      `entity.validate()` — confirms only `role: companion` opts into the companion vocabulary.
- [X] T014 [P] [US3] Add a test asserting an unrecognised status value (e.g. `status: active`) is
      still rejected for a non-overridden type, with the existing "invalid status" error family
      (Acceptance Scenario 3 for US3).

**Checkpoint**: All three user stories independently verifiable; the full existing
`tests/engine/test_entity.py` suite still passes unchanged for every pre-existing test.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T015 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` repo-wide and fix
      anything this feature's diff introduced (CLAUDE.md's lint gate).
- [X] T016 Run `PYTHONPATH=engine python3 -m unittest discover -s tests/engine -v` (the whole
      engine test suite, not just `test_entity.py`) to confirm no unrelated test regressed.
- [X] T017 Walk through `quickstart.md`'s two inline scripts by hand (companion, thread) to
      confirm the observed output matches what quickstart.md documents as "after the fix."
- [X] T018 Update the now-stale docstring/comment in `tests/engine/test_verbs.py`'s
      `_make_chronicle_dir()` (the paragraph explaining that a real companion/thread file "cannot
      currently be loaded" and that this is "a real, pre-existing gap... out of scope for #402")
      so it no longer asserts a bug that this feature just fixed — either remove the paragraph or
      correct it to state the gap is now closed, without expanding this feature's scope to
      rewriting those verb tests to use real files.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies.
- **Foundational (Phase 2)**: depends on Setup; BLOCKS every user story (all three exercise the
  same `validate()` change).
- **User Stories (Phases 3-5)**: all depend on Foundational completion; independent of each other
  and may be done in any order or in parallel (different test methods, same file — see note
  below on file-level parallelism).
- **Polish (Phase 6)**: depends on all three user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: after Foundational — no dependency on US2/US3.
- **User Story 2 (P1)**: after Foundational — no dependency on US1/US3.
- **User Story 3 (P2)**: after Foundational — no dependency on US1/US2; exists to guard against
  the fix regressing anything, so it is most useful run last, but nothing blocks doing it first.

### Within Each User Story

- Tests are the only tasks in each user story phase (the implementation itself is entirely in
  Phase 2, since all three stories exercise one shared code change) — there is deliberately no
  separate "implementation" sub-phase per story here.

### Parallel Opportunities

- T002-T005 (Foundational) are sequential — each depends on the previous.
- T006-T008 (US1), T009-T011 (US2), and T012-T014 (US3) are marked [P] against each other in the
  sense that they touch different test methods with no data dependency between them, but they all
  land in the same file (`tests/engine/test_entity.py`) — running them "in parallel" in practice
  means writing them as independent test methods, not literally concurrent file edits. Note this
  matches `docs/design/27-tooling.md`/`CLAUDE.md`'s stdlib-`unittest`-only convention: no test
  runner parallelism is introduced by this feature.

---

## Parallel Example: User Stories 1 and 2

```bash
# Both are independent additions to the same test file; write them as separate test methods:
Task: "Add EndToEndStatusVocabularyTest.test_companion_file_from_disk in tests/engine/test_entity.py"
Task: "Add EndToEndStatusVocabularyTest.test_thread_file_from_disk in tests/engine/test_entity.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (read the code).
2. Complete Phase 2 (the shared `validate()` fix) — CRITICAL, blocks everything.
3. Complete Phase 3 (US1: companion end-to-end test).
4. **STOP and VALIDATE**: run `tests.engine.test_entity` and confirm the new companion tests pass
   and nothing else regressed.

### Incremental Delivery

1. Setup + Foundational → the fix itself lands.
2. Add US1 (companion) → verify independently.
3. Add US2 (thread) → verify independently — together, US1+US2 satisfy both of the issue's
   acceptance criteria.
4. Add US3 (regression guard for every other type) → verify independently.
5. Polish: lint, full suite, quickstart walkthrough, stale-comment cleanup.

---

## Notes

- [P] tasks here mean independent test methods in one shared file, not independent files — see
  Parallel Opportunities above.
- Every task in Phases 3-5 traces directly to an Acceptance Scenario in `spec.md`.
- Commit after each phase (Foundational; US1; US2; US3; Polish), not after every single task —
  this keeps the diff reviewable without splintering one small fix into many tiny commits.
- Avoid: adding a fourth override no design document documents, changing `legal_transition()`'s
  contract, or rewriting `test_verbs.py`'s in-memory-dict tests to use real files (T018 only
  corrects that file's now-stale *comment*, per plan.md's scope decision).
