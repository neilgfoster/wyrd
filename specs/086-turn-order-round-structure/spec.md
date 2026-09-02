# Feature Specification: Turn order and round structure

**Feature Branch**: `243-turn-order-round-structure`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Implement the turn-order/round state machine: which side acts first (exchange-starter, or the armed-side/player-side tiebreak for a mutual encounter per ADR 0018), round completion, and the surprise/ambush modifiers (no action but still defends when surprised; +20 to the first round's attacks only when ambushed). Closes #243, part of #212 (Conflict), depends on #211."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The side that started the exchange goes first (Priority: P1)

A GM starts a combat where one side clearly initiated it (an ambush, a declared attack). The
engine reports that side as acting first, without asking anything about weapons or who's a
player.

**Why this priority**: This is the base rule `docs/design/03-rules.md` states first — everything
else in this feature is the fallback for when it doesn't apply.

**Independent Test**: Given a combat started with an explicit initiating side, the engine reports
that side as the first actor, regardless of armed status of either side.

**Acceptance Scenarios**:

1. **Given** a combat where side A started it, **When** the engine determines the first actor,
   **Then** it reports side A, whatever the armed status of either side.

---

### User Story 2 - A mutual encounter is decided by who's armed, then by the player's side (Priority: P1)

Neither side started the exchange — both parties become aware of each other at once. The engine
falls back to `docs/design/03-rules.md`'s own tiebreak: whichever side already holds a weapon
acts first; if both or neither do, the player's side acts first.

**Why this priority**: This is the one rule in this section decided from outside the fiction
(ADR 0018) — the engine must get it exactly right, since nothing in the fiction can override it.

**Independent Test**: Given a mutual encounter (no starting side named), the engine reports the
armed side as first actor when exactly one side is armed, and the designated player side when
both or neither are.

**Acceptance Scenarios**:

1. **Given** a mutual encounter where only side A is armed, **When** the engine determines the
   first actor, **Then** it reports side A.
2. **Given** a mutual encounter where both sides are armed, **When** the engine determines the
   first actor, **Then** it reports the designated player side.
3. **Given** a mutual encounter where neither side is armed, **When** the engine determines the
   first actor, **Then** it reports the designated player side.

---

### User Story 3 - A surprised side loses its first turn but still defends (Priority: P1)

A combat starts with one side surprised. That side is excluded from acting in round 1, but a
combat-attack targeting one of its members still resolves normally — they can still be attacked,
and can still defend against it.

**Why this priority**: `docs/design/03-rules.md` states this distinction explicitly ("they lose
their turn, not their reflexes") because getting it wrong doubles what surprise is worth.

**Independent Test**: Given a combat scene where a side is marked surprised, querying whether a
member of that side can act in round 1 returns false; nothing about resolving a `combat-attack`
against them is affected.

**Acceptance Scenarios**:

1. **Given** a side marked surprised, **When** the scene is queried for whether that side can act
   in round 1, **Then** the answer is no.
2. **Given** the same setup, **When** a `combat-attack` targets a member of the surprised side,
   **Then** it resolves exactly as an unmodified attack would (this feature adds no defensive
   penalty).
3. **Given** the scene has advanced past round 1, **When** the same side is queried again,
   **Then** the answer is yes — surprise only ever excludes the first round.

---

### User Story 4 - An ambush eases the first round's attacks, and only the first round's (Priority: P2)

A combat starts as a prepared ambush. The ambushing side's attacks in round 1 carry a +20
modifier; nothing about round 2 onward is affected.

**Why this priority**: `docs/design/03-rules.md` is explicit that this bonus applies to "the
first round's attacks... and nothing after" — a modifier that leaked into later rounds would
overstate ambush by design.

**Independent Test**: Given a side marked as having prepared an ambush, the modifier the scene
reports for that side's own attacks is `+20` in round 1 and `0` from round 2 onward.

**Acceptance Scenarios**:

1. **Given** a side marked as ambushing, **When** the scene reports that side's attack modifier
   in round 1, **Then** it is `+20`.
2. **Given** the same setup, **When** the scene has advanced to round 2, **Then** the modifier it
   reports for that side is `0`.

### Edge Cases

- What happens when a side is marked both surprised and ambushing at once? → Not a real
  combination `docs/design/03-rules.md` describes (surprise belongs to the side caught off
  guard; ambush belongs to the side that prepared it — they are properties of opposite sides of
  the same encounter, never the same side in the same scene). This feature does not guard against
  the caller passing both for one side; it is a caller-input error, not a state this feature
  needs to resolve meaningfully (see Assumptions).
- What happens when `started_by` names a side that doesn't appear in the combat's own side list? →
  A `ValueError`, the same class of caller-input validation the rest of `engine/wyrd/` already
  uses (e.g. `resolution.propose`'s unknown-mechanic check).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to start a combat scene naming its sides, each
  side's armed status, which side (if any) started the exchange, and which side (if any) is the
  designated player side.
- **FR-002**: Starting a combat scene MUST determine the first actor per `docs/design/03-rules.md`
  §2: the exchange-starter if one is named; otherwise the sole armed side; otherwise the
  designated player side (both/neither armed).
- **FR-003**: The started scene MUST persist a round counter, initialized to `1`, in chronicle
  state (`state.py`'s existing atomic save/load) — a scene's turn/round state outlives a single
  `propose`/`commit` call, the same way an actor's own persisted fields do.
- **FR-004**: The engine MUST provide a way to advance the scene to the next round.
- **FR-005**: The engine MUST provide a way to mark one or more sides as surprised, and a way to
  query whether a given side can act in the *current* round — false for a surprised side only
  while the scene's round counter is still `1`, true otherwise (and true for a non-surprised
  side always).
- **FR-006**: The engine MUST provide a way to mark one or more sides as having prepared an
  ambush, and a way to query that side's own attack modifier in the current round — `+20` while
  the round counter is `1`, `0` otherwise.
- **FR-007**: Surprise MUST NOT affect whether a `combat-attack` targeting a member of the
  surprised side resolves, or how — only whether that side's own members may act on their own
  turn (a scene-level fact this feature tracks, not something `resolution.propose` itself needs
  to consult, since `propose` already resolves whatever attack it's given regardless of turn
  order — turn order is enforced by the caller, per FR-008's own scoping note).

### Key Entities

- **Combat scene**: persisted chronicle state — `sides` (a mapping of side name to its armed/
  surprised/ambushing flags), `round` (starts at `1`), `first_actor` (computed once, at start).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: First-actor determination matches `docs/design/03-rules.md`'s own rule exactly
  for every combination User Stories 1–2 name (explicit starter; mutual + one armed; mutual +
  both armed; mutual + neither armed) — verified by tests, not asserted.
- **SC-002**: A surprised side cannot act in round 1 and can in round 2+; an attack against a
  surprised side's member is unaffected either way.
- **SC-003**: An ambushing side's attack modifier is `+20` in round 1 and `0` in round 2+.
- **SC-004**: `ruff check . && ruff format --check . && python3 -m pytest -q` is clean.

## Assumptions

- Scene state is persisted in chronicle-level state (`state.py`'s `chronicle_state.yaml`), not a
  per-entity file — a combat scene is a property of the chronicle's current moment, not of any
  one character, consistent with `docs/design/22-state.md`'s own file-per-entity-else-chronicle
  split.
- `resolution.propose`'s `combat-attack` mechanic (#211) is unmodified by this feature — turn
  order/surprise/ambush are the caller's own responsibility to consult before deciding *whether*
  to call `propose` for a given actor's turn, and to add the ambush modifier via `propose`'s
  existing `declaration_bonus` parameter when it applies (`03-rules.md`'s own Declaration
  composition already allows a numeric modifier to be supplied, not computed inside `propose`
  itself). This feature reports the numbers; it does not reach into `resolution.py` to enforce
  them.
- "Side" is a caller-supplied label (e.g. `"party"`, `"opposition"`), not tied to any particular
  entity file — this feature tracks side-level flags, not per-combatant ones (surprise and
  ambush are properties `03-rules.md` states at the side level: "a surprised **side**").
