# Feature Specification: Re-play playtest scenarios affected by rule changes made during the playtest epic

**Feature Branch**: `174-replay-affected-playtests`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "One more playtest feature before we close the epic - run through all the playtest again, for those scenarios where the rules have changed based on feedback (closes #174, part of the playtest epic #134)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every scenario a rule change actually touched is re-derived, not just noted (Priority: P1)

Someone closing out the playtest epic wants confidence that a rule change (ADR 0043/0044/0045)
didn't just get documented in the abstract — it was actually re-applied to the specific played
scenario that found the gap, using real rolls.

**Why this priority**: This is the whole point of the request — the original §7/§8/§10 sections
already carry "Resolved in ADR NNNN" notes, but none of them re-derive the actual outcome under
the new rule against the original scenario's own data.

**Independent Test**: Read the new §14; confirm each of the three affected scenarios (§7's
combat exchange, §8's Resolve gap, §10's spam sequence and Resolve recurrence) is re-derived with
real rolls, and the original section's text is untouched.

**Acceptance Scenarios**:

1. **Given** §7's three already-published defence rolls, **When** re-read against ADR 0044's
   virtual-roll formula, **Then** any blow that is now telling is identified, and its
   consequence (a changed drop round, a re-derived critical/Aftermath outcome) is carried
   through using the same already-drawn dice under the new modifier, not fresh unrelated rolls.
2. **Given** §8's Resolve gap (nothing to ever spend), **When** replayed under ADR 0043, **Then**
   a real Rally, cap, and spend are shown with fresh seeded rolls.
3. **Given** §10's spam sequence and Resolve recurrence, **When** replayed under ADR 0043 and
   ADR 0045 against Kester's own character (not only the abstract verification script), **Then**
   real Trauma and Affliction consequences are shown with fresh seeded rolls.

### Edge Cases

- Does this edit the original §7/§8/§10 text? No — those remain the historical record of the gap
  or ambiguity as it was actually found; the new §14 states what changed, cross-referencing them.
- Does this replay §12 (reroll stacking) or §6/§9/§11? No — ADR 0046 (reroll stacking) made no
  mechanical change, only documented the existing behaviour, so §12 needs no replay; §6, §9, and
  §11 exercised no mechanic later changed by any of the four ADRs.
- Does a materially different outcome (e.g. §7's earlier drop) count as a new finding needing its
  own follow-up issue? No — it is the expected, intended effect of the fix landing, not a defect.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new section MUST be added to `docs/design/30-playtest-transcript.md` re-deriving
  §7's combat exchange against ADR 0044, using the original defence rolls (not fresh ones) fed
  through the new formula.
- **FR-002**: The same section MUST re-derive the critical and Aftermath rolls affected by §7's
  changed outcome, reusing the original die values under their new modifiers rather than drawing
  fresh dice for values unaffected by the rule change.
- **FR-003**: The section MUST replay §8's blocked Resolve exercise under ADR 0043, with fresh
  seeded rolls, including an honest treatment of the single-Rally edge case rather than skipping
  straight to a favourable one.
- **FR-004**: The section MUST replay §10's Resolve recurrence and spam sequence under ADR 0043
  and ADR 0045, against Kester's own character, with fresh seeded rolls.
- **FR-005**: The original §7/§8/§10 sections MUST NOT be edited — only the new section is added.
- **FR-006**: No new design decision may be made in this section — it only re-applies decisions
  already made.

### Key Entities

*(none — this feature is a playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new §14 covering all three affected
  scenarios, with every roll traced to a real seeded draw.
- **SC-002**: §7's re-derivation correctly identifies which of the three original defence rolls
  is now a telling blow, and correctly carries the consequence through the critical/Aftermath
  rolls using the original dice under new modifiers.
- **SC-003**: §8's and §10's replays show a real Resolve spend and real Trauma/Affliction
  accrual respectively, closing the gaps those sections originally found.
- **SC-004**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (no new
  finding class beyond the already-accepted Omen false-positive pattern), and
  `python3 -m pytest -q` pass.

## Assumptions

- No new ADR — this re-applies existing decisions, it does not make one.
- The GM-chosen skill for §10's Affliction test (`08-afflictions.md`) is assumed at 50%,
  disclosed explicitly as this replay's own assumption, since the original §10 never played an
  Affliction test to establish one.
- Kester's maximum Stamina is assumed at the creation default (6), since §10 never stated one
  explicitly.
