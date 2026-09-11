# Feature Specification: Chronicle transaction lifecycle

**Feature Branch**: `125-chronicle-transaction-lifecycle`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Chronicle transaction lifecycle: interrupted sessions and proposal discard" (issue #328)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A session stopped mid-beat resumes exactly (Priority: P1)

A session ends (crash, or the player simply stopping) while a beat is still open and the player
was about to decide something. The next session, on `load`, finds `chronicle.yaml`'s `pending`
field naming exactly the beat and what the player was mid-deciding, and resumes from there rather
than recapping vaguely or re-asking a question already in flight.

**Why this priority**: this is the core promise `docs/design/22-state.md` § Interrupted sessions
makes and the reason `pending` exists at all; without it a stopped session degrades to guesswork.

**Independent Test**: write a chronicle with `pending: {beat: <id>, awaiting: "...", rolled:
null}`, load it, and confirm the resuming session recovers `beat` and `awaiting` unchanged and
takes no other action.

**Acceptance Scenarios**:

1. **Given** a chronicle whose `pending.beat`/`pending.awaiting` name an in-progress beat and
   decision, **When** a new session loads that chronicle, **Then** the session resumes at that
   beat with that decision still awaiting, without needing anything else recorded.
2. **Given** a chronicle whose `pending` is `null` (no interruption), **When** a new session
   loads it, **Then** the session proceeds through its ordinary `load -> orient -> recap` steps
   with nothing to resume.

---

### User Story 2 - An abandoned proposal is discarded at the next Rally (Priority: P1)

A player was mid-decision on a `propose`d roll (spending Fortune, deciding whether to reroll) when
the session ended before `commit` or `discard` was called. `pending.rolled` holds that
proposal's id across the session boundary. At the chronicle's next Rally, the still-open proposal
is discarded — not carried forward, not silently re-offered — because a proposal is not state
until committed, and a Rally is the recovery point docs/design/16-session.md already defines.

**Why this priority**: without this, a stale proposal that nobody ever explicitly resolved would
either leak into invariant checks it never should have reached, or linger indefinitely as an
un-discardable half-write.

**Independent Test**: given a chronicle with `pending.rolled` set to an open proposal id, run a
Rally and confirm the proposal id no longer resolves (discarded) and `pending.rolled` clears,
independent of whether `pending.beat`/`pending.awaiting` are also present.

**Acceptance Scenarios**:

1. **Given** `pending.rolled` names a proposal id that is still open when a session starts,
   **When** that session reaches its first Rally without the player having committed or
   discarded it, **Then** the proposal is discarded and `pending.rolled` is cleared.
2. **Given** `pending.rolled` is already `null` at a Rally, **When** the Rally runs, **Then**
   nothing changes about `pending.rolled` — clearing an already-clear field is a no-op, not an
   error.

---

### User Story 3 - A moot in-session proposal is explicitly discarded (Priority: P2)

Within a single live session, a player has an open proposal (staged, not yet committed) when the
situation it answered stops applying — the target flees, the player chooses to act on something
else instead. The engine explicitly discards that proposal rather than leaving it open through the
rest of the beat waiting for a `commit`/`discard` that may never come.

**Why this priority**: this is the in-session complement to User Story 2 — it prevents a stale
open proposal from ever being observable as "the only open one" when a new action needs to
propose, without waiting for a Rally to clean it up.

**Independent Test**: given an actor with one open proposal, call the moot-discard path and
confirm the proposal id no longer resolves and the actor has no open proposal, before any Rally
has run.

**Acceptance Scenarios**:

1. **Given** an actor has exactly one open proposal and its situation goes moot before `commit`
   or `discard` is called, **When** the moot-discard path is invoked for that actor, **Then** the
   proposal is discarded (nothing committed) and the actor has no open proposal afterward.

---

### User Story 4 - At most one open proposal per actor is ever representable (Priority: P2)

The engine's own state can never represent two simultaneously open proposals for the same actor.
Whatever slot records "this actor has an open proposal" is a single slot, not a list or a second
independent mechanism alongside `pending.rolled` — matching docs/design/22-state.md's explicit
statement that a session never carries more than one genuinely open proposal per actor.

**Why this priority**: this is an invariant the other three stories all depend on holding — User
Story 2's Rally discard and User Story 3's moot discard both assume there is exactly one
candidate proposal per actor to act on, not a collection to search.

**Independent Test**: attempt to record a second open proposal for an actor that already has one
recorded and confirm the attempt is rejected (or the existing one is what gets replaced/cleared
first) rather than both existing at once.

**Acceptance Scenarios**:

1. **Given** an actor already has an open proposal recorded, **When** something attempts to
   record a second open proposal for that same actor without first clearing the first, **Then**
   the attempt fails rather than silently producing two open proposals for one actor.

### Edge Cases

