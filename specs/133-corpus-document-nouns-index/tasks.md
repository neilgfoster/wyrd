# Tasks: Bibliographic and concordance indexes (documents.json, nouns.json)

**Input**: Design documents from `/specs/133-corpus-document-nouns-index/`
**Prerequisites**: plan.md, data-model.md, quickstart.md

## Phase 1: Module

- [x] T001 Create `engine/wyrd/corpus_document.py` with a module docstring matching the epic's
      style, and implement `ocr_confidence`, `build_document_record`, `build_concordance`,
      `merge_concordances` per data-model.md's signatures.

## Phase 2: Tests

- [x] T002 [P] `tests/engine/test_corpus_document.py::OcrConfidenceTests` — User Story 1 /
      FR-002 / SC-001: well-formed vs. garbled comparison, empty text.
- [x] T003 [P] `tests/engine/test_corpus_document.py::BuildDocumentRecordTests` — User Story 1 /
      FR-001 / FR-006: all fields carried, setting present.
- [x] T004 [P] `tests/engine/test_corpus_document.py::BuildConcordanceTests` — User Story 2 /
      FR-003 / FR-004 / FR-005 / FR-006 / SC-002: mid-sentence noun recorded with offsets,
      sentence-initial excluded, stop-listed word excluded regardless of position, setting
      present on entries.
- [x] T005 [P] `tests/engine/test_corpus_document.py::MergeConcordancesTests` — SC-003: two
      documents' postings kept separate, never summed into one entry.

## Phase 3: Verification

- [x] T006 `PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_document -v` green.
- [x] T007 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] T008 `PYTHONPATH=engine python3 -m pytest tests/ -q` full suite green.

## Dependencies

- T001 blocks T002-T005.
- T002-T005 are independent of each other (`[P]`).
- T006-T008 run after all of T001-T005.
