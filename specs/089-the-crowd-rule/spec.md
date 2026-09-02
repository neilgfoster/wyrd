# Feature Specification: The crowd rule

**Feature Branch**: `089-the-crowd-rule`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "The crowd rule — implement docs/design/03-rules.md §2 'Crowds' end
to end: the three-part crowd-member qualification lookup, the free clear, the crowd's own
single per-round attack (eased by body count, capped at +20), the crowd's single parting blow,
and the explicit exclusion of crowds from Aftermath. Building on #244's engagement state."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Running a crowd fight without a roll per body (Priority: P1)

A character engaged with a crowd of low-grade opponents clears one body for free at the start of
each of their turns, no roll and no action spent, and the crowd answers back with exactly one
attack a round no matter how many bodies remain — eased if it has more than one body still
pressing that character.

**Why this priority**: This is the entire feature — the rule that keeps a fight against many
opponents from becoming one roll per body.

**Independent Test**: Register a crowd of a known body count engaged with a character; clear one
body; confirm the count drops by exactly one, no roll performed, no action recorded spent; resolve
the crowd's own attack and confirm it is exactly one `combat-attack` resolution regardless of body
count.

**Acceptance Scenarios**:

1. **Given** an opponent with maximum Stamina 1, no armour, and a skill at least 20 below the
   character's own relevant skill, **When** the qualification lookup is run, **Then** it reports
   the opponent qualifies as a crowd member.
2. **Given** an opponent failing any one of the three tests (Stamina above 1, wearing armour, or
   a skill gap under 20), **When** the qualification lookup is run, **Then** it reports the
   opponent does not qualify.
3. **Given** a character in close engagement with a crowd, **When** their turn starts, **Then**
   one qualifying crowd body is cleared: no roll occurs, no action is spent, and the crowd's
   remaining body count drops by exactly one.
4. **Given** a crowd with one body remaining engaged with a character, **When** the crowd's own
   attack is resolved, **Then** it is a single `combat-attack` resolution at the crowd's base
   skill, with no ease applied.
5. **Given** a crowd with two or three-or-more bodies remaining engaged with one character,
   **When** the crowd's own attack is resolved, **Then** it is still a single `combat-attack`
   resolution, eased +10 per body beyond the first, capped at +20 (reached at three bodies).
6. **Given** a character breaking off from a crowd, **When** the parting blow is resolved,
   **Then** it is a single `combat-attack` resolution on the same eased terms as the crowd's own
   attack — never one per remaining body.

### Edge Cases

- What happens when a crowd's body count reaches zero? Clearing further from an empty crowd is
  an error — there is nothing left to clear (the caller/GM should have removed the engagement or
  ended the crowd's presence in the scene by that point).
- What happens when a character is not engaged with the crowd at all? No clear happens — "a
  character who is not engaged with the crowd... clears nobody," and attempting to clear anyway
  is an error, the same shape as `close`/`break_off`'s existing engagement-mismatch guards.
- What happens when a character is themselves untrained in the relevant skill? They have no gap
  to compare (their own skill sits at the flat 10% used for any untrained roll), so the
  qualification lookup reports no qualifying crowd member for them.
- What happens with a crowd of exactly one body? The crowd is still a crowd (the qualification
  lookup is per-body, not per-count) — its own attack applies no ease (body count 1), and a
  single clear reduces it to zero.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST determine whether an opponent qualifies as a crowd member using
  exactly the three-part lookup: maximum Stamina of 1, no armour, and the character's relevant
  skill ahead of the opponent's by 20 or more.
- **FR-002**: The system MUST let a character or companion engaged with a crowd clear exactly one
  qualifying crowd body at the start of their own turn, with no roll and no action cost.
- **FR-003**: The system MUST reject a clear attempt when the acting character is not currently
  engaged with the named crowd, or when the crowd has no bodies left to clear.
- **FR-004**: The system MUST resolve a crowd's own attack on an engaged character as exactly one
  `combat-attack` resolution per round, regardless of how many bodies the crowd still has.
- **FR-005**: The system MUST ease a crowd's own attack by +10 for each crowd body on the target
  beyond the first, capped at a total ease of +20 (reached at three bodies).
- **FR-006**: The system MUST resolve a crowd's parting blow (when broken off from) as exactly one
  `combat-attack` resolution, on the same eased terms as its own per-round attack — never one per
  remaining body.
- **FR-007**: The system MUST NOT stage or imply any Aftermath resolution for a crowd — a crowd is
  never passed as an entity to whatever the engine's own Aftermath resolution eventually is.

### Key Entities

- **Crowd**: an engaged opponent representing many low-grade bodies at once, tracked by a current
  body count rather than as individual persisted entities. Its own attack always uses one shared
  skill value regardless of body count.
- **Crowd member**: one body within a crowd, qualifying or not per the three-part lookup (FR-001)
  against a specific character's relevant skill.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The qualification lookup matches the stated thresholds exactly at their boundary
  values (Stamina 1 vs. 2, armoured vs. not, skill gap of 19 vs. 20), verified by a scripted
  check at each boundary.
- **SC-002**: A multi-round clear sequence against a crowd of known starting body count ends at
  exactly the expected remaining count, with no roll performed at any step.
- **SC-003**: The crowd's own attack resolves as exactly one roll at 1, 2, and 3-or-more bodies
  on the target, with the ease bonus at each count matching +0, +10, and +20 respectively.
- **SC-004**: The crowd's parting blow resolves as exactly one roll regardless of remaining body
  count, verified against a multi-body scenario.

## Assumptions

- A crowd is represented by its current body count, tracked per crowd within the same
  chronicle-scoped `combat` scene #243/#244 already established — not as individually persisted
  character entities, since the rule's own point is to avoid a per-body roll or per-body state.
- The crowd's own attack and its parting blow are resolved by the same underlying mechanism (one
  eased `combat-attack` request), since the design text states both use "the same terms" — this
  feature does not reuse `break_off` directly (its contract stages one attack per named engaged
  opponent with no ease channel); a crowd's parting blow is resolved by this feature's own
  function instead, called in place of `break_off` for that particular engaged crowd.
- Aftermath (#213) has no engine implementation yet — FR-007 is satisfied by this feature never
  calling into (or providing an entry point toward) any Aftermath-shaped resolution for a crowd,
  documented here as the currently-checkable form of that requirement.
- "The character's relevant skill" and "the opponent's skill" for the qualification lookup are
  supplied by the caller as plain integers, matching how skill values are supplied throughout the
  existing `combat.py`/`rules.py` functions (e.g. `resolve_ranged_attack`'s own skill lookups) —
  this feature does not introduce a new skill-resolution path.
