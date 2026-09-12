# Tasks: Setting build pipeline — scheduled execution and web augmentation policy

**Input**: Design documents from `specs/149-setting-pipeline-scheduling/`
**Prerequisites**: plan.md, research.md, data-model.md, quickstart.md

**Tests**: Included — `data-model.md` defines explicit validation rules (`ValueError` on three
distinct invalid shapes) that are worth locking down with unit tests, matching the sibling
`corpus_document.py`/`corpus_terms.py` modules' own test coverage.

**Organization**: Tasks are grouped by user story from `spec.md` to enable independent
implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new project infrastructure is needed — `engine/wyrd/` and `tests/` already exist
with the exact structure this feature reuses (plan.md's Project Structure).

- [X] T001 Confirm `engine/wyrd/corpus_document.py` and `tests/engine/test_corpus_document.py` (or
  equivalent sibling module) as the structural precedent to follow for module layout, docstring
  shape, and test style before writing new code.

**Checkpoint**: No blocking setup — proceed directly to Foundational.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Nothing here blocks either user story — the two stories touch disjoint deliverables
(a documentation section and a code module) and neither depends on scaffolding the other needs.
This phase is intentionally empty.

**Checkpoint**: N/A — proceed directly to User Story 1.

---

## Phase 3: User Story 1 - Deciding whether the pipeline runs unattended (Priority: P1)

**Goal**: A setting author can read this repo's design output and know, without asking anyone,
whether and how the pipeline runs on a schedule, inside which repository boundary, and which
steps it covers.

**Independent Test**: Read the extended `docs/design/26-corpus-index.md` section and confirm it
states the scheduled-execution recommendation, the workflow's repository boundary, and which
pipeline steps are included vs. excluded (per quickstart.md's validation steps 1 and 3).

### Implementation for User Story 1

- [X] T002 [US1] Extend the "Build and maintenance" section of
  `docs/design/26-corpus-index.md` with a new subsection (e.g. "Scheduled execution") stating:
  GitHub Actions' `schedule` trigger, defined and run inside the setting repository itself
  (never in this repo); which steps are covered (Pass 0's catalogue/gap-survey/idempotence pass,
  plus the four deterministic corpus indexes — `documents`, `nouns`, `terms`, `tables`); which
  step is excluded (the `scenarios` index's model call, staying on its existing lazy,
  on-first-need path) and why (research.md Decision 2); and that the constraint "copyrighted
  source material never leaves the private setting repo" is met because the workflow's runner,
  its `library/` read, and its `index/` write all stay inside that one repository. Include an
  illustrative (non-runnable-in-this-repo) `schedule:`-trigger YAML snippet as a code block,
  captioned as belonging in a `wyrd-setting-<name>` repo's own `.github/workflows/`, not this
  repo's.
  File: `docs/design/26-corpus-index.md`
- [X] T003 [US1] State the scheduled run's failure-visibility expectation (FR-008) in the same
  subsection: a scheduled run's failure (a step errors, or the workflow itself never fires) is
  surfaced through the runner's own failure reporting (e.g. GitHub Actions' run-failure
  notification/status), never silently absorbed, since no one is watching a scheduled run live.
  File: `docs/design/26-corpus-index.md`
- [X] T004 [US1] Run `python3 tools/check_docs.py` and confirm it still passes after the
  extension (reachability from `README.md` unaffected, no dead links introduced, no wikilink used
  in prose per ADR 0011).
  File: `docs/design/26-corpus-index.md` (verification only, no new file)

**Checkpoint**: User Story 1 is independently complete and verifiable — `docs/design/26-corpus-
index.md` alone answers "does my pipeline run on a schedule, and where does the workflow go?"

---

## Phase 4: User Story 2 - Knowing when a derived fact may draw on a public source (Priority: P1)

**Goal**: A setting author has an explicit, checkable rule for when a public source may
supplement a private library, and a provenance shape that lets any derived fact record which
origin it came from.

**Independent Test**: Read the public-augmentation policy and correctly classify three example
sources (a private-rulebook page, a public-domain reference work, an unclear-licence fan wiki);
build provenance records via `corpus_provenance.build_provenance_record` and confirm both valid
and invalid shapes behave per `data-model.md`'s validation rules (quickstart.md's runnable script
and stdlib unittest suite).

### Implementation for User Story 2

- [X] T005 [P] [US2] Create `engine/wyrd/corpus_provenance.py`: module docstring following the
  sibling `corpus_document.py`/`corpus_pipeline.py` style (states the no-I/O, no-fetch guarantee
  per CLAUDE.md and FR-006, cross-references `docs/design/26-corpus-index.md`'s new subsection
  and `specs/149-setting-pipeline-scheduling/data-model.md`); a closed `ORIGINS = frozenset({"library", "public"})`
  vocabulary constant, matching `AUTHORITY_TIERS`/`WORLD_BUILDING_CATEGORIES`'s own closed-
  vocabulary pattern; and `build_provenance_record(*, origin: str, reference: str | None = None) -> dict`
  implementing data-model.md's three validation rules, raising `ValueError` with a message naming
  the offending value/condition for each.
  File: `engine/wyrd/corpus_provenance.py`
