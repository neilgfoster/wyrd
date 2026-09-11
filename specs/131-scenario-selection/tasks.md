# Tasks: Scenario selection by thread heat and hooks

**Input**: Design documents from `/specs/131-scenario-selection/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/scenario_selection.py` with a module docstring matching the
      epic's style, and implement `rank_by_heat`, `select_scenario`, `scale_encounters`,
      `record_source` per data-model.md's signatures.

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_scenario_selection.py::RankByHeatTests` — FR-001: descending
      order, stable tie.
- [x] T003 [P] `tests/engine/test_scenario_selection.py::SelectScenarioTests` — User Story 1 /
      FR-002 / FR-003 / FR-004 / SC-001 / SC-002: hottest match wins, no-match candidate never
      beats a match, deterministic tie-break, `None` on no match / empty inputs.
- [x] T004 [P] `tests/engine/test_scenario_selection.py::ScaleEncountersTests` — User Story 2 /
      FR-005 / SC-003: unchanged ratio, scaled ratio, matches `adversary.scaled_count` exactly,
      empty encounters list.
- [x] T005 [P] `tests/engine/test_scenario_selection.py::RecordSourceTests` — User Story 3 /
      FR-006 / SC-004: source block attached, other fields unchanged.

## Phase 3: Verification

- [x] T006 `PYTHONPATH=engine python3 -m unittest tests.engine.test_scenario_selection -v`
      green.
- [x] T007 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T008 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002-T005.
- T002-T005 are independent of each other (`[P]`).
- T006-T008 run after all of T001-T005.
