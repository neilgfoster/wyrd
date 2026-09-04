# Feature Specification: Award advances against the four session triggers

**Feature Branch**: `102-advance-award-triggers`

**Created**: 2026-09-04

**Status**: Draft

**Input**: Issue #276 — "Implements docs/design/03-rules.md section 6, Advances are the currency:
1-3 advances per session awarded against the Learned, Drove, Practised and Endured triggers, at
most one of each per session, verified by the engine rather than totalled as XP."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An advance is awarded against a named trigger (Priority: P1)

A beat closes at a Rally. The GM judges that the player discovered something true about the world
they did not know, and awards an advance against **Learned**. The engine records the award, names
which trigger it was for, and the character's unspent advances go up by one.

**Why this priority**: Without this there is no advancement economy at all — every later rule in
this stage (spending, career completion) consumes the currency this story mints.

**Independent Test**: Award one advance against each of the four triggers in turn on a fresh
session record and confirm the unspent total, and the session's own record of what has been
awarded, both move as stated.

**Acceptance Scenarios**:

1. **Given** a session with no advances awarded yet, **When** an advance is awarded against
   Learned, **Then** the award is accepted, unspent advances become 1, and the session records
   Learned as used.
2. **Given** a session that has already awarded Learned, **When** an advance is awarded against
   Drove, **Then** the award is accepted and unspent advances become 2.
3. **Given** an award naming something that is not one of the four triggers, **When** it is
   submitted, **Then** it is refused, naming the trigger vocabulary — the engine never awards an
   advance against a reason it does not know.

---

### User Story 2 - A trigger fires at most once per session (Priority: P1)

The same trigger cannot pay twice in one session, however many times the fiction supplies it. A
character who learned three true things in one session has earned one Learned advance.

**Why this priority**: This is what makes the award verifiable rather than a running XP total —
the whole point of awarding against triggers instead of counting points.

**Independent Test**: Award Learned, then attempt Learned again in the same session, and confirm
refusal; then start a new session and confirm Learned is available again.

**Acceptance Scenarios**:

1. **Given** a session that has already awarded Endured, **When** Endured is awarded again in the
   same session, **Then** it is refused and unspent advances do not change.
2. **Given** a session that awarded all its advances, **When** a new session begins, **Then**
   every trigger is available again and unspent advances carry over unchanged.

---

### User Story 3 - Three advances is the session ceiling (Priority: P2)

There are four triggers and a ceiling of three. A session in which all four triggers genuinely
fired still awards three advances; the fourth is refused as the session ceiling, not as a repeat.

**Why this priority**: The ceiling and the one-of-each rule are separate constraints that only
diverge in this one case, and the divergence is invisible unless it is tested.

**Independent Test**: Award three distinct triggers, then attempt the fourth distinct trigger, and
confirm the refusal cites the ceiling rather than a repeat.

**Acceptance Scenarios**:

1. **Given** a session that has awarded Learned, Drove and Practised, **When** Endured is awarded,
   **Then** it is refused because the session ceiling of 3 is reached, and the refusal is
   distinguishable from a repeated-trigger refusal.

---

### Edge Cases

- **A fourth distinct trigger in one session** — refused on the ceiling, not on repetition; the two
  refusals must be told apart, because one says "you already had this" and the other says "that is
  all this session pays."
- **A session boundary crossed mid-award** — awards belong to the session record they were made
  against; opening a new session clears which triggers are used and never clears unspent advances.
- **A character who never spends** — unspent advances accumulate without bound. The economy caps
  the *rate*, not the balance.
- **Awarding zero advances in a session** — legal and unremarkable: the lower bound of "1-3" is
  what a typical session earns, not a floor the engine enforces by minting an advance nobody
  triggered.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST recognise exactly four award triggers — Learned, Drove, Practised,
  Endured — and refuse any award naming anything else.
- **FR-002**: Each trigger MUST be awardable at most once per session.
- **FR-003**: A session MUST award at most 3 advances, even though four triggers exist.
- **FR-004**: A refusal MUST state which rule refused it, and a ceiling refusal MUST be
  distinguishable from a repeated-trigger refusal.
- **FR-005**: An accepted award MUST increase the character's unspent advances by exactly 1.
- **FR-006**: Beginning a new session MUST clear the record of which triggers have been awarded,
  and MUST NOT change unspent advances.
- **FR-007**: The engine MUST NOT hold or derive an experience-point total; the only stored
  quantities are unspent advances and the current session's used triggers.
- **FR-008**: The engine MUST NOT judge whether a trigger's fictional condition was met — that is
  the GM's call. It verifies only that a claimed award is legal.

### Key Entities

- **Award trigger**: one of the four named conditions, each awardable once per session.
- **Session award record**: which triggers this session has already paid for, and how many
  advances it has awarded.
- **Unspent advances**: the character's balance of currency awaiting a spend, already present in
  the character shape as `advances_unspent` (docs/design/22-state.md).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the four triggers can be awarded, and each is refused on its second
  attempt within a session.
- **SC-002**: No session can be driven above 3 awarded advances by any sequence of legal awards.
- **SC-003**: The three refusal reasons — unknown trigger, repeated trigger, session ceiling — are
  each reported distinctly, so a caller can tell a mistake from a limit.
- **SC-004**: Unspent advances after N sessions equals the sum of the advances those sessions
  awarded, with no other path into or out of the balance in this feature.

## Assumptions

- **Spending is out of scope.** This feature mints advances; #277 spends them. `advances_unspent`
  only goes up here.
- **The session record lives with the chronicle, not the character.** Which triggers are used is a
  property of the session in progress, and a new session starts a fresh one.
- **"1-3 per session" is a ceiling, not a quota.** The engine enforces the 3; it never awards an
  advance nobody claimed, so a session may legally award none.
- **No calendar or Rally cadence is implemented here.** Where in the session loop an award is
  offered belongs to #219; this feature supplies the rule that a Rally would call.
