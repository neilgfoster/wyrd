# Tasks: Chronicle intent's lethality is validated against the mortality vocabulary

## Phase 1: Implementation

- [x] T001 `engine/wyrd/state.py`: add `_LETHALITY_LEVELS`, extend `validate_chronicle` per
      data-model.md.

## Phase 2: Tests

- [x] T002 `tests/engine/test_state.py`: valid values (`low`/`standard`/`high`) pass; an
      out-of-vocabulary value raises `StateError` naming the field.

## Phase 3: Verification

- [x] T003 `PYTHONPATH=engine python3 -m unittest tests.engine.test_state -v` green.
- [x] T004 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T005 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.
