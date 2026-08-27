# Feature Specification: Design the CLI's state-loading and querying surface, and the three memory tiers

**Feature Branch**: `187-cli-state-query-surface`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Design the CLI's state-loading and querying surface, and the three memory tiers (closes #187, part of #133). 02-architecture.md's CLI sketch covers dice and track mutation, not state loading, querying, or the three memory tiers it only describes in prose. Expand the CLI to cover state loading, querying, and the three memory tiers as full specification."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A GM starts a session and gets exactly the "Always loaded" context in one call (Priority: P1)

A GM resuming a chronicle needs the player character, present companions, hot threads,
`recap.md`, and the engine contract — without constructing that set by hand from individual
entity lookups.

**Why this priority**: This is the tier `02-architecture.md` already names as "Always loaded,"
"chosen by query, not manifest" — but no command exists that runs that query.

**Independent Test**: Given a chronicle with a player character, at least one present companion,
and at least one hot thread, running the session-context command returns all of them plus
`recap.md` and the contract, in one structured result.

**Acceptance Scenarios**:

1. **Given** a chronicle with a player character, two companions (`with-party` and `away`), and
   three threads (two `open`, one `resolved`), **When** the session-context query runs, **Then**
   it returns the player character, only the `with-party` companion, only the `open` threads
   ordered by heat, `recap.md`, and the contract — never the `away` companion or the `resolved`
   thread.

### User Story 2 - A GM fetches or searches any other entity on demand (Priority: P1)

A scene needs an entity not in the always-loaded set — a place, an NPC, a past thread — found by
id or by a query over type/status/tag, without the GM reading files directly.

**Why this priority**: This is the "On demand" tier — currently described in prose only, with no
command backing it.

**Independent Test**: Given a chronicle with entities of several types, fetching one by id
returns its effective (setting + overlay, or chronicle-native) frontmatter; a filtered query
returns only entities matching every given filter.

**Acceptance Scenarios**:

1. **Given** an entity that exists in the setting and has a chronicle overlay, **When** it is
   fetched by id, **Then** the returned content is the effective entity (setting merged with
   overlay), not either half alone.
2. **Given** entities of several types and statuses, **When** a query filters by type and
   status, **Then** only entities matching both are returned.

### User Story 3 - A GM reads recent log history without touching `log/` directly (Priority: P2)

The Archival tier is rarely read, but when it is needed (recapping recent events, auditing a
past outcome), it should be a command, not a raw file read.

**Why this priority**: Stated as the third tier; lower priority than the other two because it is
explicitly "rarely read."

**Independent Test**: Given a chronicle with logged beats, requesting the last N entries or
entries since a given beat returns exactly those, in order.

**Acceptance Scenarios**:

1. **Given** a chronicle with 500 logged beats, **When** the last 10 are requested, **Then**
   exactly those 10 are returned, most recent last.

### Edge Cases

- What happens when session-context is run on a chronicle with zero open threads or zero
  present companions? The query returns an empty list for that part, not an error — absence is a
  valid, common state.
- Does fetching an entity by id that doesn't exist in either the setting or the chronicle error,
  or return nothing? It MUST error clearly (distinct from "found, but empty") — a silent empty
  result on a typo'd id is a worse failure mode than a clear one.
- Is full-text/semantic search over the Archival log in scope? No — explicitly deferred (see
  Assumptions); `--since`/`--last` covers the common case of recent history.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST provide a command that runs the "Always loaded" tier's query and
  returns the player character, present companions (`role: companion`, `status: with-party`),
  open threads (`status: open`, ordered by `heat` descending), `recap.md`, and the engine
  contract, as one structured result.
- **FR-002**: The CLI MUST provide a command to fetch a single entity by id, resolving it to its
  effective form (setting + overlay, or chronicle-native, per `22-state.md`'s existing
  definition) — not either half alone.
- **FR-003**: The CLI MUST provide a generic query command filtering entities by type, status,
  and/or tag, returning only entities matching every given filter.
- **FR-004**: The CLI MUST provide named convenience commands for the query patterns
  `22-state.md` already establishes as queries (party, open threads, active threats), each a
  thin wrapper over FR-003's generic query — so a lightweight model doesn't need to construct
  the correct filter arguments by hand for an already-named concept.
- **FR-005**: The CLI MUST provide a command to read Archival log entries by a recency window
  (`--last N`) or a beat range (`--since <beat>`), returned in beat order.
- **FR-006**: Fetching a nonexistent entity id MUST error distinctly from a query returning zero
  matches — the two are different outcomes and must be distinguishable.
- **FR-007**: All query/fetch commands MUST return structured (machine-parseable) output by
  default, matching `wyrd roll`'s existing "full structured result" precedent — diegetic
  rendering is a GM-contract/skill concern, not the CLI's.
- **FR-008**: Full-text or semantic search over the Archival log is explicitly out of scope for
  this feature; `02-architecture.md` MUST state this as a deferred capability with its reason,
  not silently omit it.

### Key Entities

- **Session context** — the always-loaded bundle: player character, present companions, open
  threads, `recap.md`, contract. Not a stored entity itself — the result of a query, per
  `02-architecture.md`'s existing "chosen by query, not manifest" principle.
- **Effective entity** — `setting/<id>` + `overlay/<id>`, or `entities/<id>` if
  chronicle-native, per `22-state.md`'s existing definition, unchanged by this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `02-architecture.md`'s "Memory tiers" section states each tier's CLI backing
  concretely — the command(s), what they take, what they return.
- **SC-002**: `02-architecture.md`'s CLI sketch is expanded with the state-loading/querying
  commands, in the same format the existing dice/track commands are shown.
- **SC-003**: The deferred capability (Archival full-text search) is stated explicitly, with a
  reason, not silently absent.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass.

## Assumptions

- This is a design specification, not an implementation — the CLI commands are specified (name,
  inputs, outputs), not built; `#90` (Implement the engine) is where code lands. This matches
  every other design document in `docs/design/` describing a mechanism the engine will later
  implement (e.g. `03-rules.md` specifies resolution without shipping a resolver).
- Full-text/semantic search over the Archival log is deferred: the log is explicitly "rarely
  read" per its own tier definition, and `--since`/`--last` already covers the common real
  need (recent history); a search capability over years of log history is a materially bigger,
  separate feature with its own indexing question.
- `22-state.md`'s player-character frontmatter example predates two already-landed rules
  changes (`luck` merged into `fortune`, ADR 0041; Resolve's cap is now computed —
  `max(Taint, Trauma) + 3`, ADR 0049 — not a stored `max`) and is corrected as part of this
  feature's own state-loading work, since the session-context command returns exactly this
  frontmatter.
