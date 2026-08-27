# Feature Specification: Resolve recovers at a Rally, capped by Taint

**Feature Branch**: `052-resolve-recovery-mechanic`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Resolve has no stated gain mechanic and cannot be spent as designed (closes #157). Operator decision: Resolve recovers at a Rally/downtime, capped by Taint -- the recommended option from the two workable alternatives named when #157 was raised."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolve is genuinely spendable, at every Taint above 0 (Priority: P1)

A player whose character has accrued any Taint at all wants Resolve to actually be a resource
they can spend, not a value permanently stuck at 0.

**Why this priority**: This is the exact gap #157 raised — as originally written, Resolve had no
gain trigger at all and could never rise above its creation value of 0.

**Independent Test**: Read `docs/design/03-rules.md` §4's Resolve rule; confirm it states a gain
trigger, a spend amount, and a bonus.

**Acceptance Scenarios**:

1. **Given** a character with Taint above 0, **When** a Rally occurs, **Then** Resolve rises by 1
   toward its cap (current Taint plus 3).
2. **Given** a character at a downtime, **When** the downtime resolves, **Then** Resolve returns
   to its cap.
3. **Given** a character with positive Resolve, **When** they spend 1 after a failed roll,
   **Then** they gain a +20 bonus to an immediate reroll of that test.

### User Story 2 - The Spent state is reachable through ordinary play, not only before anything has happened (Priority: P1)

Someone reading "Resolve fallen to equal Taint" wants that state to actually occur during play,
for a character who has accrued real experience — not only, vacuously, at Taint 0.

**Why this priority**: The original gap made Spent unreachable in the way it was clearly meant to
represent (a character worn down by what happened to them); this fixes exactly that.

**Independent Test**: Run `specs/052-resolve-recovery-mechanic/check_resolve.py`; confirm it
proves Spent is reachable by spending down from a full rest at every Taint above 0, and never
reachable at Taint 0.

**Acceptance Scenarios**:

1. **Given** a character at any Taint above 0, **When** they spend their full post-recovery
   Resolve headroom, **Then** they reach exactly the Spent condition (Resolve equals Taint).
2. **Given** a character at Taint 0, **When** their Resolve is spent down to 0, **Then** they are
   never Spent, per the stated exception.

### Edge Cases

- Does a naive "cap equals Taint exactly, no margin" design work? No — checked and rejected
  during design: it puts a fully-rested character exactly at the Spent boundary, with nothing
  positive ever spendable without going below Taint. `check_resolve.py` proves this concretely
  rather than only asserting it in the ADR's prose.
- Does Resolve's spend overlap with Fortune's, recreating the fault Luck and Fortune had before
  ADR 0041? No — Fortune's reroll carries no bonus; Resolve's does (+20), a genuine functional
  distinction stated explicitly in both `03-rules.md` and ADR 0043.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `docs/design/03-rules.md` §4 MUST state Resolve's gain trigger (Rally/downtime,
  matching ADR 0020's existing rate), its cap formula (current Taint plus 3), and its spend
  (1 Resolve for a +20 reroll bonus).
- **FR-002**: The cap formula MUST leave real, positive headroom above Taint at every Taint value
  above 0, so Spent is reachable through play rather than already true at full rest.
- **FR-003**: Taint 0 MUST remain exempt from Spent, as an explicitly stated rule, not left to
  arithmetic that could otherwise make it reachable there too.
- **FR-004**: A verification script MUST prove the chosen formula avoids the naive alternative's
  failure mode (cap exactly equal to Taint), not merely assert it in prose.
- **FR-005**: A new ADR MUST record the decision, including the rejected naive first draft found
  during design, per CLAUDE.md's own test for when a decision earns a record.

### Key Entities

*(none — this feature fixes an existing track's mechanic, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/03-rules.md` §4 states all three previously-missing pieces (gain,
  spend amount, bonus) explicitly.
- **SC-002**: `python3 specs/052-resolve-recovery-mechanic/check_resolve.py` passes, proving real
  headroom exists at every Taint 0-20 and Spent is reachable at every Taint above 0.
- **SC-003**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.
- **SC-004**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- This feature carries a real ADR (0043) since two workable alternatives were rejected (Resolve
  rising with Taint directly; a plain-reroll spend matching Fortune's) and a real design flaw was
  caught and corrected in the chosen shape's own first draft.
- No follow-up playtest is required by this feature — the next condition-tracks-adjacent playtest
  (if any) should confirm the corrected mechanic plays as described, per ADR 0043's own
  Consequences, but that confirmation is not blocking this fix.
