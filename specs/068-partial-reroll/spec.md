# Feature Specification: The dependency-graph partial-reroll mechanism

**Feature Branch**: `195-partial-reroll`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Design the dependency-graph partial-reroll mechanism (closes #195, depends on #193, part of #192). A reroll request against one step in a proposed batch must discard exactly what's causally downstream of it and nothing else. Work through a worked example where an independent branch survives a reroll elsewhere in the same batch."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rerolling one step discards only what depends on it (Priority: P1)

A player spends a reroll resource against one specific staged step. Only that step and whatever
causally depends on it should be discarded and re-resolved; an independent branch in the same
batch must survive untouched.

**Why this priority**: This is the actual gap #193/#194 left open — those specify staging and
cascading, but neither addresses what happens when a player wants to redo part of what's staged.

**Independent Test**: Given a proposal with two independent steps, rerolling one and checking the
other's result is byte-identical to what `propose` originally returned for it.

**Acceptance Scenarios**:

1. **Given** a proposal with two steps that don't depend on each other, **When** one is
   rerolled, **Then** the other's roll data and mutations are unchanged from the original
   proposal.
2. **Given** a proposal where step B depends on step A (a cascade), **When** step A is
   rerolled, **Then** step B is discarded and freshly re-resolved from the new outcome of A —
   never left stale against an outcome that no longer produced it.

### User Story 2 - The reroll resource's own cost is staged alongside the re-resolution (Priority: P1)

Spending Fortune, Resolve, or the Bargain has its own cost (a point spent, or Taint gained) —
this needs to be part of the same staged proposal, not a separate call.

**Why this priority**: Otherwise the resource spend and the reroll it buys could desynchronize —
committed independently, or one without the other.

**Independent Test**: After a reroll, the proposal's mutations include the resource's own cost
alongside whatever the re-resolved step(s) produce.

**Acceptance Scenarios**:

1. **Given** a reroll via the Bargain, **When** the revised proposal is returned, **Then** its
   mutations include the Bargain's own Taint cost in addition to whatever the rerolled step
   produces.

### Edge Cases

- Does reroll invalidate the proposal id? No — the proposal stays open, revised in place; only
  `commit` or `discard` ends it.
- Can a rerolled step cascade again? Yes — a freshly-resolved step is checked against cascading
  resolution's own threshold rule exactly as it would be the first time.
- Does this feature address attack → damage-style outcome-conditional chains (as opposed to
  track-threshold cascades)? No — that remains an open question outside this feature's and
  #194's stated scope, not silently assumed resolved here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `reroll` MUST take a proposal id, a target step, and the reroll resource being
  spent.
- **FR-002**: `reroll` MUST compute the downstream set — the target step and every step that
  transitively depends on it via `depends_on` — and discard exactly that set.
- **FR-003**: Every step outside the downstream set MUST remain exactly as originally staged.
- **FR-004**: The target step MUST be freshly re-resolved under the reroll resource's own
  modifier (Resolve's `+20`, Fortune's plain reroll, the Bargain's plain reroll for Taint).
- **FR-005**: The resource's own cost MUST be staged as a mutation on the revised proposal.
- **FR-006**: A freshly-resolved step MUST be checked against cascading resolution's threshold
  rule exactly as `propose` would check it.
- **FR-007**: `reroll` MUST NOT invalidate the proposal id — the proposal remains open until
  `commit` or `discard`.

### Key Entities

*(none new — reuses the proposal/step/mutation entities #193/#194 already define)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/31-action-resolution.md` gains a "Partial reroll" section specifying
  the mechanism concretely.
- **SC-002**: A worked example (two independent Exposure tests in one proposal, one rerolled via
  the Bargain) shows the untouched branch is byte-identical to its original result.
- **SC-003**: The worked example uses real seeded rolls, including an honest reroll outcome
  (still fails), not a cherry-picked success.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- No ADR: a direct extension of ADR 0050 and #194's already-established reasoning, consuming the
  `depends_on` graph #194 already specifies, not a new fork.
- This is a design specification, not an implementation.
- Combat's own outcome-conditional chain (attack succeeding implies a damage roll) is explicitly
  NOT addressed by this feature or by #194 — noted as an open question for a future pass, not
  silently assumed covered.