- A chronicle interrupted with `pending.beat`/`pending.awaiting` set but `pending.rolled` still
  `null` (mid-beat, but no roll was in flight) resumes the beat/decision with nothing to discard
  at the next Rally.
- A chronicle interrupted with `pending.rolled` set but `pending.beat`/`pending.awaiting` both
  `null` (the beat itself had already resolved to a settled decision; only the roll was still
  open) still discards the proposal at the next Rally — the two are cleared independently, not
  as a single all-or-nothing unit.
- A Rally that runs with no pending proposal at all (the ordinary case) takes no discard action —
  discard-at-Rally is conditional on `pending.rolled` actually naming an id, not something every
  Rally does unconditionally.
- The moot-discard path is called for an actor that turns out to have no open proposal (nothing
  to discard) — this must not raise or otherwise treat "nothing to do" as an error, mirroring
  `discard`'s own existing convention for an id that does not resolve.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST read `chronicle.yaml`'s `pending.beat` and `pending.awaiting` on
  session load and resume the named beat with the named decision still outstanding, when
  `pending` is not `null`.
- **FR-002**: The engine MUST proceed through its ordinary load/orient/recap sequence with no
  resumption behaviour when `pending` is `null`.
- **FR-003**: The engine MUST, at the first Rally reached after a session finds `pending.rolled`
  naming a still-open proposal, discard that proposal and clear `pending.rolled` — never carry it
  forward past that Rally.
- **FR-004**: The engine MUST clear `pending.rolled` to `null` when it is already `null` at a
  Rally without raising or otherwise treating the no-op as an error.
- **FR-005**: The engine MUST provide an explicit discard path, invocable within a live session
  (not only at a Rally), that discards an actor's open proposal when its situation has gone moot
  before `commit` or `discard` was called for it.
- **FR-006**: The explicit moot-discard path MUST be a no-op (not an error) when the named actor
  has no open proposal.
- **FR-007**: The engine's state MUST make it structurally impossible to represent two
  simultaneously open proposals for the same actor — a second attempt to record one while the
  first is still open MUST fail rather than silently coexisting.
- **FR-008**: `pending.beat`/`pending.awaiting` and `pending.rolled` MUST be clearable
  independently of each other — clearing one MUST NOT require or imply clearing the other.
- **FR-009**: The engine MUST NOT introduce any field or mechanism, alongside `pending`, for
  recording an open, uncommitted proposal that survives a session boundary — `pending.rolled` is
  the single such record (docs/design/22-state.md § Invariants → Transaction lifecycle).

### Key Entities

- **`pending`** (on `chronicle.yaml`): `{beat, awaiting, rolled}` — `beat`/`awaiting` name an
  interrupted beat's outstanding decision; `rolled` names an open, uncommitted proposal id (or
  `null`) that survived past the end of a session. Already round-tripped opaquely by #325; this
  feature gives its three sub-fields real read/write/clear semantics.
- **Proposal** (docs/design/31-action-resolution.md): the existing `propose`/`commit`/`discard`
  unit this feature reuses unchanged — this feature only adds *when* a proposal is discarded on
  the engine's own initiative (Rally, or a moot situation), never a new proposal shape.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A session resumed after an interruption recovers the exact beat and awaiting
  decision recorded at interruption, with no additional recap step required to reconstruct them.
- **SC-002**: Every proposal left open past a session boundary is discarded at the very next
  Rally, with zero carried forward past that Rally — verified by exact-arithmetic tests (not
  eyeballed) covering both an occupied and an already-clear `pending.rolled`.
- **SC-003**: At every point in the engine's own state, an actor has at most one open proposal —
  never two, never a growing backlog.

## Assumptions

- This feature reuses `docs/design/31-action-resolution.md`'s existing `propose`/`commit`/
  `discard` mechanism unchanged (specs/083, specs/084) — it adds *callers* of `discard` (Rally,
  moot-discard) and read/write handling for `pending`'s three sub-fields, not a new proposal
  mechanism.
- "At most one open proposal per actor" is enforced by the caller-owned slot that records which
  proposal id (if any) is currently open for an actor — the same slot `pending.rolled` persists
  across a session boundary — rather than by any change to `resolution.py`'s own proposal-id
  registry, which already treats each id as independently open or invalidated.
- The invariant cascades themselves (Transformation/Affliction/`lost` triggers) and entity
  load-tier resolution are out of scope, per the issue's own scope note — this feature touches
  only `pending` semantics and proposal discard timing.
- `wyrd.session`'s existing `set_pending`/`resume_from_pending`/`clear_pending` (pre-dating this
  issue, shape `{beat_id, action, set_at}`) predates `chronicle.yaml`'s actual `pending` schema
  (`{beat, awaiting, rolled}`, specs/122); reconciling the two is in scope here as part of wiring
  real semantics onto `chronicle.yaml`'s field, per docs/design/22-state.md's explicit statement
  that `pending.rolled` — not a second mechanism — is where an open proposal lives.
