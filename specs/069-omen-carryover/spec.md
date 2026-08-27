# Feature Specification: Omen carryover across a proposed batch

**Feature Branch**: `196-omen-carryover`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Design Omen carryover across a proposed batch (closes #196, depends on #193, #195, part of #192). An Ill/Fair Omen applies to the roller's own next roll; a batch can contain more than one of one actor's own rolls, and the roll that produced an Omen may later be rerolled and need to unwind correctly."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An Omen produced mid-batch applies to that actor's own next roll, in the same batch (Priority: P1)

Two of one actor's own rolls are proposed together. If the first produces an Ill/Fair Omen, the
second — the actor's own next roll, whatever it's for — must receive the ±10 modifier.

**Why this priority**: This is a stated, existing rule (ADR 0042) that #193/#194/#195 never
addressed once more than one roll could exist in the same proposal.

**Independent Test**: Given a batch with two of one actor's own rolls, the first producing an
Omen, the second's effective% reflects the ±10 modifier.

**Acceptance Scenarios**:

1. **Given** step 0 produces a Fair Omen, **When** step 1 (the same actor's next roll) resolves,
   **Then** its effective% includes the +10 modifier.
2. **Given** a third roll of the same actor exists in the batch after the Omen was already
   consumed by step 1, **When** it resolves, **Then** it carries no modifier — the Omen was
   already spent, not renewable within the batch.

### User Story 2 - An Omen can carry from an already-committed proposal into a new one (Priority: P1)

An Omen "lapses unused if the scene or fight ends first" — implying it can persist across more
than one committed proposal, not only within a single batch.

**Why this priority**: The rule as stated is not batch-scoped; treating it as batch-local would
silently narrow an existing rule.

**Independent Test**: Given a committed proposal that left a pending Omen, a later `propose` call
for the same actor applies it to that new proposal's first roll.

**Acceptance Scenarios**:

1. **Given** an actor's persistent state has a non-null `pending_omen`, **When** `propose` is
   called for that actor, **Then** the first roll in the new batch receives the modifier.

### User Story 3 - Rerolling the Omen-producing step correctly unwinds what it produced (Priority: P1)

If the step that produced an Omen is later rerolled (per #195), whatever consumed that Omen must
be re-derived too — not left stale against an Omen that no longer exists, and not silently kept
if the reroll produces a different (or no) Omen.

**Why this priority**: This is the actual hard case the epic was raised to catch — an Ill Omen
persisting or vanishing incorrectly after a reroll would be a real, hard-to-notice bug.

**Independent Test**: Given a batch where step 1 consumed step 0's Omen, and step 0 is rerolled
via #195's mechanism, step 1 is in the downstream set and re-resolves against whatever (if
anything) the reroll actually produces.

**Acceptance Scenarios**:

1. **Given** step 0's reroll produces a different Omen (or none), **When** step 1 re-resolves,
   **Then** it uses the new state, not the original Omen.

### Edge Cases

- Does reading a persistent `pending_omen` at the start of `propose` consume it before commit?
  No — nothing writes until commit, per #193's own rule; a discarded proposal leaves the actor's
  persistent `pending_omen` exactly as it was.
- Is an Omen-consumption dependency the same kind of edge as a mutation dependency? Yes — it uses
  the same `depends_on` mechanism #194/#195 already specify, not a new one.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `propose` MUST apply a pending Omen (from persistent state or from an earlier step
  in the same batch) to the same actor's next roll.
- **FR-002**: A further Omen read before the pending one is spent MUST replace it, never stack.
- **FR-003**: An actor's committed state MUST carry a `pending_omen` field, since the modifier
  can persist across separately committed proposals.
- **FR-004**: Reading `pending_omen` MUST NOT consume it until the proposal that read it commits.
- **FR-005**: A step that consumes another step's Omen MUST record that as a `depends_on` edge,
  reusing cascading resolution's/partial reroll's existing mechanism.
- **FR-006**: Rerolling an Omen-producing step MUST correctly propagate to whatever consumed its
  Omen, via the existing downstream-set mechanism — no new reroll logic.

### Key Entities

- **`pending_omen`** — a field on the actor's persistent state: `null`, `+10`, or `−10`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/31-action-resolution.md` gains an "Omen carryover" section specifying
  the mechanism.
- **SC-002**: `docs/design/22-state.md`'s player-character frontmatter gains the `pending_omen`
  field, since this feature is the first to need it and none of #187–#195 added it.
- **SC-003**: A worked example (real seeded rolls) shows an Omen applying across two of one
  actor's own rolls, then correctly unwinding when the producing step is rerolled — the
  consuming step's result genuinely differs post-reroll, not just relabelled.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- No ADR: consumes the `depends_on` mechanism #194/#195 already specify; the Omen rule itself is
  unchanged (still ±10, still non-stacking, still lapses unused) — only how the engine tracks it
  is new, and that follows directly from #193's own staging model.
- This is a design specification, not an implementation.
