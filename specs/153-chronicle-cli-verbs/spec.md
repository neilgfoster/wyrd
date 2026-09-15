# Feature Specification: Chronicle CLI Verbs

**Feature Branch**: `153-chronicle-cli-verbs`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Wire chronicle-level CLI verbs into catalog.py" (GitHub issue
#402, part of epic #401)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Load a session's working context in one call (Priority: P1)

A GM (human or model) starting or resuming a session needs the Always-loaded memory tier —
player character, present companions, open threads worth surfacing, the recap, and the
contract — without hand-assembling it from several lookups.

**Why this priority**: This is the tier every session touches; without it the CLI cannot
replace the ad hoc context assembly the engine's memory-tier design exists to avoid.

**Independent Test**: Can be fully tested by calling `session-context` against a chronicle with
a player character, at least one companion present and one absent, and threads at varying heat,
and confirming the returned structure contains exactly the Always-loaded composition
(docs/design/02-architecture.md) and nothing from the broader on-demand tier.

**Acceptance Scenarios**:

1. **Given** a chronicle with a player character, two companions (`status: with-party` and
   `status: absent`), three threads (`heat` 5, 3, 1), a recap, and a contract, **When**
   `session-context` runs, **Then** the result includes the player character, only the
   with-party companion, only the two threads with `heat >= 3`, the recap, and the contract.
2. **Given** a chronicle with no open threads, **When** `session-context` runs, **Then** the
   threads portion of the result is an empty collection, not an error.

---

### User Story 2 - Fetch or query any entity on demand (Priority: P1)

A GM needs any entity not already in the Always-loaded tier — by id when known, or by a filter
when it is not — resolved to its effective (overlay-applied) form.

**Why this priority**: This is the on-demand tier's core mechanism; `party`, `threads`, and
`threats` are named conveniences built directly on it, so it must exist and be correct first.

**Independent Test**: Can be fully tested by calling `get` on a known id and on an id that does
not resolve (expecting a resolved entity and an error respectively), and by calling `find` with
combinations of `--type`, `--status`, and `--tag` against a fixture set with entities that match
none, one, and all of the given filters.

**Acceptance Scenarios**:

1. **Given** an entity that exists only in the setting with a chronicle overlay changing one
   field, **When** `get <id>` runs, **Then** the result is the effective (overlay-applied) form,
   not the setting's unmodified form.
2. **Given** an id that resolves in neither the setting, the overlay, nor the chronicle's own
   entities, **When** `get <id>` runs, **Then** the command reports an error distinguishable
   from an empty result.
3. **Given** entities of several types and statuses, **When** `find --type T --status S` runs,
   **Then** the result contains exactly the entities matching both filters, and an unmatched
   filter combination returns an empty result rather than an error.

---

### User Story 3 - Reach for a named query instead of building a filter (Priority: P2)

A GM reaches for `party`, `threads`, or `threats` by name for the three query patterns the
architecture document already calls out, instead of reconstructing the equivalent `find`
filters from scratch each time.

**Why this priority**: These are conveniences over User Story 2's general mechanism — valuable,
but the engine is already fully queryable without them.

**Independent Test**: Can be fully tested by confirming each named verb's result is identical to
the equivalent explicit `find` call, against a fixture set exercising each verb's specific
predicate (companion role/status for `party`; open status and heat ordering for `threads`; an
active threat block for `threats`).

**Acceptance Scenarios**:

1. **Given** entities with `role: companion` in both `status: with-party` and other statuses,
   **When** `party` runs, **Then** only the `with-party` companions are returned.
