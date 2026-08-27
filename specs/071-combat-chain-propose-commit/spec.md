# Feature Specification: Specify the attack → damage → armour → critical chain through propose/commit

**Feature Branch**: `200-combat-chain-propose-commit`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Specify the attack -> damage -> armour -> critical chain through propose/commit (closes #200, part of #192). Found while writing #195's worked example: neither #193 (single roll) nor #194 (threshold-triggered cascades specifically) covers an outcome-conditional follow-on roll like attack hits -> roll damage. Decide whether this generalises #194's own mechanism (trigger widened from 'crosses a threshold' to 'the outcome calls for it') or needs a distinct treatment, and work through a full combat exchange."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A landed attack's full consequence chain resolves in one proposal (Priority: P1)

A GM proposes a combat attack or defence roll. If it lands, the weapon damage, armour reduction,
resulting Stamina mutation, and any critical it triggers should all resolve in the same
proposal, without prose separately noticing each step.

**Why this priority**: This is the actual gap #195's own worked example ran into and
deliberately avoided rather than silently assumed handled.

**Independent Test**: Given a `combat-attack`/`combat-defence` step that lands, the returned
proposal includes the damage roll, the armour roll, the resulting Stamina mutation, and (if it
crosses below 0) a critical step and its own mutation — all staged in one call.

**Acceptance Scenarios**:

1. **Given** a landed blow, **When** `propose` returns, **Then** damage and armour are staged as
   dependent steps, and the Stamina mutation they combine into is checked against the
   below-`0` threshold exactly like any other mutation under cascading resolution.
2. **Given** the attack's own `degrees` cross 6 (a telling blow, read from the same roll data
   `propose` already returns, no separate roll), **When** damage resolves, **Then** the weapon
   roll is doubled before armour, per `03-rules.md` §2's stated order.

### User Story 2 - The general mechanism, not a special case (Priority: P1)

Whether this reuses cascading resolution's existing mechanism (generalised) or needs its own
treatment was the open question #200 raised.

**Why this priority**: Answering it wrong either invents a redundant second mechanism, or
silently stretches the existing one past what it actually said.

**Independent Test**: Read the restated "Cascading resolution" section; confirm it names two
distinct trigger shapes (a mutation crossing a threshold; a roll's own outcome calling for a
further roll) under one staging mechanism, rather than two separate mechanisms.

**Acceptance Scenarios**:

1. **Given** the two trigger shapes, **When** compared, **Then** both stage identically (as
   further steps in the same proposal, with `depends_on` edges) — only what triggers them
   differs.

### Edge Cases

- Does this earn an ADR? No — it generalises cascading resolution's own already-accepted trigger
  condition (ADR 0050's reasoning already covers "remove freehand chain-following from prose");
  no new decision with a genuine rejected alternative distinct from what's already decided.
- Is Aftermath now staged immediately too? No — unchanged; it remains deliberately deferred to
  after the fight, per cascading resolution's own existing statement.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Cascading resolution MUST be restated to name two trigger shapes explicitly: a
  mutation crossing a threshold, and a roll's own outcome calling for a further roll — both
  staging identically.
- **FR-002**: A landed attack MUST stage a dependent damage-roll step and a dependent
  armour-roll step, both depending on the landing step.
- **FR-003**: Telling blow MUST be read from the landing step's own `degrees` (or the
  virtual-roll degrees for a failed defence, per ADR 0044) — no separate roll.
- **FR-004**: The combined Stamina mutation MUST be checked against the below-`0` threshold using
  the same mechanism as any other threshold crossing (Taint, Trauma), staging a critical step on
  a crossing.
- **FR-005**: `02-architecture.md`'s CLI sketch MUST reflect that combat resolves through
  `propose`, not a separate `damage` verb.

### Key Entities

*(none new — reuses the step/mutation/`depends_on` entities already defined)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/31-action-resolution.md`'s "Cascading resolution" section states both
  trigger shapes.
- **SC-002**: A new "The combat resolution chain" subsection specifies the attack/damage/
  armour/critical mapping concretely.
- **SC-003**: A worked example, reusing the real rolls already verified in §7/§14 of the
  playtest transcript, shows the full chain staged in one proposal, matching those sections'
  own hand-worked figures exactly.
- **SC-004**: `02-architecture.md` no longer lists a separate `wyrd damage` verb.
- **SC-005**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- No ADR: generalises ADR 0050's and #194's already-accepted reasoning, not a new decision.
- This is a design specification, not an implementation.
- The worked example reuses already-verified real rolls (§7/§14) rather than inventing fresh
  dice for a scenario already played and re-checked twice.
