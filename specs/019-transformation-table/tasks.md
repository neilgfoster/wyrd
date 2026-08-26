# Tasks: The transformation table

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

## Phase 1 — Computation (must precede the design doc's claims)

- [X] T001 Write `tools/check_transformation.py`: model the threshold-spacing/severity scheme,
  compute worst-case and expected re-roll counts across Taint 0–20 and every legal single-event
  gain (1–3), and assert the hard bound (loop never exceeds the table's row count). [FR-003, SC-001]
- [X] T002 Run the script and capture its output for the design document's table. [FR-003]

## Phase 2 — Design document

- [X] T003 Write `design/03a-3-transformations.md`: thresholds (FR-001), the roll and table with a
  severity per row (FR-002), the body/mind statement (FR-004), termination proof (FR-003), the
  hidden threshold (FR-005), and Dread (FR-006). [US1, US2, US3]
- [X] T004 Update `design/03-rules.md` §4 in place: state the thresholds and the resolved body/mind
  split, point at the new document, no changelog language. [FR-007]
- [X] T005 Update `design/03a-tables.md`'s index row for Transformations: roll, link, no longer
  "not yet written". [FR-008]
- [X] T006 Add the hub row for `03a-3-transformations.md` to `README.md` for reachability.

## Phase 3 — Decision record

- [X] T007 Write `design/adr/0029-transformation-thresholds-at-every-three-taint.md`: the
  threshold-spacing decision, the Dread-reuse decision, and both rejected alternatives.
- [X] T008 Add ADR 0029 to `design/README.md`'s index.

## Phase 4 — Verification

- [X] T009 `grep` `design/03a-3-transformations.md` and the touched files for setting/system
  vocabulary and tonal register; confirm none. [FR-009]
- [X] T010 Confirm nothing produced requires showing the hidden threshold to the player (re-read
  against `10-diegesis.md`'s "never shown" class). [FR-010]
- [X] T011 Run `python3 tools/check_docs.py` — must pass. [SC-002]
- [X] T012 Run `python3 tools/backlog.py check` — must pass. [SC-002]

## Dependencies

Phase 1 before Phase 2 (the design doc's termination table is the script's output, not a guess).
Phase 3 can run alongside Phase 2 once the load-bearing decisions are fixed. Phase 4 last.
