# Tasks: Fault Line accrual bias

**Input**: [spec.md](./spec.md), [plan.md](./plan.md)

## Phase 1 — Computation (must precede the design doc's claims)

- [ ] T001 Write `tools/check_fault_line.py`: model Exposure's three tiers (minor 1, moderate 2,
  major 3) at a spread of realistic starting Taint values, compute how many failed aligned-Exposure
  events versus unaligned-Exposure events it takes to cross the next transformation threshold
  (every multiple of 3, per `03a-3-transformations.md`), and confirm the tier-worse step never
  exceeds 3 at the major-tier ceiling case. [FR-007, SC-002]
- [ ] T002 In the same script, diff-check `doc/design/10-transformations.md` against its content at
  the start of this branch and fail loudly if it changed. [FR-006, SC-003]
- [ ] T003 Run the script and capture its output for the design document. [FR-007]

## Phase 2 — Design document

- [ ] T004 Update `doc/design/03-rules.md` §4's Exposure subsection in place: state the tier-worse step
  (minor 1 → 2, moderate 2 → 3, major stays 3), the fiction-grounded GM judgment call that gates
  it (mirroring Drive invocation), the one-step-per-event cap, and its independence from an
  Invocation drawn against the same roll. [FR-002, FR-003, FR-004, FR-005]
- [ ] T005 Update §4's Fault Line subsection in place to point at the mechanism instead of standing
  as description alone. [FR-001]
- [ ] T006 Confirm no other document references the Fault Line as purely descriptive (grep
  `design/` for "Fault Line") and update any that do. [FR-001]

## Phase 3 — Decision record

- [ ] T007 Write the ADR recording the Taint-accrual-bias decision, naming both rejected
  alternatives (transformation row selection; hidden threshold bias) and why each was set aside.
- [ ] T008 Add the new ADR to `doc/README.md`'s index.

## Phase 4 — Verification

- [ ] T009 `grep` the touched files for setting/system vocabulary; confirm none.
- [ ] T010 Run `python3 tools/check_docs.py` — must pass.
- [ ] T011 Run `python3 tools/backlog.py check` — must pass.
- [ ] T012 Confirm `doc/design/10-transformations.md` is unchanged in the diff against `main`, per
  FR-006/SC-003.

## Dependencies

Phase 1 before Phase 2 (the design doc's comparison is the script's output, not a guess).
Phase 3 can run alongside Phase 2 once the load-bearing decision is fixed. Phase 4 last.
