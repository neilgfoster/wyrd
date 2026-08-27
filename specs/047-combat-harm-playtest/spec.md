# Feature Specification: Combat and harm playtest

**Feature Branch**: `047-combat-harm-playtest`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Combat and harm playtest (closes #148, part of the playtest epic #134). Extends #147's discipline (real seeded rolls) to a multi-round combat exchange, a crowd encounter, a drop, a critical, an Aftermath roll, a Fate spend, and Stamina recovery."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader trusts combat and harm play as designed across a full drop-to-recovery cycle (Priority: P1)

Someone who read #14/R3's single surviving exchange wants to see what happens when a character
actually drops — the critical, the Aftermath roll, a Fate spend against a death result, and
recovery back to full — played with real dice, not asserted.

**Why this priority**: This is the exact gap #148 was raised to close: #14/R3 proved a combat
exchange survives; nothing had yet played through a drop to its full resolution.

**Independent Test**: Read the new section in `docs/design/30-playtest-transcript.md`; confirm a
drop, a critical roll, an Aftermath roll, a Fate spend against an actual death result, and a full
Stamina recovery cycle are all present with real, seeded dice.

**Acceptance Scenarios**:

1. **Given** a real seeded combat exchange against a tougher single opponent, **When** played to
   resolution, **Then** whatever the dice produce is recorded honestly — including a drop, if one
   occurs.
2. **Given** the fight's actual Aftermath roll does not land on death, **When** the Fate-spend
   mechanic still needs demonstrating (per #148's own scope), **Then** a separately-labelled,
   honestly-reported sampling exercise (not a reroll of the fight's own outcome) is used to reach
   a real death result and play the spend through.
3. **Given** a crowd of qualifying opponents, **When** Senna is engaged with them, **Then** the
   clearing rule is played through with no roll, confirming it needs none.

### User Story 2 - A genuine rule ambiguity is found and reported, not silently resolved (Priority: P1)

If the playtest surfaces a real gap in how a rule is specified — not just an interesting roll —
it gets named and either fixed in place (if trivial) or raised as its own follow-up issue (if it
carries a real design/balance question), never quietly decided inside the playtest record itself.

**Why this priority**: #134's own Definition of Done requires this; deciding a live balance
question unilaterally inside a playtest write-up would be exactly the kind of undocumented
decision this repo's own recurring-fault list warns against.

**Independent Test**: Read the new section's Findings subsection; confirm any ambiguity found
states the two live readings, which one this playtest used and why, and whether a follow-up issue
was raised.

**Acceptance Scenarios**:

1. **Given** the actual play sequence (three blows landed via a failed defence roll, none via a
   successful attack), **When** the telling-blow rule is checked against them, **Then** a genuine
   textual gap is found (defence-side telling blow has no stated per-roll procedure) and reported,
   with the conservative reading used for this playtest and a follow-up issue raised rather than
   the ambiguity being resolved unilaterally here.

### Edge Cases

- What if the fight's own dice don't naturally produce a drop? Then the acceptance criteria
  requiring a drop/critical/Aftermath/Fate-spend demonstration would go unmet by the main
  exchange alone — mitigated here by deliberately pitting Senna against a tougher single
  opponent (still a legitimate GM/scenario choice, not dice manipulation) to make a drop likely,
  while still recording whatever the real dice actually produce.
- What if the death-band sampling exercise (for the Fate-spend demonstration) doesn't land a
  death result in a small sample? Not an issue here — three of six rolls at the 35%-death row
  landed in the death band, consistent with the published figure, so a real result was available
  to walk through without needing a larger sample.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playtest MUST use real seeded random rolls throughout, matching #147's own
  established discipline — no curated sequence for the fight's own outcome.
- **FR-002**: The playtest MUST exercise: a multi-round combat exchange, a crowd-clearing
  encounter, a drop below 0 Stamina, a critical roll, an Aftermath roll, a Fate spend against an
  actual death result, and Stamina recovery across a Rally and a downtime.
- **FR-003**: If the main exchange's own Aftermath roll does not land on death, a separately
  labelled, honestly-reported sampling exercise MUST be used to reach a real death result for the
  Fate-spend demonstration — never a silent reroll of the fight's own recorded outcome.
- **FR-004**: Any genuine rule ambiguity found MUST be reported explicitly, with the reading used
  for this playtest stated, and — if the ambiguity carries a real design/balance consequence — a
  follow-up issue raised rather than resolved unilaterally inside the playtest record.

### Key Entities

*(none — this feature is a worked playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section covering combat and
  harm end to end, following the existing document's established structure and tone.
- **SC-002**: Every roll in the new section traces to a real `python3 random` draw, seeded, in a
  stated fixed order.
- **SC-003**: The telling-blow-on-defence-failure ambiguity found during play is reported in the
  Findings subsection, with a follow-up issue raised.
- **SC-004**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass,
  with no new finding class introduced.
- **SC-005**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- The telling-blow ambiguity is a real design question (whether a defence-failure hit can ever be
  a telling blow), not a documentation typo — it is raised as its own issue rather than fixed
  in place, unlike the trivial #14/R3-style fixes this session's other features made.
- This feature carries no ADR of its own — the ambiguity it found may eventually need one, but
  that decision belongs to the follow-up issue, not to this playtest record.
- Documentation-only: no code changes; the roll-generation script is scratch tooling, not
  committed, matching #147's own precedent.
