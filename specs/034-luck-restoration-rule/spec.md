# Feature Specification: Luck restoration rule

**Feature Branch**: `034-luck-restoration-rule`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Decide and document Luck's restoration rule (issue #117)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reading the rule settles what Luck spent this arc means (Priority: P1)

A reader of `docs/design/03-rules.md` §1 (Luck), having just read that testing Luck "costs 1 Luck
for the rest of the arc, pass or fail," needs to know what happens to that spent Luck once the arc
ends — without that answer, the arc-scoped phrasing is a dangling implication rather than a stated
rule.

**Why this priority**: This is the entire gap the issue raised. Nothing else in this feature has
value if this isn't answered.

**Independent Test**: Read `03-rules.md` §1 top to bottom; confirm it states, in one place,
whether and when Luck is restored, with no follow-on question left open.

**Acceptance Scenarios**:

1. **Given** a character has spent Luck during an arc, **When** that arc ends and a new one
   begins, **Then** the document states explicitly whether the character's Luck is now at maximum,
   unchanged, or something else.
2. **Given** a reader of `18-campaign.md`'s arc/era structure, **When** they cross-reference the
   Luck restoration rule, **Then** the rule's notion of "arc boundary" matches an actual boundary
   `18-campaign.md` defines — it does not invent a boundary the campaign structure doesn't have.

### Edge Cases

- What happens to Luck spent inside a nested arc (arcs recurse per `27-entities.md`) — does
  restoration happen at every level's boundary, or only at the top-level arc boundary
  `18-campaign.md` calls out as the one with a "job the deeper ones do not"?
- What happens to Luck maximum itself — is 40 fixed for the character's life, or can it change?
  (Out of scope here unless the restoration rule depends on it.)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `docs/design/03-rules.md` §1 (Luck) MUST state explicitly whether Luck is restored,
  and if so, on what boundary.
- **FR-002**: The chosen rule MUST resolve the standing ambiguity between "costs 1 Luck for the
  rest of the arc" (which implies a reset exists) and the absence, everywhere else in
  `docs/design/`, of any stated recovery.
- **FR-003**: If the rule ties restoration to an arc boundary, it MUST name the same boundary
  `docs/design/19-campaign.md` defines for top-level arcs — not a new, unstated notion of "arc."
  Nested arcs recurse (`27-entities.md`); the rule MUST be explicit about which level of arc it
  fires on, so the two documents cannot be read as describing different boundaries.
- **FR-004**: The restoration rule MUST NOT introduce a new named track, currency, or downtime
  mechanic — Luck already has a mechanism (creation value, per-test spend); this feature adds only
  a recovery clause to the existing one.
- **FR-005**: The decision MUST be recorded as an ADR per `CLAUDE.md`'s test for one (a real
  alternative — "Luck never restores" — is being rejected, and it is the kind of thing someone
  would plausibly propose again having forgotten why not).

### Key Entities

- **Luck**: a percentage resource, set to 40/40 at creation (`05-character-creation.md`), spent in
  units of 1 by choosing to test it (`03-rules.md` §1). This feature adds: when spent Luck is
  restored.
- **Arc**: the unit `18-campaign.md` defines as recursive, where the top-level arcs directly under
  a chronicle each "end with something altered." This feature must anchor restoration to the
  correct level of this structure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader of `03-rules.md` §1 alone, with no other document open, can state whether a
  character who spent Luck last arc has it back now — with no inference required.
- **SC-002**: `python3 tools/check_docs.py` passes after the change (no broken links, no orphaned
  document introduced).
- **SC-003**: The decision is discoverable as a single, numbered ADR in `docs/adr/`, distinct from
  the design-document prose it justifies.

## Assumptions

- The leading candidate named in the issue — Luck resets to maximum at the start of each new
  **top-level** arc (the one `18-campaign.md` gives a distinguishing "job") — is adopted, since it
  is the reading that makes the existing "for the rest of the arc" phrasing true rather than
  misleading. The alternative (Luck never restores) is rejected: it would make the arc-scoping
  clause in `03-rules.md` meaningless, since a resource that never resets doesn't need its cost
  scoped to anything narrower than the character's whole life.
- Restoration fires only at a top-level arc boundary, not at every recursive arc's boundary
  beneath it — matching `18-campaign.md`'s statement that top-level arcs specifically "have a job
  the deeper ones do not."
- This is documentation-only; no code exists for Luck yet, so there is nothing to implement beyond
  the design text and its ADR.
