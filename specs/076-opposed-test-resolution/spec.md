# Feature Specification: Core opposed-test resolution

**Feature Branch**: `222-opposed-test-resolution`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "Core opposed-test resolution (d100, success/magnitude/complication) — implement the opposed-test formula and the Wyrd die from docs/design/03-rules.md section 1, exactly as specified. Depends on #221 (engine scaffolding). Part of #208/#90."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The GM resolves an opposed test with one roll (Priority: P1)

Whenever a player character or companion is opposed by an NPC (a lock picked while a guard
listens, a bluff run past a suspicious gatekeeper), the GM calls the engine once with the
character's skill and the opponent's skill (or baseline), and gets back success/failure — the
opponent never rolls.

**Why this priority**: This is the single most-used resolution shape in play (per
`docs/design/03-rules.md`, it now covers combat's attack and defence rolls too, per ADR 0027)
and the reason #222 exists as its own feature ahead of declaration/assistance/group tests.

**Independent Test**: Call the opposed-test function directly with a skill, an opponent
skill/baseline, and a fixed seed, and confirm success/failure matches the documented formula —
no CLI polish, declaration, or assistance layer needed.

**Acceptance Scenarios**:

1. **Given** skill 50 and opponent baseline 50 (an even match), **When** the test resolves,
   **Then** `effective%` is 50 and the roll succeeds if and only if the roll is ≤ 50.
2. **Given** skill 70 and opponent baseline 30, **When** the test resolves, **Then** `effective%`
   is `clip(50 + (70-30), 5, 95) = 90`.
3. **Given** a skill gap that would push `effective%` above 95 or below 5, **When** the test
   resolves, **Then** `effective%` is clipped to 95 or 5 respectively — no skill gap reaches
   certainty or impossibility.

---

### User Story 2 - Degrees of success measure how well a success landed (Priority: P2)

When an opposed test succeeds, the GM learns not just that it succeeded but by how much — a
narrow success reads differently from an overwhelming one.

**Why this priority**: Magnitude is one of resolution's three independent axes and is what lets
the GM narrate proportionally; without it every success reads identically regardless of margin.

**Independent Test**: Call the opposed-test function with a fixed seed producing a known roll
and confirm the reported degrees match `tens(effective%) - tens(roll)` exactly.

**Acceptance Scenarios**:

1. **Given** `effective% = 90` and a roll of 23, **When** the test resolves, **Then** degrees is
   `9 - 2 = 7`.
2. **Given** a failing roll, **When** the test resolves, **Then** no degrees value is reported —
   an opposed test's failure "simply fails the action," with no degrees comparison to have
   skipped (`docs/design/03-rules.md`'s "Opposed tests" subsection, point 3).

---

### User Story 3 - The Wyrd die reports what else happened, independent of success (Priority: P3)

Every roll's natural units digit tells the GM whether something *also* went wrong (Ill Omen) or
broke the player's way (Fair Omen), regardless of whether the roll itself succeeded.

**Why this priority**: This is resolution's third independent axis, and the one most likely to
be implemented incorrectly by coupling it to the success axis (the spec explicitly requires
independence). Lowest priority only because it's the smallest, most self-contained piece — a
single lookup on one digit — not because it matters less.

**Independent Test**: Call the opposed-test function repeatedly with fixed seeds chosen to
produce every units digit 0-9, and confirm the Wyrd die reading matches the units-digit-only
table regardless of the roll's success/failure.

**Acceptance Scenarios**:

1. **Given** a natural roll ending in 0, **When** the test resolves, **Then** the Wyrd die
   reports Ill Omen, whether the roll succeeded or failed.
2. **Given** a natural roll ending in 9, **When** the test resolves, **Then** the Wyrd die
   reports Fair Omen, whether the roll succeeded or failed.
3. **Given** a natural roll ending in 1-8, **When** the test resolves, **Then** the Wyrd die
   reports nothing.

### Edge Cases

- What happens when skill and opponent baseline are identical? `effective%` is exactly 50 (an
  even match is a coin flip), per FR-002.
- What happens when the opponent has no assigned skill for the contested action? The caller
  passes a baseline value in the same parameter opposed_skill occupies — this feature does not
  define what that baseline value is (that belongs to the adversary model, already settled by
  #54/ADR 0025-0026); it only clips and combines whatever value it is given.
- What happens on a tied roll exactly at the effective% boundary? Per the base rule ("succeed at
  or under"), a roll equal to `effective%` is a success.
- What happens to the Wyrd die and Taint interaction (`docs/design/03-rules.md`'s "Taint bends
  the die" table)? Out of scope for this feature — Taint is chronicle state that does not exist
  yet (a later feature in #215 Condition tracks); this feature implements the base 0/9 table only,
  as an Assumption (below).
- What happens to the Omen's ±10 modifier carrying onto the roller's next roll (`docs/design/
  03-rules.md`'s point 6, ADR 0042)? Out of scope — that requires tracking a pending modifier
  across calls (chronicle state), which is a separate, already-specified concern
  (`specs/069-omen-carryover/`) layered on top of this feature's stateless resolution primitive,
  not part of it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST resolve an opposed test from a skill value and an opponent
  skill/baseline value, rolling exactly once, on the acting side only.
- **FR-002**: `effective%` MUST be computed as `clip(50 + (skill - opponent_skill_or_baseline),
  5, 95)`.
- **FR-003**: The test MUST succeed if and only if the roll is less than or equal to
  `effective%`.
- **FR-004**: On success, the engine MUST report degrees of success as `tens(effective%) -
  tens(roll)`.
- **FR-005**: On failure, the engine MUST NOT report a degrees value — failure simply fails the
  action, with no degrees comparison performed.
- **FR-006**: The engine MUST read the Wyrd die from the units digit of the natural (unmodified)
  roll: 0 → Ill Omen, 9 → Fair Omen, 1-8 → nothing.
- **FR-007**: The Wyrd die reading MUST be independent of success/failure — computed identically
  regardless of which side of `effective%` the roll landed on.
- **FR-008**: The opponent's own dice MUST NOT be consulted at any point in this resolution — no
  resisting-side roll exists.
- **FR-009**: The engine MUST support an explicit seed (reusing #221's dice primitive), producing
  identical results for identical inputs and seed.
- **FR-010**: The CLI MUST expose this resolution as a `describe`-discoverable verb, per
  `docs/design/27-tooling.md` section 3's catalog-driven shape established in #221.
- **FR-011**: Nothing in this feature may name a specific setting, system, or source text.

### Key Entities

- **Opposed test result**: `effective_pct`, `roll`, `success`, `degrees` (present only on
  success), `wyrd` (`"ill_omen"` | `"fair_omen"` | `"none"`). Stateless — this feature reads no
  chronicle state and writes none (unlike #221's `roll` verb, which persists `last_roll`; this
  verb's result is not itself persisted by this feature, since no later feature yet depends on
  reading a stored opposed-test result back).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For 1000 distinct (skill, opponent) pairs spanning the full clip range, computed
  `effective%` matches the documented formula exactly, with zero deviation.
- **SC-002**: Degrees of success, when reported, matches `tens(effective%) - tens(roll)` exactly
  across all tested success cases.
- **SC-003**: The Wyrd die reading matches the units-digit table for all ten possible units
  digits (0-9), on both a success and a failure case for each digit (20 total cases), with zero
  deviation.
- **SC-004**: A cold run of the CLI's opposed-test verb succeeds with no setup beyond what #221
  already established.

## Assumptions

- Taint's effect on the Wyrd die's Ill Omen band (`docs/design/03-rules.md`'s "Taint bends the
  die" table) is out of scope — no Taint state exists yet in the engine (#215 Condition tracks).
  This feature implements only the base, Taint-free table (0 → Ill Omen, 9 → Fair Omen).
- The Omen's ±10 carryover modifier onto the roller's next roll (ADR 0042) is out of scope — it
  requires state this feature's stateless primitive does not hold, and is already specified
  separately (`specs/069-omen-carryover/`) as a layer on top.
- "Opponent skill or baseline" is accepted as a plain integer parameter; resolving what baseline
  value an adversary actually has is the adversary model's concern (#54/ADR 0025-0026), already
  settled, and out of scope for this feature to re-derive.
- This feature does not implement declaration bonuses, assistance, group tests, or extended
  tasks — those are #223 and #224, separate children of #208.
- Following #221's precedent: Python 3.11+, standard library only, stdlib `unittest`, no pytest,
  catalog-driven CLI dispatch per `docs/design/27-tooling.md`.
