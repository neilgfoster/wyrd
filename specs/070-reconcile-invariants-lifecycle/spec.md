# Feature Specification: Reconcile write invariants and state the transaction lifecycle

**Feature Branch**: `197-reconcile-invariants-lifecycle`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Reconcile write invariants and state the transaction lifecycle (closes #197, depends on #193, #194, #195, #196, part of #192, the wrap-up child). 22-state.md's 'persist precedes narrate' and 'Invariants' section need reconciling against the propose/commit/cascade/reroll/Omen model; the Invariants section is stale against ADR 0049; a transaction lifecycle (an abandoned proposal) needs stating."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - "Persist precedes narrate" is read correctly against the propose/commit model (Priority: P1)

A reader of `22-state.md`'s existing invariant, now that proposals exist, needs to know it
doesn't forbid narrating a *proposed* result — only narrating one as *settled* before it commits.

**Why this priority**: Left unstated, the propose/commit model's own narrate-then-commit flow
reads as a direct contradiction of an invariant that predates it.

**Independent Test**: Read the restated invariant; confirm it distinguishes "narrated as a live
possibility" from "narrated as settled."

**Acceptance Scenarios**:

1. **Given** a proposal not yet committed, **When** a GM describes its stakes to the player,
   **Then** this does not violate "persist precedes narrate," since nothing is being described
   as having already happened.
2. **Given** the same proposal, **When** a GM describes its outcome as final before `commit`,
   **Then** this does violate the invariant.

### User Story 2 - Invariants are correctly reclassified as passive validation or active triggers (Priority: P1)

Several invariants (Taint thresholds, the Trauma test trigger, a tracker at max) are not merely
checked under the propose/commit model — a mutation crossing one of them spawns a further roll,
per cascading resolution (#194). This needs to be stated, not left implicit.

**Why this priority**: Left unstated, a reader would assume every invariant is passive rejection,
when several are actually generative.

**Independent Test**: Read the reclassified list; confirm each invariant is labelled passive
validation or active trigger correctly, matching what `31-action-resolution.md`'s Cascading
resolution section already says about each.

**Acceptance Scenarios**:

1. **Given** the Taint-threshold invariant, **When** classified, **Then** it is stated as an
   active trigger (spawns a Transformation), not passive validation.

### User Story 3 - An abandoned proposal has a stated fate (Priority: P1)

Nothing has said what happens to an open, uncommitted proposal if a session ends before it's
confirmed or discarded.

**Why this priority**: Without a stated default, an implementation would have to guess.

**Independent Test**: Read the transaction-lifecycle statement; confirm it names where an
abandoned proposal is recorded and when it's cleared.

**Acceptance Scenarios**:

1. **Given** a session ending mid-beat with an open proposal, **When** the transaction lifecycle
   is checked, **Then** it states the proposal is recorded in `chronicle.yaml`'s existing
   `pending.rolled` field, cleared at the next Rally — reusing existing infrastructure, not a
   new mechanism.

### Edge Cases

- Is the Spent formula in `22-state.md`'s Invariants section still accurate? No — it predates
  ADR 0049's dual-threshold widening; corrected here since this feature is reconciling this
  exact section anyway.
- Does `02-architecture.md`'s CLI sketch include `wyrd reroll`? It was missing — added here,
  since #195 specified the mechanism but never updated the sketch.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `22-state.md`'s "persist precedes narrate" invariant MUST be restated to
  distinguish narrating a proposal from narrating a settled result.
- **FR-002**: `22-state.md`'s Invariants section MUST classify each invariant as passive
  validation or active trigger.
- **FR-003**: The Spent formula in `22-state.md`'s Invariants section MUST be corrected to ADR
  0049's dual-threshold formula.
- **FR-004**: A transaction lifecycle for an abandoned proposal MUST be stated, reusing
  `chronicle.yaml`'s existing `pending.rolled` field rather than inventing a new mechanism.
- **FR-005**: `02-architecture.md`'s CLI sketch MUST include `wyrd reroll`, which #195 specified
  but never added to the sketch.

### Key Entities

*(none new — reconciles existing entities' documentation)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `22-state.md`'s Invariants section reads consistently with
  `31-action-resolution.md`'s propose/commit/cascade/reroll/Omen model.
- **SC-002**: The Spent formula matches ADR 0049 exactly.
- **SC-003**: The transaction lifecycle is stated, reusing `pending.rolled`.
- **SC-004**: `02-architecture.md`'s CLI sketch includes `wyrd reroll`.
- **SC-005**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- No ADR: this reconciles existing documents against decisions already made (ADR 0050, #194,
  #195, #196, ADR 0049), it does not make a new one.
- This is a design specification, not an implementation.
