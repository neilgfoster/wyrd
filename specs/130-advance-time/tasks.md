# Tasks: Elapsed time and the advance-time command

**Input**: Design documents from `/specs/130-advance-time/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/advance_time.py` with a module docstring matching
      `threat.py`/`era.py`'s style, and implement `advance_calendar`,
      `expected_activation_count`, `advance_time` per data-model.md's signatures.

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_advance_time.py::AdvanceCalendarTests` — User Story 1 /
      FR-001 / SC-001: plain advance, year-boundary wrap, zero elapsed.
- [x] T003 [P] `tests/engine/test_advance_time.py::ExpectedActivationCountTests` — User Story 1
      / FR-002 / SC-002: the documented worked example (imminence 4, 5 weeks -> 2), a case
      rounding to zero, zero elapsed days.
- [x] T004 [P] `tests/engine/test_advance_time.py::AdvanceTimeTests` — User Story 2 / FR-003 /
      FR-004 / SC-003 / SC-004: effects count matches activation count exactly (including zero),
      seed reproducibility across two calls, empty threats list, multiple threats in one call.

## Phase 3: Verification

- [x] T005 `PYTHONPATH=engine python3 -m unittest tests.engine.test_advance_time -v` green.
- [x] T006 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T007 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002-T004.
- T002-T004 are independent of each other (`[P]`).
- T005-T007 run after all of T001-T004.
