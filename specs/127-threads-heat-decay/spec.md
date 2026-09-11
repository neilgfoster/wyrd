# Feature Specification: Threads: open-loop tracking, heat and decay

**Feature Branch**: `127-threads-heat-decay`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Threads: open-loop tracking, heat and decay" (issue #335)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A thread is opened when a loop is left dangling (Priority: P1)

A debt, an escaped enemy, a promise — the GM records it as a thread so the chronicle can pick it
back up later rather than losing it. The thread starts at whatever heat the situation warrants
when it opens.

**Why this priority**: nothing else in this feature — touching, decaying, closing — has anything
to act on until a thread exists in the shape the rest of the engine expects.

**Independent Test**: create a thread with an id, summary, hooks and an opened date; confirm the
returned record carries exactly those fields plus a starting heat.

**Acceptance Scenarios**:

1. **Given** an id, summary, hook list and opened date, **When** a thread is created, **Then**
   the returned record carries all four unchanged, plus a `heat` field.
2. **Given** no explicit starting heat is supplied, **When** a thread is created, **Then** it
   starts at `heat: 0` — a freshly opened thread is not assumed urgent until play makes it so.

---

### User Story 2 - A thread heats up when a scenario touches it (Priority: P1)

Selecting the next scenario consumes live threads (#339, blocked on this feature) — when one is
picked up, it gets hotter, capping so an endlessly-revisited thread doesn't run away past the
schema's own bound.

**Why this priority**: heat is what scenario selection (#339) will rank by — without a way to
raise it, "currently hot" threads never emerge from play.

**Independent Test**: touch a thread at each heat value 0 through 5 and confirm it rises by
exactly one each time, capping at 5 rather than exceeding it.

**Acceptance Scenarios**:

1. **Given** a thread at `heat: 2`, **When** it is touched, **Then** its heat becomes `3`.
2. **Given** a thread already at `heat: 5`, **When** it is touched, **Then** its heat stays `5`.

---

### User Story 3 - An ignored thread decays and eventually closes (Priority: P1)

A thread nobody has touched for a long stretch of game time cools — and if it's already cold and
still nobody follows up, it closes on its own as "never resolved". This is itself true to the
setting, per docs/design/19-campaign.md: not everything gets an answer.

**Why this priority**: without decay, every thread a chronicle ever opens accumulates forever,
which the design explicitly rules out; this is the other half of the heat mechanic User Story 2
introduces.

**Independent Test**: given a thread and an elapsed game-time span, confirm heat drops by one
point per elapsed year and the thread closes, with a recorded reason, only once decay is applied
again while already at the floor.

**Acceptance Scenarios**:

1. **Given** a thread at `heat: 2` and an elapsed span of one game year, **When** decay is
   applied, **Then** its heat becomes `1`.
2. **Given** a thread at `heat: 0` and an elapsed span of one game year, **When** decay is
   applied, **Then** the thread closes with a recorded reason ("never resolved") rather than
   going negative.
3. **Given** a thread at `heat: 2` and an elapsed span of less than one game year, **When** decay
   is applied, **Then** its heat is unchanged — decay is stepped in whole years, not fractional.

### Edge Cases

- Decay applied with an elapsed span covering more than one year at once (e.g. a long downtime
  or a returning player) drops heat by the full number of whole years elapsed, not just one step
  — mirroring `advance-time`'s own expected-value-over-a-span philosophy rather than requiring
  the caller to replay each year individually.
- Touching an already-closed thread, or decaying one, is out of scope for this feature — a closed
  thread's lifecycle ends at closure; reopening one (if ever needed) is a GM/setting-level
  decision, not an engine operation this feature provides.
- A thread created with an explicit starting `heat` above `5` or below `0` is rejected — the
  schema's own 0-5 bound (docs/design/19-campaign.md) is enforced at creation, not only at touch
  time.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to create a thread record carrying `id`, `opened`,
  `summary`, `hooks`, and `heat` (docs/design/19-campaign.md's thread schema).
- **FR-002**: A thread created without an explicit `heat` MUST default to `0`.
- **FR-003**: Thread creation MUST reject a supplied `heat` outside `0-5`.
- **FR-004**: The engine MUST provide a way to raise a thread's `heat` by exactly one point,
  capped at `5` — touching an already-maximum thread MUST leave it unchanged rather than erroring.
- **FR-005**: The engine MUST provide a way to decay a thread's `heat` given an elapsed game-time
  span, lowering it by one point per whole elapsed year, floored at `0`.
- **FR-006**: A decay call against a thread already at `heat: 0`, given at least one whole elapsed
  year, MUST close the thread and record a reason ("never resolved") rather than leaving it open
  indefinitely.
- **FR-007**: A decay call covering less than one whole elapsed year MUST leave the thread's
  `heat` unchanged.

### Key Entities

- **Thread** (docs/design/19-campaign.md): `{id, opened: {year, month}, summary, hooks, heat}`
  where `heat` is `0-5`, plus (after closure) `status: "closed"` and `close_reason`. This feature
  treats it as a plain dict, matching every other runtime module in `engine/wyrd/` (`threat.py`,
  `journey.py`) — no entity/file loading, which stays the setting repo's concern. `entity.py`
  already lists `"thread"` among its ten entity types (no dedicated schema entry yet); this
  feature does not add one, since the fields above are exactly what the design's own example
  already shows and this feature's dicts are not routed through `entity.py`'s validation layer.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A newly created thread carries every field the design's schema names, verified by
  exact-input tests, not eyeballed.
- **SC-002**: Touching a thread at every heat value 0-5 is covered by an explicit test, including
  the cap at 5.
- **SC-003**: Decay's whole-year stepping (zero years = no-op, one year = one point, partial year
  = no-op) and its close-on-floor behaviour are each covered by an explicit test.
- **SC-004**: A thread that closes via decay carries a recorded reason — never a silent
  disappearance from the active set with nothing explaining why.

## Assumptions

- "A year of game time" is fixed at 365 game-days for this feature's decay stepping — the design
  document states the qualitative rule ("a thread untouched for a year... drops in heat") but not
  an exact day count; 365 is the plain calendar year already implied by `chronicle.yaml`'s
  `calendar: {year, month, day}` shape (`state.py`), and is the same order of magnitude
  `advance-time`'s own weekly Threat cadence (#334, 7-day steps) already uses for its unit.
- This feature is a runtime-logic slice only: plain dicts in, plain dicts out, no entity/file
  loading — matching `threat.py`'s (#334) and `journey.py`'s existing division of labour. The
  weekly/elapsed-time loop that decides *when* to call `decay` (once per elapsed span, at a
  downtime or arc boundary) is `advance-time`'s concern (#338), not this feature's.
- Scenario selection's consumption/emission of threads by hook-matching (#339, blocked on this
  feature) is out of scope here — this feature provides the record shape and the heat mechanic
  #339 will read and call `touch` against; it does not implement selection itself.
- A closed thread's `close_reason` is always the literal string `"never resolved"` for this
  feature's own decay-triggered closure — a thread closed some other way (e.g. explicitly
  resolved in play) is out of scope; this feature only implements the decay path.
