# Tasks: Foundation review and the reset

**Feature**: 005-foundation-reset | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 1 — Review

- [x] T001 Re-read `doc/design/01-principles.md` in full; record the finding in `research.md`.
- [x] T002 Record the deferred tone knob and why deferring is the correct call.
- [x] T003 Measure the cost of renumbering; record it.

## Phase 2 — The rule

- [x] T004 ADR 0012: the reset, what it authorises, and what it does not.
- [x] T005 The consolidation rule — marking, location, numbering, timing.
- [x] T006 `doc/README.md`: rewrite the lifecycle table; document `superseded/`.

## Phase 3 — The guard

- [x] T007 `check_docs.py`: prose `ADR NNNN` references resolve, against live set and archive.
- [x] T008 Tolerate `superseded/` not existing yet.
- [x] T009 Tests: stale reference caught, valid one passes, archive resolution works.
- [x] T010 Run against the repo; plant a stale reference and confirm non-zero exit.

## Phase 4 — Ship

- [x] T011 Commit referencing #40, open the PR.
