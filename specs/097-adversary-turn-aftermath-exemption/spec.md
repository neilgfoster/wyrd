# Feature Specification: Adversary turn parity and the Aftermath exemption

**Feature Branch**: `097-adversary-turn-aftermath-exemption`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Adversary turn parity and the Aftermath exemption (issue #262): a
dropped bare adversary never triggers an Aftermath roll, while a dropped character-entity
antagonist still does via the existing character path; an adversary's turn and critical
resolution use the existing machinery with no adversary-specific branch."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A dropped bare adversary rolls no Aftermath (Priority: P1)

An opponent carrying only an adversary block drops. Aftermath prices a lasting consequence for
someone the chronicle carries forward, and an adversary is not that: nothing on the Aftermath
table is rolled for it, and no wound record, death row or status change is produced. What became
of it is the fiction's to say.

**Why this priority**: this is the rule the feature exists to enforce. Without it, the Aftermath
machinery -- currently wired to no caller at all -- would be wired up with no exclusion, and
every dropped opponent in a fight would generate a wound record the chronicle then has to carry.

**Independent Test**: staging Aftermath for an entity that is not a `character` entity is
refused, and the drop produces no aftermath step.

**Acceptance Scenarios**:

1. **Given** an entity state carrying an adversary block (no `type: character`), **When** it
   drops below 0 Stamina, **Then** no `aftermath` step is staged for it.
2. **Given** that same drop, **When** the proposal is read, **Then** it carries no wound
   record, no death row and no status mutation for that opponent.
3. **Given** an entity state with `type` absent entirely, **When** Aftermath is asked for,
   **Then** it is treated as a non-character and excluded, rather than defaulting to rolling.

---

### User Story 2 - A dropped named antagonist rolls Aftermath unchanged (Priority: P1)

A named antagonist is a `character` entity, and therefore rolls Aftermath by exactly the path a
player character or companion already uses. The exemption tests entity type, not importance,
faction or whether the entity is player-facing.

**Why this priority**: the exemption is only correct if it is this narrow. A rule that excluded
"anything the player is fighting" would silently drop the antagonist case the design names
explicitly.

**Independent Test**: an entity state with `type: character` drops and produces an `aftermath`
step identical in shape to the one a player character's drop produces.

**Acceptance Scenarios**:

1. **Given** an entity state with `type: character` and `role: antagonist`, **When** it drops,
   **Then** an `aftermath` step is staged, rolled and banded exactly as for a player character.
2. **Given** an entity state with `type: character` and `role: companion`, **When** it drops,
   **Then** Aftermath is staged, unchanged from the existing companion path.
3. **Given** an entity state with `type: character` and `role: player`, **When** it drops,
   **Then** Aftermath is staged, unchanged from the existing player path.

---

### User Story 3 - An adversary's turn and critical need no adversary-specific branch (Priority: P2)

An adversary acts with the same one action from the same closed list everyone else draws from,
and a critical is rolled for it on the same `1d6 + points below zero` damage-type table. Neither
path gains an adversary-specific case.

**Why this priority**: this is a confirmation rather than a change -- the design's point in this
section is that no new machinery is needed. It is worth exercising so a later change that
introduces an adversary-only branch fails a test rather than passing silently.

**Independent Test**: an adversary drives an attack and takes a drop through the existing
combat/critical machinery, with no adversary-specific argument or code path involved.

**Acceptance Scenarios**:

1. **Given** an adversary as the acting side, **When** it takes its turn, **Then** the action
   available to it is drawn from the same closed action list as any other combatant's, with no
   adversary-only action added.
2. **Given** an adversary taking damage past 0 Stamina, **When** the critical resolves, **Then**
   it is `1d6 + points below zero` on the table for the damage type, identical to a character's.

---

### Edge Cases

- An entity with `type` absent, or with a `type` other than `character`, is excluded -- the
  check is "is this a character entity", never "is this known to be an adversary".
- A `character`-entity antagonist whose block also carries adversary-style fields is still a
  character entity and still rolls; entity type decides, not the presence of block fields.
- The exemption applies at the point Aftermath would be staged. Anything already staged before
  the drop (the critical, the damage and armour steps) is unaffected.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST expose a single decision point that answers whether a given
  entity is one Aftermath is rolled for, and MUST answer yes only for a `character` entity.
- **FR-002**: Staging Aftermath for an entity that is not a `character` entity MUST be refused
  rather than silently producing an empty or partial step.
- **FR-003**: An entity whose `type` is absent MUST be treated as not a character entity.
- **FR-004**: A `character` entity MUST roll Aftermath by the existing path, unchanged in
  rolled values, banding, wound record, death-row closure and companion status handling --
  regardless of its `role`.
- **FR-005**: The exemption MUST NOT depend on any adversary-block field, trait, name or
  danger value; entity type is the whole test.
- **FR-006**: The turn/action machinery MUST remain free of any adversary-specific action or
  branch, and this MUST be exercised by test rather than asserted.
- **FR-007**: The critical machinery MUST remain free of any adversary-specific branch, and an
  adversary's critical MUST resolve identically to a character's for the same inputs and seed.

### Key Entities

- **Character entity**: an entity carrying `type: character` -- the player's own character, a
  companion, or a named antagonist. The one entity kind Aftermath is rolled for.
- **Adversary**: an opponent carrying only an adversary block. Takes turns and criticals like
  anyone else; never rolls Aftermath.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every dropped opponent that is not a character entity produces zero Aftermath
  results across a run of fights -- no wound records, no death rows.
- **SC-002**: A dropped named antagonist produces exactly one Aftermath result, the same one
  the equivalent player-character drop produces from the same seed.
- **SC-003**: An adversary's critical, for identical damage and seed, produces the same result
  a character's does -- confirming no adversary-specific branch exists in that path.
- **SC-004**: Whether Aftermath applies is decided in exactly one place, so a future caller
  cannot wire up a drop that bypasses the exemption.

## Assumptions

- An adversary participating in a fight is represented in state without `type: character`; the
  named-antagonist case is exactly the case where that field is present.
- This feature does not wire the full drop-to-Aftermath chain into combat resolution: it
  establishes and enforces the exclusion at the staging point, so whichever caller later
  invokes it inherits the rule. Aftermath's own table, banding, Fate and mortality rules are
  already implemented (#252-254) and are not re-specified here.
- Adversary block loading (#259), baseline resolution (#260), trait effects (#261) and
  encounter scaling are out of scope and already covered elsewhere.