- [X] T006 [P] [US2] Extend the same `docs/design/26-corpus-index.md` subsection (or an adjacent
  one, e.g. "Public augmentation") added in T002 with the public-augmentation policy from
  research.md Decision 3: a public source is in-bounds only with independently checkable
  provenance not contingent on the private library (public-domain text, openly published
  errata/SRD-type material, broadly attested common knowledge); "found on the open internet"
  alone is explicitly out of bounds. State the provenance record shape (`origin` +
  `reference`) in prose, referencing `corpus_provenance.py` as its implementation, without
  duplicating the module's own docstring verbatim (CLAUDE.md's "two documents describing one
  thing differently" fault).
  File: `docs/design/26-corpus-index.md`
- [X] T007 [US2] Create `tests/engine/test_corpus_provenance.py` covering: a valid `origin="library"`
  record with no reference; a valid `origin="public"` record with a non-empty reference; an
  invalid `origin` value raises `ValueError`; `origin="public"` with `reference=None` raises
  `ValueError`; `origin="public"` with an empty/whitespace-only `reference` raises `ValueError`;
  `origin="library"` with a non-`None` `reference` raises `ValueError`.
  File: `tests/engine/test_corpus_provenance.py`
- [X] T008 [US2] Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_provenance -v`
  and confirm all tests pass.
  File: `tests/engine/test_corpus_provenance.py` (verification only)

**Checkpoint**: User Story 2 is independently complete and verifiable — the policy is readable on
its own, and the provenance module is importable and tested on its own, with no dependency on
User Story 1's documentation edit landing first (both touch disjoint sections/files and can be
implemented in either order).

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Repo-wide hygiene this feature must not regress, per CLAUDE.md.

- [X] T009 [P] Run `python3 -m ruff check .` and `python3 -m ruff format --check .` repo-wide and
  confirm both exit clean (no findings introduced by this feature; fix any that are).
  File: repo-wide (verification only)
- [X] T010 [P] Grep the diff for setting/system vocabulary and copyrighted-source references
  (CLAUDE.md's "no setting or system names in docs/design", "nothing unpublishable may enter this
  repository") — confirm every example in the new design-doc subsection is generic.
  File: `docs/design/26-corpus-index.md` (verification only)
- [X] T011 Run the quickstart.md validation script end-to-end (the inline Python snippet under
  "Validating the provenance record module") and confirm it prints `ok`.
  File: `specs/149-setting-pipeline-scheduling/quickstart.md` (verification only)

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: No dependencies — T001 is a read-only precedent check.
- **Foundational (Phase 2)**: Empty — nothing blocks either story.
- **User Stories (Phase 3, Phase 4)**: Both are P1 and fully independent — Phase 3 touches only
  `docs/design/26-corpus-index.md`'s scheduling content, Phase 4 touches the provenance module,
  its tests, and the policy content in the same design doc (a different subsection than Phase
  3's). They may be implemented in either order or in parallel; T002 and T006 both edit
  `docs/design/26-corpus-index.md` so should not be applied as concurrent file edits even though
  they are logically independent (see Parallel Example below).
  - Within Phase 4: T005 (module) and T006 (doc policy) are parallel-safe (different files); T007
    (tests) depends on T005 existing; T008 depends on T007.
- **Polish (Phase 5)**: Depends on both user-story phases being complete.

## Parallel Example

```text
# Phase 4, once Phase 3 has landed or in a separate branch pass:
T005 [P] [US2] Create engine/wyrd/corpus_provenance.py
T006 [P] [US2] Extend docs/design/26-corpus-index.md with the public-augmentation policy
   (coordinate with T002's edit to the same file — apply sequentially if both are being made
   in the same working session, to avoid a merge conflict on the same document)

# Phase 5, after both stories land:
T009 [P] Repo-wide ruff check + format check
T010 [P] Setting-vocabulary/copyright grep over the diff
```

## Implementation Strategy

### MVP First

Both user stories are P1 and issue #102's acceptance criteria name both as required — there is no
smaller MVP than "both stories done." Suggested order: Phase 3 (User Story 1, the scheduling
design) first since it is the simpler, purely-documentation deliverable, then Phase 4 (User Story
2, provenance schema + policy), then Phase 5 polish.

### Incremental Delivery

1. Complete Phase 3 → `docs/design/26-corpus-index.md`'s scheduling subsection is readable and
   answers SC-001 on its own.
2. Complete Phase 4 → the provenance module is importable/tested and the policy subsection
   answers SC-002 on its own.
3. Complete Phase 5 → repo-wide hygiene confirmed clean; open the PR.
