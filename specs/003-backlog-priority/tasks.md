# Tasks: Backlog priority order

**Feature**: 003-backlog-priority | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 1 — Board

- [x] T001 Create a `Rank` number field on the `wyrd` Project (v2 #5).
- [x] T002 Add issue #24 to the board — absent, because `kord-feature-create` does not add items.
- [x] T003 Set the seeded ranks: #1=10, #24=20, #2=30, #3=40, #4=50 (plan.md, "Seeded order").

## Phase 2 — The read path

- [x] T004 `tools/backlog.py`: `gh` wrappers for project items and the open-issue graph. Read-only.
- [x] T005 Parse `Depends on: #N`, anchored on a line beginning with that prefix so the prose in
      #6/#11/#17 is not mistaken for a declaration (research.md §2).
- [x] T006 Implement the walk: roots by `(Rank, number)`, descend to leaves, first ready leaf wins.
- [x] T007 `next` subcommand — the chosen issue plus the blocked items it passed over, with `--format json`.
- [x] T008 `check` subcommand — the four drift classes of FR-4, non-zero exit on any.

## Phase 3 — Tests

- [x] T009 `tools/test_backlog.py` (`unittest`, no network) over captured fixtures:
      - the `Depends on:` parser, including the #11 prose-inversion trap
      - dependency yields to priority: a top-ranked blocked item is passed over and reported
      - descent reaches a leaf, not the epic
      - each drift class in FR-4 is detected
- [x] T010 Capture `tools/fixtures/board.json` from the live board so the tests run offline.

## Phase 4 — Record it

- [x] T011 ADR 0010 — the board field, and why not a backlog file.
- [x] T012 `CLAUDE.md` — name the mechanism, state the refinement rule on raising new work.
- [x] T013 Correct #24's own body where it claims #17–#21 are root-level.

## Phase 5 — Ship

- [x] T014 Run `check` and `next` against the live board; confirm the answer is a ready leaf.
- [x] T015 Commit referencing #24, open the PR.

## Out of scope

Raising the `kord-feature-create` board gap upstream in the kord repo. Noted in plan.md's risks;
not this branch's work.
