# Tasks: Character creation

**Feature**: 008-character-creation | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 1 — Derive

- [x] T001 Gather the four constraints already fixed by merged documents.
- [x] T002 `check_creation.py`: model damage through armour across a weapon band.
- [x] T003 Correct the overshoot threshold — ordinary case vs worst case.
- [x] T004 State the tiebreak within the passing band, rather than picking quietly.
- [x] T005 Model Luck erosion across an arc.

## Phase 1b — Background (raised in review)

- [x] T005a Derive the free-advance pool from the diegetic skill bands.
- [x] T005b Add the background step; state that origin is fiction, not mechanics.
- [x] T005c Record why a separate background skill list fails, and why rolling is refused.

## Phase 2 — Design

- [x] T006 `doc/design/05-character-creation.md`: the ordered steps.
- [x] T007 The starting values, each with its reason.
- [x] T008 What a setting must provide for creation to run.
- [x] T009 Hand-off to advancement; succession uses the same procedure.

## Phase 3 — Record

- [x] T010 ADR 0014 — chosen, not rolled, with four rejected alternatives.

## Phase 4 — Verify

- [x] T011 Indexes; confirm no other document describes creation as rolled.
- [x] T012 `check_creation.py`, `check_docs.py`, `backlog.py check`, unit tests.

## Phase 5 — Ship

- [x] T013 Commit referencing #9, open the PR.
