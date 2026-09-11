# Tasks: Corpus index retrieval queries (wyrd find)

**Input**: Design documents from `/specs/136-corpus-retrieval/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/corpus_find.py` with a module docstring matching the epic's
      style, and implement `find_noun`, `find_rule`, `find_table`, `find_scenario`, `find_doc`
      per data-model.md's signatures.

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_corpus_find.py::FindNounTests` — User Story 1 / FR-001 /
      FR-006 / SC-001 / SC-003: multi-document postings flattened, empty index, no match.
- [x] T003 [P] `tests/engine/test_corpus_find.py::FindRuleTests` — FR-002 / SC-002:
      definition-before-mention ordering, empty index.
- [x] T004 [P] `tests/engine/test_corpus_find.py::FindTableTests` — FR-003 / FR-006: dice
      filter, about substring filter (case-insensitive), None-caption never matches, empty
      index.
- [x] T005 [P] `tests/engine/test_corpus_find.py::FindScenarioTests` — FR-004 / FR-006: exact
      field match, `setting_in` membership match, empty index, no filters returns everything.
- [x] T006 [P] `tests/engine/test_corpus_find.py::FindDocTests` — FR-005 / FR-006 / SC-004:
      work/issue match, doc-only result shape (no offset), empty index.

## Phase 3: Verification

- [x] T007 `PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_find -v` green.
- [x] T008 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T009 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002-T006.
- T002-T006 are independent of each other (`[P]`).
- T007-T009 run after T001-T006.
