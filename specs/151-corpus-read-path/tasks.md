# Tasks: Corpus-build reads extracted text from corpus/, not library/

**Input**: Design documents from `specs/151-corpus-read-path/`
**Tests**: existing test suites (`tools/test_setting_build.py`, `tools/test_setting_pass0.py`)
already carry the project's coverage convention, so this feature extends them rather than
introducing a separate test-first phase.

## Phase 1: Setup

- [x] T001 Add `corpus/` counterpart tree to `tools/fixtures/setting_build/basic/` (two `.txt`
  files mirroring `library/community/house-fear-rules.md` and `library/core/rulebook.md`, plain
  fixture prose, at `tools/fixtures/setting_build/basic/corpus/community/house-fear-rules.txt` and
  `tools/fixtures/setting_build/basic/corpus/core/rulebook.txt`)
- [x] T002 [P] Add `corpus/gazetteer.txt` fixture to
  `tools/fixtures/setting_build/world_building/corpus/gazetteer.txt`, mirroring
  `library/gazetteer.md`, keeping the word "fear" in its text (the existing
  `WorldCategoryAlwaysNoneTests` asserts `"fear"` is in `terms.json`)
- [x] T003 [P] Add `corpus/` counterpart tree to `tools/fixtures/pass0/basic/` for all five present
  records (`core/rulebook.md`, `expansions/monster-manual.md`, `community/house-fear-rules.md`,
  `scenarios/the-drowning-well.md`, `miscellany.txt`), mirrored under
  `tools/fixtures/pass0/basic/corpus/` with `.txt` suffixes
- [x] T004 [P] Create new fixture `tools/fixtures/setting_build/partial_extraction/library/` with
  two present records — one classified `core-rules` document and one classified `community`
  document (front matter as in existing fixtures) — and
  `tools/fixtures/setting_build/partial_extraction/corpus/` containing the `.txt` counterpart for
  only the first record, deliberately omitting the second's

## Phase 2: Foundational

- [x] T005 In `tools/setting_build.py`, add `corpus_text_path(setting_dir: Path, record_path: str)
  -> Path` returning `setting_dir / "corpus" / Path(record_path).with_suffix(".txt")` (data-model.md)
- [x] T006 In `tools/setting_build.py`, change `corpus_step_needed`'s signature to take a
  `current: dict[str, str]` hash map directly (drop the `present_records` parameter) and compare it
  against `cache.documents` unchanged otherwise
- [x] T007 In `tools/setting_build.py`, rewrite `run_corpus_step` to: for each present record,
  resolve `corpus_text_path`; if it exists, record its `pass0.hash_file` result into a
  `current_hashes` dict and remember the record→path mapping for later text reads; if it does not
  exist, append `record.path` to a `not_yet_extracted` list. Call `corpus_step_needed` with
  `current_hashes`. On skip, return `{"built": False, "documents": len(current_hashes),
  "skipped_reason": ..., "not_yet_extracted": sorted(not_yet_extracted)}`. On build, read text only
  from the resolved `corpus/` paths (never `library_dir / record.path`), build documents only for
  extracted records, write the four index files as before, and call
  `write_corpus_build_cache(setting_dir, setting, current_hashes)`; return `{"built": True,
  "documents": len(documents), "skipped_reason": None, "not_yet_extracted": sorted(not_yet_extracted)}`
- [x] T008 In `tools/setting_build.py`'s `_format_text`, after the existing "Corpus indexes:
  built/skipped" line, append a `"Not yet extracted: N document(s) (path, path, ...)."` line only
  when `corpus["not_yet_extracted"]` is non-empty (contracts/cli.md)

**Checkpoint**: `tools/setting_build.py` reads only from `corpus/`; `tools/setting_pass0.py` is
untouched (verify with `git diff --stat tools/setting_pass0.py` showing no changes).

## Phase 3: User Story 1 - Corpus-build step reads extracted text from corpus/ (Priority: P1)

**Goal**: Running `setting_build.py` against a setting whose `library/` holds only source
documents and whose `corpus/` holds the matching extracted text builds correct indexes from that
text, and a second no-op run still skips cleanly.

**Independent Test**: `python3 -m pytest tools/test_setting_build.py -q` after T001/T002 land.

- [x] T009 [US1] Run `python3 -m pytest tools/test_setting_build.py -q` against the fixtures from
  T001/T002 and confirm `EndToEndBuildTests`, `IdempotenceTests`, `ChangeInvalidatesCacheTests`,
  `ReportingTests`, `WorldCategoryAlwaysNoneTests` all pass unmodified against the new `corpus/`
  read path (no test-file edits needed for this story — they already assert on `summary["corpus"]`
  fields this story preserves)
- [x] T010 [US1] Run `python3 -m pytest tools/test_setting_build.py::NonPresentRecordsExcludedTests
  -q` against the T003 `corpus/` tree and confirm it still passes (this test runs `sb.run()`
  against `PASS0_FIXTURES/basic`, which now needs its own `corpus/` tree to build cleanly)

