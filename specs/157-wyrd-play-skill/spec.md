# Feature Specification: The /wyrd-play skill

**Feature Branch**: `157-wyrd-play-skill`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Build the /wyrd-play skill -- the central, repeatedly-invoked
skill of actual play, resuming a chronicle and running one beat."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resume and orient at the start of a session (Priority: P1)

A player who has already bootstrapped a chronicle (via /wyrd-bootstrap) opens their chronicle
repo, invokes /wyrd-play, and is told -- in prose, without engine jargon -- where their
character is, what has changed since they last stopped, and what is unresolved. They are not
shown a menu of options.

**Why this priority**: Without a correct, minimal orientation, no beat can be run credibly --
this is the load-bearing first half of every single invocation.

**Independent Test**: Invoke /wyrd-play against a bootstrapped chronicle with no `pending`
marker and confirm it loads exactly the Always-loaded tier (player character, present
companions, hot threads, recap, contract) via `session-context`, and narrates an orientation
grounded in that data, with no invented facts and no exposed engine scaffolding (thread ids,
difficulty numbers, beat labels).

**Acceptance Scenarios**:

1. **Given** a bootstrapped chronicle with no `pending` marker, **When** the player invokes
   /wyrd-play, **Then** the skill calls `session-context`, presents a plain-prose orientation
   built from its returned player character, companions, threads and recap, and does not
   present a list of options.
2. **Given** a chronicle whose `chronicle.yaml` carries a `pending` marker from a prior
   mid-beat stop, **When** the player invokes /wyrd-play, **Then** the skill resumes exactly
   the unresolved action named in `pending` rather than starting a new beat.

---

### User Story 2 - Run a beat with code-backed resolution (Priority: P1)

Having been oriented, the player declares an action in character. The GM narrates the
situation, calls the appropriate engine verb (`propose`, an `opposed-test`, or a `track`
change) to resolve anything that needs a roll or a state change, narrates the outcome from
the verb's own returned result, and persists the beat before the closing narration.

**Why this priority**: This is the actual play loop -- the reason the skill exists. Without
it, orientation alone delivers no value.

