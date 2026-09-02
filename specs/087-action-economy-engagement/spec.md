# Feature Specification: Action economy and engagement

**Feature Branch**: `244-action-economy-engagement`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Implement engagement state (a set of close-engagement pairs) and the action-economy rules: closing consumes the turn, breaking off always succeeds and stages a parting-blow combat-attack from every still-engaged opponent, and the two named ranged-attack difficulty cases. Closes #244, part of #212 (Conflict), depends on #243."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Closing consumes the actor's turn (Priority: P1)

A combatant closes with an opponent. The engine records the resulting close-engagement pair and
marks that combatant as having acted this round — they don't also get to attack the same turn.

**Why this priority**: `docs/design/03-rules.md` states this plainly: "Closing costs the closing
combatant their action. They arrive; they do not also swing."

**Independent Test**: Given a combat scene in progress, closing an actor with an opponent
creates the engagement pair, and a second attempt to act for that same actor in the same round
is rejected.

**Acceptance Scenarios**:

1. **Given** two combatants not yet engaged, **When** one closes with the other, **Then** the
   engine records them as engaged and marks the closing combatant as having acted this round.
2. **Given** the same setup, **When** the closing combatant is checked for whether they can still
   act this round, **Then** the answer is no.

---

### User Story 2 - Breaking off always succeeds and stages a parting blow (Priority: P1)

A combatant breaks off from one or more opponents they're engaged with. It always works — no
roll to leave — but every opponent still engaged with them gets one attack (a `combat-attack`
targeting the departing combatant) as they go.

**Why this priority**: This is the exchange rate `docs/design/03-rules.md` names as what keeps
ranged and close combat in tension — getting it wrong (making it fail sometimes, or missing a
parting blow) changes that balance.

**Independent Test**: Given a combatant engaged with two opponents, breaking off removes both
engagement pairs and stages one `combat-attack` proposal per opponent, each targeting the
departing combatant.

**Acceptance Scenarios**:

1. **Given** a combatant engaged with one opponent, **When** they break off, **Then** the
   engagement pair is removed and one `combat-attack` (opponent → departing combatant) is
   staged.
2. **Given** a combatant engaged with two opponents, **When** they break off, **Then** both
   engagement pairs are removed and two `combat-attack` proposals are staged, one per opponent.
3. **Given** a combatant with no current engagements, **When** they break off, **Then** nothing
   is staged — there is no parting blow to take.

---

### User Story 3 - A ranged attack from an engaged shooter is harder (Priority: P2)

A combatant in close engagement takes a ranged shot. The shot resolves at **Difficult** —
`docs/design/03-rules.md`'s own difficulty ladder value — reflected as a modifier to the
shooter's own effective skill for that roll.

**Why this priority**: `docs/design/03-rules.md` names this as the row that "stops a fight
collapsing into everyone shooting at arm's length" — a shooter who stays engaged should usually
rather break off, and the modifier is what makes that true mechanically.

**Independent Test**: Given a shooter currently in close engagement, resolving their ranged
attack applies the Difficult modifier to their own effective skill for that roll, compared with
the same shot from an unengaged shooter.

**Acceptance Scenarios**:

1. **Given** a shooter in close engagement, **When** their ranged attack resolves, **Then** its
   `effective_pct` reflects the Difficult modifier (`-20`, `docs/design/03-rules.md` §1's
   ladder).
2. **Given** the same shooter, not engaged, **When** the same ranged attack is resolved,
   **Then** no such modifier is applied.

---

### User Story 4 - Shooting into someone else's engagement risks hitting the ally instead (Priority: P2)

A combatant fires at a target who is themselves engaged with someone else — an ally standing
between the shooter and the intended target's fight. The shot resolves at **Challenging**, and
if it reads an Ill Omen, the ally is hit instead of the intended target.

**Why this priority**: `docs/design/03-rules.md` calls this "the situation that arises
constantly and that no rule covered until it was played" — the redirect is what makes the risk
real, not decorative.

**Independent Test**: Given a target engaged with a named ally, resolving a ranged attack at
that target applies the Challenging modifier; when the resulting roll reads an Ill Omen, the
staged `combat-attack`'s own target is the ally, not the originally-named target.

**Acceptance Scenarios**:

1. **Given** a target engaged with an ally, **When** a ranged attack at that target is resolved,
   **Then** its `effective_pct` reflects the Challenging modifier (`-10`).
