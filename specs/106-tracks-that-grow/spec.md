# Feature Specification: The tracks that actually grow

**Feature Branch**: `106-tracks-that-grow`

**Created**: 2026-09-08

**Status**: Draft

**Input**: Issue #280 — "Implements docs/design/03-rules.md section 6, What actually grows:
Reputation as a score with a label rolled on meeting someone, plus Allegiances, Holdings,
Knowledge and Bonds. None of them improves a die roll -- a character ten years in is harder to
replace, not harder to kill. Part of #216."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An allegiance is gained or lost (Priority: P1)

A character's standing within an organisation is recorded as an allegiance — a pointer to that
organisation, distinct from a holding. Over a chronicle a character joins new organisations and
occasionally breaks with one.

**Why this priority**: Allegiances are named as one of the four remaining growing tracks
(Reputation and coin already shipped in #279); without a verb to add or drop one, the GM has no
way to land the consequence of "you're in" or "you're out" on the character sheet.

**Independent Test**: Add an allegiance to a character with none, confirm it appears exactly
once; add the same allegiance again and confirm it is not duplicated; drop an allegiance and
confirm it is gone.

**Acceptance Scenarios**:

1. **Given** a character with no allegiances, **When** an allegiance to an organisation is
   gained, **Then** that organisation appears once in the character's allegiances.
2. **Given** a character already carrying an allegiance to an organisation, **When** the same
   allegiance is gained again, **Then** the list still carries it exactly once.
3. **Given** a character carrying an allegiance, **When** that allegiance is lost, **Then** it no
   longer appears in the character's allegiances.
4. **Given** a character with no allegiance to an organisation, **When** that allegiance is
   lost, **Then** the request is refused naming the allegiance not held, and the list is
   unchanged.

---

### User Story 2 - A holding is gained or lost (Priority: P1)

A character accumulates things that can be taken — a dwelling, a boat, a workshop, a debt owed to
them (`docs/design/19-campaign.md` "Holdings") — recorded distinctly from allegiances. A holding
can also be seized, burned, or otherwise removed by play.

**Why this priority**: Holdings are what turns "a threat to the settlement" into "a threat to the
mill you own" — the mechanism only works if the engine can record and remove one.

**Independent Test**: Add a holding to a character with none, confirm it appears exactly once;
add the same holding again and confirm it is not duplicated; remove a holding and confirm it is
gone.

**Acceptance Scenarios**:

1. **Given** a character with no holdings, **When** a holding is gained, **Then** it appears once
   in the character's holdings.
2. **Given** a character already carrying a holding, **When** the same holding is gained again,
   **Then** the list still carries it exactly once.
3. **Given** a character carrying a holding, **When** that holding is lost (seized, burned, or
   otherwise removed by the fiction), **Then** it no longer appears in the character's holdings.
4. **Given** a character with no such holding, **When** that holding is lost, **Then** the
   request is refused naming the holding not held, and the list is unchanged.

---

### User Story 3 - Reputation is rolled against a label when meeting someone (Priority: P2)

A character's Standing (`reputation.score`, #279) already moves as a number; this story is the
missing half named in section 6: rolling that score, on meeting someone, to see whether being
recognised helps, hinders, or does nothing — never a die-roll modifier, only what the meeting
itself opens or closes.

**Why this priority**: Standing already accrues (#279); without this verb the score has nothing
that reads it, so nothing in ten years of play would ever consult it.

**Independent Test**: Roll a character's Standing against a d100 at a range of scores and confirm
the three-band outcome (recognised favourably / not recognised / recognised unfavourably) lines
up with the sign and magnitude of the score, and that the roll never touches any skill or
difficulty value.

**Acceptance Scenarios**:

1. **Given** a character with a positive Standing score, **When** they meet someone for the first
   time, **Then** the roll can land as recognised favourably, and the engine returns that outcome
   without altering any skill percentage.
2. **Given** a character with Standing 0, **When** they meet someone, **Then** the roll can land
   as not recognised at all — a legitimate, unremarkable outcome.
3. **Given** a character with a negative Standing score, **When** they meet someone, **Then** the
   roll can land as recognised unfavourably.
4. **Given** any Standing score, **When** the roll is made, **Then** nothing it returns is fed
   back into a skill test's own success chance.

---

### Edge Cases

- Gaining an allegiance or holding that is already present is a no-op that still reports success
  (idempotent add), matching how the design frames these as an open set rather than a counted
  ledger.
- Losing an allegiance or holding not currently held is refused, naming what was not found,
  rather than silently succeeding — the same shape as #279's insufficient-coin refusal.
- Knowledge and Bonds, named alongside these in section 6's prose, are out of scope for this
  feature: Bonds is the companion track already delivered under #57/ADR 0034, and Knowledge has
  no tracked field anywhere else in the design corpus — `10-the-character.md`'s own "what has
  happened to them" table and `11-character-creation.md`'s "starts empty" list both enumerate
  wounds, Marks, Reputation, Allegiances, Holdings and Bonds, omitting Knowledge in both places.
  Treating a fact a character has learned as a mechanical track would contradict the design's own
  explicit "None of them improves a die roll" — Knowledge lives in what the character has been
  told in play, not in a number, and is out of scope for the engine.
- Neither gaining nor losing an allegiance or a holding, nor rolling Reputation, ever changes a
  skill percentage, a difficulty number, or any other input to the resolution mechanic
  (`03-rules.md` §1) — the section's own governing sentence, made checkable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a verb that adds a named allegiance to a character's
  `allegiances` list, idempotently — adding one already present leaves the list unchanged in
  content and succeeds.
- **FR-002**: The engine MUST provide a verb that removes a named allegiance from a character's
  `allegiances` list, refusing and leaving the list unchanged when that allegiance is not
  present.
- **FR-003**: The engine MUST provide a verb that adds a named holding to a character's
  `holdings` list, idempotently — adding one already present leaves the list unchanged in content
  and succeeds.
- **FR-004**: The engine MUST provide a verb that removes a named holding from a character's
  `holdings` list, refusing and leaving the list unchanged when that holding is not present.
- **FR-005**: The engine MUST provide a verb that rolls a character's Standing (`reputation.score`)
  against a d100 and returns one of three outcomes — recognised favourably, not recognised,
  recognised unfavourably — banded by the score's sign and magnitude, matching the existing
  five-band oracle shape already established for other d100 rolls in this engine
  (`docs/design/20-oracle-answers.md`).
- **FR-006**: None of the verbs in FR-001 through FR-005 may read or write any skill percentage,
  difficulty value, or other input to the resolution mechanic (`03-rules.md` §1).
- **FR-007**: The engine MUST NOT introduce a mechanical field or verb for Knowledge — it stays
  outside tracked character state, consistent with its absence from every other design document's
  enumeration of what a character carries.

### Key Entities

- **Allegiance**: a pointer (by id) to an organisation entity (`docs/design/25-entities.md`),
  held on the player-character's existing `allegiances` list; distinct from a holding, which is a
  thing rather than a standing within a group.
- **Holding**: a pointer (by id) to something a character has accumulated and can lose — a
  dwelling, a boat, a workshop, a debt owed to them (`docs/design/19-campaign.md` "Holdings") —
  held on the player-character's existing `holdings` list.
- **Standing roll**: a d100 roll against the existing `reputation.score`, returning a banded
  social-recognition outcome; it does not touch, and is not touched by, the resolution mechanic.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An allegiance can be gained or lost in one verb call, with the list never
  containing a duplicate.
- **SC-002**: A holding can be gained or lost in one verb call, with the list never containing a
  duplicate.
- **SC-003**: A Standing roll always returns one of exactly three named outcomes, for any integer
  score, positive, zero, or negative.
- **SC-004**: No verb this feature introduces ever changes a skill percentage or difficulty
  value, for any input tried.

## Assumptions

- Allegiances and holdings are recorded as plain string/id lists on the player-character entity
  (`allegiances`, `holdings` — both already present and empty by default in
  `docs/design/22-state.md`), the same shape `drives` and `career_history` already use elsewhere
  on the same entity, rather than richer objects — nothing in the design corpus states a holding
  or allegiance entry needs fields beyond identifying which organisation or possession it is.
- What id an allegiance or holding names (an existing `organisation`/other entity's id versus a
  free-text label) is left to the caller, matching how the engine elsewhere holds ids without
  validating them against a setting's vault (`career`, `loyalty`).
- The Standing roll's exact band boundaries follow the same reasoning `check_oracle_answers.py`
  already applies to other d100 tables in this engine — symmetric around the neutral "not
  recognised" middle band, widening as Standing's magnitude grows — rather than a boundary this
  feature invents from nothing.
- Reputation's `label` field (`docs/design/22-state.md`) is set by the GM narrating the roll's
  outcome, not computed by the engine — the roll returns a band, not prose.
