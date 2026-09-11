# Tasks: Corpus retrieval is scoped to a setting, never unfiltered

**Input**: Design documents from `/specs/138-corpus-retrieval-setting-scoped/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Implementation

- [x] T001 `engine/wyrd/corpus_find.py`: add a required `setting` argument to all five
      functions per data-model.md; remove `find_scenario`'s `setting_in` keyword, folding it
      into `setting`.

## Phase 2: Tests

- [x] T002 `tests/engine/test_corpus_find.py`: rewrite fixtures to carry two settings each;
      update every existing test to pass `setting`; add new tests per spec.md — cross-setting
      exclusion for all five functions, `TypeError` on omitted `setting`, missing-field
      exclusion.

## Phase 3: Verification

- [x] T003 `PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_find -v` green.
- [x] T004 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T005 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002.
- T003-T005 run after T001-T002.