2. **Given** the resulting roll reads an Ill Omen, **When** the attack is finalized, **Then**
   the staged proposal's own mutations land on the ally, not the originally-named target.
3. **Given** the resulting roll does not read an Ill Omen, **When** the attack is finalized,
   **Then** the staged proposal targets the originally-named target, unaffected.

### Edge Cases

- What happens when a shooter is both engaged themselves *and* their target is engaged with
  someone else at once? → Out of scope — `docs/design/03-rules.md`'s own table lists these as
  two separate rows; this feature does not define a combined case, matching the design document's
  own silence on it (see Assumptions).
- What happens when `close` is called for an actor who has already acted this round? → A
  `ValueError` — the same "no needless silent no-op" discipline the rest of `engine/wyrd/`
  already follows (`resolution.ProposalError`'s own precedent).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST track close-engagement as a set of pairs, scoped to the current
  combat scene (`combat.py`'s existing `start_combat`/chronicle-state persistence, #243).
- **FR-002**: `close(actor, opponent)` MUST record the engagement pair and mark `actor` as having
  acted this round; MUST raise if `actor` has already acted this round.
- **FR-003**: A per-round "has acted" query MUST be available for a combatant, reset when the
  scene's round advances (`combat.advance_round`, #243).
- **FR-004**: `break_off(actor, ...)` MUST always succeed (no roll, no failure condition), remove
  every engagement pair involving `actor`, and stage one `combat-attack` proposal (via
  `resolution.propose_batch`) per opponent that was still engaged, each attacking `actor`.
- **FR-005**: `break_off` on an actor with no current engagements MUST stage nothing (an empty
  result is a valid, non-error outcome).
- **FR-006**: A ranged attack from a shooter currently in close engagement MUST apply the
  Difficult modifier (`-20`) to the shooter's own effective skill for that roll, via
  `resolution.propose`'s `declaration_bonus` channel.
- **FR-007**: A ranged attack at a target who is engaged with a *named ally* (not the shooter)
  MUST apply the Challenging modifier (`-10`); if the resulting roll's own Wyrd die reads Ill
  Omen, the finalized attack MUST target the ally instead of the originally-named target.
- **FR-008**: FR-007's redirect MUST discard the original (wrongly-targeted) proposal and
  propose a fresh attack against the ally, rather than attempting to retarget an already-staged
  proposal's mutations in place.

### Key Entities

- **Engagement**: a set of unordered pairs `(combatant_a, combatant_b)`, persisted in the current
  combat scene (extends `combat.py`'s scene dict, #243).
- **Round-acted set**: which combatants have already spent their action this round, persisted in
  the same scene, cleared on `advance_round`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Closing creates the engagement pair and consumes the actor's turn, verified by a
  test asserting both the pair and the "already acted" rejection (User Story 1).
- **SC-002**: Breaking off against two engaged opponents stages exactly two `combat-attack`
  proposals, each correctly targeting the departing combatant, and removes both engagement pairs
  (User Story 2).
- **SC-003**: An engaged shooter's ranged attack `effective_pct` differs from an unengaged
  shooter's by exactly the Difficult modifier, for a real seeded scenario (User Story 3;
  disclosed in research.md, not asserted).
- **SC-004**: A real seeded scenario demonstrates both branches of the ally-redirect (Ill Omen
  triggers the redirect; a different seed does not) — research.md discloses both.
- **SC-005**: `ruff check . && ruff format --check . && python3 -m pytest -q` is clean.

## Assumptions

- The other three actions from `docs/design/03-rules.md`'s table (Attack, Ready-or-use, Act on
  the fiction) are out of scope: Attack already exists as `resolution.py`'s `combat-attack`;
  Ready-or-use and Act-on-fiction are prose with no engine state of their own (matching #244's
  own issue scope).
- `docs/design/03-rules.md`'s other ranged-difficulty rows (clear sight/unaware, ordinary,
  cover/poor light, hard cover) are GM/fiction judgment calls about the shot itself, not
  engagement facts this feature computes — out of scope, consistent with `declaration_bonus`
  already being a caller-supplied, already-decided value everywhere else in `engine/wyrd/`
  (#235's own Assumption).
- Fixes a gap discovered while implementing FR-006: `resolution.py`'s `combat-attack` mechanic
  silently dropped a caller-supplied `declaration_bonus` (only a reroll-resource/Omen modifier
  ever reached the attacker's boosted skill) — corrected as a small, in-scope fix, since this
  feature's own ranged-difficulty modifiers depend on that channel actually working.
