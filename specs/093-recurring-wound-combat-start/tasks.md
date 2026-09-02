---

description: "Task list for the recurring wound's combat-start effect"
---

# Tasks: The recurring wound's combat-start effect

**Input**: Design documents from `/specs/093-recurring-wound-combat-start/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: included -- this is an engine correctness feature; tests are how it's verified.

**Organization**: tasks are grouped by user story per spec.md.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

No setup needed -- this feature extends existing modules (`engine/wyrd/combat.py`) in the
existing project; no new dependencies, no new project structure.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: the shared computation every user story depends on.

- [ ] T001 Add a module-level helper `_recurring_wound_penalties(wounds: list[dict]) -> dict[str, int]`
  in `engine/wyrd/combat.py` that takes a list of raw wound records (the same shape
  `character.active_wound_effects` reads from), filters to `wound.get("recurring")` and
  `wound.get("closed") is None`, and sums `CHALLENGING_MODIFIER` per `bears_on` skill,
  returning `{}` when there are none. Reuses the existing `CHALLENGING_MODIFIER` constant
  (research.md) -- no new `-10` literal.
- [ ] T002 Extend `start_combat`'s `sides` handling in `engine/wyrd/combat.py`: read an optional
  `"wounds"` key per side (default `[]`, same default-handling pattern as `armed`/`surprised`/
  `ambush`), compute its penalties via T001, and set `scene["wound_penalties"]` to
  `{combatant: penalties}` for every combatant whose computed penalties are non-empty (data-model.md:
  absent, not empty-dict, for a combatant with none).

**Checkpoint**: `start_combat` now computes and persists `wound_penalties`; every user story
below is a test/verification pass over this one change.

---

## Phase 3: User Story 1 - A recurring wound fires at the start of a fight (Priority: P1) 🎯 MVP

**Goal**: one active recurring wound produces the Challenging penalty on its named skill at
combat start; a combatant with none gets nothing.

**Independent Test**: start a combat scene for a combatant with one recurring wound on file and
assert the penalty on `scene["wound_penalties"]`.

### Tests for User Story 1

- [ ] T003 [P] [US1] `test_start_combat_applies_recurring_wound_penalty` in
  `tests/engine/test_combat.py`: one combatant with one active recurring wound bearing on a
  named skill; assert `scene["wound_penalties"][combatant][skill] == combat.CHALLENGING_MODIFIER`.
- [ ] T004 [P] [US1] `test_start_combat_no_wounds_no_penalty` in `tests/engine/test_combat.py`:
  a combatant with no wounds (or an empty `wounds` list, or the key omitted entirely) has no
  entry in `scene["wound_penalties"]`.

### Implementation for User Story 1

Covered by Phase 2 (T001/T002) -- no additional implementation; this phase is verification.

**Checkpoint**: User Story 1 passes independently.

---

## Phase 4: User Story 2 - Multiple recurring wounds stack (Priority: P2)

**Goal**: two or more active recurring wounds all fire; two bearing on the same skill stack
(sum), not just the strongest applying.

**Independent Test**: start a combat scene for a combatant with two recurring wounds (once on
different skills, once on the same skill) and assert both fire / stack.

### Tests for User Story 2

- [ ] T005 [P] [US2] `test_start_combat_two_recurring_wounds_different_skills` in
  `tests/engine/test_combat.py`: two active recurring wounds on two different skills both
  appear in `wound_penalties`, each at `CHALLENGING_MODIFIER`.
- [ ] T006 [P] [US2] `test_start_combat_two_recurring_wounds_same_skill_stack` in
  `tests/engine/test_combat.py`: two active recurring wounds bearing on the same skill sum to
  `2 * combat.CHALLENGING_MODIFIER` on that skill.

### Implementation for User Story 2

Covered by Phase 2 (T001's summation already handles stacking) -- no additional implementation.

**Checkpoint**: User Stories 1 and 2 both pass independently.

---

## Phase 5: User Story 3 - The penalty is scoped to the fight it fires in (Priority: P3)

**Goal**: the penalty is fixed at combat start, unaffected by `advance_round`, and does not
appear on a later, separate combat scene unless that combatant still carries the wound and is
passed in again.

**Independent Test**: advance a round and re-check `wound_penalties` is unchanged; start a
second combat scene without wound data for that combatant and confirm no penalty.

### Tests for User Story 3

- [ ] T007 [P] [US3] `test_wound_penalties_unchanged_by_advance_round` in
  `tests/engine/test_combat.py`: after `start_combat` with a recurring wound, call
  `advance_round` and assert `scene["wound_penalties"]` is byte-for-byte identical before and
  after.
- [ ] T008 [P] [US3] `test_wound_penalties_not_carried_to_new_combat_scene` in
  `tests/engine/test_combat.py`: after one combat scene with a recurring-wound penalty, start a
  fresh `start_combat` call for the same state path without passing `wounds` for that combatant
  and assert `wound_penalties` no longer contains them (i.e. the new scene is computed fresh,
  never inherited from the old one).
- [ ] T009 [P] [US3] `test_closed_wound_does_not_apply_penalty` in `tests/engine/test_combat.py`
  (FR-008): a wound with `recurring: True` but `closed` set to a non-`None` value contributes no
  penalty (covers the "general closed-wounds rule still governs" requirement even though a
  recurring wound is never expected to close in practice).

### Implementation for User Story 3

Covered by Phase 2 -- `wound_penalties` is set once per `start_combat` call and untouched by
`advance_round`, satisfying this story's requirements by construction. No additional
implementation.

**Checkpoint**: All three user stories pass independently and together.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T010 Update `engine/wyrd/combat.py`'s module docstring to mention the recurring-wound
  combat-start hook alongside its existing feature-reference list (matching the file's existing
  convention of citing `docs/design/...` and `specs/...` per feature, per the surrounding
  docstring style).
- [ ] T011 Run `python3 -m pytest tests/engine/test_combat.py -q` and the full suite
  (`ruff check . && ruff format --check . && python3 -m pytest -q`) to confirm nothing else
  regressed.
- [ ] T012 Walk through `quickstart.md`'s three scenarios manually (or as a scratch script) to
  confirm the examples there match actual behavior; fix quickstart.md if the real API shape
  drifted during implementation.

---

## Dependencies & Execution Order

- **Foundational (Phase 2)**: no dependencies; must land before any test task below can pass.
- **User Stories (Phases 3-5)**: all depend only on Phase 2, not on each other -- their test
  tasks (T003-T009) can all be written and run in parallel once T001/T002 exist.
- **Polish (Phase 6)**: depends on Phases 2-5 being complete.

## Parallel Opportunities

- T003, T004, T005, T006, T007, T008, T009 are all `[P]` -- distinct test functions in the same
  file, safe to write concurrently, each independent of the others once T001/T002 land.

## Implementation Strategy

Given the whole feature is one small addition to `start_combat`, there is no meaningful MVP slice
below "the foundational change" -- implement T001/T002 first, then write all test tasks
(T003-T009) as one pass, then Phase 6. The user-story split above documents *what's being
verified*, not a staged rollout.
