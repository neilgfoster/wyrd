# Feature Specification: Chronicle intent's lethality is validated against the mortality vocabulary

**Feature Branch**: `140-lethality-validation`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Chronicle intent's lethality is validated against the mortality vocabulary" (issue #369)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A chronicle's lethality can never drift from what creation/Aftermath expect (Priority: P1)

`chronicle.yaml`'s `intent.lethality` names the same concept `creation.MORTALITY_FATE` (starting
Fate) and `resolution.MORTALITY_LEVELS` (death-row closure) already consume as `mortality` — but
nothing today checks the chronicle-schema value against that vocabulary before it reaches those
functions, which currently fail with a raw `KeyError`/silent mismatch rather than a clear
chronicle-validation error.

**Why this priority**: this is a real coupling between two parts of the schema that currently
have no shared check — exactly the "two documents describing one thing differently" fault class
this repo has been bitten by before.

**Independent Test**: given a chronicle with `intent.lethality` set to each of the three valid
values, confirm it validates; given any other value, confirm it is rejected with a clear message.

**Acceptance Scenarios**:

1. **Given** a chronicle with `intent.lethality` set to `"low"`, `"standard"`, or `"high"`,
   **When** it is validated, **Then** validation succeeds.
2. **Given** a chronicle with `intent.lethality` set to any other value (e.g. `"deadly"`,
   `"safe"`, `""`), **When** it is validated, **Then** `StateError` is raised naming the field
   and the rejected value.

### Edge Cases

- A chronicle omitting `intent.lethality` entirely still fills in via the existing
  `_INTENT_DEFAULTS` (`"standard"`) before this check runs — the default itself is always valid,
  so an omitted field never triggers the new rejection path.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `state.validate_chronicle` MUST reject an `intent.lethality` value outside
  `{"low", "standard", "high"}` — the same three-value vocabulary `creation.MORTALITY_FATE`
  and `resolution.MORTALITY_LEVELS` already use.
- **FR-002**: The rejection MUST raise `StateError` naming the field and the offending value,
  matching this module's existing error convention for other rejected fields (e.g. negative
  `sessions`/`danger_rating`).
- **FR-003**: The three already-valid values (`low`/`standard`/`high`) MUST continue to
  validate successfully — no regression to existing chronicles.

### Key Entities

- No new entities — this feature adds one validation rule to `state.validate_chronicle`'s
  existing `intent` handling.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three valid lethality values pass validation; every tested invalid value is
  rejected with a clear `StateError` message naming the field.
- **SC-002**: The existing `_INTENT_DEFAULTS`-fill-then-validate behaviour is unaffected for
  every other intent field.

## Assumptions

- `state.py` cannot import `creation.py`/`resolution.py` directly (doing so would create an
  import cycle via `character.py`, which `creation.py` already imports and which itself imports
  `state.py`) — this feature declares its own local `{"low", "standard", "high"}` constant in
  `state.py`, mirroring `resolution.py`'s own already-existing independent declaration of the
  same three-value set (`MORTALITY_LEVELS`) rather than introducing a new cross-module coupling
  pattern.
- This feature validates the chronicle-schema side of the coupling only — it does not change
  `creation.py`'s `MORTALITY_FATE` or `resolution.py`'s `MORTALITY_LEVELS`, and it does not wire
  `intent.lethality` through to an actual `create_character` call (that wiring is
  session-orchestration, out of scope here, the same boundary every sibling feature in this
  epic keeps).
