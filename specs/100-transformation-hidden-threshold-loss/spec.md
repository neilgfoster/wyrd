# Feature Specification: Transformation count reaching the hidden threshold

**Feature Branch**: `100-transformation-hidden-threshold-loss`

**Created**: 2026-09-03

**Status**: Draft

**Input**: GitHub issue #271 — "Transformation count reaching the hidden threshold: character is
lost"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A player character's transformation count reaches their hidden threshold (Priority: P1)

A player character has been taking Transformations across the chronicle. Each one is recorded.
Eventually the count of Transformations they have taken reaches the number the GM secretly rolled
at their first Transformation. From that point the character is no longer played by the operator:
they leave `status: with-party`, pass to GM control, and the chronicle continues with a successor
in the ordinary way a lost protagonist's chronicle does.

**Why this priority**: This is the mechanic the issue exists to close — the cascade already rolls
and stores the hidden threshold, but nothing yet acts on it. Without this, a character can take
Transformations forever with no consequence, which is not what the design describes.

**Independent Test**: Drive a Transformation cascade (via `_stage_transformation_chain` /
`_cascade_from_mutation`) against a player-character state whose `transformations` count is one
below `hidden_threshold`. Confirm the resulting steps stage a transition that removes the
character from `status: with-party` and marks them GM-controlled, with Fate untouched.

**Acceptance Scenarios**:

1. **Given** a player character with `hidden_threshold: 5` and four prior Transformations
   recorded, **When** a further Taint crossing stages one more Transformation, **Then** the
   cascade records that fifth Transformation and stages a step that ends the character's
   chronicle: no longer `with-party`, now GM-controlled, Fate unchanged.
2. **Given** a player character whose Transformation count is still below their hidden threshold
   after a Transformation is staged, **When** the cascade completes, **Then** no loss transition
   is staged and the character's status is untouched.

---

### User Story 2 - A companion's transformation count reaches their hidden threshold (Priority: P2)

A companion accumulates Transformations the same way a player character does. When their count
reaches their hidden threshold, the party simply loses them — no successor mechanism, no
chronicle-ending step, just removal from the party's `with-party` roster and a hand-off to GM
control.

**Why this priority**: The design draws a real distinction between losing a player character
(ends a chronicle, a successor may follow) and losing a companion (the party loses them, nothing
more) — both must be covered, but the player-character path is the one with more machinery riding
on it, so it is P1.

**Independent Test**: Drive the same cascade against a companion state (`role: companion`) whose
Transformation count reaches their hidden threshold. Confirm the character leaves
`status: with-party`, becomes GM-controlled, and that nothing resembling the player character's
chronicle-ending step is staged for them.

**Acceptance Scenarios**:

1. **Given** a companion with `hidden_threshold: 3` and two prior Transformations recorded,
   **When** a further Transformation is staged, bringing the count to three, **Then** the cascade
   stages a step removing them from `status: with-party` and marking them GM-controlled, and Fate
   (if the companion tracks any) is untouched.

---

### Edge Cases

- A Transformation staged when the count is already at or past the hidden threshold before this
  roll (should not happen in ordinary play, since the transition removes the character from play
  at the moment it is first reached, but the cascade must not double-stage the loss transition if
  it is ever called again against an already-lost character).
- The re-roll loop inside `_stage_transformation_chain` (docs/design/07-transformations.md
  "Termination of the re-roll loop") can stage more than one Transformation in a single cascade.
  If the count reaches the hidden threshold partway through that loop, the loss transition stages
  once, attached to the Transformation that reached it — the loop does not continue staging
  further Transformation rolls for a character who has just been lost.
- The hidden threshold is `null` until the character's first Transformation. A count can only
  reach a `null` threshold if the comparison is written carelessly — this must never fire before
  `hidden_threshold` is set.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The cascade MUST record every Transformation a character takes as a durable entry
  on that character's `transformations` field (docs/design/22-state.md), the same way afflictions
  are already recorded — currently the field is initialized empty and never appended to.
- **FR-002**: After staging a Transformation, the cascade MUST compare the character's resulting
  `transformations` count against their `hidden_threshold` and, when the count reaches the
  threshold, stage the loss transition as part of the same cascade that produced the triggering
  Transformation (docs/design/22-state.md's invariants: "`transformations` count exceeding
  `hidden_threshold` sets `status: lost`" — read together with docs/design/07-transformations.md's
  "reaches", both meaning the count is no longer below the threshold).
- **FR-003**: The loss transition MUST remove the character from `status: with-party`
  (docs/design/22-state.md) and mark them GM-controlled, without touching `fate` in any way
  (docs/design/07-transformations.md "The hidden threshold").
- **FR-004**: For a player character (`role: player`), the loss transition MUST end that
  character's chronicle in the way a lost protagonist's chronicle ends
  (docs/design/19-campaign.md) — the state transition this feature stages is `status: lost`; any
  further succession machinery is a separate, already-existing concern this feature must not
  duplicate or reimplement.
- **FR-005**: For a companion (`role: companion`), the loss transition MUST set `status: lost`
  and nothing more — no chronicle-ending step is staged for a companion.
- **FR-006**: The loss transition MUST NOT ever reveal the hidden threshold's numeric value to
  the player, in any rendered form, including as unease (docs/design/13-diegesis.md's "never
  shown" visibility class already covers this field; this feature must not introduce a new path
  that leaks it, e.g. in a step's recorded roll data or a rendered message).
- **FR-007**: The comparison MUST only ever fire once `hidden_threshold` is set (non-`null`) —
  before a character's first Transformation there is nothing to compare against.
- **FR-008**: Within a single cascade invocation, once the loss transition has been staged for a
  character, the cascade MUST NOT stage any further Transformation rolls for that character (the
  re-roll loop that continues while Taint remains at or over the crossed threshold must stop for a
  character who has just been lost).

### Key Entities

- **Character** (`engine/wyrd/character.py`, docs/design/22-state.md): carries `transformations`
  (a list, currently always empty), `hidden_threshold` (secret, set once), and `status` (for a
  companion; a player character's equivalent chronicle-ending signal is `status: lost` per
  docs/design/22-state.md's invariants, read for both roles by this feature).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A character whose Transformation count reaches their hidden threshold is staged out
  of `status: with-party` and marked GM-controlled within the same cascade that produced the
  triggering Transformation, with no further action required.
- **SC-002**: Fate is unchanged by the loss transition, verified by comparing `fate` before and
  after the cascade in a test.
- **SC-003**: A rendered view of a lost character's state never contains the numeric hidden
  threshold, verified the same way the existing "never shown" tests for `hidden_threshold` already
  do.
- **SC-004**: Player-character and companion loss are each covered by an independent, passing test
  under `PYTHONPATH=engine`.

## Assumptions

- `transformations` is recorded as a list of the row numbers (or row keys) taken, mirroring how
  `afflictions` already records its rows — the exact per-entry shape is an implementation
  decision, not fixed by the design documents, since none specify it beyond "a durable entry" by
  analogy with afflictions.
- The engine-level signal for "this character is lost" is a `status` field set to `lost` for both
  player characters and companions, per docs/design/22-state.md's own invariant line. Any
  operator-facing or narrative machinery for picking a successor (docs/design/19-campaign.md) is
  out of scope, as the issue states, and is assumed to already exist or to be handled outside this
  cascade.
- No new visibility class or diegetic-rendering work is needed beyond what already exists for
  `hidden_threshold` (docs/design/13-diegesis.md) — this feature only needs to avoid leaking the
  number, not add new masking machinery.
- Fault Line alignment (mentioned as explicitly out of scope in the issue) is untouched by this
  feature.
