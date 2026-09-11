# Tasks: Eras: named periods and boundary recording

**Input**: Design documents from `/specs/128-eras-boundary-recording/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Schema and module

- [x] T001 Extend `engine/wyrd/state.py`'s `default_chronicle_state`/`validate_chronicle` with
      `eras: []` and `era_crossings: []`, filled the same way `migrations`/`intent` already are.
- [x] T002 Create `engine/wyrd/era.py` with a module docstring matching `chronicle.py`'s style,
      and implement `ambient_register`, `cross_era` per data-model.md's signatures.

## Phase 2: Tests

- [x] T003 [P] `tests/engine/test_state.py` — new test(s) confirming `eras`/`era_crossings`
      default to `[]` and round-trip through `validate_chronicle` unchanged when supplied.
- [x] T004 [P] `tests/engine/test_era.py::AmbientRegisterTests` — User Story 1 / FR-001 / FR-002 /
      SC-001: correct lookup, `era is None`, empty `eras` list.
- [x] T005 [P] `tests/engine/test_era.py::CrossEraTests` — User Story 2 / FR-003 / FR-004 /
      FR-005 / FR-006 / SC-002 / SC-003: first crossing from `null`, a later crossing, undeclared
      target rejected, no-op target rejected.

## Phase 3: Verification

- [x] T006 `PYTHONPATH=engine python3 -m unittest tests.engine.test_era tests.engine.test_state -v`
      green.
- [x] T007 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T008 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T003 and T005 (state.py fields must exist first for the round-trip test, and
  T002/era.py needs no state.py field to exist to be written, but T005's crossing test benefits
  from the same schema existing conceptually — no hard code dependency, ordered for clarity).
- T002 blocks T004 and T005.
- T006-T008 run after all of T001-T005.
