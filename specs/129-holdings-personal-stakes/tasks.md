# Tasks: Holdings: accumulated stakes

**Input**: Design documents from `/specs/129-holdings-personal-stakes/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/holding.py` with a module docstring matching `threat.py`'s style,
      and implement `flag_personal_stakes` per data-model.md's signature.

## Phase 2: Tests

- [x] T002 `tests/engine/test_holding.py::FlagPersonalStakesTests` — User Story 1 / FR-001 /
      FR-002 / FR-003 / SC-001 / SC-002: held entity flagged True, unheld flagged False, empty
      `threats` list, empty `holdings` list, entity with no `id`, order/length preserved.

## Phase 3: Verification

- [x] T003 `PYTHONPATH=engine python3 -m unittest tests.engine.test_holding -v` green.
- [x] T004 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T005 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002.
- T003-T005 run after T001-T002.
