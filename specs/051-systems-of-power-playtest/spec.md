# Feature Specification: Systems-of-power balance playtest

**Feature Branch**: `051-systems-of-power-playtest`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Systems-of-power balance playtest (closes #151, part of the playtest epic #134). Dedicated balance scrutiny: cost, intensity tiers, and Ill Omen consequences under ordinary and sustained/optimised (minmaxing) use, compared against a non-user."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ordinary use of a system of power costs and risks what the schema states (Priority: P1)

Someone reading `09-systems-of-power.md`'s worked example wants to see it actually played:
cost paid win-or-lose, an Ill Omen feeding the existing Taint-accrual path.

**Why this priority**: Confirms the baseline mechanic plays as documented before stress-testing it.

**Independent Test**: Read the new section's "Ordinary use" subsection; confirm cost and any
Ill Omen consequence match `09-systems-of-power.md`'s stated rule exactly.

**Acceptance Scenarios**:

1. **Given** a trained practitioner invoking a system of power at its `minor` tier, **When**
   played with real dice, **Then** Strain is paid identically on success and failure, and an Ill
   Omen (if any) applies the declared Taint through the existing accrual path.

### User Story 2 - A deliberate minmax attempt surfaces whether the cost structure actually discourages spam (Priority: P1)

Someone worried that a player could exploit systems of power by repeatedly declaring the most
ambitious tier and not caring about failure wants to see that tested directly, with real dice,
not argued from the rules text alone.

**Why this priority**: This is the operator's own explicit special-focus request — game balance
around systems of power — and the exact class of exploit a single-mechanic check couldn't surface
(it requires playing a sustained sequence, not computing one roll's probability).

**Independent Test**: Read the new section's "Minmax" subsection; confirm a real, honestly-reported
sequence of repeated high-tier invocations is played, with every roll shown, not a curated
handful chosen to make a point.

**Acceptance Scenarios**:

1. **Given** a character spamming the highest intensity tier repeatedly with no Rally in between,
   **When** played to a natural stopping point (not cut short to avoid an inconvenient result),
   **Then** the actual cost/consequence accumulation is reported honestly, including if it turns
   out to be smaller or larger than expected.
2. **Given** the sequence played out, **When** a genuine gap is found in what discourages the
   spam, **Then** it is reported as a finding and raised as its own follow-up issue, not silently
   fixed inline or omitted.

### User Story 3 - The Resolve gap (#157) is checked for recurrence, not re-derived from scratch (Priority: P2)

Since `09-systems-of-power.md`'s own worked example declares a `resolve_cost`, and #149 already
found Resolve has no gain mechanic, this playtest should confirm whether that gap recurs here
rather than silently avoiding it.

**Why this priority**: #162 (the cross-playtest findings review) explicitly asks whether a
finding recurs across more than one playtest — this is exactly that check, done at the point of
contact rather than deferred.

**Independent Test**: Read the new section's "The Resolve gap recurs" subsection; confirm it
states plainly that a system of power with a declared `resolve_cost` hits the same #157 blocker.

**Acceptance Scenarios**:

1. **Given** a system of power declared with `resolve_cost` (the schema's own worked example),
   **When** an invocation is attempted, **Then** the same Resolve-has-no-gain-mechanic gap #149
   found is confirmed to recur, with an explicit cross-reference rather than re-deriving it as if
   new.

### Edge Cases

- Is the minmax sequence cut short once it's "made the point"? No — it continues to a genuine
  stopping condition (enough invocations to observe both the un-widened and Taint-widened Ill
  Omen bands), with every roll disclosed, matching the honest-sampling discipline #148/#149
  established.
- Does this playtest fix the cost-structure gap it finds? No — per #134's Definition of Done, a
  real balance gap with more than one workable mitigation is raised as its own follow-up issue
  (#163), not decided inside the playtest record.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playtest MUST use real seeded random rolls throughout, matching the established
  discipline.
- **FR-002**: The playtest MUST exercise ordinary use, a sustained minmax sequence at the highest
  intensity tier, and a comparison against a non-user, per #151's own scope.
- **FR-003**: Any genuine balance gap found in the cost/consequence structure MUST be reported as
  a finding and raised as its own follow-up issue, not fixed inline.
- **FR-004**: The playtest MUST explicitly check whether the Resolve gap (#157) recurs when a
  system of power's `resolve_cost` field is exercised, rather than avoiding the field to sidestep
  a known issue.

### Key Entities

*(none — this feature is a worked playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section covering ordinary use,
  a minmax sequence, and a non-user comparison, following the existing document's established
  structure and tone.
- **SC-002**: Every roll in the new section traces to a real `python3 random` draw, seeded, in a
  stated fixed order, with the full minmax sequence disclosed (no rolls omitted).
- **SC-003**: The cost-structure finding is reported with a follow-up issue raised (#163); the
  Resolve-gap recurrence is reported with a cross-reference to #157.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass,
  with no new finding class introduced.
- **SC-005**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- This feature carries no ADR of its own — the cost-structure gap's eventual resolution belongs
  to #163's own follow-up, not this playtest record.
- The new character (Kester) reuses `09-systems-of-power.md`'s own worked example (`ember-craft`)
  rather than inventing a new one, since the document's own example is already
  setting-agnostic and this playtest's job is to test the schema, not invent new flavor.
- Documentation-only: no code changes; the roll-generation script is scratch tooling, not
  committed, matching the established precedent.