**Checkpoint**: Every pre-existing test in `tools/test_setting_build.py` passes against the new
read path with no test-body changes required — only fixtures gained files.

---

## Phase 4: User Story 2 - A record with no extracted text is reported as a gap, not a crash (Priority: P1)

**Goal**: A present record with no `corpus/` counterpart never crashes the run; it's named in
`not_yet_extracted`, and every other record still builds correctly.

**Independent Test**: A new test class run alone against the T004 `partial_extraction` fixture.

- [x] T011 [US2] Add `NotYetExtractedTests` class to `tools/test_setting_build.py`:
  `test_missing_corpus_file_is_reported_not_raised` — runs `sb.run()` against
  `_copy_fixture(FIXTURES, "partial_extraction")`, asserts no exception, asserts the un-extracted
  record's path is in `summary["corpus"]["not_yet_extracted"]`, and asserts the extracted record's
  path is in `documents.json` while the un-extracted one is not
- [x] T012 [US2] In the same class, add
  `test_extraction_appearing_later_triggers_rebuild_and_clears_the_gap` — after the first `sb.run()`,
  write the missing `.txt` file into the copied fixture's `corpus/` tree, run `sb.run()` again,
  assert `summary["corpus"]["built"] is True`, the gap list is now empty, and the newly-extracted
  record's path is in `documents.json`
- [x] T013 [US2] In the same class, add
  `test_extraction_disappearing_reverts_to_not_yet_extracted` — starting from a fully-extracted
  copy of the `basic` fixture (T001), delete one `corpus/` `.txt` file, run `sb.run()` again,
  assert that record's path is now in `not_yet_extracted` and absent from `documents.json` (not a
  stale cache hit)
- [x] T014 [US2] Add `test_text_report_names_the_gap` to `ReportingTests` in
  `tools/test_setting_build.py`: run against `partial_extraction`, assert the un-extracted record's
  path appears in `sb._format_text(summary)`'s output

**Checkpoint**: `python3 -m pytest tools/test_setting_build.py -q` green including the four new
tests; a present record with no `corpus/` file never raises `UnicodeDecodeError` or any other
exception.

---

## Phase 5: User Story 3 - Pass 0's own classification is unaffected (Priority: P2)

**Goal**: Confirm (not construct) that Pass 0 needed no change.

**Independent Test**: `python3 -m pytest tools/test_setting_pass0.py -q`.

- [x] T015 [US3] Run `python3 -m pytest tools/test_setting_pass0.py -q` unmodified and confirm
  every test still passes with zero edits to `tools/setting_pass0.py` or
  `tools/test_setting_pass0.py`
- [x] T016 [US3] `grep -n "corpus" tools/setting_pass0.py` and confirm zero matches, evidencing
  Pass 0's code path never opens or reasons about `corpus/`

**Checkpoint**: Pass 0 is provably untouched.

## Phase 6: Polish & Cross-Cutting

- [x] T017 `python3 -m ruff check tools/setting_build.py tools/test_setting_build.py` and
  `python3 -m ruff format --check tools/setting_build.py tools/test_setting_build.py`, both clean
- [x] T018 `PYTHONPATH=engine python3 -m pytest tools/test_setting_build.py tools/test_setting_pass0.py -q`
  full run, all green
- [x] T019 Update `docs/design/26-corpus-index.md` if it describes the corpus-build step's read
  path from `library/` (design docs are rewritten in place, per CLAUDE.md) — check first with
  `grep -n "library" docs/design/26-corpus-index.md` before editing; skip this task with a note if
  the document never made that claim

## Dependencies

- Phase 1 (fixtures) blocks Phase 3 and Phase 4 (both need fixture data to test against).
- Phase 2 (foundational code change) blocks Phase 3, Phase 4 (both need the new read path to
  exist before their tests can pass).
- Phase 5 has no code dependency on Phases 2-4 — it is a confirmation phase and can run any time
  after Phase 1, but is sequenced last since it is lowest priority (P2 vs P1).
- Phase 6 depends on everything above being complete.

## Parallel execution opportunities

- T002, T003, T004 (fixture creation for different directories) are parallelizable with each other
  and with T001.
- T015/T016 (Pass 0 confirmation) can run in parallel with Phase 3/4's test-writing, since Pass 0's
  code is untouched by this feature.

## Implementation strategy

**MVP = Phase 1 + Phase 2 + Phase 3 (User Story 1)**: the corpus-build step reads from `corpus/`
and existing behavior (build, skip, idempotence) is preserved. Phase 4 (User Story 2, the gap
path) is the other half of the issue's acceptance criteria and should land in the same PR — the
issue's Definition of Done requires both "reads from corpus/" and "a missing extraction is a gap,
not a crash" together, so there is no meaningful partial-delivery split here despite the priority
labels.
