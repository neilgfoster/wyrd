# Tasks: Generalise corpus extraction and indexing for any setting repo

**Input**: Design documents from `/specs/148-generalise-corpus-extraction/`
**Prerequisites**: plan.md, research.md, data-model.md, quickstart.md

**Tests**: this repo has no test-optional convention for engine modules — every sibling corpus
feature (#354–#357) ships its module and its test file in the same PR, so tests are included
below, organized per user story (TDD-ish but not gated: write the function, assert it against
spec.md's own Acceptance Scenarios).

## Phase 1: Setup

- [x] T001 Create `engine/wyrd/corpus_pipeline.py` with its module docstring (issue #101,
      referencing `docs/design/26-corpus-index.md` and #354/#355, matching the docstring
      convention every sibling corpus module already uses) and the imports
      (`from wyrd import corpus_document, corpus_terms`).

## Phase 2: Foundational

- [x] T002 Define `WORLD_BUILDING_CATEGORIES = frozenset({"geography", "factions", "history",
      "daily-life"})` in `engine/wyrd/corpus_pipeline.py` (FR-003, FR-004; data-model.md).
- [x] T003 Create `tests/engine/test_corpus_pipeline.py` with its module-level imports
      (`unittest`, `from wyrd import corpus_pipeline`) and a shared helper building a minimal
      valid `PipelineDocument` dict (data-model.md) to keep individual tests short.

**Checkpoint**: module skeleton exists; user story phases can now each add functions and tests
to the same two files.

---

## Phase 3: User Story 1 - Build a whole setting's deterministic indexes in one call (P1) 🎯 MVP

**Goal**: one orchestration call over a document list returns the four merged, setting-scoped
indexes, raising on a same-setting duplicate id.

**Independent Test**: spec.md User Story 1's own Independent Test — a multi-setting document
list produces correctly-scoped indexes matching hand-merged #354/#355 output; a same-setting
duplicate id raises; an empty list returns four empty indexes.

- [x] T004 [US1] Implement `build_setting_corpus_indexes(documents: list[dict]) -> dict` in
      `engine/wyrd/corpus_pipeline.py`: for each document call
      `corpus_document.build_document_record` and `corpus_document.build_concordance`, merge
      concordances via `corpus_document.merge_concordances`, and (for now, before T008 adds the
      world-building exclusion) call `corpus_terms.build_terms_index`/`build_tables_index` for
      every document; return the `IndexBundle` shape from data-model.md.
- [x] T005 [US1] Add same-setting duplicate-id detection to `build_setting_corpus_indexes`:
      raise `ValueError` naming the offending `(setting, id)` pair when two documents in the
      list share both (FR-002); a duplicate `id` across different `setting` values is not an
      error.
- [x] T006 [P] [US1] In `tests/engine/test_corpus_pipeline.py`, add
      `TestBuildSettingCorpusIndexes` covering spec.md's Acceptance Scenarios 1–3 for User Story
      1: multi-setting scoping (records carry the right `setting`; #357's `corpus_find`-style
      scoping holds), the same-setting duplicate-id `ValueError`, a cross-setting duplicate id
      NOT raising, and an empty document list returning four empty indexes (SC-001, SC-004).

**Checkpoint**: `build_setting_corpus_indexes` is usable standalone for an all-mechanical
document set — this is the MVP slice.

---

## Phase 4: User Story 2 - World-building content stays out of the mechanical indexes (P2)

**Goal**: a document tagged with a world-building category contributes to `documents`/`nouns`
but never to `terms`/`tables`; an invalid category value is rejected.

**Independent Test**: spec.md User Story 2's own Independent Test — one world-building-tagged
document and one untagged document, both containing text that would trip the terms/tables
detectors; only the untagged one contributes postings to `terms`/`tables`.

- [x] T007 [US2] Extend `build_setting_corpus_indexes` (from T004) to read each document's
      optional `world_category`: validate it against `WORLD_BUILDING_CATEGORIES` (T002), raising
      `ValueError` naming the offending value when set but not in the closed vocabulary (FR-004).
- [x] T008 [US2] Extend `build_setting_corpus_indexes` so a document carrying a valid
      `world_category` is skipped by the `corpus_terms.build_terms_index`/`build_tables_index`
      calls added in T004, while still going through `build_document_record`/`build_concordance`
      unchanged (FR-003).
- [x] T009 [P] [US2] In `tests/engine/test_corpus_pipeline.py`, add
      `TestWorldBuildingRouting` covering spec.md's Acceptance Scenarios 1–3 for User Story 2:
      a world-building document with term/table-shaped text contributing zero `terms`/`tables`
      postings but full `documents`/`nouns` entries (SC-002); an untagged document indexed by
      all four builders exactly as #354/#355 do per-document; an invalid `world_category` value
      raising `ValueError`.

**Checkpoint**: `build_setting_corpus_indexes` now fully implements FR-001 through FR-004; User
Stories 1 and 2 are both independently verifiable via the test file.

---

## Phase 5: User Story 3 - The thematic (arcs/scenario) index is generated lazily and cached (P3)

**Goal**: a pure, deterministic cache-freshness rule plus an orchestration function that calls
an injected generator only for stale/missing documents.

**Independent Test**: spec.md User Story 3's own Independent Test — a cache with one fresh, one
hash-stale, one schema-stale, and one missing entry; the injected generator is called for
exactly the three non-fresh documents.

- [x] T010 [US3] Implement `scenario_cache_status(doc_id: str, setting: str, content_hash: str,
      schema_version, cache: dict) -> str` in `engine/wyrd/corpus_pipeline.py`, returning
      `"missing"` when no entry exists for `(setting, doc_id)`, `"stale"` when the entry's
      `content_hash` or `schema_version` differs from the arguments given, and `"fresh"`
      otherwise (FR-005; data-model.md).
- [x] T011 [US3] Implement `documents_needing_scenario_generation(documents: list[dict], cache:
      dict) -> list[dict]` in `engine/wyrd/corpus_pipeline.py`, filtering `documents` (each
      carrying `id`, `setting`, `content_hash`) to those whose `scenario_cache_status` (T010) is
      not `"fresh"` for the given `schema_version` (FR-005).
- [x] T012 [US3] Implement `build_scenario_index(documents: list[dict], cache: dict, generate,
      schema_version) -> tuple[list[dict], dict]` in `engine/wyrd/corpus_pipeline.py`: call
      `generate(document)` only for documents from T011's filter, merge each result into a new
      cache entry keyed by `(setting, doc_id)` with the given `content_hash`/`schema_version`,
      reuse the cached `record` unchanged for every fresh document, and return `(records,
      updated_cache)` without mutating the `cache` argument in place. A `generate` exception for
      one document must not discard cache entries already computed earlier in the same call
      (Edge Cases) — reraise after the entries computed so far are preserved in the returned
      cache, or use a per-document try/collect pattern; either way the partial-progress
      guarantee is the requirement, not a specific control-flow shape.
- [x] T013 [P] [US3] In `tests/engine/test_corpus_pipeline.py`, add
      `TestScenarioCache` covering spec.md's Acceptance Scenarios 1–4 for User Story 3 (missing
      → generated and cached; fresh → generator not called; content-hash-stale → regenerated;
      schema-version-stale → regenerated even with an unchanged hash), SC-003's exact-call-count
      assertion across all four cases in one fixture, and the Edge Cases generator-exception
      partial-progress case.

**Checkpoint**: all three user stories are implemented and independently tested; FR-001 through
FR-008 are all covered.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T014 [P] Update `docs/design/26-corpus-index.md` in place (CLAUDE.md: design docs are
      rewritten in place, never appended-to) to document: (a) that the four deterministic
      indexes are now built across a whole document set by
      `wyrd.corpus_pipeline.build_setting_corpus_indexes`, not only per-document; (b) the
      world-building-category boundary (`WORLD_BUILDING_CATEGORIES`) and that world-building
      documents are still catalogued and concordance-findable, reconciling the existing "What is
      not indexed" section's prose-setting-material framing with this feature's actual
      mechanism; (c) the scenario/arcs index's lazy-cache mechanism now has a concrete, tested
      shape (`scenario_cache_status`/`build_scenario_index`) implementing the "lazy... cached...
      regenerated only when the schema changes" rule already stated there.
- [x] T015 Run `PYTHONPATH=engine python3 -m unittest discover -s tests -v` from the repo root
      and confirm every existing and new test passes.
- [x] T016 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` from the repo
      root and confirm both report clean repo-wide (CLAUDE.md's standing requirement).
- [x] T017 Re-read `specs/148-generalise-corpus-extraction/spec.md`'s Functional Requirements
      and Success Criteria against the finished `engine/wyrd/corpus_pipeline.py` and
      `tests/engine/test_corpus_pipeline.py`, confirming every FR-00x and SC-00x is satisfied and
      covered by name.

## Dependencies & Execution Order

- **Setup (Phase 1)** → **Foundational (Phase 2)**: no dependencies, sequential (both touch the
  same new files).
- **User Story 1 (Phase 3)**: depends on Phase 2 only. This is the MVP slice.
- **User Story 2 (Phase 4)**: depends on Phase 3 (extends the same `build_setting_corpus_indexes`
  function T004 introduced) — not independently implementable before US1's core function exists,
  though it is independently *testable* once both land (spec.md's own Independent Test for US2).
- **User Story 3 (Phase 5)**: depends on Phase 2 only (`scenario_cache_status` and friends are a
  separate function family from `build_setting_corpus_indexes`) — could be implemented in
  parallel with Phases 3–4 by a second author, but is sequenced after them here since one file
  (`corpus_pipeline.py`) is being edited throughout.
- **Polish (Phase 6)**: depends on Phases 3–5 all being complete.

## Parallel Execution Examples

- T006, T009, and T013 (the three test-writing tasks) each touch only
  `tests/engine/test_corpus_pipeline.py` in a different `TestCase` class — they can be written in
  any order relative to each other once their corresponding implementation tasks land, but not
  concurrently with each other in the same file without care over merge conflicts in one file.
- T014 (docs update) is independent of T015–T017 (verification) and can be done in parallel with
  them.

## Implementation Strategy

**MVP first**: Phase 3 (User Story 1) alone is a usable, testable slice — an all-mechanical
document set can already be indexed correctly. Phases 4 and 5 each add one more of issue #101's
acceptance criteria (world-building distinction; lazy-cached thematic index) without touching
Phase 3's own behaviour for documents that don't use the new optional fields.
