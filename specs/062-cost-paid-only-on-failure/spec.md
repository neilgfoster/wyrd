# Feature Specification: Systems-of-power costs paid only on a failed invocation

**Feature Branch**: `180-cost-paid-only-on-failure`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "raise feature + adr etc. resolve should follow strain and be consistent with rest of system as you have found. Ensure changes are reflect back through all of design, and include another playtest to prove the impact of the changes anywhere this change may impact (closes #180, part of the playtest epic #134)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Strain and Resolve costs match the rest of the engine's failure-driven model (Priority: P1)

Systems of power currently cost Strain/Resolve win-or-lose — the only mechanism in the engine
that does. Strain's own generic definition (`03-rules.md` §5) is already failure-driven. A
character should not pay for a system of power they used successfully.

**Why this priority**: This is the actual design smell raised in conversation: a competent,
mostly-successful caster accrues Strain invisibly through every success, with nothing at the
table signalling it, until a single failure (correctly, per ADR 0047) charges the whole backlog.

**Independent Test**: Read `09-systems-of-power.md`'s Resolution section and both worked
examples; confirm cost is stated as paid only on failure, for both `strain_cost` and
`resolve_cost`.

**Acceptance Scenarios**:

1. **Given** a successful invocation with a declared `strain_cost`/`resolve_cost`, **When** it
   resolves, **Then** neither field is paid.
2. **Given** a failed invocation, **When** it resolves, **Then** both declared fields are paid in
   full, exactly as before.

### User Story 2 - resolve_cost follows strain_cost's timing, not diverging from it (Priority: P1)

The operator's own direction: Resolve should be consistent with the rest of the system, not left
win-or-lose while Strain becomes failure-only.

**Why this priority**: Two cost fields on the same schema, timed differently with no stated
reason, is the exact class of unexamined inconsistency this repo's own review passes keep
finding and correcting.

**Independent Test**: Read ADR 0048's Decision section and `check_spam_brake.py`'s
`resolve_cost`-timing check; confirm both fields share the same failure-only rule.

**Acceptance Scenarios**:

1. **Given** a system of power with both `strain_cost` and `resolve_cost` declared, **When**
   invocations succeed and fail across a run, **Then** Resolve is spent exactly once per failure
   and never on a success — matching Strain's own pattern exactly.

### User Story 3 - Every playtest scenario this change touches is re-derived with real rolls (Priority: P1)

The operator's own direction: reflect the change back through design and prove its impact with
another playtest, not just restate the rule.

**Why this priority**: Every prior fix in this thread (#178→ADR 0047, this feature→ADR 0048) has
been verified against the exact sequences already on record, not asserted from arithmetic alone.

**Independent Test**: Read the new playtest section; confirm it replays the major/minor-tier
spam sequences, the "ordinary use" worked example, and the Resolve-recurrence check, all with
real seeded rolls, without editing any prior section's text.

**Acceptance Scenarios**:

1. **Given** the exact seeds already on record (`20260842`, `20260850`, `20260841`), **When**
   replayed under the corrected cost timing, **Then** the resulting figures are computed, not
   asserted, and compared directly against the prior (win-or-lose) figures.

### Edge Cases

- Does this change the schema fields themselves, or ADR 0036's "one configurable mechanism"
  decision? No — only when `strain_cost`/`resolve_cost` are paid.
- Does this re-litigate ADR 0047's cumulative-Strain-crossing check? No — that stays adopted as
  general-purpose correctness, even though the specific scenario that motivated it can no longer
  arise through `strain_cost` once cost is failure-only.
- Does this edit any prior playtest section's text? No — a new section states the corrected
  figures, cross-referencing them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `09-systems-of-power.md` MUST state that `strain_cost` is paid only on a failed
  invocation.
- **FR-002**: `09-systems-of-power.md` MUST state that `resolve_cost` follows the same
  failure-only timing as `strain_cost`.
- **FR-003**: Both worked examples in `09-systems-of-power.md` MUST be corrected to reflect
  failure-only cost.
- **FR-004**: A real, workable rejected alternative exists (keep win-or-lose; split
  Strain/Resolve timing), so this decision MUST be recorded as an ADR.
- **FR-005**: `check_spam_brake.py` MUST be updated for failure-only accrual and re-verify every
  property it already established, plus a direct win-or-lose-vs-failure-only comparison on the
  exact sequences already on record.
- **FR-006**: A new playtest section MUST replay the major/minor-tier spam sequences, the
  "ordinary use" worked example, and the Resolve-recurrence check under the corrected timing,
  with real seeded rolls, without editing prior sections.

### Key Entities

*(none — this feature is a rules correction plus a playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: ADR 0048 records the decision, including the rejected alternatives.
- **SC-002**: `09-systems-of-power.md`'s Resolution section and both worked examples state
  failure-only cost for both fields.
- **SC-003**: `check_spam_brake.py`'s full assertion suite passes, including the new
  win-or-lose-vs-failure-only comparison matching ADR 0048's own quantified figures (major tier
  34→30, minor tier 8→2, raw Trauma).
- **SC-004**: A new playtest section states the corrected figures for every affected scenario,
  with real seeded rolls.
- **SC-005**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (no new
  finding class beyond the already-accepted Omen/Very-Hard/Senna-Vask pattern), and
  `python3 -m pytest -q` pass.

## Assumptions

- Reuses the exact seeds already on record (`20260842`, `20260850`, `20260841`, plus the
  "ordinary use" example's own three rolls), so the corrected figures are directly comparable to
  the ones the win-or-lose rule produced.
- Documentation-only: no engine code changes.
