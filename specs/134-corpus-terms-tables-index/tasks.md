# Tasks: Curated term and structural table indexes (terms.json, tables.json)

**Input**: Design documents from `/specs/134-corpus-terms-tables-index/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/corpus_terms.py` with a module docstring matching #354's style,
      and implement `CURATED_TERMS`, `build_terms_index`, `build_tables_index` per
      data-model.md's signatures.

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_corpus_terms.py::BuildTermsIndexTests` — User Story 1 /
      FR-001 / FR-002 / FR-003 / SC-001: heading-adjacent ranked definition, plain-prose ranked
      mention, non-curated word produces no entry, case-insensitive match.
- [x] T003 [P] `tests/engine/test_corpus_terms.py::BuildTablesIndexTests` — User Story 2 /
      FR-004 / FR-005 / FR-006 / SC-002 / SC-003: all four dice types (d6/d10/d66/d100), caption
      guess, single stray row-shaped line produces no table, no row-shaped lines at all.

## Phase 3: Verification

- [x] T004 `PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_terms -v` green.
- [x] T005 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T006 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002-T003.
- T002-T003 are independent of each other (`[P]`).
- T004-T006 run after T001-T003.
