# Feature Specification: Solo procedures and session/campaign structure playtest

**Feature Branch**: `053-solo-procedures-playtest`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Solo procedures and session/campaign structure playtest (closes #152, part of the playtest epic #134). Extends the established discipline to a full session shape, an oracle consultation of each family, a companion beat, a journey leg, and Fortune's actual refresh trigger (corrected from the epic's original arc-boundary expectation, stale since #137)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Solo-play procedures play cleanly across one session (Priority: P1)

Someone who has read the individually-specified oracle tables, companion mechanics, and journey
rules wants to see them play out together across one session, the way an actual chronicle would
use them.

**Why this priority**: This is #134's own purpose — proving mechanics in combination across a
session-shaped sequence, not only individually.

**Independent Test**: Read the new section; confirm the session loop, an oracle-answer
consultation, an oracle-prompt consultation, a companion beat exercising Bond/Tension, and a
journey leg with a hazard roll are all present with real, seeded dice.

**Acceptance Scenarios**:

1. **Given** a beat played to a natural close, **When** the session loop's Rally step resolves,
   **Then** Strain and Stamina both recover 1, and state is committed.
2. **Given** an oracle-bound question (a yes/no fact the fiction hasn't settled, that could
   plausibly be asked again), **When** an answer oracle is consulted, **Then** the GM's declared
   likelihood band and the roll together produce a result matching `14-oracle-answers.md`'s
   published table.
3. **Given** a companion event that would raise Tension and names a specific companion with a
   positive Bond, **When** the event resolves, **Then** the Tension added is reduced per
   `16-session.md`'s Bond table exactly.

### User Story 2 - A stale scope assumption is caught and corrected, not played against a rule that no longer exists (Priority: P2)

The epic's own original decomposition (#134, written before #137's Luck/Fortune merge) expected
this pass to confirm Fortune resets at a top-level arc boundary — Luck's old behaviour, retired
when Luck merged into Fortune.

**Why this priority**: Playing against a stale expectation would either silently fail or produce
a misleading finding; catching and correcting it is itself worth recording.

**Independent Test**: Read the new section's "Fortune's actual refresh" subsection; confirm it
states the original expectation, why it's stale, and what the current rule actually is.

**Acceptance Scenarios**:

1. **Given** the epic's original scope description, **When** compared against the current state
   of `03-rules.md` §3, **Then** the mismatch (arc-boundary vs. daily) is stated explicitly, not
   silently substituted without explanation.

### Edge Cases

- Is succession (a character dying, being lost, or retiring) played here? No — forcing it to fit
  the playtest's schedule would mean manufacturing a death or loss rather than letting one arise
  from play, which is exactly the kind of curated outcome this document's own dice discipline
  exists to avoid. Recorded as untested rather than faked.
- Is every downtime undertaking played? No — only Mend (from an earlier downtime, not detailed in
  this section). Recover, Cultivate, Learn and Ask remain untested by this document.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playtest MUST use real seeded random rolls throughout, matching the established
  discipline.
- **FR-002**: The playtest MUST exercise a full session-loop shape ending at a Rally, an
  oracle-answer consultation, an oracle-prompt consultation, a companion beat exercising Bond's
  offset of Tension, and a journey leg with a hazard roll.
- **FR-003**: Where the epic's own original scope description has gone stale (Fortune's refresh
  trigger, superseded by #137), the playtest MUST state the discrepancy explicitly rather than
  silently substitute the current behaviour without explanation.
- **FR-004**: Succession MUST NOT be forced to fit this playtest's schedule — if no death, loss,
  or retirement arises organically, it is recorded as untested, not manufactured.

### Key Entities

*(none — this feature is a worked playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section covering the session
  loop, both oracle families, a companion Bond/Tension interaction, and a journey hazard roll,
  following the existing document's established structure and tone.
- **SC-002**: Every roll in the new section traces to a real `python3 random` draw, seeded, in a
  stated fixed order.
- **SC-003**: The stale Fortune-refresh expectation is named and corrected explicitly.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass,
  with no new finding class introduced.
- **SC-005**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- This feature carries no ADR — nothing found required a design decision; the Fortune-refresh
  point is a stale scope description caught and corrected, not a rule gap.
- Documentation-only: no code changes; the roll-generation script is scratch tooling, not
  committed, matching the established precedent.
