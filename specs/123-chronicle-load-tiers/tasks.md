---
description: "Task list for Chronicle load-tier resolution and recap.md"
---

# Tasks: Chronicle load-tier resolution and recap.md

**Input**: Design documents from `specs/123-chronicle-load-tiers/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/loadtier.md,
quickstart.md

**Tests**: Included — CLAUDE.md expects the repo to stay ruff-clean, and this feature's own
acceptance scenarios are directly testable; a new `tests/engine/test_loadtier.py`.

**Organization**: one new module (`engine/wyrd/loadtier.py`), one small fix in
`engine/wyrd/entity.py`, one small addition in `engine/wyrd/state.py`, one wiring point in
`engine/wyrd/session.py`.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Confirm the existing suite passes before any change:
      `PYTHONPATH=engine python3 -m unittest discover -s tests -p 'test_*.py'`

## Phase 2: Foundational (blocking prerequisites for all user stories)

**Purpose**: fix the pre-existing gap that blocks any player-character entity from loading.

- [ ] T002 Add `"player"` to `_ROLES` in `engine/wyrd/entity.py` (research.md, data-model.md) —
      `validate()`/`load()`/`load_set()` currently reject a real `role: player` character file.
- [ ] T003 Expose `state.py`'s existing atomic-write helper publicly as
      `write_text_atomic(text: str, path: pathlib.Path) -> None` in `engine/wyrd/state.py`
      (thin wrapper over `_atomic_write_text`, per research.md's "reuse, don't duplicate" call).

**Checkpoint**: player-character entities load correctly; a public atomic-write entry point
exists for `recap.md`.

---

## Phase 3: User Story 1 - Always-tier resolves without a manifest (Priority: P1) 🎯 MVP

**Goal**: `loadtier.always_tier(entities)` returns exactly the player character, with-party
companions and `heat >= 3` threads, recomputed fresh from current entity state every call.

**Independent Test**: build an entity set with a player character, two with-party companions, one
departed companion, and threads at heat 2/3/5; assert the query's result; flip a status/heat
value with no other write and assert the result changes on the next call.

### Tests for User Story 1

- [ ] T004 [P] [US1] In `tests/engine/test_loadtier.py`, test `always_tier` returns the player
      character, both with-party companions, and both `heat >= 3` threads, excluding the departed
      companion and the `heat: 2` thread (spec.md Acceptance Scenario 1).
- [ ] T005 [P] [US1] In `tests/engine/test_loadtier.py`, test that changing a companion's
      `status` (or a thread's `heat`) between two calls changes `always_tier`'s result on the
      second call with no other state touched (FR-009, spec.md Acceptance Scenario 2).
- [ ] T006 [P] [US1] In `tests/engine/test_loadtier.py`, test the edge case of an entity set with
      no with-party companions and no `heat >= 3` thread: `always_tier` still returns the player
      character and empty `companions`/`threads` mappings, not an error.
- [ ] T007 [P] [US1] In `tests/engine/test_loadtier.py`, test that two entities both carrying
      `role: player` raises `ValueError` naming both ids (contracts/loadtier.md).

### Implementation for User Story 1

- [ ] T008 [US1] Implement `always_tier(entities: dict[str, dict]) -> dict` in
      `engine/wyrd/loadtier.py`, per contracts/loadtier.md and data-model.md.

**Checkpoint**: User Story 1 is independently testable and passing.

---

## Phase 4: User Story 2 - On-demand entities are reachable by id or search (Priority: P2)

**Goal**: any entity not in the always tier is reachable by id, and findable by a text search.

**Independent Test**: fetch a non-always-tier entity by id; search a term that appears only in an
on-demand entity's body/frontmatter and confirm it is found.

### Tests for User Story 2

- [ ] T009 [P] [US2] In `tests/engine/test_loadtier.py`, test `lookup` returns an on-demand
      entity's full frontmatter by id, and `None` for an absent id (spec.md Acceptance Scenario
      1).
- [ ] T010 [P] [US2] In `tests/engine/test_loadtier.py`, test `search` finds an entity by a term
      present in its frontmatter, a term present only in its supplied body text, is
      case-insensitive, and returns `[]` for an empty term (spec.md Acceptance Scenario 2,
      contracts/loadtier.md).

### Implementation for User Story 2

- [ ] T011 [P] [US2] Implement `lookup(entity_id, entities)` in `engine/wyrd/loadtier.py`.
- [ ] T012 [US2] Implement `search(term, entities, bodies=None)` in `engine/wyrd/loadtier.py`.

**Checkpoint**: User Stories 1-2 are independently testable and passing.

---

## Phase 5: User Story 3 - recap.md regenerates at session close (Priority: P1)

**Goal**: `generate_recap` produces a ~200-word document from current state, wired into
`session.run_close` so it actually regenerates at close.

**Independent Test**: call `generate_recap` with a built entity set/chronicle and confirm every
required section (data-model.md) is present, threads are capped at three by heat, and word count
is close to 200; wire it into `run_close` and confirm it runs at the right step.

### Tests for User Story 3

- [ ] T013 [P] [US3] In `tests/engine/test_loadtier.py`, test `generate_recap` includes the
      `where`, `changes` and `body_mind` text supplied, the with-party companions by name, and at
      most the three highest-`heat` `status: open` threads (spec.md Acceptance Scenarios 1-2,
      data-model.md).
- [ ] T014 [P] [US3] In `tests/engine/test_loadtier.py`, test `generate_recap`'s word count lands
      within roughly 150-250 words for a typical chronicle (spec.md Acceptance Scenario 3,
      SC-003), and that a chronicle with zero open threads names none rather than fabricating
      placeholders (spec.md Edge Cases).
- [ ] T015 [US3] In `tests/engine/test_session.py`, test that a `run_close` call wired with a
      `generate_recap`-backed step writes `recap.md`'s new content (contracts/loadtier.md
      "Wiring into session.py").

### Implementation for User Story 3

- [ ] T016 [US3] Implement `generate_recap(entities, chronicle, *, where=None, changes=None,
      body_mind=None) -> str` in `engine/wyrd/loadtier.py`, per data-model.md and
      contracts/loadtier.md.
- [ ] T017 [US3] Wire a `generate_recap` + `state.write_text_atomic` closure into a
      `run_close(steps)` call site (or document the call pattern where session orchestration
      lives), matching contracts/loadtier.md's "Wiring into session.py" — `session.py` itself
      gains no new public function, per that contract.

**Checkpoint**: All user stories independently testable and passing.

---

## Phase 6: Polish

- [ ] T018 Add module docstring to `engine/wyrd/loadtier.py` matching this repo's convention
      (why this module exists, what it builds on, what it deliberately leaves out — see
      `session.py`'s own docstring for the pattern), and update `docs/design/22-state.md` if any
      wording there no longer matches the implemented behavior (CLAUDE.md: design docs describe
      the present).
- [ ] T019 `python3 -m ruff check .` and `python3 -m ruff format --check .` both clean
      repo-wide (SC-004).
- [ ] T020 `python3 tools/check_docs.py` clean (no design doc left unreachable/stale).
- [ ] T021 Full suite green: `PYTHONPATH=engine python3 -m unittest discover -s tests -p
      'test_*.py'`.

## Dependencies

- Phase 2 (T002-T003) blocks every user story — `always_tier` cannot load a real player character
  without T002, and US3's `generate_recap` write needs T003.
- User Story 1 (T004-T008) has no dependency on Stories 2 or 3, and is the MVP.
- User Story 2 (T009-T012) is independent of Story 3; both depend only on Phase 2.
- User Story 3 (T013-T017) reuses `always_tier`'s thread/companion queries internally but is
  tested and can be implemented independently of Story 2.
- Phase 6 runs after every story lands.
