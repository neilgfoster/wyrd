# Feature Specification: The recurring wound's combat-start effect

**Feature Branch**: `093-recurring-wound-combat-start`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "The recurring wound's combat-start effect (issue #254): at the
moment a fight begins, apply a -10 penalty to the skill each of a combatant's recurring wounds
bears on, for that fight. Multiple recurring wounds all fire and stack. The penalty never fires
mid-fight, has no effect between fights, and Mend cannot touch it. Reuse the existing Challenging
difficulty constant rather than a new literal."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A recurring wound fires at the start of a fight (Priority: P1)

A character carrying a recurring wound (an ongoing condition recorded from an earlier Aftermath
result) enters a new fight. The engine applies the wound's penalty to the skill it bears on for
that fight, without any test or roll, so the wound's cost shows up the moment combat begins.

**Why this priority**: this is the entire feature -- without it, a recurring wound is recorded
but never actually affects play.

**Independent Test**: start a combat scene for a character with one recurring wound on file, and
confirm the penalty is applied to the named skill for that combat scene.

**Acceptance Scenarios**:

1. **Given** a combatant with one active recurring wound bearing on a named skill, **When** a
   combat scene starts for them, **Then** that skill carries the Challenging-difficulty penalty
   for the duration of that fight.
2. **Given** a combatant with no recurring wounds, **When** a combat scene starts for them,
   **Then** no wound-derived penalty is applied.

---

### User Story 2 - Multiple recurring wounds stack (Priority: P2)

A character who has survived more than one brush with death carries more than one recurring
wound. Each one fires independently at the start of a fight; if two bear on the same skill, that
skill takes both penalties.

**Why this priority**: the design explicitly calls out stacking ("the family is repeatable, so a
character may carry more than one; each fires") as a case the engine must not silently collapse.

**Independent Test**: start a combat scene for a character carrying two recurring wounds (one
bearing on each of two different skills, and separately a case where both bear on the same
skill), and confirm each wound's penalty is present and, where they share a skill, both apply.

**Acceptance Scenarios**:

1. **Given** a combatant with two active recurring wounds bearing on two different skills,
   **When** a combat scene starts, **Then** both skills each carry their own penalty.
2. **Given** a combatant with two active recurring wounds bearing on the same skill, **When** a
   combat scene starts, **Then** that skill carries both penalties stacked.

---

### User Story 3 - The penalty is scoped to the fight it fires in (Priority: P3)

The penalty is not a permanent skill change and not something that needs to be reapplied
mid-fight or cleared by hand. It applies once, at the moment the fight starts, for that fight
only, and leaves no trace once the fight is over or before the next one begins.

**Why this priority**: this is what keeps the effect "fires once per fight" rather than
becoming a persistent stat change or requiring per-round bookkeeping; it's a correctness
boundary rather than new player-facing behavior.

**Independent Test**: start a combat scene, confirm the penalty is present; end that combat
scene (or otherwise check skill state outside of combat) and confirm the penalty is gone; start
a second, later combat scene and confirm the penalty is applied fresh rather than assumed to
still be there.

**Acceptance Scenarios**:

1. **Given** a fight already in progress with a recurring wound's penalty applied at its start,
   **When** a later round of that same fight is checked, **Then** the penalty is still exactly
   what it was at combat start -- not reapplied, not doubled.
2. **Given** a combatant between fights, **When** their skill is checked outside of any combat
   scene, **Then** no recurring-wound penalty is present.

### Edge Cases

- A recurring wound whose `bears_on` names a skill the character does not otherwise have on
  file: the penalty still applies to that named skill (a wound doesn't require the character to
  already be trained in what it now makes worse).
- A character with a recurring wound that is later closed: out of scope for this feature (the
  design states a recurring wound never closes, and closing/Mend is explicitly out of scope --
  epic #219).
- Starting a second combat scene for the same character in the same session: each combat start
  recomputes the penalty from the character's current wounds; it is never carried over from a
  prior scene's cached value.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST, at the moment a combat scene starts, apply a skill penalty for
  every active recurring wound the starting combatant carries.
- **FR-002**: The penalty applied per recurring wound MUST be the existing Challenging-difficulty
  modifier value, not a separately defined number.
- **FR-003**: The penalty MUST apply to the skill named by the recurring wound's `bears_on`
  field.
- **FR-004**: When a combatant carries more than one active recurring wound, every one of them
  MUST apply its penalty; where two or more bear on the same skill, their penalties MUST stack
  (sum) rather than the strongest alone applying.
- **FR-005**: The penalty MUST NOT require, or be gated behind, any test or roll -- it applies
  unconditionally once a combat scene starts for the combatant.
- **FR-006**: The penalty MUST NOT be reapplied or recomputed mid-fight (e.g. on each round
  advance) -- it is fixed once, at the fight's start, for that fight.
- **FR-007**: The penalty MUST have no effect on the combatant outside of the combat scene it
  was applied for (no effect between fights, and no effect before the fight it fires in starts).
- **FR-008**: A recurring wound that is not active (its record's `closed` is set, or -- per
  design -- it has no other route to being closed) MUST NOT contribute a penalty. (Recurring
  wounds never close per the design, but the engine's general "closed wounds don't apply" rule,
  already implemented elsewhere, MUST still govern here rather than a parallel exception.)
- **FR-009**: A combatant with no active recurring wounds MUST see no wound-derived penalty
  applied at combat start.

### Key Entities

- **Recurring wound**: a wound record on a character with `recurring: true` and an effect naming
  a skill penalty; already defined and validated by the existing wound machinery. This feature
  reads that record but does not create, close, or otherwise modify it.
- **Combat scene**: the per-chronicle state a fight is tracked under, already created when a
  fight starts. This feature adds to what is computed/recorded at that moment; it does not
  change how the scene itself is structured or sequenced.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For any combatant carrying one or more active recurring wounds, the skill each
  wound bears on is measurably worse (by the Challenging modifier, once per active recurring
  wound bearing on it) for every fight that starts after the wound exists, with no exceptions
  and no manual step required to apply it.
- **SC-002**: A combatant's recurring-wound penalty is never visible to a check of their skills
  outside of an active combat scene.
- **SC-003**: A fight that runs multiple rounds shows the same penalty value throughout -- it is
  computed exactly once per fight.

## Assumptions

- "The skill each of a combatant's recurring wounds bears on" (issue #254) is read from the same
  `active_wound_effects`-style machinery `engine/wyrd/character.py` already exposes for wound
  effects generally, rather than a new parallel read of the wounds list -- per the issue's own
  "Current state" note. This feature's job is the combat-start hook that consumes that data, not
  a new way of reading it.
- The existing Challenging-difficulty value already defined for other Challenging-difficulty
  cases (docs/design/03-rules.md's difficulty table) is the single source of truth for the -10;
  this feature reuses it by reference rather than repeating the literal `-10` in a new place.
- This feature concerns only player-character combatants' recurring wounds in the sense the
  issue describes (wound records on a character entity); it does not introduce any new entity
  type or extend the effect to non-player-character sides.
- Where the penalty is applied is scoped to "the skill test(s) run within that combat scene" --
  it is exposed as a modifier available to combat's skill-test machinery for the scene's
  duration, not written back onto the character's stored skill value.
