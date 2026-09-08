# Feature Specification: Standing and coin as one material position

**Feature Branch**: `105-standing-and-coin`

**Created**: 2026-09-08

**Status**: Draft

**Input**: Issue #279 — "Implements docs/design/03-rules.md section 2, Gear and coin: coin as a
stated total spent against a gear.yaml price, Standing as what a character's position owes them,
the martial-weapon Standing cost, and Standing moving outside Upkeep as a scene consequence.
Encumbrance stays a question asked of the fiction, with no weight number. Upkeep's own session
cadence belongs to #219."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Coin is spent against a gear price (Priority: P1)

A character with a stated coin total buys a weapon or armour piece from the setting's
`gear.yaml`. The engine takes the item's price from coin and refuses the purchase outright if
coin does not cover it.

**Why this priority**: This is the one place the material economy actually moves a number, and
it is the dependency `check_gear.py`'s schema (specs/023) was validated against but never wired
to a character.

**Independent Test**: Buy a gear entry from a fresh coin total, twice — once affordable, once
not — and confirm coin falls by exactly the price on the first and the second is refused with
coin unchanged.

**Acceptance Scenarios**:

1. **Given** a character with 20 coin and a gear entry priced at 12, **When** they buy it,
   **Then** coin is 8 and the purchase succeeds.
2. **Given** a character with 5 coin and a gear entry priced at 12, **When** they buy it,
   **Then** the purchase is refused naming the shortfall, and coin stays 5.
3. **Given** a gear id not present in the loaded `gear.yaml`, **When** a purchase is attempted,
   **Then** it is refused naming the unknown id.

---

### User Story 2 - Carrying a martial weapon visibly costs Standing (Priority: P1)

A character carrying a martial weapon is seen with it in a scene where that is illegal — most
civilised places, per `03-rules.md` §2. The moment it becomes visible, Standing falls by 1,
once per sighting, never doubled with an encounter trigger for the same sighting.

**Why this priority**: This is the one Standing trigger the design already commits to a fixed
size (1) and a fixed cause, so it is checkable without inventing a number.

**Independent Test**: Trigger the martial-weapon sighting against a character's current Standing
and confirm it falls by exactly 1, and that invoking it again for the same already-open sighting
does not fall it twice.

**Acceptance Scenarios**:

1. **Given** a character with Standing 3 carrying a martial weapon, **When** it becomes visible
   in a scene where that is illegal, **Then** Standing becomes 2.
2. **Given** the same sighting already recorded as costing Standing this scene, **When** the
   trigger is invoked again for that sighting, **Then** Standing does not fall a second time.

---

### User Story 3 - Standing moves outside Upkeep as a scene consequence (Priority: P2)

The GM raises or lowers Standing directly, as a scene's own consequence, the same way Taint or
Trauma can move outside their own listed triggers. This is a general adjustment, not a fixed-size
rule like the martial-weapon cost.

**Why this priority**: Without this, every future Standing consequence the GM discovers in play
has no verb to land through, and would have to be tracked by hand outside the character sheet.

**Independent Test**: Apply a stated Standing delta as a scene consequence and confirm it lands
on the character's current Standing exactly, with no bound the engine invents.

**Acceptance Scenarios**:

1. **Given** a character with Standing 4, **When** the GM applies a scene consequence of −2
   Standing, **Then** Standing becomes 2.
2. **Given** a character with Standing 0, **When** the GM applies a scene consequence of −1
   Standing, **Then** Standing becomes −1 — Standing is an open count with no floor, matching how
   Taint and Trauma are already specified as unbounded accruals.

---

### Edge Cases

- A purchase priced at exactly the character's current coin succeeds and leaves coin at 0.
- A Standing delta of 0 is accepted and is a no-op (nothing in the design forbids a GM-narrated
  scene consequence that turns out to change nothing).
- Encumbrance is never computed by the engine: no weight field, no carrying-capacity score is
  introduced by this feature, matching `13-diegesis.md`'s existing "realistic, not logistic" rule
  and `03-rules.md` §2's explicit statement that encumbrance stays a question asked of the
  fiction.
- Upkeep's own Standing-or-coin choice and its session cadence are explicitly out of scope here
  (#219); this feature supplies the Standing and coin primitives Upkeep will spend against, not
  the Upkeep step itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Character state MUST carry a coin total (a plain, small integer) alongside the
  existing Standing count (`reputation.score`, docs/design/22-state.md).
- **FR-002**: The engine MUST provide a verb that spends coin against a named `gear.yaml` entry's
  price, refusing the spend and leaving coin unchanged when the price exceeds current coin, and
  refusing outright when the id is not present in the loaded gear catalogue.
- **FR-003**: The engine MUST provide a verb that applies the martial-weapon sighting cost: −1
  Standing, applied once per open sighting, not re-applied while that sighting is already
  recorded as costing Standing.
- **FR-004**: The engine MUST provide a general verb that applies a stated Standing delta
  (positive or negative, including zero) as a scene consequence, with no floor or ceiling the
  engine invents.
- **FR-005**: The engine MUST NOT introduce any encumbrance field, weight value, or
  carrying-capacity score.
- **FR-006**: None of these verbs may resolve Upkeep's own Standing-or-coin choice or its session
  cadence — that remains #219's scope.

### Key Entities

- **Coin**: a plain integer on the player-character entity, spent against a `gear.yaml` price or
  at Upkeep (Upkeep itself out of scope here).
- **Standing** (`reputation.score`): the existing open-ended count of social position, moved by
  the martial-weapon trigger, by a general scene-consequence verb, and — out of this feature's
  scope — by Upkeep.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A gear purchase against a character's coin total resolves in one verb call, with
  no follow-up bookkeeping step.
- **SC-002**: The martial-weapon Standing cost never applies twice for the same open sighting.
- **SC-003**: A GM-narrated Standing consequence can be applied to any character in one verb
  call, for any delta the fiction calls for.
- **SC-004**: No encumbrance number appears anywhere in character state after this feature lands.

## Assumptions

- "Once per sighting" is tracked the same shape combat already uses for a standing condition —
  the caller (GM/session log) identifies the sighting; the engine does not invent scene-detection
  of its own.
- Coin has no design-stated ceiling; like Standing, it is an open count.
