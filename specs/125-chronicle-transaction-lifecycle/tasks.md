---

description: "Task list for chronicle transaction lifecycle"
---

# Tasks: Chronicle transaction lifecycle

**Input**: Design documents from `/specs/125-chronicle-transaction-lifecycle/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: included — spec.md's acceptance scenarios are directly testable and the constraints
section requires ruff-clean, exact-arithmetic-style verification (CLAUDE.md).

## Phase 1: Foundational

- [ ] T001 Create `engine/wyrd/chronicle.py` with `resume_state`, `discard_at_rally`,
      `discard_moot`, `record_rolled` (data-model.md) — pure functions, no I/O, module docstring
      following the repo's existing per-module convention (see `rally.py`/`session.py` for style).

## Phase 2: User Story 1 — Resume a mid-beat interruption (P1)

- [ ] T002 [US1] `chronicle.resume_state(pending)`: returns `{"beat", "awaiting"}` when both are
      set, `None` when `pending` is `None` or both sub-fields are null (data-model.md).
- [ ] T003 [P] [US1] Tests in `tests/engine/test_chronicle.py`: resume with both sub-fields set;
      resume with `pending=None`; resume with `pending={"beat": None, "awaiting": None, "rolled":
      None}` (spec.md Acceptance Scenarios 1-2, Edge Cases).

## Phase 3: User Story 2 — Discard an abandoned proposal at the next Rally (P1)

- [ ] T004 [US2] `chronicle.discard_at_rally(pending)`: returns `{"pending": <new pending with
      rolled cleared>, "to_discard": <the id that was in rolled, or None>}` (data-model.md).
- [ ] T005 [US2] `rally.apply_rally` gains an optional pending-discard step: given the chronicle's
      current `pending`, call `chronicle.discard_at_rally`, then (if `to_discard` is not `None`)
      call `resolution.discard(to_discard)`, then persist the returned `pending` — every Rally,
      unconditionally checked, before/alongside the existing recovery/award/commit sequence
      (research.md's "Rally-discard is an optional step in apply_rally" decision).
- [ ] T006 [P] [US2] Tests: a Rally with `pending.rolled` naming a still-open proposal discards it
      and clears `rolled`; a Rally with `pending.rolled` already `None` changes nothing (no-op,
      not an error) (spec.md Acceptance Scenarios 1-2, Edge Cases, SC-002).
- [ ] T007 [P] [US2] Test: `pending.beat`/`pending.awaiting` are untouched by a Rally's discard of
      `pending.rolled`, and vice versa — the two clear independently (spec.md Edge Cases, FR-008).

## Phase 4: User Story 3 — Explicit moot-discard within a live session (P2)

- [ ] T008 [US3] `chronicle.discard_moot(pending)`: same shape/behaviour as `discard_at_rally`
      (data-model.md) — a distinct, separately-invocable entry point for the in-session call site.
- [ ] T009 [P] [US3] Tests: an actor with one open proposal has it discarded via the moot path
      before any Rally; calling the moot path when there is no open proposal is a no-op, not an
      error (spec.md Acceptance Scenarios, Edge Cases, FR-006).

## Phase 5: User Story 4 — At most one open proposal per actor (P2)

- [ ] T010 [US4] `chronicle.record_rolled(pending, proposal_id)`: sets `pending.rolled` to
      `proposal_id`; raises `ValueError` if `pending.rolled` is already non-null (data-model.md).
- [ ] T011 [P] [US4] Test: recording a second open proposal while one is already open raises
      `ValueError` rather than silently overwriting or coexisting (spec.md Acceptance Scenario 1,
      FR-007).

## Phase 6: Reconciliation and polish

- [ ] T012 Remove `wyrd.session.set_pending`/`resume_from_pending`/`clear_pending` and their tests
      in `tests/engine/test_session.py` (`test_set_pending_and_resume`,
      `test_clear_pending_returns_the_cleared_value`) — superseded by `chronicle.py`'s functions
      against the real `pending` schema; confirmed zero other call sites by grep (data-model.md
      "Reconciling wyrd.session's pre-existing helpers"). Update `session.py`'s module docstring
      to drop its now-inaccurate mention of owning "the `pending:` mid-beat marker."
- [ ] T013 [P] Update `docs/design/16-session.md` and/or `docs/design/22-state.md` only if either
      makes a now-stale claim about where `pending` semantics live (both currently describe the
      target behaviour correctly per this feature's research — check before editing; CLAUDE.md
      design docs are rewritten in place only when actually stale).
- [ ] T014 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` repo-wide; fix any
      findings (CLAUDE.md: both must stay green, including under `specs/`/`tools/`).
- [ ] T015 Run `PYTHONPATH=engine python3 -m pytest -q`; confirm full suite green, not just the
      new tests.

## Dependencies

- T001 blocks T002, T004, T008, T010 (all live in the module T001 creates).
- T002 blocks T003. T004 blocks T005, T006, T007. T008 blocks T009. T010 blocks T011.
- T012 depends on T002-T011 landing first (nothing left to fall back on once removed).
- T013-T015 run last, after all implementation and the T012 removal.

## Parallel example

T003, T006, T007, T009, T011 touch only `tests/engine/test_chronicle.py` additions independent of
each other's assertions and can be written together once their respective implementation task is
done; T013 (docs) is independent of T014/T015 (verification) and can run alongside them.
