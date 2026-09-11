# Tasks: world_acts_offstage gates threat activation while the character is elsewhere

## Phase 1: Implementation

- [x] T001 `engine/wyrd/advance_time.py`: `advance_time` gains `world_acts_offstage`/
      `witnessed` per data-model.md.

## Phase 2: Tests

- [x] T002 `tests/engine/test_advance_time.py::AdvanceTimeTests`: default reproduces prior
      behaviour, suppressed case zeroes every activation, calendar unaffected, witnessed=True
      overrides suppression, no roll offset consumed when suppressed (verified against a
      subsequent non-suppressed call with the same seed).

## Phase 3: Verification

- [x] T003 `PYTHONPATH=engine python3 -m unittest tests.engine.test_advance_time -v` green.
- [x] T004 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T005 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.
