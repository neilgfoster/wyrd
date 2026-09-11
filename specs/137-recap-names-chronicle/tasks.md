# Tasks: Recap names its chronicle and setting

**Input**: Design documents from `/specs/137-recap-names-chronicle/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Implementation

- [x] T001 `engine/wyrd/loadtier.py`: `generate_recap` reads `chronicle`'s `name`/
      `setting.repo`, adds a "## Chronicle" section, falls back to `_RECAP_PLACEHOLDER` per
      data-model.md.

## Phase 2: Tests

- [x] T002 `tests/engine/test_loadtier.py::GenerateRecapTest` — new cases: names present,
      differing chronicles produce differing recaps, missing name/setting falls back to
      placeholder, existing cases still pass unchanged.

## Phase 3: Verification

- [x] T003 `PYTHONPATH=engine python3 -m unittest tests.engine.test_loadtier -v` green.
- [x] T004 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T005 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002.
- T003-T005 run after T001-T002.
