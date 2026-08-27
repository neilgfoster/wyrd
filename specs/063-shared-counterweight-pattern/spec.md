# Feature Specification: Name the shared scarce-resource-plus-counterweight pattern

**Feature Branch**: `182-shared-counterweight-pattern`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Taint/Resolve and Fate/Fortune are already the same mechanism -- a scarce or near-permanent resource paired with a renewable counterweight -- applied to two different domains. Name this explicitly (closes #182), part of a design review looking for physical/mental/spiritual mirroring across the track roster (part of epic #1)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader sees Taint/Resolve and Fate/Fortune as one pattern, not two coincidences (Priority: P1)

Someone reading the track table wants to recognize that these two pairs share a shape, so a
future third instance of the same pattern reads as completing something established.

**Why this priority**: This is the whole point of #182 — naming a pattern that already exists
implicitly, at zero mechanical cost.

**Independent Test**: Read `03-rules.md`'s new passage; confirm it states the shared shape and
names both existing pairs as instances of it.

**Acceptance Scenarios**:

1. **Given** the track table listing Taint, Resolve, Fate, and Fortune separately, **When** a
   reader continues past it, **Then** a stated passage identifies the shared "scarce resource +
   renewable counterweight" shape both pairs already have.

### Edge Cases

- Does this change any mechanic? No — documentation-only, no rule changes.
- Does this merge Taint/Resolve with Fate/Fortune into one track? No — they remain two separate
  pairs; only the shared shape between them is named.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `03-rules.md` MUST state the shared "scarce/permanent resource + renewable
  counterweight" pattern explicitly.
- **FR-002**: The passage MUST name both existing instances (Taint/Resolve, Fate/Fortune).
- **FR-003**: The passage MUST NOT alter either pair's own existing mechanics.

### Key Entities

*(none — this feature is a design-document clarification, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `03-rules.md` contains the new passage.
- **SC-002**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (no new
  finding class), and `python3 -m pytest -q` pass.

## Assumptions

- No ADR — this states an existing pattern, it makes no new design decision (no real rejected
  alternative to naming a pattern that already exists in both pairs' own text).
- Documentation-only: no engine code changes.
