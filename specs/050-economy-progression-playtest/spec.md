# Feature Specification: Economy and progression playtest

**Feature Branch**: `050-economy-progression-playtest`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Economy and progression playtest (closes #150, part of the playtest epic #134). Extends the established discipline to advancement (trigger-based awards, spending), career completion, a career change, Standing (the martial-weapon rule, Upkeep), and coin."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Advancement, career completion and a career change play cleanly end to end (Priority: P1)

Someone who has read the individually-computed checks for the career cap and Stamina ceiling
wants to see a character actually earn advances, complete a career, and change to a new one, with
every step traced to the ruleset's own tables.

**Why this priority**: This is #134's own purpose — proving mechanics in combination and through
a full cycle, not only individually.

**Independent Test**: Read the new section in `docs/design/30-playtest-transcript.md`; confirm a
session's trigger-based advance awards, the 70% career cap, a completion's +1 Stamina and Mark
grant, and a free career change are all present and traced to `03-rules.md` §6.

**Acceptance Scenarios**:

1. **Given** a session with several plausible triggers, **When** advances are awarded, **Then**
   the total stays within the stated 1–3 per session, with no more than one of each trigger kind
   counted.
2. **Given** a career reaches every granted skill at its 70% cap, **When** completion resolves,
   **Then** the character gains +1 maximum Stamina and a permanent Mark.
3. **Given** a completed career and a free choice of a new entry career, **When** the character
   changes career, **Then** the new career's skill list, not the old one's, governs future
   advances.

### User Story 2 - Standing and coin play as one material position, not two resources (Priority: P1)

Someone who has read `03-rules.md`'s "Standing and coin are two sides of one material position"
line wants to see both branches of Upkeep, and the martial-weapon Standing cost, actually played.

**Why this priority**: Both mechanics are stated in prose but had not been played through
together with a real character's actual Standing and coin totals.

**Independent Test**: Read the new section; confirm the martial-weapon Standing cost, and both
Upkeep branches (pay in Standing, pay in coin), are each played through explicitly.

**Acceptance Scenarios**:

1. **Given** a character visibly carrying a martial weapon in a civilised place, **When** the
   sighting occurs, **Then** Standing drops by 1, with no roll.
2. **Given** an Upkeep due away from home, **When** each payment branch is played, **Then**
   Standing drops by 1 in one branch, and coin drops by an amount equal to current Standing in
   the other.

### Edge Cases

- Does a completed career's skills survive a later career change? Not stated explicitly anywhere
  in `docs/design/`. This playtest reads the absence of any stated reset, plus
  `10-the-character.md`'s "a career, and a career history" phrasing, as sufficient grounds to
  keep them — recorded as an inference this playtest made, not a gap requiring a follow-up issue,
  since a future reading has this playtest's own reasoning to argue against directly if it
  disagrees.
- Is the maximum-Stamina ceiling at 10 re-derived here? No — `check_advancement.py` already
  computes it exactly; re-deriving it by hand would mean grinding four full career completions
  for no new information.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playtest MUST exercise trigger-based advance awards (1–3 per session, at most
  one of each kind), the deterministic spend table, the 70% career cap, a completion's +1
  Stamina/Mark grant, and a free career change.
- **FR-002**: The playtest MUST exercise the martial-weapon Standing cost and both Upkeep payment
  branches (Standing, coin).
- **FR-003**: Where a mechanic's full extent would require excessive repetition to play by hand
  (the Stamina-10 ceiling), the playtest MUST state plainly that it relies on the existing
  computed check instead of re-deriving it, rather than silently skipping the claim.
- **FR-004**: Any inference the playtest makes to fill a genuine documentation silence (whether
  a completed career's skills survive a career change) MUST be stated explicitly as an inference,
  with its reasoning, not asserted as settled fact.

### Key Entities

*(none — this feature is a worked playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section covering advancement,
  career completion, a career change, Standing and coin, following the existing document's
  established structure and tone.
- **SC-002**: Every mechanical claim in the new section traces to `03-rules.md` §2 or §6, or
  `16-session.md`'s Upkeep row.
- **SC-003**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass,
  with no new finding class introduced.
- **SC-004**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- This feature carries no ADR — nothing found required a design decision; the one genuine
  documentation silence found (career-change skill retention) is recorded as a stated inference,
  not escalated to a follow-up issue, since the playtest's own reasoning is sufficient grounds
  and reversible if a future reading disagrees.
- Documentation-only: no code changes; this feature has no dice-roll generation script since
  nothing in its scope involves a roll (advancement, career completion, Standing and coin are all
  deterministic).
