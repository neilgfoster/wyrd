# Feature Specification: Player-facing opposed tests

**Feature Branch**: `029-player-facing-opposed-tests`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Extend player-facing rolls to all opposed tests" (issue #77)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An opposed test against an NPC resolves as one roll (Priority: P1)

A player character or companion attempts something an NPC/opponent is actively resisting outside
combat — picking a lock while a guard listens, talking past a suspicious gatekeeper, wrestling free
of a captor's grip. Today this is a double gate: the acting side must succeed, then (if they do)
the GM rolls for the resisting NPC and compares degrees. Most of those NPC rolls are wasted the same
way combat's were.

**Why this priority**: This is the entire point of the feature — it is what #69 established for
combat and what this issue generalises. Without it, nothing changes.

**Independent Test**: Take any opposed test in play where one side is an NPC/opponent. Resolve it
with a single player roll against `effective%` and confirm the NPC's dice are never touched.

**Acceptance Scenarios**:

1. **Given** a player character attempting an action an NPC/opponent is resisting, **When** the
   test is resolved, **Then** only the player rolls, once, against
   `effective% = clip(50 + (skill − opponent_skill_or_baseline), 5, 95)`, and degrees are read
   `tens(effective%) − tens(roll)` exactly as combat already does.
2. **Given** a companion (not the player character) attempting an action an NPC/opponent is
   resisting, **When** the test is resolved, **Then** the same single-roll shape applies — the
   companion's player rolls, the opponent's dice are never consulted.
3. **Given** an opposed test against an NPC/opponent, **When** the roll fails, **Then** the action
   simply fails — there is no degrees comparison and no NPC roll to have skipped.

---

### User Story 2 - A contest between two player-controlled entities still has a resolution (Priority: P2)

A player character and a companion are in genuine tension with each other — arm-wrestling, a
disagreement resolved by a dice-off, a race between the two of them — where neither side is an
NPC/opponent, so there is no opponent skill to set `effective%` against.

**Why this priority**: The generalised shape only has meaning when one side is an NPC/opponent.
This case is rare in a one-player, one-party-of-companions game, but it is not empty, and #77
requires it be decided explicitly rather than left implicit.

**Independent Test**: Construct a contest between the player character and a companion (or two
companions) with no NPC/opponent side, and confirm the ruleset states a specific resolution for it
without contradicting the retired two-sided shape.

**Acceptance Scenarios**:

1. **Given** two player-controlled entities in genuine tension with no NPC/opponent side,
   **When** the GM needs a resolution, **Then** the design states one explicitly (an ordinary test
   for whichever side is acting, or the GM naming an actor and resisting party) rather than
   silently falling back to the retired two-sided roll-both shape.

---

### Edge Cases

- An opposed test where the resisting side is an NPC but the *acting* side has no clear
  actor (a race for the same outcome, no one "acting against" anyone) — already routed to the GM
  either naming an actor or calling two ordinary tests; this is unchanged by the conversion and
  must still be stated.
- Assistance, declaration bonuses and the untrained-10% rule must each still apply to the single
  roll exactly as they already do for combat's attack/defence rolls — no divergent composition
  rule may be introduced for the generalised case.
- Every design document that currently cites "opposed test" as a mechanism (not just its
  definition) must be checked; one left describing the retired two-sided shape as live would
  contradict this feature's own acceptance criteria.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Wherever a player character or companion is opposed by an NPC/opponent outside
  combat, the ruleset MUST resolve it as a single player roll against
  `effective% = clip(50 + (skill − opponent_skill_or_baseline), 5, 95)`, with the opponent's dice
  never consulted — the same shape §2 already uses for combat's attack and defence rolls.
- **FR-002**: Degrees for this generalised roll MUST be read `tens(effective%) − tens(roll)`,
  matching combat's computation exactly, with no separate formula introduced.
- **FR-003**: A failed roll under the generalised shape MUST simply fail the action — no degrees
  comparison, no resisting-side roll.
- **FR-004**: The ruleset MUST state an explicit resolution for a contest between two
  player-controlled entities where neither side is an NPC/opponent, rather than leaving it as an
  unexamined edge case or silently retaining the retired two-sided shape for it.
- **FR-005**: Assistance, declaration and the untrained-10% rule MUST compose with the generalised
  roll exactly as they already compose with combat's attack/defence rolls — no new or divergent
  composition rule.
- **FR-006**: `design/03-rules.md` §1's "Opposed tests" subsection MUST be rewritten to the
  player-facing shape, generalised from §2's combat wording, rather than duplicating combat's
  prose or leaving both a live two-sided description and a live player-facing one.
- **FR-007**: Every place in `design/` that cites "opposed test" as a live mechanism (not merely
  its historical definition in an ADR) MUST either be updated to the generalised shape or
  confirmed to already route through it — none may be left depending on the retired two-sided
  shape.
- **FR-008**: [ADR 0016](../../design/adr/0016-opposed-tests-need-a-successful-actor.md)'s
  remaining scope (already narrowed once by ADR 0027) MUST be resolved explicitly — either a new
  ADR supersedes it entirely, or a new ADR states precisely what scope (if any) still needs
  two-sided resolution. ADR 0016 itself is never edited.
- **FR-009**: The calibration `effective% = clip(50 + (skill − opponent_skill_or_baseline), 5,
  95)` MUST be reused as-is; this feature does not recompute or re-justify it.

### Key Entities

- **Opposed test**: a resolution shape where a player character or companion is opposed by
  another side. After this feature, splits into two cases: opposed by an NPC/opponent (resolved
  as a single player-facing roll) and opposed by another player-controlled entity (resolved by
  whatever FR-004 decides).
- **`effective%`**: the target percentage a player-facing roll is made against, computed from the
  acting side's skill and the opposing side's skill-or-baseline. Already defined and merged by
  #69; reused, not recomputed, here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every opposed test in `design/` where one side is an NPC/opponent is described as a
  single player roll against `effective%`, with zero remaining references to an opponent-side roll
  in that context.
- **SC-002**: The two-player-controlled-entities case has exactly one stated resolution in
  `design/`, not zero and not two conflicting ones.
- **SC-003**: `python3 tools/check_docs.py` and `python3 tools/backlog.py check` both exit zero
  after the change.
- **SC-004**: A grep for "opposed test" across `design/` turns up no description of the two-sided
  roll-both shape outside ADR 0016's own historical text and the new superseding/narrowing ADR's
  own quotation of it.

## Assumptions

- "NPC/opponent" has the same meaning here as it does in #69/ADR 0027 and `03d-the-adversary.md`:
  a side whose capability is a static number, never a die roll.
- The two-player-controlled-entities case is expected to be resolved with the same tool ADR 0016
  already named for the "neither is acting" carve-out — an ordinary test or the GM naming an
  actor — not a new mechanic; this feature decides which, it does not invent a third resolution
  shape.
- No new engine vocabulary is introduced; this feature edits `design/03-rules.md` §1 in place and
  adds one ADR (superseding or narrowing ADR 0016), per the project's existing ADR/design-document
  conventions.
- Out of scope, per the source issue: anything specific to combat itself (already settled by
  #69/ADR 0027/ADR 0028), and reopening group tests, extended tasks or assistance's own mechanics
  (#53, landed) beyond confirming compatibility.
