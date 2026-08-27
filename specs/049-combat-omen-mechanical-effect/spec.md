# Feature Specification: Combat Omens carry a ±10 modifier on the roller's next roll

**Feature Branch**: `049-combat-omen-mechanical-effect`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Give combat Ill/Fair Omens a material mechanical effect (+/-10 to the roller's next roll) (closes #159). Operator decision: in combat, an Ill Omen applies -10 to the roller's own next roll in that fight, a Fair Omen +10 -- keeping the existing narrative framing alongside the mechanical effect, not replacing it."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An Omen in combat measurably costs or buys something, not just flavour (Priority: P1)

A player whose attack or defence roll carries an Ill Omen wants that to matter beyond a line of
narration — their next roll should be harder. A Fair Omen should make it easier.

**Why this priority**: This is the exact gap the operator raised, after three playtest-epic
features (#147/#148/#149) each noted Omens faithfully without them ever mattering mechanically —
the documented default working as designed, but judged under-weighted specifically in combat.

**Independent Test**: Read `docs/design/03-rules.md` §2's Omen rule; confirm it states a ±10
modifier on the roller's own next roll, alongside — not instead of — the existing narrative
framing.

**Acceptance Scenarios**:

1. **Given** a character rolls an attack with an Ill Omen, **When** they next roll (attack or
   defence) in the same fight, **Then** that roll's effective% is reduced by 10 before the clip
   bounds apply.
2. **Given** a character has a pending Fair Omen modifier and then rolls another Omen (Ill or
   Fair) before spending it, **When** the second Omen resolves, **Then** the pending modifier is
   replaced by the new one, not added to it.
3. **Given** a character has a pending Omen modifier when the fight ends, **When** the fight
   ends, **Then** the modifier lapses unused.

### User Story 2 - The change doesn't meaningfully shift the fight-length/damage figures ADR 0028 already published (Priority: P1)

Someone who trusts ADR 0028's damage-multiplier and fight-length figures wants confidence this
new mechanic doesn't quietly invalidate them.

**Why this priority**: CLAUDE.md's own "check the maths" principle, and this feature's own
Definition of Done, requires this be computed, not assumed.

**Independent Test**: Run `specs/049-combat-omen-mechanical-effect/check_omen_effect.py`; confirm
it reports the shift in expected damage per round across every representative pairing and states
whether it crosses a materiality threshold.

**Acceptance Scenarios**:

1. **Given** the representative pairing span `check_conversion.py` already uses, **When** the
   Omen-effect model is compared against the baseline (no Omen effect), **Then** the largest
   shift in expected damage per round across every pairing is reported and checked against a
   stated materiality threshold.

### Edge Cases

- Since the opponent never rolls (ADR 0027), does the opponent ever get an Omen-driven modifier?
  No — every roll in combat belongs to the player, so every Omen's consequence belongs to the
  player too. There is no "opponent's next roll" to modify.
- Which specific roll is "the roller's own next roll" when an Omen falls on an attack that also
  ends the fight (opponent drops)? Moot — there is no next roll to apply it to; the modifier
  simply never gets spent (same as the "lapses unused" case).
- Does this collide with the already-established opt-in Omen consequences (shooting into someone
  else's fight; systems of power's Ill-Omen-Taint)? No — those are a different kind of
  consequence (a narrative branch, or a track cost) and apply independently alongside the new
  roll modifier, not in place of it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: In combat, an Ill Omen MUST apply −10, and a Fair Omen +10, to the roller's own
  next roll (attack or defence) in the same fight.
- **FR-002**: The modifier MUST NOT stack — a second Omen before the pending modifier is spent
  replaces it.
- **FR-003**: An unspent modifier MUST lapse if the fight ends before the character rolls again.
- **FR-004**: The mechanical effect MUST be additive to the existing narrative framing (§1's
  "something also goes wrong/breaks your way"), never a replacement for it.
- **FR-005**: This MUST be scoped to combat only — an ordinary (non-combat) test's Omen stays
  narrative-only, per the existing default.
- **FR-006**: The shift in expected damage per round this mechanic introduces MUST be computed
  against `check_conversion.py`'s own representative pairing span, and checked against a stated
  materiality threshold, before concluding ADR 0028's figures don't need re-deriving.
- **FR-007**: A new ADR MUST record the decision and its rejected alternative (status quo:
  narrative-only in combat too), per CLAUDE.md's own test for when a decision earns a record.

### Key Entities

*(none — this feature adds a rule and a verification script, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/03-rules.md` §2 states the ±10 mechanic explicitly, alongside the
  existing narrative framing.
- **SC-002**: `specs/049-combat-omen-mechanical-effect/check_omen_effect.py` computes the shift
  in expected damage per round across every pairing in `check_conversion.py`'s own representative
  span, with exact-fraction arithmetic.
- **SC-003**: The computed shift is confirmed below a stated materiality threshold, or ADR 0028's
  figures are flagged for re-derivation if not.
- **SC-004**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
  `python3 tools/check_probability_coverage.py` all pass.
- **SC-005**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- The materiality threshold (0.1 damage/round, ~2% of starting Stamina per round) is a judgment
  call stated and justified in the check script's own comments, not asserted without reasoning.
- The Omen's own trigger rate (20%, or wider under `houserules.yaml`) and Taint's die-bending
  effect (`03-rules.md` §4) are unchanged by this feature — only what happens once an Omen is
  read is affected.
- This feature carries a real ADR (0042) since a real, workable alternative (the status quo) is
  being rejected, and the choice is one someone could plausibly re-propose.
