# Tasks: The affliction table

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

## Phase 1 — Computation (must precede the design doc's claims)

- [ ] T001 Write `tools/check_affliction.py`: model Trauma accrual (criticals taken, failed Terror
  tests) across a stated spread of per-session event rates and representative test skills, compute
  expected sessions between Afflictions at each combination, and flag any combination giving an
  implausible cadence. [FR-006, SC-001]
- [ ] T002 Run the script and capture its output for the design document's cadence table. [FR-006]

## Phase 2 — Design document

- [ ] T003 Write `design/03a-4-afflictions.md`: the fiction-chosen §1 test fired on every Trauma
  point past 6 (FR-001), the twelve-row `1d12` table with rows phrased as behaviour and carrying an
  applicable effect (FR-002, FR-003), the repeatable-family statement and what a repeat draw does
  (FR-004), the restated Taint/Trauma split matching `03a-3-transformations.md` (FR-005), and the
  computed cadence (FR-006). [US1, US2, US3]
- [ ] T004 Update `design/03-rules.md` §5 in place: name the test, point at the new document, no
  changelog language. [FR-007]
- [ ] T005 Update `design/03a-tables.md`'s index row for Afflictions: roll, link, no longer "not
  yet written". [FR-008]
- [ ] T006 Add the hub row for `03a-4-afflictions.md` to `README.md` for reachability.

## Phase 3 — Decision record

- [ ] T007 Write the ADR recording the repeatable-family decision and the fiction-chosen-test
  decision, with both rejected alternatives (unique-per-family default; a new named
  "Willpower"-style skill).
- [ ] T008 Add the new ADR to `design/README.md`'s index.

## Phase 4 — Verification

- [ ] T009 `grep` `design/03a-4-afflictions.md` and the touched files for setting/system vocabulary
  and tonal register; confirm none, and that no row presumes a particular moral reading of mental
  harm. [FR-009]
- [ ] T010 Run `python3 tools/check_docs.py` — must pass. [SC-002]
- [ ] T011 Run `python3 tools/backlog.py check` — must pass. [SC-002]

## Dependencies

Phase 1 before Phase 2 (the design doc's cadence table is the script's output, not a guess).
Phase 3 can run alongside Phase 2 once the load-bearing decisions are fixed. Phase 4 last.
