# Tasks: Chronicle Entity Loader Layout

**Input**: Design documents from `/specs/170-chronicle-entity-loader-layout/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — spec.md's own Acceptance Criteria and Success Criteria require a regression
test exercising the nested layout (SC-001/SC-002/SC-003), and CLAUDE.md's "playtest before build"
/ "deterministic over inference" conventions treat an assertion of engine behaviour as something
to check, not claim.

**Organization**: The fix itself is one function (`_load_chronicle_entities`) shared by all three
user stories, so it lands as a single Foundational task rather than three independent
implementations — attempting to split "find nested files" from "don't crash on stray files" into
separate code changes would mean writing and re-writing the same glob twice. Each user story then
gets its own independently-runnable test task proving its specific acceptance scenarios, plus
User Story 3's own documentation task.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single project (existing engine library layout, confirmed in plan.md):
- `engine/wyrd/resolution.py` — the fix
- `tests/engine/test_resolution.py` — existing test file, extended
- `docs/design/22-state.md` — existing design doc, updated

---

## Phase 1: Setup

No setup required — existing repo, existing dependencies, existing test tooling
(`PYTHONPATH=engine python3 -m pytest`). Nothing to initialize.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The corrected loader all three user stories' tests exercise.

**⚠️ CRITICAL**: No user story test can pass until this phase is complete.

- [X] T001 In `engine/wyrd/resolution.py`, change `_load_chronicle_entities` to build its
  `setting_paths`, `overlay_paths`, `invented_paths` lists from **both** the previously-supported
  flat top-level glob (`(root / "setting").glob("*.md")`, etc. — kept unchanged, FR-004) **and** a
  new per-type-subdirectory `.yaml` walk: `(root / "setting" / "entities").glob("*/*.yaml")` for
  the setting side, `(root / "overlay").glob("*/*.yaml")` for overlay, and
  `(root / "entities").glob("*/*.yaml")` for invented entities (FR-001, FR-002; layout confirmed
  in research.md and spec.md's Clarifications). Concatenate each pair of lists (sorted) before
  passing to `entity.load_set`/the overlay loop — no change to the resolution logic that follows.
- [X] T002 **Correction during implementation**: research.md's "non-entity files resolve
  themselves" decision was wrong for the flat back-compat glob kept for FR-004 — every real
  chronicle checked has a `setting/README.md` that the *existing* flat `*.md` glob still matches
  regardless of the nested-layout addition (T003's test caught this: `entity.load()` raised
  `state.StateError` on the README, exactly the crash #440 reported). Fixed by adding
  `_looks_like_entity_file` (peeks at a candidate path's first line for the `---` frontmatter
  delimiter `state.parse_entity` requires) and a shared `_entity_paths` helper that both globs
  route through and filters by it, in `engine/wyrd/resolution.py`. A `.gitkeep` inside a type
  subdirectory still needs no guard (never matches `*.yaml`); only the flat-glob/README
  interaction needed one. research.md updated to record the corrected decision.

**Checkpoint**: `_load_chronicle_entities` now finds nested `.yaml` entities and keeps finding
flat `.md` entities. User story tests can now be written against it.

---

## Phase 3: User Story 1 - A proposal is validated against a real chronicle's entities (Priority: P1) 🎯 MVP

**Goal**: `_load_chronicle_entities` returns the full, non-empty effective entity set for a
chronicle laid out with nested per-type `.yaml` subdirectories.

**Independent Test**: Run T003 alone (after Phase 2) — it builds its own fixture chronicle and
does not depend on any other user story's test.

- [X] T003 [P] [US1] In `tests/engine/test_resolution.py`, add a test that builds a temporary
  chronicle fixture with `setting/entities/<type>/<id>.yaml`, `overlay/<type>/<id>.yaml`, and
  `entities/<type>/<id>.yaml` files (matching the confirmed nested layout — at minimum one entity
  per directory, one entity type), calls `_load_chronicle_entities`, and asserts every one of
  those entities is present in the returned dict, keyed by id (spec.md Acceptance Scenario 1).
- [X] T004 [US1] Extend the same fixture (or add a second test) so the `overlay/<type>/<id>.yaml`
  file sets `overlay_of` on an existing `setting/entities/<type>/<id>.yaml` entity and changes one
  field; assert the resolved effective entity carries the overlay's value for that field and the
  setting entity's value for every other field (spec.md Acceptance Scenario 2 — proves overlay
  resolution is unaffected by the nested layout).

**Checkpoint**: User Story 1 is independently verifiable — `_load_chronicle_entities` is proven
correct against the nested layout on its own.

---

## Phase 4: User Story 2 - A non-entity file doesn't crash the loader (Priority: P2)

**Goal**: A stray `README.md` and an empty type subdirectory's `.gitkeep` don't stop the load or
get counted as entities.

**Independent Test**: Run T005 alone (after Phase 2) — builds its own fixture, independent of
User Story 1's.

- [X] T005 [P] [US2] In `tests/engine/test_resolution.py`, add a test that builds a chronicle
  fixture with `setting/README.md` at `setting/`'s top level alongside
  `setting/entities/<type>/<id>.yaml` real entity files, calls `_load_chronicle_entities`, and
  asserts the call succeeds (no `state.StateError`) and the returned dict does not contain an
  entry for the README (spec.md Acceptance Scenario 1 under Story 2).
- [X] T006 [P] [US2] Extend the same fixture (or add a second test) with an `entities/<type>/`
  directory containing only a `.gitkeep` file and no real entity files; assert the load succeeds
  and that directory contributes zero entities (spec.md Acceptance Scenario 2 under Story 2).

**Checkpoint**: User Story 2 is independently verifiable — the loader is proven robust against
the exact incidental files real chronicles contain.

---

## Phase 5: User Story 3 - Documentation matches the actual layout (Priority: P3)

**Goal**: `docs/design/22-state.md` names the confirmed layout instead of leaving file structure
unspecified.

**Independent Test**: Read `docs/design/22-state.md` after T007 and confirm it names the
per-type-subdirectory structure and `.yaml` format without needing to read `resolution.py`.

- [X] T007 [US3] Update `docs/design/22-state.md`'s description of `setting/`, `overlay/`, and
  `entities/` to state that entity files are nested one level under a per-entity-type
  subdirectory (`setting/entities/<type>/<id>.yaml`, `overlay/<type>/<id>.yaml`,
  `entities/<type>/<id>.yaml`), rewriting the existing prose in place per this repo's "design
  documents are rewritten in place, always describing the present" convention (CLAUDE.md) — no
  changelog note, no "previously assumed flat" aside.
- [X] T008 [US3] Run `python3 tools/check_docs.py` after the T007 edit to confirm the design
  document graph is still whole (reachability, dead links, ADR index, link policy) — this
  document is already linked from README.md's hub per the existing design-doc index, so this
  should be a clean pass, not a new linking task.

**Checkpoint**: All three user stories independently satisfied.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T009 Run `PYTHONPATH=engine python3 -m pytest tests/engine/test_resolution.py -v` and
  confirm every new and existing test in the file passes (no regression to the flat-`.md`
  back-compat path, FR-004 / SC-003).
- [X] T010 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` repo-wide and
  confirm both exit clean, including under `specs/170-chronicle-entity-loader-layout/`
  (CLAUDE.md).
