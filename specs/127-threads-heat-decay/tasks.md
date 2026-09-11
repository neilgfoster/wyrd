# Tasks: Threads: open-loop tracking, heat and decay

**Input**: Design documents from `/specs/127-threads-heat-decay/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/thread.py` with a module docstring matching `threat.py`/`journey.py`'s
      style, and implement `new_thread`, `touch`, `decay` per data-model.md's signatures.

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_thread.py::NewThreadTests` — User Story 1 / FR-001 / FR-002 /
      FR-003 / SC-001: all fields carried, default heat 0, rejects out-of-range heat.
- [x] T003 [P] `tests/engine/test_thread.py::TouchTests` — User Story 2 / FR-004 / SC-002: rises
      by one at each value 0-5, caps at 5.
- [x] T004 [P] `tests/engine/test_thread.py::DecayTests` — User Story 3 / FR-005 / FR-006 /
      FR-007 / SC-003 / SC-004: one year drops by one, partial year no-op, multi-year span drops
      by full count, closes with reason once already at floor.

## Phase 3: Verification

- [x] T005 `PYTHONPATH=engine python3 -m unittest tests.engine.test_thread -v` green.
- [x] T006 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T007 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002-T004.
- T002-T004 are independent of each other (`[P]`).
- T005-T007 run after all of T001-T004.
