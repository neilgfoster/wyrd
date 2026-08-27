# Feature Specification: Healing items have no mechanical effect on Stamina

**Feature Branch**: `037-healing-items-stamina`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Decide whether healing items/consumables have any mechanical effect on Stamina (closes #120)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A setting author introduces a healing draught (Priority: P1)

A setting author wants to include an in-fiction consumable — a potion, a draught, battlefield
medicine — as part of their world's flavour, and needs to know whether it does anything to a
character's Stamina track when it is used.

**Why this priority**: This is the exact gap the design left silent. Without an explicit answer,
a setting author either invents a shortcut that quietly undermines ADR 0020's Rally/downtime
recovery rule, or avoids the item entirely for fear of breaking something unstated.

**Independent Test**: Read the updated design document and confirm it states, without needing to
infer from silence, that a consumable item has no mechanical effect on Stamina recovery.

**Acceptance Scenarios**:

1. **Given** a setting author drafting their world's gear list, **When** they consult the design
   document covering Stamina, **Then** they find an explicit statement that a consumable healing
   item is flavour only and does not advance, add to, or otherwise affect the Stamina track.
2. **Given** a GM running a session where a player's character uses an in-fiction healing item,
   **When** the GM looks for the mechanical rule governing it, **Then** the document confirms
   there is none to apply beyond the existing Rally/downtime/Mend recovery already in play.

### Edge Cases

- What if a setting wants an item with a narrative-only effect (e.g. numbing pain, buying time)
  that never touches a track? That remains available — the decision only forecloses a *mechanical*
  Stamina effect, not narrative colour.
- What about an item that affects a different track (Strain, Taint, Trauma)? Out of scope here;
  this decision concerns Stamina specifically, per the issue that raised it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The design MUST state explicitly that a consumable healing item (potion, draught,
  medicine, or similar) has no mechanical effect on Stamina recovery.
- **FR-002**: The design MUST place this statement where a setting author or GM would look for it
  — alongside the existing Stamina recovery rule in `docs/design/03-rules.md`.
- **FR-003**: The design MUST explain the reasoning in terms already established by ADR 0020 (no
  new cadence; recovery lives on the Rally/downtime/Mend clocks the engine already has), rather
  than asserting the position without grounding it.
- **FR-004**: The design MUST NOT introduce a new mechanism, clock, or item-effect vocabulary —
  this is a documentation-only closure of a silent gap, not a new capability.

### Key Entities

*(none — this feature adds no new data or mechanism)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader of `docs/design/03-rules.md`'s Stamina section can state, without
  consulting any other document or making an inference, whether a consumable item affects Stamina
  recovery.
- **SC-002**: `python3 tools/check_docs.py` and the project's dangling-mechanic check both pass
  with the new text in place — no new mechanic name is introduced for anything to dangle.

## Assumptions

- The position taken is procedural-only: no consumable item shortcuts, adds to, or otherwise
  affects the Rally/downtime/Mend recovery clocks. This follows directly from ADR 0020's
  "no new cadence" reasoning (a third clock, or an exception to the existing two, is "a parallel
  mechanic" — the exact fault ADR 0020 was written to avoid) and from "Stamina is not meat," which
  already establishes that Stamina loss is not literal injury a potion would sensibly restore.
- This is a documentation-only change per the issue's own Definition of Done: no new mechanism is
  being defined, so no code, schema, or validator changes are in scope.
- Narrative/flavour uses of a healing item (it exists in the fiction, a character can carry and
  use one, it colours a scene) remain entirely available to a setting; only a *mechanical* Stamina
  effect is foreclosed.
