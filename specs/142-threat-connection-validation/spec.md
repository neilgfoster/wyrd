# Feature Specification: Every seeded Threat carries a personal connection

**Feature Branch**: `142-threat-connection-validation`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Every seeded Threat carries a personal connection" (issue #371)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A Threat with no connection to anyone is caught, not carried forward as scenery (Priority: P1)

docs/design/19-campaign.md is explicit: "Every active threat must have at least one connection
to the player or a companion... A threat with no connection is scenery, and belongs in the
setting rather than in a chronicle's active set." `threat.py` (#334) documents `connection` as a
schema field but nothing checks it. This feature adds the structural check: a caller (bootstrap
seeding, a `wyrd doctor`-style report, or anything else building a set of active Threats) can
confirm every one of them actually satisfies the invariant before treating it as active.

**Why this priority**: this is the entire content of the design's own stated rule — without a
check, a connectionless Threat silently passes as "active" when the design says it shouldn't be
one at all.

**Independent Test**: given a mixed list of Threats, some with a real `connection`, some without,
confirm the check reports exactly the ones missing it, by id, and never raises.

**Acceptance Scenarios**:

1. **Given** a Threat with a non-empty `connection` string, **When** the check runs, **Then**
   it is not reported as a problem.
2. **Given** a Threat with `connection` absent entirely, `None`, `""`, or whitespace-only,
   **When** the check runs, **Then** it is reported as a problem, naming its id.
3. **Given** a mixed list of several Threats, **When** the check runs, **Then** the returned
   problem list names exactly the ones failing, in the order they appeared, and nothing else.
4. **Given** an empty list of Threats, **When** the check runs, **Then** it returns an empty
   problem list, never an error.

### Edge Cases

- A Threat entity with no `id` field at all is still reported (using whatever fallback
  identifies it, e.g. the dict's own repr) rather than being silently skipped — a Threat that
  can't even be identified is not thereby exempt from the check.
- This feature checks the *shape* of `connection` only (present and non-blank) — it makes no
  judgment about whether the connection's *content* is actually meaningful prose; that remains
  GM/interview judgment, matching every other prose field this codebase already treats as
  opaque (`threat.py`'s own `effects`/`ambient`/`weakness`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to check a list of Threat entity dicts and report
  every one whose `connection` field is absent, `None`, empty, or whitespace-only.
- **FR-002**: A Threat with a non-empty, non-whitespace `connection` MUST NOT be reported.
- **FR-003**: The check MUST return an empty result (never raise) for an empty input list or a
  list where every Threat passes.
- **FR-004**: Each reported problem MUST identify the offending Threat by its `id` (or an
  identifying fallback when `id` itself is absent).

### Key Entities

- No new entities — this feature adds one function to the existing `threat.py` module (#334),
  reading the `connection` field the schema already documents.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every combination of absent/`None`/empty/whitespace-only `connection` is reported,
  and every non-blank `connection` is not — verified by exact-input tests, not eyeballed.
- **SC-002**: A mixed list's problem report names exactly the failing subset, preserving input
  order.
- **SC-003**: The function never raises for any tested input, including an empty list and a
  Threat missing its own `id`.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts/lists in, plain strings out — no I/O,
  matching every sibling module in this epic and `threat.py`'s own existing convention.
- This feature validates connection *presence*, not selection or assignment — deciding *which*
  threats bootstrap seeds, and *writing* a real connection onto one (via `threat.promote` or at
  chronicle creation), remain out of scope, matching the issue's own explicit framing ("this
  feature does not implement which threats bootstrap selects, or how a connection gets
  written").
- Follows the "report, don't raise" convention this codebase already uses for cross-cutting
  invariant checks (`resolution._validate_proposal`'s naming-the-violation pattern, #327's
  passive-validation precedent) — a caller decides what a non-empty problem list means for its
  own flow (reject a bootstrap, log a warning, etc.).