**Independent Test**: Walk one full beat against a real bootstrapped chronicle (a real
setting's data) that includes at least one moment calling for a roll, and confirm every
mechanical outcome (success/failure, degrees, a track's new value) traces verbatim to a CLI
verb's return value, with `propose`/`commit` (or `discard`, for a declined proposal) called
in the correct order and no state written before a roll's result is known.

**Acceptance Scenarios**:

1. **Given** an oriented session, **When** the player declares an action requiring a skill
   test, **Then** the skill calls `propose` (or `opposed-test`, if a companion is opposed by
   an NPC), narrates the outcome using only the returned result, and either `commit`s the
   staged mutation or `discard`s it consistent with the fiction.
2. **Given** a declared action with no mechanical uncertainty (no opposition, no meaningful
   chance of failure), **When** the player takes it, **Then** the skill narrates the outcome
   in prose without inventing a roll the fiction did not call for.
3. **Given** a beat that ends at a natural stopping point, **When** the beat resolves,
   **Then** the skill runs a Rally (recovering Strain/Stamina via the `rally` verb) and
   writes state to disk before the closing narration is shown.

---

### User Story 3 - Leave valid, saved state at every stopping point (Priority: P2)

Whether the player continues to another beat or stops after one, the chronicle is left in a
state that a later invocation (of /wyrd-play or /wyrd-end-session) can resume correctly --
including the case where the player has to stop mid-beat.

**Why this priority**: A skill that runs a beat but leaves invalid or unsaved state defeats
the persistence guarantee the whole engine depends on (docs/design/01-principles.md principle
2: "persist before narrate").

**Independent Test**: Interrupt an invocation mid-beat (simulate the player stopping before a
roll's outcome is narrated) and confirm the chronicle's `pending` marker is written accurately
and `validate` reports no errors afterward; separately, complete a beat cleanly and confirm no
`pending` marker is left and `validate` still reports no errors.

**Acceptance Scenarios**:

1. **Given** the player says they must stop before the current action resolves, **When** the
   skill ends the invocation, **Then** it writes a `pending` marker naming the beat and the
   unresolved action, saves state, and does not fabricate a resolution.
2. **Given** a beat resolves cleanly to a Rally, **When** the invocation ends, **Then**
   `chronicle.yaml` has no `pending` marker, all mutations from the beat are committed, and
   `validate` reports the chronicle as valid.

---

### Edge Cases

- What happens when /wyrd-play is invoked before /wyrd-bootstrap has ever run (no
  `chronicle.yaml` yet)? The skill must say so plainly and stop, rather than attempting to
  load a session-context that does not exist.
- What happens when `session-context` reports a `pending` marker left by a previous
  invocation that never reached /wyrd-end-session? The skill resumes exactly that unresolved
  action rather than starting a fresh beat or silently discarding it.
- What happens when the player's declared action doesn't map cleanly to any single existing
  mechanic (no skill test, no opposition, no track change)? The GM narrates the outcome
  entirely in prose -- not every player action requires a CLI call, and inventing one where
  none is warranted is itself a fault.
- What happens when a `propose` call returns a refusal or an error (e.g. an unknown skill
  name, a missing actor)? The skill reports that error to the player honestly, and does not
  proceed to `commit` against a proposal id that never opened.
- What happens when the party includes companions who are not present (`status` other than
  `with-party`)? They are not loaded into the Always-loaded tier and take no part in the
  beat's mechanical resolution, though the GM may still reference them if the fiction calls
  for it (an absent companion's own agenda continuing off-page).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The skill MUST be invocable, by name, from within a chronicle repository whose
  `chronicle.yaml` already exists (i.e. bootstrap has already completed).
- **FR-002**: If `chronicle.yaml` does not exist, the skill MUST say so plainly and stop
  without calling `session-context` or any other verb that assumes a bootstrapped chronicle.
- **FR-003**: At the start of every invocation, the skill MUST load the Always-loaded memory
  tier via the `session-context` engine verb, and MUST NOT construct that tier's contents
  (player character, present companions, hot threads, recap, contract) by any other means
  (e.g. reading entity files directly, or guessing which companions are present).
- **FR-004**: If `session-context`'s returned state (via `chronicle.yaml`) carries a `pending`
  marker, the skill MUST resume exactly the action it names before offering any new beat.
- **FR-005**: The skill MUST orient the player in prose -- what changed, where their
  character is, what is unresolved -- without exposing engine scaffolding (thread ids, beat
  labels, difficulty numbers, Tension/Bond values) in that narration, per
  docs/design/01-principles.md's GM contract.
- **FR-006**: The skill MUST NOT present the player with a menu of options at any point; it
  narrates a scene and stops for the player's own declared action.
- **FR-007**: For every mechanical step within a beat (a skill test, an opposed test, combat,
  a track change, elapsed time, threat activation), the skill MUST call the corresponding
  existing engine verb (`propose`, `commit`, `discard`, `opposed-test`, `track`,
  `advance-time`, `threat-check`) and MUST use only that verb's own returned values for any
  number or outcome reported to the player -- it MUST NOT recompute a roll, a degree of
  success, a threshold, or a state mutation in its own prose logic.
- **FR-008**: When the player's declaration carries a specific, in-character detail that
  plausibly earns a declaration bonus, the skill MUST resolve that bonus via the engine's own
  `declaration-bonus` lookup (by category) rather than assigning a bonus value itself, per
  docs/design/01-principles.md ("reward declaration over verbosity... never for length").
- **FR-009**: The skill MUST follow `propose`/`commit`/`discard`'s write-nothing-until-commit
  contract: no proposal's mutation may be treated as applied, or narrated as having happened,
  before the matching `commit` call succeeds.
- **FR-010**: At a clean beat boundary, the skill MUST run the Rally CLI verb (fixed
  Strain/Stamina recovery, discard of any leftover open proposal, optional advance award) and
  persist the resulting state before showing the player the closing narration for that beat
  (docs/design/01-principles.md principle 2: "persist before narrate").
- **FR-011**: If the player must stop before the current action resolves, the skill MUST
  write a `pending` marker naming the current beat and the unresolved action, save state, and
  MUST NOT fabricate an outcome to reach a clean stopping point instead.
- **FR-012**: The skill MUST leave the chronicle passing `validate` at the end of every
  invocation, whether the invocation ended at a clean Rally or at a `pending` marker.
- **FR-013**: The skill's own prose MUST NOT bake in any setting- or system-specific
  vocabulary, tone, or name; voice, tone and register come from whatever setting the
  chronicle was bootstrapped against (its `voice.md`/tone contract), read fresh each
  invocation rather than assumed.
- **FR-014**: The skill MUST NOT perform character creation, downtime, or end-of-session
  compaction -- those remain the responsibility of /wyrd-bootstrap, /wyrd-downtime, and
  /wyrd-end-session respectively; /wyrd-play may mention that one of those is available when
  the fiction calls for it, but does not reimplement any of their steps.
- **FR-015**: Companions loaded and referenced during a beat MUST be limited to those with
  `status: with-party` in the entities `session-context` returns; a companion not present is
  not consulted for the beat's mechanical resolution.

### Key Entities

- **Chronicle state** (`chronicle.yaml`): the calendar, session count, and the `pending`
  marker this skill reads and writes at a beat's boundary.
- **Player character** (`pc.yaml`): the character whose action the beat resolves; loaded
  read-only via `session-context`, updated only through a committed proposal or a `track`
  change.
- **Companion**: a `with-party` character entity that may act, be addressed, or be affected
  during a beat; loaded via `session-context`'s own always-loaded companion set.
- **Thread**: an open narrative thread with `heat >= 3`, surfaced by `session-context` as
  something the orientation may reference.
- **Beat**: the atomic unit of play this skill runs one of per invocation (per
  docs/design/16-session.md) -- a single goal, attempted and resolved (or left `pending`).
- **Proposal**: the staged-but-uncommitted result of a `propose` call, referenced by its
  `proposal_id` until this skill's own `commit` or `discard` call resolves it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A player resuming a chronicle after any length of absence receives a correct
  orientation -- grounded entirely in `session-context`'s returned data -- before being asked
  to declare an action.
- **SC-002**: In a full run against a real bootstrapped chronicle, 100% of mechanical outcomes
  narrated to the player (rolls, degrees of success, track changes) trace verbatim to a CLI
  verb's own return value; zero are computed or invented in the skill's own prose logic.
- **SC-003**: Every invocation that reaches a beat boundary leaves the chronicle passing
  `validate` with no errors, whether the beat closed cleanly (Rally, no `pending`) or was
  interrupted (a correctly-populated `pending` marker).
- **SC-004**: Across a full run of at least one beat, the player is never presented with a
  menu of options, and no engine-internal identifier (a thread id, a beat id, a raw
  difficulty number, a Tension/Bond value) appears in in-character narration.
- **SC-005**: The skill's own SKILL.md contains no setting- or system-specific name in its
  prose or its examples.

## Assumptions

- /wyrd-bootstrap has already run at least once on the chronicle being played, so
  `chronicle.yaml` and `pc.yaml` already exist (per issue #405's stated dependency on #403).
- The chronicle-level CLI verbs this skill depends on (`session-context`, `get`, `find`,
  `party`, `threads`, `threats`, `advance-time`, `threat-check`) already exist in the engine
  (per issue #405's stated dependency on #402) and are reachable the same way the four
  existing skills locate the engine package (`find engine -maxdepth 4 -type d -name wyrd`).
- Exactly one beat is run per invocation under normal play; a player who wants to keep going
  simply invokes /wyrd-play again, rather than this skill looping internally across multiple
  beats (docs/design/16-session.md: "REPEAT until the player stops" describes a session,
  which in a Claude Code skill context is a sequence of separate invocations, not one
  unbroken internal loop).
- Session-shape classification (Single beat / Interlude / Downtime / Extended) and the choice
  of whether to play a beat in full detail or summarise it remain entirely the GM's own prose
  judgment, per docs/design/02-architecture.md's code/prose split table -- this skill does not
  compute or announce a shape.
- A known, already-tracked engine defect (#411, career skill-cap shape) may be present
  concurrently but does not block this skill, since /wyrd-play never calls `create-character`
  or any advancement path that exercises it directly.
