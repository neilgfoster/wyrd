# Tasks: Corpus excerpt retrieval — a bounded read at a doc+offset

**Input**: Design documents from `specs/152-corpus-excerpt-retrieval/`
**Tests**: stdlib `unittest`, new `tests/engine/test_corpus_excerpt.py`, matching
`tests/engine/test_corpus_find.py`'s existing style (`docs/design/27-tooling.md` section 6).

## Phase 1: Setup

- [x] T001 Create `tests/engine/fixtures/corpus_excerpt/` with a small real-shaped corpus tree:
  `setting-dir/corpus/doc-a.txt` (a few hundred characters of prose, with a known phrase at a
  known offset) and `setting-dir/corpus/nested/doc-b.txt` (to exercise a nested `path`).

## Phase 2: Foundational

- [x] T002 Create `engine/wyrd/corpus_excerpt.py` with module docstring explaining why this is a
  separate, I/O-performing module from `corpus_find.py` (research.md's decision), and a
  `_corpus_text_path(setting_dir: Path, record_path: str) -> Path` helper reimplementing
  `tools/setting_build.py`'s `corpus_text_path` rule (`setting_dir / "corpus" /
  Path(record_path).with_suffix(".txt")`) — reimplemented rather than imported, since `engine/`
  never imports from `tools/` (research.md, grep-verified).
- [x] T003 In `corpus_excerpt.py`, implement `read_excerpt(documents_index, setting, setting_dir,
  doc, offset, window=400)`: find the matching record (`id == doc and setting == setting`) in
  `documents_index`; if none, return `None`. Resolve its corpus text path via `_corpus_text_path`;
  if the file does not exist, return `None`. Read its text; if `offset < 0` or `offset >=
  len(text)`, return `None`. Otherwise return `text[max(0, offset - window):offset + window]`
  (data-model.md).

**Checkpoint**: `corpus_excerpt.py` exists, importable, no dependency on `tools/` or
`corpus_find.py`.

## Phase 3: User Story 1 - A query result carries its own excerpt (Priority: P1)

**Goal**: Given real `documents.json` shape and corpus text, `read_excerpt` returns the correct
surrounding passage, deterministically, and never resolves across settings.

**Independent Test**: `PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_excerpt -v`

- [x] T004 [US1] In `tests/engine/test_corpus_excerpt.py`, test: a known doc+offset returns text
  containing the expected phrase from T001's fixture.
- [x] T005 [US1] [P] In the same file, test: calling `read_excerpt` twice with identical arguments
  returns identical strings (determinism, FR-005).
- [x] T006 [US1] [P] In the same file, test: a record that exists but belongs to a different
  `setting` than the one requested returns `None` (FR-002, mirrors `test_corpus_find.py`'s
  `test_other_setting_never_returned` pattern).
- [x] T007 [US1] [P] Against a real setting fixture (skip gracefully if not present — see note
  below), verify `read_excerpt` against `wyrd-setting-titan`'s or `wyrd-setting-darkfuture`'s real
  `index/documents.json` and `corpus/` returns text containing an expected known phrase (SC-001) —
  guarded with a fixture-path existence check so this test is skipped, not failed, in an
  environment without a sibling setting checkout.

**Checkpoint**: User Story 1 fully tested and passing in isolation.

## Phase 4: User Story 2 - Out-of-bounds requests are quiet, never a crash (Priority: P1)

**Goal**: Every named failure mode returns `None`, never raises.

**Independent Test**: same test file, run together with Phase 3 (shares the module).

- [x] T008 [US2] Test: unknown `doc` id returns `None`, no exception (FR-004).
- [x] T009 [US2] [P] Test: `offset >= len(text)` for a real document returns `None` (FR-004).
- [x] T010 [US2] [P] Test: negative `offset` returns `None` (FR-004, Edge Cases).
- [x] T011 [US2] [P] Test: a `documents.json` record whose corpus text file is missing on disk
  returns `None` rather than raising `FileNotFoundError` (FR-004, Edge Cases).
- [x] T012 [US2] [P] Test: `offset=0` is treated as a valid start-of-document offset, not as
  falsy/missing (Edge Cases) — returns the first `window` characters, not `None`.
- [x] T013 [US2] [P] Test: `window=0` returns a valid (possibly empty) string, not `None` and not
  a raised error (Edge Cases).

**Checkpoint**: every FR-004 failure mode covered; `corpus_excerpt.py`'s contract matches
`corpus_find.py`'s existing "never raise on an unmatched/malformed query" convention.

## Phase 5: User Story 3 - `wyrd find` carries the excerpt (Priority: P2)

**Goal**: A `wyrd find noun|rule|table` CLI call returns results that already include a resolved
excerpt alongside `doc`/`offset`.

**Independent Test**: `quickstart.md`'s step 3 (a real `wyrd find noun` call against
`wyrd-setting-titan`).

- [x] T014 [US3] In `engine/wyrd/client.py`, add a `find` subparser with `noun`/`rule`/`table`
  sub-shapes per `contracts/find-verb.md` (`--setting` required on all three; `--name`/`--term`
  required on `noun`/`rule` respectively; `--dice`/`--about` optional on `table`).
- [x] T015 [US3] In `client.py`, add `_run_find_noun`/`_run_find_rule`/`_run_find_table`: load
  `nouns.json`/`terms.json`/`tables.json` and `documents.json` from the setting directory (the
  current working directory, matching `wyrd find`'s intended invocation from inside a setting
  repo per `quickstart.md`), call the matching `corpus_find` function, then extend each
  `doc`/`offset`-bearing result with `"excerpt": read_excerpt(...)` (or `None` on failure — the
  coordinate lookup and excerpt resolution are independent per `contracts/find-verb.md`'s Error
  behavior).
- [x] T016 [US3] Wire the three new `_run_find_*` functions into `main()`'s verb dispatch, matching
  the existing `elif args.verb == "..."` pattern.
- [x] T017 [US3] [P] Add `tests/engine/test_client_find.py` (or extend an existing client test
  file if one already covers verb dispatch) covering: a `find noun` call returns a result with a
  non-null `excerpt`; a `find` call against an unknown setting/no matches returns
  `{"results": []}`; a result whose excerpt can't resolve still appears with `"excerpt": None`
  rather than being dropped (contracts/find-verb.md).

**Checkpoint**: `wyrd find` is callable end-to-end; `quickstart.md`'s step 3 passes against a real
setting checkout.

## Phase 6: Polish

- [x] T018 [P] Run `ruff check .` and `ruff format --check .` repo-wide; fix anything flagged
  (CLAUDE.md — must stay clean, including this feature's own new files).
- [x] T019 [P] Update `docs/design/26-corpus-index.md`'s "Retrieval" section to note the excerpt
  step is now implemented (rewrite-in-place per CLAUDE.md's design-document convention — no
  changelog note, just describe the present state) and add the `wyrd find` command shape actually
  shipped if it differs from the section's current illustrative examples.
- [x] T020 Run `PYTHONPATH=engine python3 -m unittest discover tests/engine -v` and
  `python3 -m unittest discover tools -v` (or repo's full test invocation) to confirm nothing
  else broke.

## Dependencies

- Phase 1 (T001) blocks Phase 2 (T002-T003 need the fixture).
- Phase 2 (T002-T003) blocks every later phase — `read_excerpt` must exist before it can be
  tested or wired into the CLI.
- Phase 3 and Phase 4 both extend `test_corpus_excerpt.py` and can proceed in any order once
  Phase 2 lands; tasks marked `[P]` within a phase are independent of each other.
- Phase 5 depends on Phase 2 (needs `read_excerpt`) but not on Phase 3/4 passing first, though
  landing them first is safer.
- Phase 6 runs last, after every user story's tests pass.

## Parallel execution notes

T005/T006/T007 (Phase 3) and T009-T013 (Phase 4) are independent test cases in the same file —
safe to write in any order, `[P]`-marked. T002/T003 (Phase 2) touch the same file sequentially
(T003 depends on T002 existing) and are not parallel despite being adjacent. T018/T019 (Phase 6)
touch unrelated files and are parallel.
