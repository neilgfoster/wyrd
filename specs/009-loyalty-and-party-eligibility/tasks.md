# Tasks: Loyalty and party eligibility

**Feature**: 009-loyalty-and-party-eligibility | **Spec**: [spec.md](./spec.md)

## Phase 1 — Research
- [x] T001 Establish why this is engine work, not setting data.
- [x] T002 Check the vocabulary for collisions; pick a free name.
- [x] T003 Establish why a boolean is too weak and a matrix too heavy.

## Phase 2 — Design
- [x] T004 `03b` — the character carries a Loyalty.
- [x] T005 `04-session` — the three relations, enforcement, and the change rule.
- [x] T006 `strained` feeds Party Tension rather than a new track.
- [x] T007 `03c` — creation chooses one.
- [x] T008 `06-state` — the field.
- [x] T009 `13-authoring` — the engine/setting contract row.

## Phase 3 — Record
- [x] T010 ADR 0015 — three relations, and the rejected shapes.

## Phase 4 — Verify
- [x] T011 No Loyalty named in `design/`; no moral register.
- [x] T012 `check_docs.py`, `backlog.py check`, unit tests.

## Phase 5 — Ship
- [x] T013 Commit referencing #34, open the PR.
