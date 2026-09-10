# Tasks: Beat/arc structure and the session loop

**Input**: Design documents from `/specs/114-beat-arc-session-loop/`

## Phase 1: Setup

- [ ] T001 Create `engine/wyrd/session.py` with the module docstring (mirroring `entity.py`'s
      style) naming the design doc it implements: `docs/design/16-session.md`, and noting it
      builds on `wyrd.entity`'s containment primitives (`children_of`, `RECURSIVE_TYPES`) rather
      than duplicating them.
- [ ] T002 Create `tests/engine/test_session.py` with the `PYTHONPATH=engine` import pattern used
      by `tests/engine/test_entity.py`.

## Phase 2: Foundational

- [ ] T003 In `engine/wyrd/session.py`, define module constants `LOOP_STEPS` and
      `SESSION_SHAPES` per `contracts/session_module.md`.
- [ ] T004 In `engine/wyrd/session.py`, import `wyrd.entity` and confirm (via a short comment or
      assertion, not new logic) that `"beat"` is absent from `entity.RECURSIVE_TYPES` — this
      module's enforcement in Phase 3 depends on that invariant holding.

## Phase 3: User Story 1 - Arcs contain, beats are played (P1)

**Goal**: A beat given a child is rejected, per FR-001/FR-002.

**Independent Test**: Construct an arc with a beat child and an arc with an arc child; attempt to
give a beat a child of its own and confirm it is rejected.

- [ ] T005 [P] [US1] Write `test_arc_may_contain_beat_or_arc` in `tests/engine/test_session.py`
      (acceptance scenarios 1 and 3).
- [ ] T006 [P] [US1] Write `test_beat_with_child_is_rejected` in `tests/engine/test_session.py`
      (acceptance scenario 2), asserting the returned `{"valid": False, "beat": ..., "child": ...}`
      shape from `data-model.md`.
- [ ] T007 [US1] Implement `check_beat_has_no_children(entities: dict) -> dict` in
      `engine/wyrd/session.py` per `contracts/session_module.md`, using `entity.children_of`
      against every entity of type `"beat"` in the set.

**Checkpoint**: Beat/arc containment enforcement works standalone; no dependency on any later
phase.

## Phase 4: User Story 2 - Played or summarised is the GM's call, not the beat's property (P1)

**Goal**: `narrate_beat` produces an independent per-narration record carrying `mode`, per
FR-003/FR-004.

**Independent Test**: Narrate the same beat definition twice, once as played and once as
summarised, and confirm the engine records the mode as a property of that particular narration,
not of the beat's definition.

- [ ] T008 [P] [US2] Write `test_narrate_beat_records_mode` in `tests/engine/test_session.py`
      (acceptance scenario 1).
