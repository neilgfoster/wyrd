# Feature Specification: world_acts_offstage gates threat activation while the character is elsewhere

**Feature Branch**: `141-world-acts-offstage`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "world_acts_offstage gates threat activation while the character is elsewhere" (issue #370)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An unwitnessed span produces no Threat activations when the setting opts out (Priority: P1)

`chronicle.yaml`'s `intent.world_acts_offstage` (#325) already asks "should the world act when
you are not looking?" — but `advance_time.advance_time` (#338) computes every Threat's
expected-value activation unconditionally, never reading it. This feature wires the two
together: when `world_acts_offstage` is `False` and a given elapsed span was not witnessed by
the player, no Threat activates over that span.

**Why this priority**: this is the entire mechanical content of the design's own stated
question — without it, the intent field is decoration, not a real chronicle-shaping choice.

**Independent Test**: given identical calendar/Threats/span inputs, confirm
`world_acts_offstage=False, witnessed=False` suppresses every activation to zero while the
calendar still advances, and confirm the default (`world_acts_offstage=True`) reproduces #338's
existing behaviour exactly.

**Acceptance Scenarios**:

1. **Given** `world_acts_offstage=True` (the default), **When** time is advanced over any span,
   **Then** the result is identical to #338's existing behaviour for the same inputs/seed —
   no regression for a chronicle that never sets the field.
2. **Given** `world_acts_offstage=False` and `witnessed=False`, **When** time is advanced,
   **Then** every Threat's `activation_count` is `0` and its `effects` list is empty,
   regardless of imminence or elapsed span — but the calendar still advances by the full span.
3. **Given** `world_acts_offstage=False` and `witnessed=True` (a scene the player was actually
   present for), **When** time is advanced, **Then** Threats activate normally, exactly as
   under the default.

### Edge Cases

- `world_acts_offstage=True` and `witnessed=False` together still activate Threats normally —
  the intent field, not the witnessed flag alone, is what opts a chronicle out; a default-intent
  chronicle never suppresses activation regardless of whether a given span happened to be
  witnessed.
- No seeded roll is consumed when activation is suppressed — a caller advancing time twice with
  the same seed, once suppressed and once not, should not see the un-suppressed call's rolls
  shifted by rolls the suppressed call never drew.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `advance_time` MUST accept `world_acts_offstage: bool = True` and
  `witnessed: bool = True` parameters.
- **FR-002**: When `world_acts_offstage` is `False` AND `witnessed` is `False`, every Threat's
  computed `activation_count` MUST be `0` and its `effects` list MUST be empty — no
  expected-value computation and no roll drawn for any Threat.
- **FR-003**: The calendar MUST advance by the full elapsed span regardless of
  `world_acts_offstage`/`witnessed` — only Threat activation is gated, never the clock.
- **FR-004**: The default parameter values (`world_acts_offstage=True`, `witnessed=True`) MUST
  reproduce #338's existing behaviour exactly, for every one of its existing test cases.
- **FR-005**: Suppressing activation MUST NOT consume any seeded roll — the roll-offset
  sequence for a later, non-suppressed call with the same seed must be unaffected by an earlier
  suppressed call.

### Key Entities

- No new entities — this feature adds two parameters to `advance_time.advance_time`'s existing
  signature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every pre-existing `test_advance_time.py::AdvanceTimeTests` case continues to
  pass unchanged (regression safety, FR-004).
- **SC-002**: A suppressed call's activation results are `[]`-effects/`0`-count for every
  Threat, verified across multiple Threats with different imminence values in one call.
- **SC-003**: The calendar's advanced value is identical whether or not activation was
  suppressed, for the same elapsed span.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts/lists/bools in, plain dicts out — no
  I/O, matching #338's own convention. Reading `chronicle["intent"]["world_acts_offstage"]` and
  deciding `witnessed` for a given span (a narrated scene vs. a skipped downtime) remain the
  caller's own judgment — this feature only wires the already-existing intent field through to
  the already-existing activation computation, it does not decide what counts as "witnessed."
- `witnessed` defaults to `True` (not derived from `world_acts_offstage`) so a caller who never
  passes either parameter reproduces #338's original behaviour exactly, matching FR-004 — the
  gate only actually fires when a caller explicitly asserts both "the setting wants this off"
  and "this particular span was unwitnessed."
