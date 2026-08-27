# Feature Specification: Widen Resolve to counter both Taint and Trauma

**Feature Branch**: `185-resolve-dual-threshold`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Widen Resolve to counter both Taint and Trauma, via a dual threshold (closes #185, part of epic #1). Trauma has no counterweight; investigated a dedicated new track vs widening Resolve; widening chosen since a dedicated track would double the spendable +20-reroll currency with no balance justification."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolve's cap and Spent state respond to whichever of Taint or Trauma is worse (Priority: P1)

A character whose Trauma outweighs their Taint should have Resolve behave sensibly against
Trauma, not silently ignore it because the formula only ever looked at Taint.

**Why this priority**: This is the actual gap #185 raised — Taint and Fate both have a
counterweight, Trauma has none.

**Independent Test**: Read `03-rules.md` §4's restated cap/Spent rule; confirm it reads
`max(Taint, Trauma) + 3` and Spent triggers via whichever axis is higher.

**Acceptance Scenarios**:

1. **Given** a character with Trauma higher than Taint, **When** Resolve is computed, **Then**
   its cap and Spent threshold are governed by Trauma, not Taint.
2. **Given** a character with Taint higher than Trauma, **When** Resolve is computed, **Then**
   the formula behaves exactly as ADR 0043 originally specified — no regression on the
   already-covered case.

### User Story 2 - Each axis's zero-exemption is independent (Priority: P1)

A character with Taint 0 but nonzero Trauma should still be able to reach Spent via Trauma, and
vice versa; a character with both at 0 should never be Spent.

**Why this priority**: The original Taint-0 exemption's own stated reason ("nothing yet for
Resolve to be a counterweight to") applies per-axis, not only to Taint.

**Independent Test**: Read `check_resolve.py`'s exemption checks; confirm both single-axis cases
and the both-zero case are verified independently.

**Acceptance Scenarios**:

1. **Given** Taint 0 and Trauma 8, **When** Resolve falls to 8, **Then** Spent triggers via
   Trauma.
2. **Given** Taint 8 and Trauma 0, **When** Resolve falls to 8, **Then** Spent triggers via
   Taint.
3. **Given** Taint 0 and Trauma 0, **When** Resolve falls to 0, **Then** Spent never triggers.

### Edge Cases

- Does this add a new track? No — a dedicated track ("Composure") was investigated and rejected;
  it would double the total spendable +20-reroll currency with no balance justification.
- Does this change Resolve's recovery cadence, spend amount, or distinction from Fortune? No —
  only the cap formula and Spent trigger change.
- Is Spent, once reached, a persisting state or a one-instant boundary crossing? Persisting — a
  bug in the check script's own first draft (exact-equality `is_spent`) was caught and fixed to
  "at or below," since Resolve spent past a threshold must still read Spent, not only the exact
  instant it lands on the threshold.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `03-rules.md` §4 MUST state Resolve's cap as `max(Taint, Trauma) + 3`.
- **FR-002**: Spent MUST trigger when Resolve falls to at or below whichever of Taint or Trauma
  is higher.
- **FR-003**: Each axis's zero-exemption MUST be independent — Taint 0 exempts only
  Spent-via-Taint, Trauma 0 exempts only Spent-via-Trauma.
- **FR-004**: A real, workable rejected alternative exists (a dedicated new track), so this
  decision MUST be recorded as a superseding ADR (ADR 0043 is Accepted and merged, cannot be
  edited in place).
- **FR-005**: `check_resolve.py` MUST verify the dual-threshold formula and both exemptions
  across a representative range, including the Trauma-higher case ADR 0043's own verification
  never exercised.
- **FR-006**: A playtest section MUST demonstrate the corrected formula with a worked character,
  including the Trauma-higher case.

### Key Entities

*(none — this feature is a rules correction plus a playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: ADR 0049 supersedes ADR 0043, including the rejected dedicated-track alternative
  and the resource-economy reasoning against it.
- **SC-002**: `03-rules.md` §4 states the dual-threshold cap and per-axis Spent exemption.
- **SC-003**: `check_resolve.py` passes, verifying the dual-threshold formula, both exemptions,
  and the Trauma-higher case, at a representative range of Taint/Trauma combinations.
- **SC-004**: A new playtest section works through a character where Trauma is the binding
  threshold, with real rolls where a roll is actually involved.
- **SC-005**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (no new
  finding class), and `python3 -m pytest -q` pass.

## Assumptions

- No change to Resolve's recovery cadence, spend amount, or distinction from Fortune.
- No change to Taint's or Trauma's own accrual rules — only what bounds Resolve's cap and
  triggers Spent.
- Documentation-only: no engine code changes; the verification script is a design artefact under
  `specs/`, matching this repo's established precedent.
