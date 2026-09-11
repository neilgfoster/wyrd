# Tasks: Threats aspect & activation

**Input**: Design documents from `/specs/126-threat-aspect-activation/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/threat.py` with a module docstring matching `journey.py`'s style
      (what it implements, why plain dicts/no I/O, what's out of scope), and implement
      `active_threats`, `check_activation`, `resolve_effects`, `promote` per data-model.md's
      signatures. `resolve_effects`'s range-key matching reuses `journey._parse_range`'s logic
      (duplicate the small parsing helper locally rather than importing a private `_`-prefixed
      name from `journey.py`).

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_threat.py::test_active_threats_*` — User Story 1 / FR-001 / FR-002 /
      SC-001: mixed entity types with live/zero/absent `threat` blocks; empty input.
- [x] T003 [P] `tests/engine/test_threat.py::test_check_activation_*` — User Story 2 / FR-003 / SC-002:
      activates at `roll == imminence * 10`, does not at `+1`, never activates at `imminence == 0`.
- [x] T004 [P] `tests/engine/test_threat.py::test_resolve_effects_*` — User Story 2 / FR-004: single-value
      key, range key, unmatched roll, empty table.
- [x] T005 [P] `tests/engine/test_threat.py::test_promote_*` — User Story 3 / FR-005 / FR-006 / SC-003:
      attaches block+objective and preserves other fields; rejects re-promotion; rejects
      `imminence <= 0`.
- [x] T006 `tests/engine/test_threat.py::test_fade_*` — User Story 4 / FR-007 / SC-004: an entity whose
      `imminence` is set to `0` is excluded by `active_threats` on the next call, with its
      `threat` block still present on the entity dict.

## Phase 3: Verification

- [x] T007 `PYTHONPATH=engine python3 -m pytest tests/engine/test_threat.py -q` green.
- [x] T008 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T009 Walk quickstart.md's example by hand (or as a doctest-shaped assertion in the test file)
      to confirm it runs as written.

## Dependencies

- T001 blocks T002-T006 (nothing to test before the module exists).
- T002-T006 are independent of each other (`[P]`) — separate test functions, no shared mutable
  state.
- T007-T009 run after all of T001-T006.
