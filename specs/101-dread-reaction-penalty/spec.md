# Feature Specification: Dread as a reaction/social test penalty

**Feature Branch**: `101-dread-reaction-penalty`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Apply Dread as a social/reaction test penalty against a transformed character (issue #272)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dread penalises a test toward an unfamiliar witness (Priority: P1)

A transformed character with accumulated Dread is seen by a stranger, crowd, or official who has
not made their peace with the transformation. Any reaction or social test the party makes toward
that witness resolves at a harder effective chance, penalised by the transformed character's
total Dread, on top of whatever the difficulty ladder already applies.

**Why this priority**: This is the entire feature — Dread accrues today but nothing reads it back.
Without this, the "standing price of being seen" the design document promises never actually
bites at the table.

**Independent Test**: Resolve a reaction/social test where the caller states the target carries
nonzero Dread and the witness has not made peace with it; confirm the resolved chance is reduced
by exactly that Dread total, stacked with any other modifier already in play, and that it never
drops below 0%.

**Acceptance Scenarios**:

1. **Given** a transformed character with Dread 3, and a witness the GM has ruled has not made
   peace with the transformation, **When** a party member makes a reaction or social test toward
   that witness, **Then** the test resolves at skill plus the ordinary difficulty modifier minus
   3, clipped to no lower than 0%.
2. **Given** the same character and witness, **When** the test also carries another points
   modifier (e.g. a favourable difficulty), **Then** Dread stacks with that modifier rather than
   replacing it, before the 0% floor is applied.

---

### User Story 2 - No penalty when peace is established or Dread is zero (Priority: P2)

The same reaction/social test resolves exactly as it does today when the GM rules the witness has
already made their peace with the transformation, or when the transformed character carries no
Dread at all.

**Why this priority**: A feature that always penalises, or that a caller cannot switch off, would
misrepresent the rule — the design explicitly gates the penalty on the GM's fictional judgment,
made once per test, not computed by the engine.

**Independent Test**: Resolve a reaction/social test toward the same transformed character with
the caller instead flagging established peace, or with Dread at 0, and confirm the resolved chance
is unaffected by Dread either way.

**Acceptance Scenarios**:

1. **Given** a transformed character with Dread 3, **When** the caller flags that the witness has
   already made peace with the transformation, **Then** the test resolves with no Dread penalty
   applied.
2. **Given** a transformed character with Dread 0, **When** the caller flags no established peace,
   **Then** the test resolves with no Dread penalty applied (there is nothing to apply).

### Edge Cases

- A test with no target entity at all (nothing being reacted to or socially engaged) carries no
  Dread penalty — the caller simply does not flag a target, and today's ordinary-test behaviour is
  unchanged.
- Dread large enough that, combined with the difficulty ladder and any other modifier, the
  effective chance would go negative: the result clips at 0%, the same floor every other
  points-modifier stack already respects.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST let a caller resolving a reaction or social test identify a target
  entity (the transformed character being reacted to) whose Dread total is read for that test.
- **FR-002**: The engine MUST let the caller state, per test, whether the witness has already made
  their peace with the target's transformation — this is a caller-supplied fact, never computed or
  inferred by the engine.
- **FR-003**: When a target is identified, its Dread is nonzero, and the caller states peace has
  not been made, the engine MUST subtract the target's total Dread from the effective chance,
  stacked with the difficulty ladder and any other points modifier already applied to that test.
- **FR-004**: When peace has been made, or the target's Dread is 0, or no target is identified, the
  engine MUST resolve the test exactly as it does today — no Dread term enters the calculation.
- **FR-005**: The engine MUST clip the final effective chance to no lower than 0%, the same floor
  already applied to every other points-modifier stack.
- **FR-006**: The Dread penalty applies only to a reaction or social test — it MUST NOT be read or
  applied by any other mechanic (combat, Exposure, Terror, and so on).

### Key Entities

- **Target's Dread**: the running total already carried on a character/companion's state
  (`dread`), read but not mutated by this feature.
- **Peace flag**: a per-test, caller-supplied boolean recording the GM's fictional call on whether
  the witness has made their peace with the target's transformation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reaction/social test toward a transformed character with nonzero Dread, witnessed
  by someone without established peace, resolves at exactly skill plus modifiers minus Dread,
  clipped at 0%, in 100% of cases exercised by the test suite.
- **SC-002**: A test where peace is established, or Dread is 0, resolves identically to the
  feature's absence — no regression in existing reaction/social test behaviour.
- **SC-003**: The full engine test suite (`PYTHONPATH=engine`) and `ruff check .` /
  `ruff format --check .` stay green with this feature in place.

## Assumptions

- Reaction and social tests resolve through the engine's existing ordinary-test mechanic
  (`docs/design/03-rules.md` §1); this feature extends that mechanic's request/resolution shape
  rather than introducing a new mechanic.
- "Made their peace" is never computed, stored, or tracked by the engine — it is supplied fresh by
  the caller on each test, the same pattern already used for Fault Line bias and Exposure's
  resist-skill choice (both already-decided caller inputs, not engine-computed judgments).
- No new persistent state is introduced. Dread itself already accrues correctly
  (`engine/wyrd/resolution.py`, `_stage_transformation_chain`) and is read, not written, by this
  feature.