- [X] T011 Run the quickstart.md manual spot-check against a real chronicle
  (`wyrd-chronicle-darkfuture-rookie-op`, or an equivalent local checkout) to confirm the fix
  behaves correctly outside the unit-test fixtures — the actual reported failure this feature
  closes (issue #440).

---

## Dependencies & Execution Order

- **Phase 2 (Foundational)** blocks every user story phase — T001/T002 must land before T003-T008
  can pass.
- **User Story 1 (Phase 3)**, **User Story 2 (Phase 4)**, and **User Story 3 (Phase 5)** are
  mutually independent once Phase 2 is done — T003/T004, T005/T006, and T007/T008 touch disjoint
  files (`tests/engine/test_resolution.py` test functions vs. `docs/design/22-state.md`) and can
  proceed in any order, or in parallel across stories.
- **Phase 6 (Polish)** runs last, after every user story phase.

### Parallel example (after Phase 2 completes)

```text
T003 [P] [US1] — test_resolution.py: nested-layout full-load test
T004 [US1]     — test_resolution.py: overlay-resolution-under-nested-layout test (same file as T003, run after it)
T005 [P] [US2] — test_resolution.py: README.md non-crash test
T006 [P] [US2] — test_resolution.py: .gitkeep non-crash test (same file as T005, run after it)
T007 [US3]     — docs/design/22-state.md: layout description update
T008 [US3]     — tools/check_docs.py (run after T007)
```

T003/T005/T007 can start in parallel; T004/T006/T008 each depend only on their own story's prior
task, not on the other stories.

## Implementation Strategy

**MVP = User Story 1 alone** (T001, T002, T003, T004): this is the exact failure reported in
#440 — a real chronicle's entities being invisible to validation. User Story 2's non-crash
guarantee and User Story 3's documentation update are valuable but the engine is already correct
for the reported bug once US1's tests pass.

Suggested delivery order: Phase 2 → Phase 3 (US1, MVP) → Phase 4 (US2) → Phase 5 (US3) → Phase 6
(Polish), running the full test suite and lint/format checks (T009/T010) before opening the PR,
and the real-chronicle spot-check (T011) as final confirmation the reported issue is actually
closed.
