# Feature Specification: Downtime phase, including Mend

**Feature Branch**: `311-downtime-mend`

**Created**: 2026-09-10

**Status**: Draft

**Input**: User description: "Downtime phase, including Mend" (issue #311)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Spend a Downtime period (Priority: P1)

A player character reaches a point between adventures where the chronicle enters Downtime.
The engine walks the fixed sequence of steps — where the time is spent, what it costs, what
earned advances buy, the one activity chosen for the period, and the automatic rest — and
each step's outcome is checkable rather than left to narration alone.

**Why this priority**: Downtime is one of the four legitimate session shapes
(docs/design/16-session.md); without engine support for its steps, a Downtime session has
no checkable state at all, unlike every other session shape.

**Independent Test**: Can be fully tested by stepping a Downtime state through Destination,
Upkeep, Advances, Undertaking and Rest and asserting each step's resulting state, with no
dependency on Mend's own internals.

**Acceptance Scenarios**:

1. **Given** a character away from home entering Downtime, **When** Upkeep resolves,
   **Then** either Standing has dropped by 1 or coin has dropped by an amount equal to the
   Standing value before the trade — never both, never neither.
2. **Given** a Downtime period with no undertaking chosen yet, **When** the player selects
   one undertaking (e.g. Mend), **Then** that selection is recorded and a second undertaking
   selection in the same period is rejected.
3. **Given** a Downtime period at any stage, **When** Rest resolves, **Then** Stamina is set
   to its maximum, regardless of which undertaking (if any) was chosen.
4. **Given** a completed Downtime period, **When** it closes, **Then** the calendar has
   advanced and that fact is exposed to the caller (without this feature itself triggering
   Threat activation).

---

### User Story 2 - Mend a lasting wound (Priority: P1)

A player character carrying a lasting wound spends a Downtime's undertaking on Mend, naming
the wound by its `id`. The wound's effect steps one grade toward nothing, per the ladder ADR
0021 already fixed; a wound that reaches nothing is marked closed but kept, never deleted.

**Why this priority**: Mend is the one undertaking this feature must deliver mechanically in
full (per #311's scope), and it is the sole path by which a lasting wound record ever
changes after it is recorded.

**Independent Test**: Can be fully tested by calling Mend against a wound record with each
effect type at each rung of its ladder and asserting the resulting record, independent of
the rest of the Downtime sequence.

**Acceptance Scenarios**:

1. **Given** a wound with effect `skill: -10`, **When** Mend is applied to its `id`,
   **Then** the effect becomes `skill: -5` and the wound is not closed.
2. **Given** a wound with effect `skill: -5`, **When** Mend is applied to its `id`,
   **Then** the wound is closed and its `id`, origin and description are unchanged.
3. **Given** a wound with effect `stamina_max: -1` or `dread: +1`, **When** Mend is applied
   to its `id`, **Then** the wound is closed directly (single-rung ladder).
4. **Given** a wound with `recurring: true`, **When** Mend is applied to its `id`,
   **Then** the call is rejected and the wound record is unchanged.
5. **Given** a Downtime period, **When** Mend is chosen as the undertaking, **Then** it
   consumes the period's one undertaking slot exactly as any other undertaking would.

---

### Edge Cases

- Upkeep at home (not away) costs nothing — no Standing loss, no coin spend — and is not a
  choice between the two trade paths.
- Mend named against a wound `id` that does not exist in the character's `wounds` list is
  rejected, not silently skipped.
- Mend named against a wound that is already closed is rejected — Mend only ever moves an
  active wound.
- Upkeep away from home with insufficient coin and insufficient Standing headroom to spend
  (the engine does not floor Standing, so the coin path is the only one that can be refused
  on insufficient funds) is rejected with the reason stated.
- A Downtime period that closes with zero undertakings chosen is legal — choosing one is
  optional, not mandatory (docs/design/16-session.md lists undertakings as what a player may
  spend the period on; only *choosing two* is illegal).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST represent a Downtime period's progress through its five steps
  (Destination, Upkeep, Advances, Undertaking, Rest) as checkable state, mirroring
  `wyrd.session`'s own loop-state pattern.
- **FR-002**: The engine MUST resolve Upkeep away from home as exactly one of two trades:
  Standing -1, or coin -= current Standing — and MUST reject a resolution that applies
  neither or both.
- **FR-003**: The engine MUST NOT apply any Upkeep cost when Destination is "at home".
- **FR-004**: The engine MUST allow spending advances during Downtime through the existing
  advance-spend machinery (`career`/`advancement` modules), unchanged by this feature.
- **FR-005**: The engine MUST allow choosing at most one undertaking per Downtime period, and
  MUST reject a second undertaking selection within the same period.
- **FR-006**: The engine MUST apply automatic Stamina rest — Stamina set to its maximum —
  unconditionally at the Rest step, regardless of which undertaking (if any) was chosen.
- **FR-007**: The engine MUST expose that Downtime has advanced the calendar (a discrete
  fact the caller can act on), without itself invoking Threat activation.
- **FR-008**: The engine MUST provide a Mend operation that, given a wound `id` and the
  character's `wounds` list, steps that wound's `effect` one grade toward nothing per the
  fixed ladder (`skill: -10` → `-5` → closed; `stamina_max: -1` → closed; `dread: +1` →
  closed), leaving every other field on the record (`id`, origin, description) unchanged.
- **FR-009**: Mend MUST reject an attempt against a wound whose `recurring` field is `true`,
  leaving the wound record unchanged.
- **FR-010**: Mend MUST reject an attempt against an unknown wound `id` or an already-closed
  wound, leaving the wounds list unchanged.
- **FR-011**: A wound whose effect reaches nothing under Mend MUST be marked closed (its
  `closed` field set, per `docs/design/22-state.md`'s additive field) rather than removed
  from the `wounds` list.
- **FR-012**: Mend MUST be selectable as a Downtime undertaking through the same
  exactly-one-undertaking gate FR-005 defines — it has no separate selection path.

### Key Entities

- **Downtime state**: the per-period record of progress through Destination, Upkeep,
  Advances, Undertaking and Rest — analogous to `wyrd.session.new_loop_state()` but scoped to
  a Downtime period rather than the whole session loop.
- **Wound record**: unchanged by this feature (`engine/wyrd/character.py`'s existing shape —
  `id`, `effect`, `bears_on`, `recurring`, `closed`); Mend reads and, where legal, mutates one
  record's `effect` and `closed` fields only.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the five Downtime steps has a corresponding engine function whose
  result can be asserted in a test, with no step's outcome left implicit in narration.
- **SC-002**: Mend applied to a wound at every rung of every effect ladder (`skill`,
  `stamina_max`, `dread`) produces the exact next-rung-or-closed state the design's ladder
  states, verified for all three effect types.
- **SC-003**: A recurring wound subjected to any number of Mend attempts never reaches
  `closed` — provable by a test that asserts this after repeated attempts, not merely
  documented.
- **SC-004**: `specs/014-stamina-recovery/check_recovery.py`'s published figures (0.61 wound
  records, 0.62 downtimes of Mend) are unchanged by this feature, or the script's diffed
  output is included in the change if they are.

## Assumptions

- Downtime is triggered by the caller (end of scenario/arc, or on player request) exactly as
  `wyrd.session.SESSION_SHAPES` already names "downtime" as a shape; this feature does not
  add new triggering logic beyond exposing the calendar-advance fact (FR-007).
- "Home" vs. "away" is a caller-supplied fact about the Destination step (the engine has no
  location model of its own), matching how `economy.py`'s Standing trigger already treats
  scene detection as caller-owned.
- Advances spending during Downtime reuses `career.py`/`advancement.py`'s existing spend
  verbs unchanged; this feature adds no new spend logic (FR-004).
- The five other undertakings (Recover, Pursue, Cultivate, Learn, Ask) are represented only
  as named choices the exactly-one gate accepts; their own mechanical effects beyond Mend are
  out of scope per #311's own scope note, and are not stubbed with placeholder logic here.
- The calendar itself (a concrete date/season value) is out of scope; this feature only
  exposes that an advance happened, matching #311's "expose that the calendar advanced, not
  reimplement Threats" framing.
