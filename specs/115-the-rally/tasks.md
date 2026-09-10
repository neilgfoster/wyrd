# Tasks: The Rally: recovery, advance award and commit

**Input**: Design documents from `/specs/115-the-rally/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/rally_module.md, quickstart.md

**Tests**: Included -- every existing `engine/wyrd/*` module ships a matching `tests/engine/test_*.py`
(stdlib `unittest`, `PYTHONPATH=engine`, per `docs/design/27-tooling.md` §6), and this feature
follows that convention.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing
of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single project (the existing `engine/` package): `engine/wyrd/`, `tests/engine/`.

---

## Phase 1: Setup

**Purpose**: Create the new module and test file shells; no user-story logic yet.

- [x] T001 Create `engine/wyrd/rally.py` with the module docstring (per plan.md's Summary: what
      this module does, what it explicitly does not implement, and its relationship to
      `session.py`/`advancement.py`) and `from __future__ import annotations`.
- [x] T002 [P] Create `tests/engine/test_rally.py` with `import unittest`, `from wyrd import
      advancement, rally`, and an empty `class RallyTests(unittest.TestCase):` shell (matching
      `tests/engine/test_session.py`'s existing structure).

---

## Phase 2: Foundational

**Purpose**: No blocking prerequisites beyond Phase 1 -- `engine/wyrd/advancement.py` (the
dependency this feature calls into) already exists and needs no changes. This phase is
intentionally empty; proceed directly to User Story 1.

---

## Phase 3: User Story 1 - Fixed recovery at a Rally (Priority: P1)

**Goal**: `apply_recovery` reduces Strain by 1 (floored at 0) and raises Stamina by 1 (capped at
maximum), matching `docs/design/03-rules.md` §2's stated amounts.

**Independent Test**: Apply recovery to a character below Stamina maximum and above 0 Strain;
confirm both tracks move by exactly 1. Apply it at each boundary (Strain 0, Stamina at maximum);
confirm neither goes out of range.

- [x] T003 [US1] Write `test_apply_recovery_reduces_strain_and_raises_stamina` in
      `tests/engine/test_rally.py`, asserting `rally.apply_recovery(strain=3, stamina=4,
      stamina_max=6) == {"strain": 2, "stamina": 5}` (data-model.md's Rally recovery result;
      matches quickstart.md's first example).
- [x] T004 [P] [US1] Write `test_apply_recovery_floors_strain_at_zero` in
      `tests/engine/test_rally.py`, asserting `rally.apply_recovery(strain=0, stamina=4,
      stamina_max=6)["strain"] == 0`.
- [x] T005 [P] [US1] Write `test_apply_recovery_caps_stamina_at_maximum` in
      `tests/engine/test_rally.py`, asserting `rally.apply_recovery(strain=1, stamina=6,
      stamina_max=6)["stamina"] == 6`.
- [x] T006 [US1] Implement `apply_recovery(strain: int, stamina: int, stamina_max: int) -> dict`
      in `engine/wyrd/rally.py` per contracts/rally_module.md: `{"strain": max(strain - 1, 0),
      "stamina": min(stamina + 1, stamina_max)}`.

**Checkpoint**: `PYTHONPATH=engine python3 -m unittest tests.engine.test_rally -v` passes for
every `US1` test; `apply_recovery` is independently usable by a caller with no award or commit
step involved.

---

## Phase 4: User Story 2 - The advance award is optional (Priority: P1)

**Goal**: An optional trigger claimed at a Rally is passed straight to
`advancement.award_advance`, unchanged; a Rally with no trigger claimed leaves the advancement
record untouched.

**Independent Test**: Apply a Rally with no award claimed; confirm the advancement record is
unchanged. Apply one with a valid trigger; confirm the result matches calling
`award_advance` directly. Apply one with an already-awarded trigger; confirm the same refusal
`award_advance` gives directly, with recovery still applied.

- [x] T007 [US2] Write `test_apply_rally_with_no_trigger_leaves_award_none` in
      `tests/engine/test_rally.py`: build `record = advancement.new_record()`, call
      `rally.apply_rally(strain=3, stamina=4, stamina_max=6, advancement_record=record)`, assert
      `result["award"] is None` and `result["strain"] == 2` and `result["stamina"] == 5` (recovery
      still applies -- FR-003).
- [x] T008 [P] [US2] Write `test_apply_rally_with_valid_trigger_matches_award_advance_directly`
      in `tests/engine/test_rally.py`: call `rally.apply_rally(..., trigger="endured")` against a
      fresh record, and separately call `advancement.award_advance("endured",
      advancement.new_record())` directly; assert the two `award` results are equal field-for-field
      (SC-002/FR-002).
- [x] T009 [P] [US2] Write `test_apply_rally_refused_award_still_applies_recovery` in
      `tests/engine/test_rally.py`: award `"endured"` once via `advancement.award_advance` to get
      an already-awarded record, then call `rally.apply_rally(..., advancement_record=that_record,
      trigger="endured")`; assert `result["award"]["awarded"] is False`,
      `result["award"]["refusal"] == "already_awarded"`, and `result["strain"]`/`result["stamina"]`
      still reflect the fixed recovery (FR-003/FR-006).
- [x] T010 [US2] Implement `apply_rally`'s recovery-plus-award composition in
      `engine/wyrd/rally.py` per contracts/rally_module.md: call `apply_recovery` first, then --
      only when `trigger is not None` -- call `advancement.award_advance(trigger,
      advancement_record)` and place its result under `"award"`; leave `"award"` as `None`
      otherwise. (Signature complete except the `commit` parameter, added in Phase 5.)

**Checkpoint**: `PYTHONPATH=engine python3 -m unittest tests.engine.test_rally -v` passes for every
`US1`+`US2` test; `apply_rally` is usable end-to-end for recovery and an optional award, with no
persist/commit step wired in yet.

---

## Phase 5: User Story 3 - State is written and committed only at a Rally (Priority: P1)

**Goal**: `apply_rally` accepts a caller-supplied `commit` callable and calls it exactly once,
after recovery and any award are both computed; omitting it is a valid Rally with nothing
persisted.

**Independent Test**: Call `apply_rally` with a `commit` callable that appends to a list; confirm
the list has exactly one entry after the call, regardless of whether a trigger was claimed. Call
`apply_rally` with `commit=None` (or omitted); confirm it completes without error.

- [x] T011 [US3] Write `test_apply_rally_calls_commit_exactly_once` in
      `tests/engine/test_rally.py`: pass `commit=lambda: calls.append("committed")` alongside a
      claimed `trigger`; assert `calls == ["committed"]` after the call (FR-004, SC-003).
- [x] T012 [P] [US3] Write `test_apply_rally_calls_commit_even_with_no_award` in
      `tests/engine/test_rally.py`: pass `commit=...` with no `trigger`; assert the commit
      callable still ran exactly once (FR-003 combined with FR-004).
- [x] T013 [P] [US3] Write `test_apply_rally_with_no_commit_does_not_raise` in
      `tests/engine/test_rally.py`: call `apply_rally` with `commit` omitted (its default);
      assert it returns normally (commit is optional, per contracts/rally_module.md).
- [x] T014 [US3] Implement the `commit` parameter on `apply_rally` in `engine/wyrd/rally.py`:
      add `commit: Callable[[], None] | None = None` to the signature (import
      `collections.abc.Callable`), and call it (`if commit is not None: commit()`) exactly once,
      after the recovery and award steps from Phase 3/4 -- never inside a conditional on whether
      an award was claimed or accepted (FR-004/FR-005).

**Checkpoint**: `PYTHONPATH=engine python3 -m unittest tests.engine.test_rally -v` passes in full;
`apply_rally` implements all three user stories end-to-end, matching quickstart.md's examples
exactly.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Repo-wide hygiene and design-doc reconciliation, per CLAUDE.md.

- [x] T015 Run `PYTHONPATH=engine python3 -m unittest discover -s tests/engine -v` to confirm this
      feature introduces no regression in `test_session.py`, `test_advancement.py`, or any other
      existing engine test.
- [x] T016 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` from the repo
      root; fix any finding this feature introduced (CLAUDE.md: both must stay green repo-wide).
- [x] T017 [P] Walk every example in `specs/115-the-rally/quickstart.md` against the finished
      `engine/wyrd/rally.py` and confirm each `assert` holds exactly as written (no implementation
      drift from the contract).
- [x] T018 Re-read `docs/design/16-session.md`'s "The Rally -- the save point" section against the
      finished implementation; if the design doc is found to describe the Rally with any detail
      this implementation contradicts or the design doc leaves ambiguous in a way this feature
      resolved, update the design doc in place (CLAUDE.md: "design documents ... always describing
      the present").

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** has no dependencies -- start here.
- **Phase 2 (Foundational)** is empty -- proceed directly from Phase 1 to Phase 3.
- **Phase 3 (US1)** depends only on Phase 1. Fully independent -- `apply_recovery` needs nothing
  from US2 or US3.
- **Phase 4 (US2)** depends on Phase 3's `apply_recovery` existing (T006), since `apply_rally`
  calls it. Independently testable once T006 lands.
- **Phase 5 (US3)** depends on Phase 4's `apply_rally` signature existing (T010), since it adds
  the `commit` parameter to the same function. Independently testable once T010 lands.
- **Phase 6 (Polish)** depends on Phases 3-5 all being complete.

Within each user-story phase, test tasks (T003/T004/T005, T007/T008/T009, T011/T012/T013) may run
in parallel with each other (marked `[P]`, different test methods in the same file, no shared
mutable state) but must all be written before that phase's single implementation task, which is
not parallel (it is the one place each phase's logic lands).

## Parallel Execution Examples

Phase 3: T004 and T005 (after T003 establishes the test file's shape) can be written together.

Phase 4: T008 and T009 can be written together, both after T007.

Phase 5: T012 and T013 can be written together, both after T011.

Phase 6: T017 can run in parallel with T015/T016 (read-only verification, touches no shared file).

## Implementation Strategy

**MVP = User Story 1 alone** (`apply_recovery`): delivers the fixed Strain/Stamina recovery in
isolation, independently testable and independently useful to a caller that is not yet ready to
wire in the advance-award hook or a commit step. User Story 2 (the award hook) and User Story 3
(the commit step) both build directly on top of it, in priority order, each independently
testable at its own checkpoint before the next begins.
