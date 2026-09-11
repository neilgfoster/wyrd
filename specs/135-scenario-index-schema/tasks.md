# Tasks: Scenario index schema and deterministic selection (scenarios.json)

**Input**: Design documents from `/specs/135-scenario-index-schema/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/corpus_scenario.py` with a module docstring matching the epic's
      style, and implement `validate_scenario_record`, `scale_danger`, `check_requirements`,
      `check_helped_by`, `is_eligible_for_setting` per data-model.md's signatures.

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_corpus_scenario.py::ValidateScenarioRecordTests` — User
      Story 1 / FR-001 / FR-002 / FR-003 / SC-001: all nine scale values, all four season
      values, rejection naming the field.
- [x] T003 [P] `tests/engine/test_corpus_scenario.py::ScaleDangerTests` — User Story 2 /
      FR-004 / FR-005 / SC-002: matches adversary.danger_effective exactly, party of one still
      produces a value.
- [x] T004 [P] `tests/engine/test_corpus_scenario.py::CheckRequirementsTests` — User Story 3 /
      FR-006 / SC-003: met/unmet reported correctly, empty requirements trivially met, never
      excludes.
- [x] T005 [P] `tests/engine/test_corpus_scenario.py::CheckHelpedByTests` — User Story 3 /
      FR-007: reports met/unmet regardless, never filters.
- [x] T006 [P] `tests/engine/test_corpus_scenario.py::IsEligibleForSettingTests` — FR-008 /
      SC-004: eligible vs. ineligible by settings membership.

## Phase 3: Verification

- [x] T007 `PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_scenario -v` green.
- [x] T008 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T009 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002-T006.
- T002-T006 are independent of each other (`[P]`).
- T007-T009 run after T001-T006.
