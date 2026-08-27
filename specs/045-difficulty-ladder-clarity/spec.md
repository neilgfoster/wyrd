# Feature Specification: Clarify the difficulty ladder's asymmetry and the untrained-attempt table's stacked bonuses

**Feature Branch**: `045-difficulty-ladder-clarity`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Clarify the difficulty ladder's asymmetry and separate the stacked bonuses in the untrained table (closes #139). The ladder has one step above Average and four below, unexplained anywhere. The untrained-attempt table's 50% row reads like a hidden Very Easy tier or a mystery +40, when it's actually two separate +20 bonuses (Easy difficulty, and a declaration bonus) stacking."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader understands why the difficulty ladder is asymmetric (Priority: P1)

Someone reading `03-rules.md`'s difficulty ladder (Easy +20 / Average +0 / Challenging −10 /
Difficult −20 / Hard −30 / Very Hard −40) wants to know why there's one step above Average and
four below, rather than wondering if a tier is missing.

**Why this priority**: This is the exact gap #139 raised — the asymmetry is real and was
unexplained anywhere in the document or in any ADR.

**Independent Test**: Read the ladder and the text immediately following it; confirm the
asymmetry has a stated rationale.

**Acceptance Scenarios**:

1. **Given** the difficulty ladder, **When** a reader asks why there's no "Very Easy" tier,
   **Then** the text explains a task easier than Easy isn't rolled at all — it's covered by the
   Declaration table's "so well-judged it removes the risk" row and the "only roll when it is
   dramatic" principle.

### User Story 2 - A reader can see which bonus is which in the untrained-attempt table (Priority: P1)

Someone reading the untrained-attempt table's "easy, specific and leveraging something
established → 50%" row wants to see that it's two named +20 bonuses stacking on the 10% base
(Easy difficulty, and the declaration bonus), not one opaque modifier.

**Why this priority**: This is the second half of #139's finding — the math was always correct,
but the table hid its own working.

**Independent Test**: Read the reworked table and confirm each row shows the base, the difficulty
contribution, and the declaration contribution separately, summing to the published total.

**Acceptance Scenarios**:

1. **Given** the reworked untrained-attempt table, **When** any row is checked, **Then** its
   Base + Difficulty + Declaration columns sum to the "At" column's published figure.
2. **Given** the "easy, specific and leveraging something established" row specifically,
   **When** read, **Then** it visibly shows Easy (+20) and the declaration bonus (+20) as two
   separate contributions to the 10% base, summing to 50%.

### Edge Cases

- Does explaining the asymmetry change any actual modifier value? No — this is presentation only;
  every published percentage is unchanged, only how the table shows its working.
- Is the "hard" row ("impossible — the modifier takes it below zero") still correct under the new
  table shape? Yes — 10% base + Hard (−30) + no declaration bonus = −20%, below zero, impossible;
  the reworked table states this explicitly rather than as a bare assertion.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The difficulty ladder MUST be followed by a stated rationale for its asymmetry
  (one step up, four down).
- **FR-002**: The untrained-attempt table MUST show each row's contributing modifiers (base,
  difficulty, declaration) separately, not only the combined result.
- **FR-003**: No published percentage or modifier value MUST change — this is a presentation
  fix, not a rule change.

### Key Entities

*(none — this feature clarifies existing prose/tables, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader of `03-rules.md` alone can state why the difficulty ladder has one step up
  and four down, without needing to infer it.
- **SC-002**: Every row in the reworked untrained-attempt table sums correctly (Base + Difficulty
  + Declaration = At), verified by direct arithmetic check.
- **SC-003**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass
  with no new finding introduced by the new prose.

## Assumptions

- Documentation-only, presentation fix: no ADR needed (no rule value changes, no alternative
  rejected), no code changes.
- The rationale given for the ladder's asymmetry (very-easy tasks aren't rolled at all; the
  dramatic range lives below Average) is grounded in text already present elsewhere in the same
  document (the Declaration table's "no roll" row, and "only roll when it is dramatic") rather
  than invented from scratch.
