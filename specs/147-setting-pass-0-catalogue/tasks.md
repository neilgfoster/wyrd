# Tasks: Setting build pipeline — Pass 0 catalogue, gap survey and idempotence

**Input**: Design documents from `/specs/147-setting-pass-0-catalogue/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/cli.md, quickstart.md

## Phase 1: Fixtures

- [ ] T001 [P] Create `tools/fixtures/pass0/basic/library/` — a small tree with one file per
      authority tier (core-rules, expansion, community, scenario) plus one unclassified file,
      using front-matter/sidecar signals per research.md's classification decision.
- [ ] T002 [P] Create `tools/fixtures/pass0/empty/library/` — an empty directory (no files),
      for the empty-library edge case and User Story 2's "everything is a gap" scenario.
- [ ] T003 [P] Create `tools/fixtures/pass0/conflicting/library/` — one core-rules and one
      community document sharing the same classified `kind` and `subject` signal, for User
      Story 4's conflict-detection scenario.
- [ ] T004 [P] Create `tools/fixtures/pass0/covers-requirements/` — a fixture whose `library/`
      documents' `provides` signals cover every setting-authoring requirement, for the "empty
      gap report" scenario (User Story 2, Acceptance Scenario 2).

## Phase 2: Core module

- [ ] T005 Create `tools/setting_pass0.py` with a module docstring in this repo's established
      style (see `tools/check_settings_catalogue.py`), implementing, per data-model.md:
      `classify_document(path, front_matter) -> (kind, authority_tier, subject, provides)`,
      `hash_file(path) -> str`, `load_catalogue(setting_dir) -> Catalogue`,
      `build_catalogue(setting_dir, previous) -> (Catalogue, processed, removed)`,
      `processing_order(catalogue) -> list[CatalogueRecord]`,
      `detect_conflicts(catalogue) -> list[ConflictRecord]`,
      `build_gap_report(catalogue) -> list[GapReportEntry]` (reading the fixed requirement table
      research.md derives from docs/design/24-authoring-a-setting.md), and
      `write_catalogue`/`write_gap_report`. Stdlib only (`hashlib`, `json`, `pathlib`).
- [ ] T006 Add the CLI entry point to `tools/setting_pass0.py` per contracts/cli.md: argument
      parsing (`<setting-dir>`, `--format json`), exit codes 0/1, the run summary, and the two
      JSON artefact writes under `<setting-dir>/index/`.

## Phase 3: Tests

- [ ] T007 [P] `tools/test_setting_pass0.py::ClassifyDocumentTests` — User Story 1 / FR-001 /
      FR-002 / FR-009: one record per file, kind+tier assigned, unclassified files get the
      `unclassified` kind at the lowest tier (spec.md Edge Cases).
- [ ] T008 [P] `tools/test_setting_pass0.py::ProcessingOrderTests` — User Story 1 / FR-003:
      every higher-authority record precedes every lower-authority record, using
      `tools/fixtures/pass0/basic/`.
- [ ] T009 [P] `tools/test_setting_pass0.py::GapReportTests` — User Story 2 / FR-004 / SC-004:
      missing bestiary-shaped material is named as a gap (`tools/fixtures/pass0/basic/`, which
      omits some requirements); `tools/fixtures/pass0/covers-requirements/` produces an empty
      gap report; `tools/fixtures/pass0/empty/` reports every requirement as a gap.
- [ ] T010 [P] `tools/test_setting_pass0.py::IdempotenceTests` — User Story 3 / FR-005 / FR-006 /
      FR-007 / SC-002 / SC-003: a second run with no changes processes zero files; changing one
      file's content reprocesses only that file and leaves every other record's hash untouched;
      adding one new file processes only that file.
- [ ] T011 [P] `tools/test_setting_pass0.py::RemovedFileTests` — User Story 3 Acceptance
      Scenario 4 / FR-011: a file removed from disk is marked `status: removed` in the
      catalogue, not deleted from it.
- [ ] T012 [P] `tools/test_setting_pass0.py::ConflictDetectionTests` — User Story 4 / FR-008 /
      SC-005: `tools/fixtures/pass0/conflicting/` produces a conflict entry naming both
      documents, and neither document's own catalogue record is mutated by the other's
      presence.
- [ ] T013 [P] `tools/test_setting_pass0.py::UnreadableFileTests` — spec.md Edge Cases / FR-010:
      an unreadable file (e.g. permission-denied, simulated via a mock or a file replaced with a
      broken symlink) is recorded with `status: unreadable`, never silently skipped.
- [ ] T014 [P] `tools/test_setting_pass0.py::CliContractTests` — contracts/cli.md: exit code 1
      for a missing `library/` directory; exit code 0 and the documented summary shape
      otherwise; `index/catalogue.json` and `index/gap_report.json` match the documented shapes.

## Phase 4: Verification

- [ ] T015 `PYTHONPATH=engine python3 -m unittest tools.test_setting_pass0 -v` green.
- [ ] T016 `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [ ] T017 `PYTHONPATH=engine python3 -m pytest tools/ tests/ -q` full suite green.
- [ ] T018 Run the quickstart.md scenarios by hand against the fixtures to confirm the CLI
      output matches contracts/cli.md.

## Dependencies

- T001-T004 (fixtures) are independent of each other (`[P]`) and block every test in Phase 3
  that references them.
- T005 blocks T006; T005-T006 block every task in Phase 3.
- T007-T014 are independent of each other (`[P]`) once T001-T006 are done.
- T015-T018 run after all of T001-T014.
