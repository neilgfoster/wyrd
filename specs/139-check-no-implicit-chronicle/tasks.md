# Tasks: Check: no implicit current-chronicle global state

**Input**: Design documents from `/specs/139-check-no-implicit-chronicle/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Implementation

- [x] T001 Create `tools/check_no_implicit_chronicle.py` per data-model.md, matching
      `check_dangling_mechanics.py`'s CLI/exit-code conventions.

## Phase 2: Tests

- [x] T002 Create `tools/test_check_no_implicit_chronicle.py` (scratch-tree-per-test, matching
      `test_check_dangling_mechanics.py`'s convention): unjustified global flagged, justified
      ("process-local") global not flagged, immutable/populated module-level values never
      flagged, real repo tree passes clean (SC-001).

## Phase 3: Verification

- [x] T003 `python3 -m unittest discover -s tools -p 'test_check_no_implicit_chronicle.py'`
      green.
- [x] T004 `python3 tools/check_no_implicit_chronicle.py` passes clean against the real repo.
- [x] T005 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T006 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite still green (unaffected).

## Dependencies

- T001 blocks T002.
- T003-T006 run after T001-T002.
