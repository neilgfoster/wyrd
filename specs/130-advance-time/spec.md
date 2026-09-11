# Feature Specification: Elapsed time and the advance-time command

**Feature Branch**: `130-advance-time`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Elapsed time and the advance-time command" (issue #338)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Downtime advances the calendar and generates what happened (Priority: P1)

A Downtime period ends, or a journey's summarised leg passes, or an arc gives way to another —
game time moves forward by a stated span. `close_downtime` (#311) already exposes the *fact*
that this happens ("Downtime advances the calendar... which means Threats activate") without
computing anything concrete, by its own explicit scope note. This feature is the still-missing
"elsewhere" that fact deferred to: advancing the chronicle's calendar by the span, and generating
the expected-value Threat activations over it, in one deterministic call.

**Why this priority**: this is the entire mechanical content of docs/design/19-campaign.md's
"Elapsed time" section — without it, every caller that advances time (`close_downtime`,
`journey.resolve_leg`'s summarised legs, an explicit narrated wait) has nowhere to route the
consequence.

**Independent Test**: given a starting calendar, an elapsed span in days, and a set of active
Threats, confirm the calendar moves forward by exactly that span and the reported activation
count for each Threat matches the documented expected-value formula.

**Acceptance Scenarios**:

1. **Given** a calendar at `{year: 1, day: 100}` and an elapsed span of `20` days, **When**
   time is advanced, **Then** the returned calendar is `{year: 1, day: 120}`.
2. **Given** a calendar whose `day` would cross a 365-day year boundary, **When** time is
   advanced, **Then** `year` increments and `day` wraps, rather than growing without bound.
3. **Given** a Threat at `imminence: 4` and an elapsed span of `21` days (3 weeks), **When**
   time is advanced, **Then** its reported activation count is the expected value over 3 weeks
   at a 40%-per-week chance (`3 * 0.4 = 1.2`, rounded to the nearest whole activation).

---

### User Story 2 - Each activation resolves an effects-table roll (Priority: P1)

"Take the expected value over the span. Roll those, apply them, and generate the resulting
state" (docs/design/19-campaign.md) — the expected-value count is not the end of it; each of a
Threat's activations still rolls its own effects-table entry, the same way a single weekly
check's activation would (#334's `resolve_effects`).

**Why this priority**: an activation count with nothing attached to it tells the GM nothing
usable — this is what makes advancing time actually generate play-relevant state, not just a
number.

**Independent Test**: given a Threat with an activation count of 2 and a fixed seed, confirm
exactly 2 effects-table results are returned for it, and that the same seed reproduces the same
results on a second call.

**Acceptance Scenarios**:

1. **Given** a Threat whose computed activation count is `2`, **When** time is advanced,
   **Then** exactly 2 effects-table results are returned for that Threat (via #334's
   `resolve_effects`).
2. **Given** the same calendar, Threats, elapsed span and seed, **When** time is advanced twice,
   **Then** both calls return identical activation results — deterministic given a fixed seed
   (this issue's own acceptance criterion).
3. **Given** a Threat whose computed activation count is `0`, **When** time is advanced,
   **Then** no effects-table roll is made for it and its result list is empty — never a
   spurious roll for zero expected activations.

### Edge Cases

- An elapsed span of `0` days advances the calendar and every Threat's activation count by
  nothing — a no-op, not an error.
- A Threat list containing no active Threats (empty list) still advances the calendar normally,
  with an empty activations result.
- Rounding the expected-value formula (`weeks * imminence / 10`) to the nearest whole activation
  can round to `0` even for an active Threat over a short span (e.g. imminence 2 over 1 week:
  `0.2`, rounds to `0`) — this is expected, not a bug; the formula is explicitly an
  approximation over the span, not a guarantee of at least one activation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to advance a chronicle's calendar by a given number
  of elapsed days, rolling `day` over into `year` at the 365-day year boundary already fixed by
  #335's decay stepping.
- **FR-002**: The engine MUST provide a way to compute, for a given Threat's `imminence` and an
  elapsed span in days, the expected-value activation count: `round(weeks * imminence / 10)`
  where `weeks = elapsed_days // 7`.
- **FR-003**: For each computed activation, the engine MUST roll and resolve one effects-table
  entry (via #334's `resolve_effects`), producing exactly as many results as the computed
  activation count — zero for a count of zero.
- **FR-004**: Given a fixed seed, advancing time over the same calendar/Threats/span MUST
  produce identical results on every call (this issue's own acceptance criterion).
- **FR-005**: Advancing time MUST be the only path that moves a chronicle's calendar forward —
  this feature introduces no second mechanism alongside it, per docs/design/19-campaign.md's
  explicit statement that "closing the session advances nothing" and nothing else does either.

### Key Entities

- **Elapsed span**: a plain integer count of game-days, supplied by the caller (a Downtime close,
  a journey's summarised leg, an explicit wait) — this feature does not decide when time has
  passed, only what happens once a caller says it has.
- **Activation result**: `{"id": <threat id>, "activation_count": int, "effects": [<matched
  entry from resolve_effects>, ...]}` — one per Threat passed in.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The calendar-advance arithmetic is correct at and across the year boundary,
  verified by exact-input tests, not eyeballed.
- **SC-002**: The expected-value formula's exact output is asserted for specific
  imminence/span combinations, including a case that rounds to zero.
- **SC-003**: A fixed seed reproduces identical activation results across repeated calls.
- **SC-004**: The number of effects-table results returned for a Threat always equals its
  computed activation count exactly — never more, never fewer.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts/lists in, plain dicts out, no
  file I/O and no CLI wiring — matching every sibling module in this epic (`threat.py`,
  `thread.py`, `era.py`, `holding.py`). No CLI verb (`catalog.py`/`client.py`) exists yet for any
  chronicle-level session/campaign operation in this codebase (the closest precedent,
  `chronicle.py`/`rally.py`, is called by session-orchestration code, not exposed as a CLI tool)
  — the design document's `wyrd advance-time <game-days>` notation is read as the library
  operation's name, not a literal CLI-argument-parsing requirement; wiring a CLI/session-loop
  entry point for it is out of scope here, consistent with how #325-#337 each left their own
  library functions uncalled by any concrete session loop.
- The `month` sub-field of `calendar` is left untouched by the calendar-advance function — its
  semantics (which month-length convention, if any) are not defined anywhere else in this
  codebase yet, and every existing example (`state.py`'s default, docs/design's own examples)
  treats it as `null`/informational. Only `year`/`day` are advanced.
- A 365-day year is reused unchanged from #335's `thread.py` decision (see specs/127's
  research.md) rather than re-litigated here, keeping the engine's elapsed-time handling
  consistent across features.
- This feature directly imports and reuses `threat.resolve_effects` (#334) — unlike `holding.py`
  (#337), which deliberately avoided importing `threat.py` to stay decoupled from a Threat's own
  domain, this feature's entire purpose (per the issue's own "Depends on: #334") is applying
  Threat activation and effects resolution, so the dependency is direct and intentional.
- Which entities' Threats are "active" for a given chronicle (an entity-store-wide scan) is out
  of scope — this feature takes an already-filtered list of Threat entity dicts as input (as
  `threat.active_threats` produces), the same boundary every sibling module in this epic keeps.
