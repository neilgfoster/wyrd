# Tasks: Beat/arc entry and exit conditions, and thread-matched selection

**Input**: Design documents from `/specs/120-arc-beat-selection/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, quickstart.md

**Tests**: Included — this repo's convention (`docs/design/27-tooling.md` §6, and every prior
`engine/wyrd/*` feature) pairs each module with a stdlib `unittest` test file.

**Organization**: Tasks are grouped by user story from spec.md to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)

## Path Conventions

Single-project layout: `engine/wyrd/`, `tests/engine/`.

---

## Phase 1: Setup

- [ ] T001 Create `engine/wyrd/arc_selection.py` with the module docstring (per plan.md's
      Summary/Technical Context) and imports (`from wyrd import entity`), no logic yet.
- [ ] T002 Create `tests/engine/test_arc_selection.py` with the `unittest.TestCase` skeleton,
      following `tests/engine/test_entity.py`'s existing structure and imports.

## Phase 2: Foundational (blocking prerequisites)

- [ ] T003 In `engine/wyrd/arc_selection.py`, define the entry/exit shape constants
      (`_ENTRY_LIST_FIELDS = ("requires_threads", "requires_state", "hooks")`,
      `_EXIT_LIST_FIELDS = ("changes",)`) per data-model.md's Entry/Exit block tables.

**Checkpoint**: Module exists and is importable; no user story depends on anything beyond this.

---

## Phase 3: User Story 1 - A beat or arc declares what it needs and leaves behind (Priority: P1)

**Goal**: Validate an optional `entry`/`exit` block on any arc or beat, per data-model.md's
Validation rules.

**Independent Test**: Construct an arc and a beat each carrying a full `entry`/`exit` block and
confirm both validate; corrupt one required sub-field at a time and confirm rejection.

- [ ] T004 [P] [US1] Write `test_entry_exit_valid_block_accepted`,
      `test_entry_exit_absent_accepted`, and per-field rejection tests (bad `requires_threads`
      type, bad `emits_threads` entry missing `tag`, bad `leads_to` type) in
      `tests/engine/test_arc_selection.py`.
- [ ] T005 [US1] Implement `validate_entry_exit(frontmatter: dict) -> dict` in
      `engine/wyrd/arc_selection.py`: checks `entry.requires_threads`/`requires_state`/`hooks`
      are lists when present (FR-001), `exit.emits_threads` is a list of `{tag, if?}` mappings
      with `tag` required (FR-002), `exit.changes` is a list of strings, `exit.leads_to` is a
      string when present; returns `entity.validate`-shaped `{"valid": True}` /
      `{"valid": False, "error": "..."}`. Absent `entry`/`exit` always validates (FR-003).
- [ ] T006 [US1] Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_arc_selection -v`
      and confirm T004's tests pass.

**Checkpoint**: User Story 1 independently functional — entry/exit blocks validate correctly.

---

## Phase 4: User Story 2 - The engine picks the next beat by matching live threads (Priority: P1)

**Goal**: A selection function returning every candidate whose `entry.requires_threads` is a
subset of a caller-supplied live-thread set.

**Independent Test**: Build a small pool of candidates with varied `requires_threads`, run
selection against a chosen live-thread set, and confirm exactly the satisfied candidates return.

- [ ] T007 [P] [US2] Write `test_select_returns_matching_candidates`,
      `test_select_empty_requires_threads_always_eligible`, and
      `test_select_partial_match_excluded` in `tests/engine/test_arc_selection.py`.
- [ ] T008 [US2] Implement `_thread_match(frontmatter: dict, live_threads: set[str]) -> bool` in
      `engine/wyrd/arc_selection.py`: `entry.requires_threads` (or `[]` if absent) must be a
      subset of `live_threads` (FR-004, FR-005).
- [ ] T009 [US2] Implement `select(live_threads, candidates, *, current=None) -> list[dict]` in
      `engine/wyrd/arc_selection.py`, thread-match branch only for now: return every candidate in
      `candidates` for which `_thread_match` is true (FR-004). (The `leads_to` fallback and
      `current` parameter are completed in US3.)
- [ ] T010 [US2] Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_arc_selection -v`
      and confirm T007's tests pass.

**Checkpoint**: User Stories 1 AND 2 independently functional.

---

## Phase 5: User Story 3 - `leads_to` is a fallback, never an equal-weight candidate source (Priority: P1)

**Goal**: When no thread match exists, fall back to `current`'s `exit.leads_to`; when a thread
match exists, never consult `leads_to` at all.

**Independent Test**: Construct a case where both a `leads_to` target and a thread-matched
candidate exist and confirm the thread match wins; remove the thread match and confirm the
`leads_to` target returns; remove both and confirm an empty result (no exception).

- [ ] T011 [P] [US3] Write `test_select_thread_match_wins_over_leads_to`,
      `test_select_falls_back_to_leads_to`, `test_select_no_match_returns_empty`, and
      `test_select_dangling_leads_to_returns_empty` in `tests/engine/test_arc_selection.py`.
- [ ] T012 [US3] Extend `select()` in `engine/wyrd/arc_selection.py`: when the thread-match branch
      (T009) returns no candidates, resolve `current["exit"]["leads_to"]` via
      `entity.resolve_wikilink`, look it up by `id` in `candidates`, and return `[that entity]` if
      found, else `[]` (FR-006, FR-007, FR-008). Never evaluate `leads_to` when a thread match
      already exists.
- [ ] T013 [US3] Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_arc_selection -v`
      and confirm T011's tests pass.

**Checkpoint**: User Stories 1, 2 AND 3 independently functional — this is the feature's core
selection behavior end to end.

---

## Phase 6: User Story 4 - Selection works at every nesting level, including an undecomposed stub (Priority: P2)

**Goal**: Confirm (and, if needed, adjust) that `select()` treats a `status: stub` candidate
exactly like any other — evaluated on its own `entry` block, never required to have children —
and never itself descends into a selected result's children.

**Independent Test**: Include an arc still at `status: stub` in the candidate pool alongside
decomposed arcs/beats and confirm it is selected on the same footing.

- [ ] T014 [P] [US4] Write `test_select_stub_arc_selectable_without_children` and
      `test_select_does_not_descend_into_children` in `tests/engine/test_arc_selection.py`.
- [ ] T015 [US4] Verify `select()` needs no code change for T014 (it already operates on the flat
      `candidates` list passed in, never reading `entity.children_of`); if T014 reveals a gap
      (e.g. an accidental dependency on a `children` field), fix it in
      `engine/wyrd/arc_selection.py`.
- [ ] T016 [US4] Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_arc_selection -v`
      and confirm T014's tests pass.

**Checkpoint**: All four user stories independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [ ] T017 [P] Add module- and function-level docstrings to `engine/wyrd/arc_selection.py`
      matching the style of `engine/wyrd/session.py` (docs/design cross-references, scope notes).
- [ ] T018 Run `python3 -m ruff check . && python3 -m ruff format --check .` from repo root and
      fix any findings.
- [ ] T019 Run the full suite: `PYTHONPATH=engine python3 -m unittest discover -s tests/engine -v`
      and confirm nothing outside this feature regressed.
- [ ] T020 Compare implementation against `docs/design/18-arcs-and-beats.md`'s "Selection, and why
      `leads_to` is only a hint" and "Recursion at every level" sections; update the design doc in
      place only if implementation revealed a genuine gap (none expected — spec.md's Assumptions
      already scope this feature to match it as written).

---

## Dependencies & Execution Order

- **Setup (Phase 1)** → **Foundational (Phase 2)**: no user story starts before both complete.
- **User Story 1 (P1)**: depends only on Foundational. No dependency on US2/US3/US4.
- **User Story 2 (P1)**: depends only on Foundational (does not require US1's validation to run
  first, though in practice both land together since they touch the same file).
- **User Story 3 (P1)**: depends on US2's `select()` skeleton (T009) to extend.
- **User Story 4 (P2)**: depends on US3's completed `select()` (T012) to verify against.
- **Polish (Phase 7)**: depends on all user stories.

## Parallel Execution Examples

- T004, T007, T011, T014 (the four stories' test-writing tasks) can be drafted in parallel by
  different contributors before their corresponding implementation tasks land, since they all
  land in the same file but as additive test methods.
- T001 and T002 (Setup) are independent of each other and can run in parallel.

## Implementation Strategy

**MVP scope**: User Story 1 alone (T001-T006) delivers validated entry/exit schema — useful on
its own for any caller that wants to author arcs/beats with entry/exit fields even before
selection exists. User Stories 2 and 3 together are what make the feature's stated goal (the
engine picks the next beat) actually true, and should land in the same PR as US1 given how small
this module is — splitting them across separate PRs would leave selection non-functional in
between for no real benefit.

**Incremental delivery**: T001-T006 (US1) → T007-T010 (US2) → T011-T013 (US3, completes core
selection) → T014-T016 (US4, confirms recursion/stub behavior) → T017-T020 (polish). Each
checkpoint above is independently testable; all four stories are expected to land in one PR given
the module's size (data-model.md: "one new module... engine/wyrd/entity.py gains no new required
fields").
