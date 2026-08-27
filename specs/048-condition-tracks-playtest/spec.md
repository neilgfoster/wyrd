# Feature Specification: Condition-tracks playtest

**Feature Branch**: `048-condition-tracks-playtest`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Condition-tracks playtest (closes #149, part of the playtest epic #134). Extends the established discipline (real seeded rolls) to Taint (both gain routes, a threshold crossing, the hidden threshold, the Fault Line's bias), Trauma (the sawtooth to an Affliction), Strain (accrual and Rally recovery), and Resolve/Spent."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Taint, Trauma and Strain are proven end to end with real dice (Priority: P1)

Someone who has read the individually-computed checks for Taint thresholds, the affliction
sawtooth, and the Fault Line's bias wants to see them play out together, across one character's
arc, with real dice — not asserted from separate proofs.

**Why this priority**: This is #134's own purpose — proving mechanics in combination, not only
individually.

**Independent Test**: Read the new section in `docs/design/30-playtest-transcript.md`; confirm
both Taint gain routes (Bargain and Exposure), a threshold crossing with its Transformation roll,
the first-Transformation hidden-threshold roll, the Fault Line's one-tier bias applied to exactly
the Exposure event it should apply to, the Trauma sawtooth reaching an Affliction, and Strain's
Rally recovery are all present with real, seeded dice.

**Acceptance Scenarios**:

1. **Given** a scene where the first real roll attempted succeeds, **When** the Bargain still
   needs demonstrating, **Then** further real attempts are made and all are reported, not just
   the one that finally failed.
2. **Given** an Exposure event that runs with the character's Fault Line, **When** it fails,
   **Then** its tier is bumped exactly one step worse, and a second, unrelated Exposure event does
   not receive the same bias.
3. **Given** Taint crosses a threshold, **When** the resulting Transformation roll's severity
   does not drop Taint below the threshold in one roll, **Then** the re-roll loop continues until
   it does (not exercised in the actual run here, since the first roll sufficed, but the logic is
   stated in case a future re-run needs it).

### User Story 2 - A genuine specification gap in Resolve is found and reported, not invented around (Priority: P1)

If the playtest cannot actually exercise a mechanic because the mechanic itself is
underspecified — not because the scene didn't call for it — that gap is named plainly rather than
papered over with an invented amount or trigger.

**Why this priority**: #134's own Definition of Done requires correcting or explicitly justifying
every fault found; inventing a plausible-sounding Resolve mechanic to make the playtest look
complete would be exactly the kind of undocumented decision this repo's recurring-fault list
warns against.

**Independent Test**: Read the new section's Findings subsection; confirm it states the two
missing pieces (a gain trigger, and the spend amount/bonus size) precisely, explains why this
makes the mechanic currently non-functional as written, and confirms a follow-up issue was raised
rather than a mechanic being invented inline.

**Acceptance Scenarios**:

1. **Given** Resolve starts at 0 with no stated gain trigger anywhere in `docs/design/` or
   `docs/adr/`, **When** the playtest reaches the point where Resolve/Spent should be exercised,
   **Then** it reports plainly that this cannot be demonstrated as written, rather than
   substituting an invented value.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playtest MUST use real seeded random rolls throughout, matching #147/#148's
  established discipline.
- **FR-002**: Where a scene needs a specific outcome a mechanic requires (a failure, to
  demonstrate the Bargain; 6+ Trauma, to reach the Affliction test), further real attempts MUST
  be made and every attempt reported — never a single curated roll standing in for a needed
  outcome, and never a discarded attempt.
- **FR-003**: The playtest MUST exercise both Taint gain routes, a threshold crossing and its
  Transformation roll, the first-Transformation hidden-threshold roll, the Fault Line's bias
  applied correctly to only the Exposure event it should apply to, the Trauma sawtooth to an
  Affliction, and Strain accrual with a Rally recovery.
- **FR-004**: If Resolve cannot be demonstrated because its own specification lacks a gain
  trigger and spend amount, this MUST be reported as a finding, not resolved by inventing a
  mechanic inline.
- **FR-005**: A follow-up issue MUST be raised for the Resolve gap, per #134's Definition of Done.

### Key Entities

*(none — this feature is a worked playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section covering Taint, Trauma
  and Strain end to end, following the existing document's established structure and tone.
- **SC-002**: Every roll in the new section traces to a real `python3 random` draw, seeded, in a
  stated fixed order, with every repeated-attempt sequence shown in full.
- **SC-003**: The Resolve gap is reported in the Findings subsection with a follow-up issue
  raised (#157).
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass,
  with no new finding class introduced.
- **SC-005**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- This feature carries no ADR of its own — the Resolve gap's eventual resolution belongs to
  #157's own follow-up, not this playtest record.
- Invocation, a second Transformation reaching the hidden threshold, and Dread's own social
  effects are explicitly out of scope for this pass and recorded as such, matching #147/#148's
  own "what this pass does not prove" convention.
- Documentation-only: no code changes; the roll-generation script is scratch tooling, not
  committed, matching the established precedent.
