# Tasks: Escape and pursuit

**Input**: Design documents from `specs/088-escape-and-pursuit/`
**Prerequisites**: plan.md

## Phase 1: Difficulty ladder

- [ ] **T001** Implement `escape_difficulty(pursuer_count)` in `combat.py`: `None` for 0,
      `"challenging"` for 1, one rung harder per further pursuer, floored at `"very_hard"` for 4+
      (FR-002, FR-003).

## Phase 2: Escape resolution

- [ ] **T002** Implement `escape_scene(party_skills, pursuer_count, *, seed=None, state_path=...)`
      in `combat.py`: resolves via `rules.group_test(..., mode="least_capable", opponent=50 -
      DIFFICULTY_BONUSES[difficulty])`; clears the chronicle's `combat` key on success or on the
      no-test (zero-pursuer) case; leaves state untouched on failure; reports which party member
      was slowest (FR-001, FR-004, FR-005, FR-006).

## Phase 3: Tests

- [ ] **T003** [P] `tests/engine/test_combat.py`: `escape_difficulty` covers 0 through 5+
      pursuers against the exact ladder (SC-001).
- [ ] **T004** [P] Test: a seeded escape attempt against one pursuer that succeeds clears the
      `combat` scene (User Story 1, SC-003).
- [ ] **T005** [P] Test: a seeded escape attempt that fails leaves `engaged`/`acted` state
      byte-for-byte unchanged, and reports the slowest member (User Story 1, SC-002).
- [ ] **T006** [P] Test: zero pursuers skips the roll entirely and clears the scene
      unconditionally (User Story 2, SC-003).
- [ ] **T007** [P] Test: escape difficulty against two, three and four-or-more pursuers matches
      Difficult/Hard/Very Hard respectively, reusing the same seed to isolate the difficulty
      change (SC-001).

## Phase 4: Polish

- [ ] **T008** `ruff check . && ruff format --check . && python3 -m pytest -q` clean.
- [ ] **T009** `python3 tools/check_docs.py` still passes (no design document is touched).

## Dependencies

T001 before T002. T002 before T004-T007. T003 only needs T001. Polish (T008-T009) last.
