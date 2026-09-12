# Tasks: Setting Build Command

**Input**: Design documents from `/specs/150-setting-build-command/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/cli.md, quickstart.md

## Phase 1: Fixtures

- [x] T001 [P] Create `tools/fixtures/setting_build/basic/library/` — a small tree (2-3 files
      across a couple of authority tiers, reusing `tools/fixtures/pass0/basic/`'s front-matter
      style) sized for exercising the combined build end to end.
- [x] T002 [P] Create `tools/fixtures/setting_build/world_building/library/` — one document
      containing a curated term (e.g. "fear") near a heading, standing in for prose world-building
      material. Used to confirm this command's documented `world_category=None` simplification
      (spec.md Edge Cases): the document still ends up in `terms.json`, since Pass 0's catalogue
      carries no `world_category` signal for this feature to pass through today.

## Phase 2: Core module

- [x] T003 Create `tools/setting_build.py` with a module docstring in this repo's established
      `tools/` style (see `tools/setting_pass0.py`), importing `setting_pass0` and
      `wyrd.corpus_pipeline`/`wyrd.corpus_document` unmodified (research.md's entry-point
      decision). Implement `build_corpus_document(record: setting_pass0.CatalogueRecord, text:
      str, setting: str) -> dict` per research.md's document-dict construction decision.
- [x] T004 Implement `load_corpus_build_cache(setting_dir) -> dict` and
      `write_corpus_build_cache(setting_dir, setting: str, documents: dict[str, str]) -> None`
      per data-model.md's `index/corpus_build_cache.json` shape.
- [x] T005 Implement `corpus_step_needed(catalogue, cache) -> bool` per research.md's idempotence
      decision: compares the current present-record `(path, content_hash)` set (and setting name)
      against the cache; returns `False` only on an exact match.
- [x] T006 Implement `run_corpus_step(setting_dir, catalogue) -> dict` — reads each present
      record's `library/<path>` text, builds the document list via `build_corpus_document`, calls
      `corpus_pipeline.build_setting_corpus_indexes`, writes `index/documents.json`,
      `index/nouns.json`, `index/terms.json`, `index/tables.json`, and rewrites the build cache;
      returns the `corpus` report sub-object (`built`, `documents`, `skipped_reason`) per
      data-model.md. On a `ValueError` from `build_setting_corpus_indexes`, propagate it after
      confirming no output file was written for this run (FR-012).
- [x] T007 Implement `run(setting_dir) -> dict` — calls `setting_pass0.run(setting_dir)`
      unmodified, then `corpus_step_needed`/`run_corpus_step` (or a skip with
      `skipped_reason`), and returns the combined report shape from data-model.md.
- [x] T008 Add the CLI entry point to `tools/setting_build.py` per contracts/cli.md: argument
      parsing (`<setting-dir>`, `--format json`), exit codes 0/1, the combined text/JSON report.

## Phase 3: Tests

- [x] T009 [P] `tools/test_setting_build.py::BuildCorpusDocumentTests` — FR-003: a present
      catalogue record plus its file text produces a document dict carrying every field
      `build_setting_corpus_indexes` requires, with `document_type` from the record's `kind` and
      `world_category` always `None` (spec.md's documented `CatalogueRecord`-has-no-
      `world_category` simplification).
- [x] T010 [P] `tools/test_setting_build.py::EndToEndBuildTests` — User Story 1 / FR-001 / FR-004:
      running the command against `tools/fixtures/setting_build/basic/` produces
      `index/catalogue.json`, `index/gap_report.json`, `index/documents.json`,
      `index/nouns.json`, `index/terms.json`, `index/tables.json`, `index/corpus_build_cache.json`,
      each `documents.json` entry corresponding to a present catalogue record.
- [x] T011 `tools/test_setting_build.py::IdempotenceTests` — User Story 2 / FR-005 / FR-006 /
      SC-002, run against a copied fixture: run the command twice; assert the second run's report
      shows zero processed Pass-0 documents and `corpus.built == False`; assert every file under
      `index/` is byte-identical before and after the second run. This is the feature's own
      Definition-of-Done test (epic #28) — run it literally, not as an inferred property.
- [x] T012 [P] `tools/test_setting_build.py::ChangeInvalidatesCacheTests` — FR-006: after the
      first run, modify one library file's content and rerun; assert the corpus step rebuilds
      (`corpus.built == True`) and the cache reflects the new hash; a second rerun after that is a
      no-op again.
- [x] T013 [P] `tools/test_setting_build.py::ReportingTests` — User Story 3 / FR-007 / FR-008:
      text-format output names both processed and skipped documents/steps with a reason;
      `--format json` output carries the same distinction in the shape data-model.md documents.
- [x] T014 [P] `tools/test_setting_build.py::WorldCategoryAlwaysNoneTests` — Edge Cases: a
      document from `tools/fixtures/setting_build/world_building/` still contributes to
      `terms.json`/`tables.json` (not excluded), confirming this command always passes
      `world_category=None` today — the documented simplification, not a bug.
- [x] T015 [P] `tools/test_setting_build.py::CorpusPipelineErrorPropagationTests` — Edge Cases /
      FR-012: since a present catalogue record's `id` is always its (unique) path, a genuine
      duplicate-`(setting, id)` collision cannot arise from this command's own document
      construction -- so this test injects a `build_setting_corpus_indexes` failure (patching it
      to raise `ValueError`, per research.md) and asserts `run`/`main` propagates a clear error,
      exits 1, and writes no corpus index file for that run.
- [x] T016 [P] `tools/test_setting_build.py::NoLibraryDirTests` — Edge Cases: a directory with no
      `library/` subdirectory exits 1 with a clear error, identical to
      `tools/setting_pass0.py`'s own behavior, without attempting the corpus step.
- [x] T017 [P] `tools/test_setting_build.py::NonPresentRecordsExcludedTests` — Edge Cases: a
      removed or unreadable catalogue record is excluded from the corpus-index document list
      (never attempted as a text read).

## Phase 4: Polish

- [x] T018 Run `python3 -m ruff check tools/setting_build.py tools/test_setting_build.py` and
      `python3 -m ruff format --check tools/setting_build.py tools/test_setting_build.py`; fix
      any findings.
- [x] T019 Run `PYTHONPATH=engine python3 -m pytest tools/test_setting_build.py -q` and the full
      repo-wide `PYTHONPATH=engine python3 -m pytest -q`; confirm no regression.
- [x] T020 Update `docs/design/26-corpus-index.md`'s "Scheduled execution" illustrative workflow
      snippet to reference `tools/setting_build.py` as the single combined step, in place of the
      two separate illustrative lines it currently shows (keeping it explicitly "illustrative
      only", unchanged in every other respect) — closes the loop this feature's own issue #388
      names between the design doc's own scheduling section and the command it describes.

## Dependencies

- T001-T002 (fixtures) before T009-T017 (tests that use them).
- T003 before T004-T008 (module scaffolding before the functions built on it).
- T004-T005 before T006 (cache read/decide before the step that uses them).
- T006-T007 before T008 (core logic before the CLI wrapper).
- T003-T008 before T009-T017 (implementation before tests exercising it).
- T009-T017 before T018-T020 (tests green before polish/lint/docs pass).

## Parallel execution guidance

Tasks marked `[P]` touch disjoint files (distinct fixture directories, or independent test
classes appended to the same new test file only after T003-T008 land) and may be batched; T011
(the idempotence test) is not marked `[P]` since it is this feature's own defining acceptance
test and is worth running in isolation to read its failure clearly if it ever fails.