2. **Given** several `status: open` threads with distinct `heat` values, **When** `threads`
   runs, **Then** all of them are returned, ordered by `heat` descending (the full open set —
   broader than `session-context`'s `heat >= 3` slice).
3. **Given** entities with and without an active threat block, **When** `threats` runs, **Then**
   only those with an active threat block are returned.

---

### User Story 4 - Read recent history without loading the whole log (Priority: P3)

A GM reads the Archival tier — recent log entries — bounded by count or since a named beat,
without pulling the entire chronicle history into context.

**Why this priority**: The archival tier is read rarely by design; it matters for correctness
and auditability but is not on the critical path of ordinary play the way Stories 1-3 are.

**Independent Test**: Can be fully tested by calling `log --last N` and `log --since <beat>`
against a fixture log with several entries in known beat order and confirming each returns
exactly the expected subset, in beat order.

**Acceptance Scenarios**:

1. **Given** a log with more than N entries, **When** `log --last N` runs, **Then** exactly the
   N most recent entries are returned, in beat order.
2. **Given** a log and a beat id known to be partway through it, **When** `log --since <beat>`
   runs, **Then** only entries from that beat onward are returned.

---

### User Story 5 - Persist, validate, and recap chronicle state (Priority: P2)

A GM saves and loads chronicle state atomically, validates it against its schema, and
regenerates the recap from current state, as explicit CLI operations rather than side effects
buried inside other verbs.

**Why this priority**: Persistence and validation are prerequisites for every other verb to be
trustworthy across a session boundary, but they are operational plumbing rather than a
session's primary interaction.

**Independent Test**: Can be fully tested by saving a modified state, loading it back and
confirming it matches, running `validate` against both a schema-conformant and a
non-conformant state, and running `recap` against a state with known content and confirming the
regenerated `recap.md` reflects it.

**Acceptance Scenarios**:

1. **Given** an in-memory state with a pending change, **When** `save` then `load` run in
   sequence, **Then** the loaded state matches what was saved, with no partial or corrupted
   write visible even if the process were interrupted mid-write.
2. **Given** a state that violates the chronicle schema, **When** `validate` runs, **Then** it
   reports the specific violation rather than merely pass/fail.
3. **Given** a chronicle whose entities and log have changed since the last recap, **When**
   `recap` runs, **Then** `recap.md` is regenerated to reflect current state.

---

### User Story 6 - Advance the calendar and resolve threats (Priority: P3)

A GM advances chronicle time by a number of days, letting the calendar move forward, threats
activate, and expected-value events resolve, and separately runs a single threat's activation
roll on demand.

**Why this priority**: Time advancement and threat activation are periodic, downtime-adjacent
operations rather than something every session invokes.

**Independent Test**: Can be fully tested by calling `advance-time <days>` against a chronicle
with an active threat whose imminence guarantees activation within that span, and confirming the
calendar moved, the threat activated, and by calling `threat-check` directly against a single
threat and confirming its activation roll is resolved deterministically from a given seed.

**Acceptance Scenarios**:

1. **Given** a chronicle at a known date with an active threat, **When** `advance-time <days>`
   runs, **Then** the calendar advances by exactly that many days and any threat whose
   activation condition is met over that span is activated.
2. **Given** a single active threat and its imminence, **When** `threat-check` runs, **Then** it
   returns a definite activated/not-activated result derived from one roll against that
   imminence.

### Edge Cases

- `get <id>` on an id that exists in the setting but has no chronicle overlay: still resolves,
  using the setting form as its effective form.
- `find`/`party`/`threads`/`threats` against a chronicle with no matching entities: returns an
  empty result, never an error — only `get` on an unresolved id is an error condition.
- `log --last N` where N exceeds the total number of log entries: returns the whole log, not an
  error.
- `advance-time 0`: a no-op that still validates the argument rather than silently succeeding on
  a nonsensical input.
- `validate` on already-valid state: reports success with no findings, not merely silence.
- `save`/`load` interrupted mid-write (process killed partway): the next `load` must see either
  the old state or the new state in full, never a torn file.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST expose a `session-context` verb returning the Always-loaded memory
  tier in one call: the player character, companions with `status: with-party`, threads with
  `heat >= 3`, the recap, and the contract.
- **FR-002**: The CLI MUST expose a `get <id>` verb resolving one entity to its effective form
  (setting + overlay, or chronicle-native), and MUST report an error — distinguishable from an
  empty result — when `<id>` does not resolve.
- **FR-003**: The CLI MUST expose a `find --type T [--status S] [--tag G]` verb returning every
  entity matching all filters given; omitted filters are not applied; no filters given returns
  every entity.
- **FR-004**: The CLI MUST expose a `party` verb returning entities with `role: companion` and
  `status: with-party` — the same underlying entity-matching mechanism `find` uses, filtered on
  fields `find`'s own public `--type/--status/--tag` flags do not need to expose, since `party`
  is a distinct named verb rather than a literal `find` invocation.
- **FR-005**: The CLI MUST expose a `threads` verb returning the full `status: open` set ordered
  by `heat` descending — the general query, broader than `session-context`'s `heat >= 3` slice.
- **FR-006**: The CLI MUST expose a `threats` verb returning entities with an active threat block
  (`imminence > 0`).
- **FR-007**: The CLI MUST expose a `log --last N | --since <beat>` verb reading the Archival
  tier in beat order; `--last N` and `--since <beat>` are mutually exclusive alternatives.
- **FR-008**: The CLI MUST expose `save`, `load`, and `validate` verbs performing atomic writes
  and schema validation against chronicle state, per docs/design/22-state.md.
- **FR-009**: The CLI MUST expose a `recap` verb regenerating `recap.md` from current chronicle
  state, per docs/design/16-session.md.
- **FR-010**: The CLI MUST expose an `advance-time <days>` verb advancing the calendar by the
  given number of days and resolving threat activation and expected-value events across that
  span, per docs/design/19-campaign.md.
- **FR-011**: The CLI MUST expose a `threat-check` verb resolving a single threat's activation
  roll on demand.
- **FR-012**: Every verb in this feature MUST return structured, machine-parseable output by
  default (the same convention `propose` already follows), not prose.
- **FR-013**: `doctor` and `optimise` are explicitly out of scope for this feature (deferred per
  docs/design/28-maintenance.md).
- **FR-014**: Each verb MUST be implemented as a thin wrapper over existing pure functions in
  `session.py`, `chronicle.py`, `state.py`, `era.py`, `thread.py`, `threat.py` rather than
  duplicating their logic; new pure-function logic is added only where no existing function
  covers a verb's behaviour.
- **FR-015**: Each verb MUST be registered in `catalog.py`'s `TOOLS` registry following the
  pattern established by `find-noun`/`find-rule`/`find-table` (#397/PR #398), and dispatched
  through `client.py`'s existing argparse-from-`TOOLS` mechanism.

### Key Entities

- **Chronicle state**: the persisted state a chronicle's verbs read and write — entities,
  overlay, log, recap, calendar, active threads and threats (docs/design/22-state.md).
- **Entity**: any named thing (player character, companion, thread, threat, arc, beat, etc.) in
  the ten types docs/design/25-entities.md defines; each resolves to one effective form.
- **Thread**: an open narrative element tracked with a `heat` value that governs how prominently
  it surfaces in the Always-loaded tier versus the general `find`/`threads` query.
- **Threat**: an entity carrying a threat block with an `imminence` value governing activation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every verb named in docs/design/02-architecture.md's verb list, except
  `doctor`/`optimise`, is callable via `wyrd <verb>` and exits successfully against a
  well-formed chronicle fixture.
- **SC-002**: Each verb has at least one automated test asserting its output against real
  computed values (not merely that it runs without raising).
- **SC-003**: `ruff check .` and `ruff format --check .` report no findings repo-wide after this
  feature lands.
- **SC-004**: No verb added by this feature introduces logic duplicating an existing pure
  function in `session.py`, `chronicle.py`, `state.py`, `era.py`, `thread.py`, or `threat.py` —
  verified by each verb's implementation calling the existing function rather than
  reimplementing its behaviour.

## Clarifications

### Session 2026-09-15

- Q: `party`'s filter is `role: companion` + `status: with-party`, but `find`'s public flags are
  only `--type`/`--status`/`--tag`; does `party` need to be expressible through those same public
  flags, or is it a distinct verb sharing `find`'s underlying matching mechanism on fields
  `find`'s own flags don't expose? → A: distinct verb sharing the underlying mechanism — `find`'s
  public flag surface is not extended to cover `role` for this feature.

## Assumptions

- The pure-function logic each verb needs mostly already exists in the six named modules, per
  the issue's own framing; where a genuine gap exists (e.g. no existing function directly
  implements the `session-context` composition query, or `find`'s general filtering), this
  feature adds the minimal pure function needed and wires it in the same way, rather than
  leaving the verb unimplemented.
- "Effective form" for `get`/`find` follows docs/design/22-state.md's existing definition
  (setting + overlay, or chronicle-native entities) unchanged by this feature.
- CLI output format follows the existing structured-output convention `propose` already uses;
  no new output format is introduced.
- This feature does not add the five `wyrd-*` skills that would consume these verbs
  conversationally — those are separate sibling features under epic #401.
