# Feature Specification: Cascading resolution for threshold-triggered sub-rolls

**Feature Branch**: `194-cascading-resolution`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Design cascading resolution for threshold-triggered sub-rolls (closes #194, depends on #193, part of #192). A staged mutation that crosses a threshold (Taint every 3, Trauma past 6, Strain crossing max Stamina) spawns a further sub-resolution inside the same proposed batch, deterministically. Work through a Taint-threshold cascade into a Transformation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A threshold crossing resolves fully within one proposal, without prose noticing it (Priority: P1)

A GM proposes an Exposure test. The failure happens to cross Taint's threshold. The GM should
not have to notice this, compute it, or make a second call — the returned proposal already
contains the Transformation roll and its own consequences.

**Why this priority**: This is the actual freehand work #193's base mechanism didn't yet remove
— a single roll that happens to trigger a rule-mandated further roll still left prose to notice
and act on the crossing.

**Independent Test**: Given a mutation that crosses a track's threshold, the returned proposal
contains the further step(s) that threshold's own rule calls for, and their own resulting
mutations, without a second `propose` call.

**Acceptance Scenarios**:

1. **Given** a staged Taint mutation that crosses a multiple of 3, **When** `propose` returns,
   **Then** the proposal already includes a Transformation roll step and its own mutations
   (Taint reduced by severity, Dread increased by severity, the hidden threshold set if this is
   the first Transformation).
2. **Given** a mutation that does NOT cross any threshold, **When** `propose` returns, **Then**
   no further step is staged — cascading only fires on an actual crossing.

### User Story 2 - The cascade terminates, reusing each track's own existing proof (Priority: P1)

A cascade must not risk looping forever, but this mechanism should not need to reprove
termination from scratch when each affected track's own rule already has a stated bound.

**Why this priority**: Re-deriving termination here would duplicate work `check_transformation.py`
and `08-afflictions.md`'s own sawtooth shape already establish.

**Independent Test**: Read the new section's termination reasoning; confirm it explicitly reuses
each track's own existing bound rather than asserting a new one.

**Acceptance Scenarios**:

1. **Given** the cascading-resolution mechanism as specified, **When** its termination is
   justified, **Then** the justification cites the Transformation hidden-threshold proof and the
   Affliction sawtooth's own bound, not a new proof invented for this mechanism.

### Edge Cases

- Does every consequence cascade into the same proposal? No — a critical rolled the moment
  damage takes a combatant below 0 does NOT spawn an immediate Aftermath step, since Aftermath is
  explicitly deferred to after the fight (`06-aftermath.md`). Cascading resolution only stages
  what a triggering rule itself says happens immediately.
- Does this earn a new ADR? No — it is a direct extension of ADR 0050's own already-stated
  reasoning (removing freehand threshold-noticing work from prose), not a new fork with its own
  rejected alternative distinct from what ADR 0050 already decided.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `propose` MUST check every mutation it stages against its track's own threshold
  rule, and on a crossing, stage the further roll(s) that rule calls for as additional steps in
  the same proposal.
- **FR-002**: A staged cascade step MUST record what it depends on (the mutation that crossed the
  threshold, and the roll that produced that mutation).
- **FR-003**: Cascading MUST support recursion — a sub-roll's own mutation crossing a further
  threshold MUST itself spawn a further step, not just one level deep.
- **FR-004**: Cascading resolution MUST NOT re-derive termination proofs for tracks that already
  have one (Transformation's hidden-threshold loop, the Affliction sawtooth) — it MUST cite them.
- **FR-005**: A consequence a triggering rule itself defers (Aftermath, deferred to after the
  fight) MUST NOT be staged as an immediate cascade step.

### Key Entities

- **Cascade step** — a staged step produced not by the original `propose` call's own action, but
  by a threshold crossing within the same proposal; carries `depends_on` naming the mutation (and
  transitively, the roll) that triggered it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/31-action-resolution.md` gains a "Cascading resolution" section
  specifying the mechanism concretely.
- **SC-002**: A worked example (a Taint-threshold crossing into a Transformation) shows the full
  staged proposal, including both legs' mutations.
- **SC-003**: The worked example reuses real rolls already on record (§8 of the playtest
  transcript), not fresh dice invented for this feature, and states this explicitly.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- No ADR: this is a direct extension of ADR 0050's own reasoning, not a new decision with its own
  distinct rejected alternative.
- This is a design specification, not an implementation.
- The worked example deliberately reuses already-published real rolls (§8, seeded originally) for
  continuity and to avoid re-rolling a scenario already verified, per this repo's own precedent
  for reusing established numbers under a new lens.
