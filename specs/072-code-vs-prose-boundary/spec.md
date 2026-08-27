# Feature Specification: Decide the engine-code vs. GM-contract-prose boundary

**Feature Branch**: `188-code-vs-prose-boundary`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Decide the engine-code vs. GM-contract-prose boundary (closes #188, depends on #187, #192, part of #133). 02-architecture.md's Code versus prose section predates the full CLI surface; reconcile it now that #187/#192 have specified the CLI's actual state and action-resolution surface."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A stated, checkable test decides which side any GM behaviour falls on (Priority: P1)

Someone deciding whether a given piece of GM behaviour should be a CLI command or a documented
judgment call needs a rule to apply, not a case-by-case guess.

**Why this priority**: This is the actual gap #188 raised — the prior section asserted a split
("does the things the GM must not be trusted to do freehand") without a checkable test behind
it.

**Independent Test**: Read the new test statement; confirm it can be applied to a GM-contract
principle not explicitly listed and produce a clear answer.

**Acceptance Scenarios**:

1. **Given** a GM behaviour that is deterministic given current state and mechanically
   checkable, **When** the test is applied, **Then** it belongs in code.
2. **Given** a GM behaviour that requires creative judgment with no computable right answer,
   **When** the test is applied, **Then** it stays prose.

### User Story 2 - The GM contract's own principles are checked against the test, not assumed (Priority: P1)

`01-principles.md`'s seven engine principles are the constitution everything else must be
consistent with — the test needs to actually hold up against them, not just sound reasonable in
the abstract.

**Why this priority**: A boundary that contradicts the GM contract it's supposed to serve would
be worse than no stated boundary at all.

**Independent Test**: Read the classification of §1–§7; confirm each classification is checked
against what that principle and its cross-referenced document actually say, not asserted.

**Acceptance Scenarios**:

1. **Given** §6 (one chronicle per session), **When** classified, **Then** the classification is
   checked against `21-parallel-chronicles.md`'s actual isolation mechanism (explicit chronicle
   paths, no global state) rather than assumed to be entirely prose.

### Edge Cases

- Does a player's or GM's choice supplied as a parameter to a code call count as "code's
  decision"? No — explicitly stated as still a prose/player decision, even though the call it
  feeds is code.
- Does this earn an ADR? No — applies principles already established (§1's own "the dice bind
  the GM," ADR 0050's already-accepted reasoning) rather than deciding something new.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `02-architecture.md`'s "Code versus prose" section MUST state a checkable test
  distinguishing code-appropriate from prose-appropriate GM behaviour.
- **FR-002**: The test MUST be checked against `01-principles.md`'s seven engine principles, with
  each classification verified against that principle's own text (and cross-referenced document,
  where one exists), not asserted.
- **FR-003**: The test MUST be applied to concrete elements of `16-session.md`'s session
  structure (the Rally, Downtime, session shapes, the session loop), not only stated in the
  abstract.
- **FR-004**: A parameter a GM or player supplies to a code call MUST be stated as still their
  decision, not code's, even when the call itself is code.

### Key Entities

*(none — this feature is a design-document reconciliation, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `02-architecture.md`'s "Code versus prose" section states the test and applies it
  to `01-principles.md`'s seven principles.
- **SC-002**: A table applies the test to concrete `16-session.md` elements.
- **SC-003**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- No ADR: applies already-established principles (§1's own rule, ADR 0050's reasoning) rather
  than deciding something new with a genuine rejected alternative.
- This is a design specification, not an implementation.
