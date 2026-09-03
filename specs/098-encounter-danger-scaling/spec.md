# Feature Specification: Encounter danger scaling

**Feature Branch**: `098-encounter-danger-scaling`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Encounter danger scaling (issue #263): give the engine a function
that takes a bestiary block plus a target danger level and returns the two scaled quantities
docs/design/03-rules.md section 7 settled -- opponent count and the percentage they're run at --
without ever rewriting the underlying block entry."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The identity case: a party matching `written_for` runs content exactly as written (Priority: P1)

A party's effective size equals the effective size of `written_for` bodies (the common case: a
party of four runs content written for four). The scaled opponent count equals the written
count, and the scaled skill equals the block's own value, unchanged.

**Why this priority**: this is the case ADR 0024's whole ratio construction exists to preserve
-- if it doesn't hold, nothing else about the equation can be trusted either.

**Independent Test**: `scaled_count(written_count=6, danger=3, party=4, written_for=4)` returns
6; `adjusted_skill(skill=45, party=4, written_for=4)` returns 45.

**Acceptance Scenarios**:

1. **Given** a party of 4 running content written for 4, **When** the engine scales an opponent
   count of 6 at danger 3, **Then** the scaled count is 6.
2. **Given** the same party, **When** the engine scales a skill of 45, **Then** the scaled skill
   is 45 (an adjustment of +0).

---

### User Story 2 - A smaller party thins the encounter and eases the opponents' skill (Priority: P1)

A party smaller than `written_for` produces a lower `danger_effective`, a lower (or equal)
scaled opponent count, and a non-positive skill adjustment (opponents test worse against them).

**Why this priority**: this is the direction the design document's own worked example uses --
the case a GM actually reaches for when a chronicle's roster has shrunk.

**Independent Test**: the worked case from docs/design/03-rules.md section 7 -- a danger-3 arc
written for four, run by three bodies (one character, two companions): `danger_effective` is
exactly `2.64`; six cultists scale to five; three watchmen stay three.

**Acceptance Scenarios**:

1. **Given** `party=3, written_for=4, danger=3`, **When** the engine computes
   `danger_effective`, **Then** it is exactly `Fraction` `2.64` (unrounded).
2. **Given** the same inputs, **When** the engine scales a written count of 6, **Then** the
   result is 5.
3. **Given** the same inputs, **When** the engine scales a written count of 3, **Then** the
   result stays 3.
4. **Given** the same inputs, **When** the engine adjusts an opponent's skill, **Then** the
   adjustment is a non-positive number of points, rounded to the nearest 5 and clipped to -20.

---

### User Story 3 - A larger party thickens the encounter and toughens the opponents' skill (Priority: P2)

A party larger than `written_for` produces a higher `danger_effective`, a higher (or equal)
scaled opponent count, and a non-negative skill adjustment.

**Why this priority**: the mirror direction of User Story 2 -- both directions of the same
equation must hold, or the identity case in User Story 1 could pass by coincidence at one
extreme only.

**Independent Test**: `party=6, written_for=4` produces a scaled count at or above the written
count, and a skill adjustment that is negative or zero.

**Acceptance Scenarios**:

1. **Given** `party=6, written_for=4, danger=3`, **When** the engine scales a written count of
   6, **Then** the result is at least 6.
2. **Given** the same inputs, **When** the engine adjusts a skill, **Then** the adjustment is
   zero or positive.

---

### User Story 4 - The two quantities never rewrite the source block (Priority: P1)

