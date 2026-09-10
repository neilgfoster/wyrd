# Feature Specification: Beat/arc structure and the session loop

**Feature Branch**: `309-beat-arc-session-loop`

**Created**: 2026-09-10

**Status**: Draft

**Input**: GitHub issue #309 — Beat/arc structure and the session loop

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Arcs contain, beats are played (Priority: P1)

A GM (or another engine module) represents the containment hierarchy — a chronicle's arcs nest
recursively to whatever depth the material warrants, and a beat is always a leaf: one goal,
attempted, resolved, persisted. `docs/design/25-entities.md` already gives `arc` and `beat` entity
types; this feature is the engine logic that enforces the distinction between them ("arcs
organise, beats are played") rather than leaving it as an unenforced convention.

**Why this priority**: Every other part of the session loop (recap, Rally boundary, session
shapes) is defined in terms of "a beat closing" or "an arc's children" — without an enforced
container/leaf distinction nothing downstream has solid ground to stand on.

**Independent Test**: Construct an arc with a beat child and an arc with an arc child; attempt to
give a beat a child of its own and confirm it is rejected.

**Acceptance Scenarios**:

1. **Given** an arc with children, **When** a beat is added as one of them, **Then** it is
   accepted (a beat is a valid child of an arc).
2. **Given** a beat, **When** an attempt is made to give it a child of its own, **Then** the
   engine rejects it — a beat is never a container, regardless of how few children an arc above
   it has.
3. **Given** an arc with exactly one beat child, **When** its structure is inspected, **Then** it
   is still reported as an arc, not collapsed into being "just a beat."

---

### User Story 2 - Played or summarised is the GM's call, not the beat's property (Priority: P1)

A GM narrates a beat either **played** (zoomed in — opposed actions, sequence matters) or
**summarised** (zoomed out — travel, a week of work, no real opposition). The same beat's content
does not dictate which mode applies; the choice is made each time the beat is narrated, and one
chronicle may play a beat that another summarises.

**Why this priority**: This is the mechanism `docs/design/16-session.md` names as the primary
lever for pacing ("one session can cover a fortnight of travel in two paragraphs and then spend
fifteen minutes in a cellar") — getting it backed by a stored, inferred property instead of a
live choice would silently defeat the point.

**Independent Test**: Narrate the same beat definition twice, once as played and once as
summarised, and confirm the engine records the mode as a property of that particular narration,
not of the beat's definition.

**Acceptance Scenarios**:

1. **Given** a beat with no prior narration, **When** the GM narrates it as played, **Then** the
   record of that beat's resolution carries `mode: played`.
2. **Given** the same beat definition used in a different chronicle, **When** the GM narrates it
   as summarised there, **Then** that chronicle's record carries `mode: summarised` independent of
   the first chronicle's choice.
3. **Given** a beat's stored definition (goal, description), **When** inspected before any
   narration, **Then** it exposes no field that predicts or fixes which mode will be chosen.

---

### User Story 3 - The session loop walks load → orient → recap → beat → repeat → close (Priority: P1)

Loading a chronicle for play runs a fixed sequence: load state, orient (advance elapsed time
*before* the recap is generated, so the recap can describe what changed), recap (three sentences),
then one or more beats, until the player stops, then close (compaction, recap regeneration,
commit).

**Why this priority**: This is the shape every session takes; without an engine-checkable
representation of the six steps, nothing enforces that orient happens before recap (the design
doc calls this out specifically: "the world having moved is the first thing the player learns"),
or that a session cannot silently skip straight from load to beat.

**Independent Test**: Drive the loop through a scripted sequence of steps and confirm each step
is only reachable from its declared predecessor, and that orient always completes before recap
runs.

**Acceptance Scenarios**:

1. **Given** a chronicle with elapsed time since last play, **When** the session loop starts,
   **Then** orient runs and completes before recap is generated.
2. **Given** a session mid-beat, **When** the player stops, **Then** the loop does not proceed to
   close without a Rally or an explicit mid-beat persistence (see User Story 4) having happened
   first.
3. **Given** a session that repeats through several beats, **When** the player stops after any
   beat closes cleanly, **Then** close (compaction, recap regeneration, commit) runs exactly once
   for that session.

---

### User Story 4 - No session ever ends mid-beat (Priority: P2)

If the player must stop before a beat resolves, the engine persists a `pending:` marker naming
the unresolved action, so the next session resumes exactly where play left off rather than
re-adjudicating or silently dropping the interrupted action.

**Why this priority**: This is the specific promise the design doc makes about real interruption
("I have to get off the train" mid-fight) — lower priority than the structural stories above
because it is a single, well-scoped edge case layered on top of them, but still required for the
feature to be complete.

**Independent Test**: Stop a scripted session partway through a beat's resolution; reload the
chronicle and confirm the `pending:` marker names the exact unresolved action and resumption
continues from it rather than from the beat's start or the arc's start.

**Acceptance Scenarios**:

1. **Given** a beat with an action in progress, **When** the player stops before it resolves,
   **Then** the engine persists a `pending:` marker naming that action.
2. **Given** a chronicle with a `pending:` marker, **When** the next session loads, **Then** the
   beat resumes from the named action, not from the beat's start.
3. **Given** a beat that resolves cleanly (no interruption), **When** it closes, **Then** no
   `pending:` marker is written.

---

### User Story 5 - Session shape is an internal pacing read, never player-facing (Priority: P3)

The engine classifies a session's likely shape — single beat, interlude, downtime, or extended —
for its own pacing purposes, but this classification never appears in any string shown to the
player; it changes nothing about what the player is told.

**Why this priority**: Useful for internal pacing signals and future tooling, but the design doc
is explicit that this is never announced ("the player does not get told they are in an
Interlude") — lowest priority because nothing else in this feature depends on it, and getting it
wrong is a leak, not a structural failure.

**Independent Test**: Run each of the four shapes through the loop and grep every player-facing
output the engine produces for that session for shape-identifying vocabulary.

**Acceptance Scenarios**:

1. **Given** a completed session of any shape, **When** its classification is computed, **Then**
   the result is available to the GM/engine but does not appear in any player-facing narration
   string.
2. **Given** a session matching each of the four shapes' stated characteristics (length, dice use,
   calendar advancement), **When** classified, **Then** it is assigned the matching shape.
3. **Given** a session that doesn't cleanly match any one shape, **When** classified, **Then** the
   engine still returns a definite answer rather than failing — the classification is a pacing
   read, not a strict validator with a rejection path.

---

### Edge Cases

- What happens when an arc has zero children (neither beats nor further arcs)? It is still a
  valid, empty container — arcs are not required to be immediately populated.
- How does the engine handle a beat that is re-narrated after already being resolved (e.g. the GM
  revisits it)? Out of scope for this feature: `docs/design/29-evolution.md` establishes rules
  apply forward only and history is never recomputed, so a resolved beat's record does not change;
  a genuine re-visit is a new beat.
- What happens if orient finds no elapsed time (the player picked up again immediately)? Orient
  still runs (it is a fixed step in the loop) but produces no changes to narrate; recap proceeds
  unaffected.
- What happens to the `pending:` marker if the arc containing the beat is itself later closed
  without the beat resolving? Out of scope for this feature — arc closure/exit-condition
  interaction with an open `pending:` marker belongs to campaign/chronicle-state features under
  this same epic (#297), not this one.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST represent arcs as containers that may nest recursively (an arc's
  children may be further arcs or beats) and beats as leaves that may never have children.
- **FR-002**: The engine MUST reject any attempt to add a child to a beat.
- **FR-003**: The engine MUST record, for a beat's narration, an explicit `mode` of `played` or
  `summarised` as a property of that narration event, never as a stored or inferred property of
  the beat's own definition.
- **FR-004**: The same beat definition MUST be narratable as `played` in one context and
  `summarised` in another without any change to the beat's stored definition.
- **FR-005**: The engine MUST expose the session loop as six ordered steps — load, orient, recap,
  beat, repeat, close — where orient MUST complete before recap begins.
- **FR-006**: The beat step MUST be able to repeat zero or more times before the loop proceeds to
  close (recap may advance directly to close), ending only when the player stops or an arc's exit
  condition is reached.
- **FR-007**: The close step MUST run exactly once per session and MUST sequence compaction,
  recap regeneration, and commit in that order. The engine exposes this ordering as an interface
  a caller supplies concrete steps to; the concrete content of compaction, recap regeneration and
  commit is out of scope for this feature (it depends on the chronicle state layer, #300, which
  does not exist yet).
- **FR-008**: When a session stops before a beat resolves, the engine MUST expose a way to
  persist a pending marker naming the specific unresolved action, for the caller to store.
- **FR-009**: When a session resumes with an existing pending marker, the engine MUST resume from
  the named action rather than restarting the beat or its containing arc.
- **FR-010**: The engine MUST expose a way to clear a pending marker once its beat resolves
  cleanly (no interruption), distinct from the way it is set.
- **FR-011**: The engine MUST classify a completed (or in-progress, for pacing purposes) session
  into exactly one of the four session shapes — single beat, interlude, downtime, extended.
- **FR-012**: The session shape classification MUST NOT appear in, or influence the wording of,
  any player-facing narration string the engine produces.
- **FR-013**: Arc and beat data MUST be representable using the entity file format's common
  schema and containment relation (`parent`) established in #296 / `docs/design/25-entities.md`,
  without introducing a second, competing containment mechanism.

### Key Entities *(include if feature involves data)*

- **Arc**: A container in the chronicle hierarchy; nests to whatever depth the material warrants;
  has entry/exit conditions and children (arcs or beats). Never itself "played" — it organises.
- **Beat**: The atomic unit of play — one goal, attempted, resolved, persisted. Always a leaf.
  Carries a `mode` (`played`/`summarised`) once narrated, set per-narration rather than stored on
  the beat's definition.
- **Session**: One or more beats played in sequence during one sitting; walks the six-step loop;
  classified after the fact (or provisionally, mid-session) into one of four shapes.
- **Pending marker**: A record naming the specific unresolved action inside a beat that was
  interrupted before resolving, used to resume exactly on the next session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given any arc/beat tree constructed through the engine, attempting to add a child
  to a beat fails 100% of the time, with no code path that succeeds.
- **SC-002**: A beat definition narrated twice under different chosen modes produces two
  independent resolution records whose `mode` fields differ, with zero shared mutable state
  between them.
- **SC-003**: In a scripted session that both interrupts and cleanly resolves beats, resumption
  from a `pending:` marker reaches the exact named action 100% of the time, and no marker is left
  behind after a clean resolution.
- **SC-004**: Grepping all player-facing narration strings produced by the reference test scenarios
  for shape-identifying vocabulary (interlude, downtime, extended, single beat, session shape)
  returns zero matches.

## Assumptions

- "Player-facing narration string" means any text the engine hands off to be shown to the player
  (recap text, beat narration); internal state/log fields are not player-facing and may name the
  shape freely.
- This feature builds directly on the entity file format (#296, closed) for how arcs and beats are
  stored; it does not redesign that format, only adds the containment-enforcement and
  session-loop logic on top of it.
- This module holds no persistent state of its own (matching `wyrd.entity`'s pure-function
  style): the session loop state and the pending marker are plain values a caller stores in
  per-chronicle state; "persisting" and "clearing" the pending marker (FR-008/FR-010) mean the
  caller assigning the module's returned values into that storage, not this module writing to
  disk itself.
- The Rally mechanic (Strain/Stamina recovery, advance award, commit-on-Rally) and the Downtime
  phase's own internal steps (upkeep, undertakings, Mend) are explicitly out of scope — they are
  specified separately as #310 and #311 under the same parent epic (#297), and this feature's
  "beat closing" / "session shape: downtime" hooks are the interface points they will build on.
- Party/companion mechanics (Bond, Tension, Loyalty) are already implemented (`engine/wyrd/party.py`,
  #292/#286) and are not touched by this feature.
