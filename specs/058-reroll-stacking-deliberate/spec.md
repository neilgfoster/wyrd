# Feature Specification: Decide whether reroll resources may stack unbounded on one roll

**Feature Branch**: `167-reroll-stacking-deliberate`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Decide whether reroll resources (Bargain, Resolve, Fortune) may stack unbounded on one failed test (closes #167, found during #153, playtest epic #134). Nothing in 03-rules.md states a limit; #153's seven trials showed the stack materially raises success (6/7) but is not automatic (1/7 still failed after exhausting everything). Operator direction: deliberately unbounded (recommended option), not capped."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A GM knows whether stacking reroll resources on one roll is intended, not an accident (Priority: P1)

A GM running a scene where a player wants to spend the Bargain, then Resolve, then Fortune on the
same failed roll needs to know this is the intended design, not a table-improvised ruling.

**Why this priority**: This is #167's own gap — the mechanic was playable but undocumented as a
deliberate choice, exactly the "reads as an oversight rather than a decision" class of issue this
repo treats as needing a real decision.

**Independent Test**: Read `03-rules.md` §3 and §4; confirm both state explicitly that Fortune,
Resolve, and the Bargain compose without limit on one roll.

**Acceptance Scenarios**:

1. **Given** a character who fails an original roll and has Taint to spend, Resolve available,
   and Fortune remaining, **When** they choose to spend all three in sequence against the same
   roll, **Then** the rules explicitly permit this, with no engine-imposed cap.
2. **Given** the design decision, **When** a real rejected alternative exists (a per-test cap),
   **Then** it is recorded as an ADR, not left as an implicit choice.

### Edge Cases

- Does this change how Fortune, Resolve, or the Bargain each work individually? No — ADR
  0041/0042/0043 govern each unchanged; this only states that they compose.
- Is a new verification script needed? No — #153's own seven-trial playtest record already
  serves as the evidence this decision relies on (one of seven trials failed after the full stack
  was spent, confirming the stack is not a guaranteed win); re-deriving it would duplicate
  disclosed work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `03-rules.md` §3 and §4 MUST state explicitly that Fortune, Resolve, and the
  Bargain may all be spent against the same original failed roll, with no engine-imposed cap.
- **FR-002**: The decision MUST be recorded as an ADR, since a real, workable rejected alternative
  (a per-test cap) exists with a different play consequence.
- **FR-003**: The decision MUST reference #153's own seven-trial playtest evidence rather than
  re-deriving new evidence.
- **FR-004**: The decision MUST NOT change how any of the three mechanics work individually.

### Key Entities

*(none — this feature is a rules clarification, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `03-rules.md` §3 and §4 state the stacking rule, cross-referencing each other and
  the new ADR.
- **SC-002**: ADR 0046 records the decision, including the rejected per-test-cap alternative.
- **SC-003**: `docs/design/30-playtest-transcript.md` §12's finding and §13's synthesis table are
  updated to reflect the resolution.
- **SC-004**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
  `python3 -m pytest -q` pass.

## Assumptions

- No new verification script — the resolution reuses #153's own already-disclosed seven-trial
  evidence rather than re-deriving it, per the operator's instruction and the issue's own
  Definition of Done ("checked against a re-run" applies only if a cap were introduced; this
  keeps the status quo).
- Documentation-only: no engine code changes.
