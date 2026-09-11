# Tasks: Succession: successor selection and inheritance

**Input**: Design documents from `/specs/132-succession/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/succession.py` with a module docstring matching the epic's style,
      and implement `rank_candidates`, `propose_successors`, `inherit`, `record_predecessor` per
      data-model.md's signatures.

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_succession.py::RankCandidatesTests` — User Story 1 / FR-001 /
      FR-002 / SC-001: priority order, stable tie, rejects unknown entanglement.
- [x] T003 [P] `tests/engine/test_succession.py::ProposeSuccessorsTests` — User Story 1 /
      FR-003: caps at 3, returns fewer when fewer exist, empty input.
- [x] T004 [P] `tests/engine/test_succession.py::InheritTests` — User Story 2 / FR-004 / FR-005
      / FR-006 / SC-002 / SC-003: inherited fields carried, excluded fields absent, reputation
      preserved separately, holding only when explicitly passed and always encumbered.
- [x] T005 [P] `tests/engine/test_succession.py::RecordPredecessorTests` — User Story 3 /
      FR-007 / SC-004: each of the three outcomes, fact/rumour independence for `died`, rejects
      an unknown outcome.

## Phase 3: Verification

- [x] T006 `PYTHONPATH=engine python3 -m unittest tests.engine.test_succession -v` green.
- [x] T007 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T008 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002-T005.
- T002-T005 are independent of each other (`[P]`).
- T006-T008 run after all of T001-T005.
