# Tasks: Every seeded Threat carries a personal connection

## Phase 1: Implementation

- [x] T001 `engine/wyrd/threat.py`: add `validate_connections` per data-model.md.

## Phase 2: Tests

- [x] T002 `tests/engine/test_threat.py`: non-empty connection passes; absent/None/empty/
      whitespace-only each reported; mixed list order preserved; empty input list; Threat
      missing its own `id`.

## Phase 3: Verification

- [x] T003 `PYTHONPATH=engine python3 -m unittest tests.engine.test_threat -v` green.
- [x] T004 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T005 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.