Given a loaded adversary block (#259), computing a scaled skill or an effective danger for an
encounter never mutates the block passed in -- the block stays reusable, unaltered, for the next
encounter that reads it at a different danger or party size.

**Why this priority**: named explicitly in the issue's Definition of Done and in
docs/design/12-the-adversary.md section 6 ("The block is absolute... never by rewriting an
entry") -- a scaling call that mutated its input would corrupt every later read of that
adversary in the same session.

**Independent Test**: pass the same block dict to `adjusted_skill` twice, at two different
`party`/`written_for` pairs; the dict is unchanged (`==` its original snapshot) after both
calls, and the two results can differ.

**Acceptance Scenarios**:

1. **Given** a loaded adversary block, **When** the engine computes an adjusted skill for it at
   any `party`/`written_for`/skill name, **Then** the block dict passed in is unchanged
   afterward.

### Edge Cases

- `written_for` missing or zero: content runs as written -- `ratio` is 1, `danger_effective`
  equals `danger` exactly, scaled counts and skills are unchanged (docs/design/03-rules.md
  section 7: "Where `written_for` is missing or zero, the content runs as written").
- An adjusted skill that would go negative (an opponent already near the untrained floor, met by
  a large party against a small `written_for`): floors at 0, never negative.
- `written_count` of 0 (an optional quantity a piece of content does not use): scales to 0, not
  floored at 1 -- the floor-at-1 rule in docs/design/03-rules.md section 7 only applies "where
  the written quantity was at least 1."
- A party or `written_for` of 1: `H(1)` is exactly 1, so the ratio and adjustment behave as the
  smallest case of the same formula, not a special-cased shortcut.
- A party of none (`party <= 0`): the ratio is exactly 0, so the skill adjustment clips to its
  bottom rung (-20) rather than evaluating a logarithm of zero.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST compute a party's effective size as the harmonic-style sum
  `1 + 1/2 + ... + 1/p` for `p` bodies (ADR 0024), exact (a `Fraction`, not a rounded float).
- **FR-002**: The engine MUST compute the scaling ratio as the effective size of the present
  party divided by the effective size of `written_for` bodies, reading both sides through the
  same effective-size function; when `written_for` is missing or zero, the ratio MUST be 1.
- **FR-003**: The engine MUST compute `danger_effective` as `danger x ratio`, carried exact and
  never rounded at this step.
- **FR-004**: The engine MUST compute a scaled opponent count from a written count as
  `written_count * danger_effective / danger`, rounded half up at the point of use, floored at 1
  when the written count was at least 1, and left at 0 when the written count was 0.
- **FR-005**: The engine MUST compute a skill adjustment, in points, as
  `15.5 x log2(ratio)`, rounded to the nearest 5, clipped to the closed interval [-20, +20].
- **FR-006**: The engine MUST compute an adjusted skill as the block's own percentage for that
  skill (resolved via the existing baseline rule, #260) plus the skill adjustment, floored at 0.
- **FR-007**: None of this feature's computations MUST mutate the adversary block or any other
  input passed in -- every function returns a new value.
- **FR-008**: At `party == written_for` (including both equal to 1, and both missing/zero via
  FR-002), every quantity this feature computes MUST reproduce the input unchanged (ratio 1,
  `danger_effective == danger`, scaled count == written count, skill adjustment 0).

### Key Entities

- **Adversary block**: the loaded, validated shape #259 produces. This feature reads a named
  skill off it (via #260's `resolve_skill`) and never writes to it.
- **Party size**: a plain integer body count -- how many bodies are present, per
  docs/design/03-rules.md section 7's "query, not a roster" framing. Computing that count from
  the live party roster is out of scope here; this feature takes it as an input.
- **Danger level**: a plain integer or number, the content's own stated `danger` rating.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every `party`/`written_for` pair from 1 to 6, the computed skill adjustment
  matches, exactly, the published table in docs/design/03-rules.md section 7 (the same figures
  `specs/017-adversary-model/check_adversary.py` already verified for the design programme).
- **SC-002**: The danger-3, three-of-four worked example in docs/design/03-rules.md section 7
  reproduces exactly: `danger_effective = 2.64`, a written count of 6 scales to 5, a written
  count of 3 stays 3.
- **SC-003**: At `party == written_for`, for every value 1 through 6, every scaled quantity
  equals its unscaled input (the identity case holds at every point on the diagonal, not only
  the one worked example).
- **SC-004**: No test in this feature's suite observes a mutated input block or ratio/danger
  argument after any call.

## Assumptions

- This feature implements the equation only, reusing #259 (block loading) and #260 (baseline
  resolution) as already-settled inputs; it does not compute a live party's effective size from
  a chronicle's actual roster (docs/design/22-state.md's `status: with-party` query) -- that
  remains a separate concern for whichever caller assembles `party` before calling in.
- The published coefficient `15.5` (docs/design/03-rules.md section 7) is used directly, not
  re-derived from the achievable ratio range at run time -- the design document already recorded
  it as the number a GM reads, and `check_adversary.py` established that the fitted and
  published coefficients agree to the precision the ladder rounds to. Re-deriving it at runtime
  would add complexity with no observable difference to any figure this feature outputs.
- The engine already exposes `resolve_skill(block, skill)` (#260) for reading an opponent's
  percentage at a skill it may or may not list; this feature's `adjusted_skill` calls that
  rather than duplicating its baseline-fallback logic.
