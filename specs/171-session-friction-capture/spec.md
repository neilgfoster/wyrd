# Feature Specification: Session friction capture

**Feature Branch**: `171-session-friction-capture`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "Specify how session friction is captured during play" (issue #94, child of epic #93 "Closed feedback loop: chronicle play back to the engine backlog")

## Clarifications

### Session 2026-09-17

- Q: Where does the friction log file live, exactly? → A: `log/friction.md`, inside the existing `log/` directory where session logs already live (per `docs/design/23-chronicle-bootstrap.md`'s chronicle layout).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The GM notices friction mid-beat and records it without leaving the fiction (Priority: P1)

While running a beat, the GM (the engine, narrating) hits a moment where a mechanic reads one
way in the design documents and plays differently, or a table produces a result that feels
wrong, or something the rules never covered has to be improvised on the spot. The GM appends a
short, structured note to a durable file in the chronicle repo and continues narrating — the
player never sees this happen and the beat is not interrupted.

**Why this priority**: This is the entire point of the feature. If capture costs more than a
moment of GM attention, it will not happen, and the loop epic #93 exists to close stays open.

**Independent Test**: Can be fully tested by hand-authoring a beat that provokes a friction
moment (e.g. an undefined edge case in a table lookup), appending one note in the specified
format, and confirming the chronicle repo now durably records it — no other subsystem involved.

**Acceptance Scenarios**:

1. **Given** a beat in progress, **When** the GM encounters a mechanic that read one way in a
   design document and played another, **Then** the GM appends one structured entry to the
   session's friction log, in the format this spec defines, without pausing the narration the
   player sees.
2. **Given** a beat in progress, **When** the GM has to improvise because a rule left something
   undefined, **Then** the GM appends an entry recording what was undefined and what the GM did
   instead.
3. **Given** ordinary narrative color — a well-received description, a player's in-character
   joke, a color detail that provoked no rules question — **Then** no entry is written; capture
   is for friction only.

---

### User Story 2 - A future harvest pass can read entries without seeing the chronicle's story (Priority: P1)

Sibling issue #95 will later read every chronicle's friction entries across a fleet of
chronicles and propose `wyrd` engine issues from the genuine gaps among them. For that to be
possible without importing narrative content into the public `wyrd` repo, each entry must state
the mechanical finding in setting-agnostic, self-contained terms — nameable without the reader
having played the session.

**Why this priority**: This is the acceptance criterion in epic #93 that makes the whole loop
publishable — "only the mechanical finding travels, never the narrative." A capture format that
can't be read this way defeats the epic's purpose even if capture itself is cheap.

**Independent Test**: Can be fully tested by writing one entry per the format and independently
checking that a reader with no chronicle context can state what engine behaviour it's about
without needing the surrounding session transcript.

**Acceptance Scenarios**:

1. **Given** a written friction entry, **When** it is read in isolation, **Then** it names the
   mechanic or table involved and what happened, without naming characters, places, or plot
   specific to the chronicle's story.
2. **Given** a written friction entry that unavoidably needs one concrete example to be legible,
   **When** that example is written, **Then** it is phrased generically (values and outcome only)
   rather than quoting the chronicle's actual scene.

---

### User Story 3 - The convention holds in a solo, GM-plays-the-party session (Priority: P2)

Wyrd's default play mode is one player with the GM running the entire rest of the party
([`docs/design/16-session.md`](../../docs/design/16-session.md) "The party"). There is no second
real person who might notice friction the player misses. The capture convention must not assume
someone else is present to flag it — the GM (the engine itself, in its narrating role) is the
one who notices and records.

**Why this priority**: Confirmed explicitly in issue #94's scope. A convention that only works
with two real people at the table would fail Wyrd's primary play mode.

**Independent Test**: Can be fully tested by running the single-player scenario from Story 1
and confirming the same mechanism applies with no second participant assumed anywhere in the
convention's wording or file format.

**Acceptance Scenarios**:

1. **Given** a solo chronicle session with only the player and the GM-run party, **When**
   friction occurs, **Then** the same GM-authored entry mechanism applies unchanged — nothing in
   the convention requires a second real person to flag the moment.

---

### Edge Cases

- What happens when a beat produces friction but the session is stopped mid-beat (a `pending:`
  marker, per [`docs/design/16-session.md`](../../docs/design/16-session.md) "The Rally")? The
  entry is still appended at the moment it occurs, independent of whether the beat later
  completes at a Rally — capture is not deferred to session close.
- What happens when the same friction recurs across several sessions (e.g. the same table keeps
  producing an odd result)? Each occurrence gets its own entry; deduplication and pattern-finding
  are the harvest step's job (#95), not capture's.
- What happens when a note would require quoting story content to make sense (a character's
  specific secret, a plot twist)? The entry is not written that way — see User Story 2's second
  acceptance scenario. If a finding genuinely cannot be stated without narrative content, this
  spec treats that as a signal the note belongs in ordinary session prose instead, not in the
  friction log.
- What happens if the GM is unsure whether something is friction or just color? The triage line
  below (Functional Requirements) is the test; when a moment fails all three of that line's
  criteria, no entry is written.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The convention MUST define a single, durable location per chronicle repo where
  friction entries accumulate — `log/friction.md` inside the chronicle's existing `log/`
  directory (per Clarifications), distinct from `recap.md` and from the beat-by-beat session
  log files so that harvesting (#95) has one predictable path to read across any chronicle,
  and so ordinary narrative log content is never conflated with it.
- **FR-002**: The convention MUST define an entry format that is short to produce (no more GM
  attention than reading a Wyrd die) and structured enough for a later, unattended pass to parse
  and triage without needing to re-read the session.
- **FR-003**: Each entry MUST record, at minimum: what mechanic, table, or design document
  section is implicated; what happened (the reading that turned out wrong, the undefined case,
  the result that felt off); and what the GM did about it in the moment (improvised a ruling,
  played it as written and noted the friction, or something else).
- **FR-004**: The convention MUST state an explicit triage line, testable at the moment of the
  friction, distinguishing what is worth an entry from ordinary session prose. An entry is
  warranted when at least one of the following holds:
  1. a mechanic or table in `docs/design/` (or the setting's equivalent) produced a reading in
     play that a reasonable GM following that document would not have predicted;
  2. a table or roll produced an outcome that, given the situation, felt wrong even though the
     mechanic was followed correctly;
  3. the GM had to improvise a ruling because no document — engine or setting — covered the
     situation.

  Ordinary narrative color (a scene description, an in-character line, a companion's flavor
  reaction) never qualifies on its own, even when memorable.
- **FR-005**: The convention MUST work with capture performed entirely by the GM (the engine, in
  its narrating role) — it MUST NOT require a second real participant to notice or flag
  friction, since Wyrd's default and primary play mode is one player with a GM-run party
  ([`docs/design/16-session.md`](../../docs/design/16-session.md)).
- **FR-006**: The convention MUST require each entry to be self-contained and setting-agnostic
  in its *mechanical* description — nameable and understandable by a reader with no access to
  the chronicle's narrative content — while permitting the entry to omit or generalize any
  detail that would otherwise require quoting the chronicle's actual story.
- **FR-007**: The convention MUST NOT require any extra step, confirmation, or ceremony visible
  to the player. Capture happens entirely on the GM's/engine's side of the fourth wall, the same
  side other engine bookkeeping (state persistence, Rally accounting) already happens on.
- **FR-008**: The convention MUST NOT block or delay a beat's narration — an entry is appended
  and play continues; there is no synchronous confirmation step.
- **FR-009**: The convention MUST be engine-defined and generic: nothing in the entry format or
  its triage line may reference a specific setting's vocabulary, tone, or content
  ([`CLAUDE.md`](../../CLAUDE.md) "the engine is setting-agnostic").
- **FR-010**: [`docs/design/16-session.md`](../../docs/design/16-session.md) MUST document this
  convention as part of session structure, including the file location, entry format, the
  triage line, and one worked example each of a qualifying friction note and a non-qualifying
  color note (per issue #94's acceptance criteria).

### Key Entities

- **Friction entry**: One record of a single friction moment. Fields: which mechanic/table/design
  section is implicated, what happened, what the GM did, and (optionally) the beat/session it
  occurred in for traceability — never a narrative summary of the scene itself.
- **Friction log**: The durable, per-chronicle file that accumulates friction entries across the
  chronicle's life, in append-only order, ready for a later harvest pass (#95) to read across
  one or more chronicles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A GM narrating a beat can record a friction moment in the time it takes to note a
  die result — a few seconds, not a pause that the player would notice as a break in the scene.
- **SC-002**: Every entry produced under this convention can be understood by a reader with zero
  context on the chronicle's story — no character name, place name, or plot detail is required
  to understand what engine behaviour the entry is about.
- **SC-003**: A chronicle played entirely solo (one player, GM-run party) produces friction
  entries at the same rate and format as the convention describes generally — nothing about the
  convention depends on a second real participant.
- **SC-004**: Given a set of session transcripts containing both genuine engine-gap moments and
  ordinary narrative color, a GM applying the stated triage line produces entries for the former
  and none for the latter, consistently.

## Assumptions

- The convention is authored into `docs/design/16-session.md`, the existing home for session
  structure, rather than a new top-level design document — the parent epic #93 and issue #94 both
  point there, and the file already documents the Rally (the other point at which state is
  written during play).
- The friction log lives in each `wyrd-chronicle-<name>` repo (per
  [`docs/design/23-chronicle-bootstrap.md`](../../docs/design/23-chronicle-bootstrap.md)'s layout),
  not in the `wyrd` engine repo itself — chronicles carry player-specific content and this repo
  must never receive it directly ([`CLAUDE.md`](../../CLAUDE.md) "nothing unpublishable may enter
  this repository").
- This feature is a design/spec change only: it defines the convention and updates
  `docs/design/16-session.md`. It does not build the harvest tooling that reads friction logs
  across chronicles — that is sibling issue #95, explicitly out of scope here, and depends on
  this issue's outcome.
- A plain-text, human-readable file format (not YAML/JSON) is assumed adequate for "structured
  enough to triage later" per issue #94's own phrasing, since the GM authoring an entry mid-beat
  should not need to satisfy a schema in the moment; the harvest step (#95) is responsible for
  whatever parsing its own implementation needs, informed by the format this spec settles.
- No new engine code accompanies this feature — the convention is authored guidance and file
  location/format, consistent with #94 being scoped as a design question inside session
  structure rather than a new tool (per epic #93's own scope note).