- [ ] T009 [P] [US2] Write `test_narrate_beat_independent_across_records` in
      `tests/engine/test_session.py` (acceptance scenarios 2 and 3: two records for the same
      `beat_id` share no mutable state, and a beat's own frontmatter never gains a `mode` field).
- [ ] T010 [P] [US2] Write `test_narrate_beat_rejects_invalid_mode` in
      `tests/engine/test_session.py` for a `mode` outside `{"played", "summarised"}`.
- [ ] T011 [US2] Implement `narrate_beat(beat_id: str, mode: str) -> dict` in
      `engine/wyrd/session.py` per `contracts/session_module.md` and `data-model.md`'s "Beat
      resolution record".

**Checkpoint**: Beat narration works standalone; does not depend on Phase 3's containment check
at runtime (independent module functions), though both build on the same entity data.

## Phase 5: User Story 3 - The session loop walks load → orient → recap → beat → repeat → close (P1)

**Goal**: `new_loop_state`/`advance_loop` enforce step order, with orient required before recap
and close reachable at most once, per FR-005/FR-006/FR-007.

**Independent Test**: Drive the loop through a scripted sequence of steps and confirm each step is
only reachable from its declared predecessor, and that orient always completes before recap runs.

- [ ] T012 [P] [US3] Write `test_loop_happy_path` in `tests/engine/test_session.py`: load → orient
      → recap → beat → beat → close, asserting `elapsed_applied`/`closed` flip at the right
      points and `beats_this_session` records each beat id (acceptance scenarios 1 and 3).
- [ ] T012a [P] [US3] Write `test_recap_may_advance_directly_to_close` (FR-006: zero beats is a
      legal session) and `test_rejects_beat_without_beat_id` in `tests/engine/test_session.py`.
- [ ] T013 [P] [US3] Write `test_loop_rejects_recap_before_orient` and
      `test_rejects_close_before_recap` in `tests/engine/test_session.py`.
- [ ] T014 [P] [US3] Write `test_rejects_transition_after_close` in
      `tests/engine/test_session.py` (FR-007's exactly-once requirement), and
      `test_runs_steps_in_order`/`test_empty_close_is_valid` for `run_close`.
- [ ] T015 [US3] Implement `new_loop_state() -> dict`,
      `advance_loop(loop_state: dict, to_step: str, *, beat_id: str | None = None) -> dict`, and
      `run_close(steps=None) -> None` in `engine/wyrd/session.py` per `contracts/session_module.md`
      and `data-model.md`'s "Session loop state", raising `ValueError` naming the illegal
      transition and returning a new dict rather than mutating the input in place. `recap` may
      advance directly to `close` (FR-006); `beat_id` is required when advancing to `beat` and is
      appended to `beats_this_session`.

**Checkpoint**: The loop's ordering guarantee is independently verifiable without Phases 3/4.

## Phase 6: User Story 4 - No session ever ends mid-beat (P2)

**Goal**: `set_pending`/`resume_from_pending` persist and resume the interrupted action exactly,
per FR-008/FR-009/FR-010.

**Independent Test**: Stop a scripted session partway through a beat's resolution; reload the
chronicle and confirm the `pending:` marker names the exact unresolved action and resumption
continues from it rather than from the beat's start or the arc's start.

- [ ] T016 [P] [US4] Write `test_set_pending_and_resume` in `tests/engine/test_session.py`
      (acceptance scenarios 1 and 2).
- [ ] T017 [P] [US4] Write `test_clean_resolution_leaves_no_pending_marker` (asserting
      `narrate_beat` never itself produces a pending-marker shape as a side effect) and
      `test_clear_pending_returns_the_cleared_value` in `tests/engine/test_session.py`
      (acceptance scenario 3).
- [ ] T018 [US4] Implement `set_pending(beat_id: str, action: str) -> dict`,
      `resume_from_pending(pending: dict) -> str`, and `clear_pending() -> None` in
      `engine/wyrd/session.py` per `contracts/session_module.md` and `data-model.md`'s "Pending
      marker" — `clear_pending` is the value a caller stores in place of a cleared marker, since
      this module holds no state of its own to delete.

**Checkpoint**: Mid-beat interruption and resumption verified independently of loop/narration
internals (this phase only wraps a plain record and an accessor).

## Phase 7: User Story 5 - Session shape is an internal pacing read, never player-facing (P3)

**Goal**: `classify_shape` returns one of the four shapes from session facts, and nothing in this
module threads its result into player-facing text, per FR-011/FR-012.

**Independent Test**: Run each of the four shapes through the loop and grep every player-facing
output the engine produces for that session for shape-identifying vocabulary.

- [ ] T019 [P] [US5] Write `test_classify_shape_each_of_four_shapes` in
      `tests/engine/test_session.py` (acceptance scenario 2), covering single beat, interlude,
      downtime, extended per `docs/design/16-session.md`'s "Session shapes" table.
- [ ] T020 [P] [US5] Write `test_classify_shape_never_fails_on_ambiguous_input` in
      `tests/engine/test_session.py` (acceptance scenario 3) — an input matching no shape
      cleanly still returns a definite label rather than raising.
- [ ] T021 [US5] Implement `classify_shape(beats_this_session, used_dice, ran_downtime) -> str`
      in `engine/wyrd/session.py` per `contracts/session_module.md` and `data-model.md`'s
      "Session shape".
- [ ] T022 [US5] Grep `engine/wyrd/session.py` for any function whose docstring or return value
      suggests it produces player-facing narration text, and confirm none of them import or call
      `classify_shape` — record this as a code comment next to `classify_shape` itself
      (acceptance scenario 1 / SC-004's static-check half; the dynamic half is T019/T020's
      grep-based test against actual narration strings in `tests/engine/test_session.py`).

**Checkpoint**: All five user stories independently verifiable; module complete per spec.md.

## Phase 8: Polish & Cross-Cutting Concerns

- [ ] T023 [P] Run `python3 -m ruff check .` and `python3 -m ruff format --check .` repo-wide and
      fix any finding introduced by this feature.
- [ ] T024 [P] Update `docs/design/16-session.md` in place only if implementation surfaced a
      genuine gap against the design doc's text (per `CLAUDE.md`'s "design documents describe the
      present" rule) — otherwise skip, the doc already matches.
- [ ] T025 Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_session -v` and confirm
      all tests pass; then run the full suite (`PYTHONPATH=engine python3 -m unittest discover -s
      tests/engine -p "test_*.py"`) to confirm no regression in `wyrd.entity`/`wyrd.party`/other
      modules.
- [ ] T026 Walk through every command in `quickstart.md` manually (or as a scratch script) to
      confirm it runs as written against the finished module.

## Dependencies & Execution Order

- **Setup (Phase 1)** → **Foundational (Phase 2)**: no user story starts before both complete.
- **User Stories (Phases 3-7)**: all five are independent of each other at the code level (each
  adds its own free functions to `session.py`, none calling another's). They may be implemented
  and tested in any order, though priority order (US1, US2, US3, US4, US5) is recommended so an
  interruption after any phase still leaves the highest-priority stories complete.
- **Polish (Phase 8)**: after all desired user stories are complete.

## Parallel Execution Examples

Within Phase 3, T005 and T006 (different test functions in the same new test file, no shared
state) can be written in parallel before T007 implements the function both depend on. The same
pattern repeats in every user-story phase: `[P]`-marked test-writing tasks precede the single
non-`[P]` implementation task in that phase, since all the test tasks target the same not-yet-
existing function and the implementation task is the one every test in that phase needs to pass.

Across phases, Phases 3, 4, 6 and 7 touch disjoint functions in the same file and could be
implemented in parallel by different contributors without merge conflict on any single function's
body, provided each phase's `[P]` test tasks land before its own implementation task.

## Implementation Strategy

**MVP scope**: User Story 1 (Phase 3) alone — the beat-cannot-be-a-container enforcement — is the
minimum increment that closes the specific gap `wyrd.entity` leaves open. User Stories 2 and 3
(Phases 4-5) are also P1 and needed for #310/#311 to have something to build the Rally and
Downtime phase's own "beat closing" hooks against, so a complete delivery covers Phases 1-5 before
Phases 6-7 (P2/P3) are added incrementally.
