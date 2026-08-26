# Feature Specification: Fault Line accrual bias

**Feature Branch**: `021-fault-line-direction`

**Created**: 2026-08-26

**Status**: Draft

**Input**: Issue [#58](https://github.com/neilgfoster/wyrd/issues/58) — give the Fault Line a
mechanical direction: two characters at equal Taint with different Fault Lines must differ
mechanically, not just in how the Fault Line is described.

## Why this exists

`design/03-rules.md` §4 names the Fault Line — "each character has a Fault Line derived at
creation from their Drives and Misfortune. It names *how* they fall — the direction, not only the
quantity" — and stops there. Nothing reads it, checks it, or lets it change an outcome. Two
characters at the same Taint with different Fault Lines currently play identically, which makes
the Fault Line prose rather than mechanism, and leaves the transformation table (#18, merged)
carrying all of Taint's texture alone.

## Clarifications

**What the Fault Line modifies.** Three candidates were on the table: which transformation is
rolled, how a threshold reads, or how Taint accrues. The first two both require restructuring or
biasing an existing roll or table — either a direction-keyed rework of
`design/03a-3-transformations.md`'s six rows, or a skew on the secretly-rolled hidden threshold
that stays invisible to the player by design, sitting awkwardly against the issue's own acceptance
criteria. The chosen answer keeps the transformation table exactly as `design/03a-3-transformations.md`
already defines it — untouched, no duplicate table — and instead extends the mechanism
`design/03-rules.md` §1 already uses for Drives ("against the character's established nature, the
GM may invoke a Drive for −20") to Exposure: when an Exposure source runs with the grain of a
character's Fault Line (the GM's call, grounded in the fiction, the same judgment call a Drive
invocation already is), the Taint gained is one tier worse. This stays out of the resolution die
entirely — the roll to resist Exposure is untouched; only the Taint number consumed on a failure
changes — so it does not compound invisibly with the way Taint already bends the Wyrd die.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Two characters take equal Exposure with different Fault Lines (Priority: P1)

Two characters, identical Taint, face the same moderate Exposure. For one it runs with the grain
of their Fault Line; for the other it does not. The first takes worse Taint for the same failed
resistance.

**Why this priority**: this is the mechanical difference the issue exists to create; nothing else
in scope matters without it.

**Independent Test**: run the feature's check script and confirm, at real Taint values a character
plausibly reaches, that a Fault-Line-aligned Exposure source measurably shortens the number of
Exposure events before the next threshold, compared with an unaligned one at the same starting
Taint.

**Acceptance Scenarios**:

1. **Given** two characters at Taint 4 with different Fault Lines, **When** each resists a
   moderate Exposure (base 2) that runs with their own Fault Line and fails, **Then** each takes 3
   Taint (one tier worse), not 2.
2. **Given** the same two characters, **When** each instead resists an Exposure that does not run
   with their Fault Line and fails, **Then** each takes the source's base Taint unmodified.
3. **Given** a character already at the top tier (major, base 3), **When** an aligned Exposure is
   failed, **Then** Taint gained stays at 3 — the tier-worse step never exceeds the existing
   minor/moderate/major ceiling.

---

### User Story 2 - The GM decides whether an Exposure source runs with the grain (Priority: P2)

The invocation is a fiction-grounded judgment call, the same shape as invoking a Drive — not an
automatic lookup against a fixed keyword list, because the Fault Line is prose describing a
direction, not a tag.

**Why this priority**: without a stated boundary on when the bias applies, every future Exposure
becomes a live argument about whether it "counts," which is the ambiguity the issue exists to
close.

**Independent Test**: confirm the design document states the same two-condition shape the Drive
invocation already uses (grounded in the fiction, the GM's call, never automatic) and that it caps
at one step per Exposure event, mirroring the "maximum one per check" cap already stated for
Invocation.

**Acceptance Scenarios**:

1. **Given** an Exposure event, **When** the GM judges it does not run with the character's Fault
   Line, **Then** no bias applies and the source's stated Taint gain stands.
2. **Given** an Exposure event the GM has already ruled aligned, **When** the same event is also
   an Invocation drawing on the character's own Taint, **Then** the tier-worse step and the
   Invocation penalty are independent — one affects the Taint gained on this failure, the other
   affects the difficulty of the roll that produced it — and neither doubles the other's effect.

### Edge Cases

- What happens at Taint 0, where a character can never be Spent? The bias still applies to Taint
  gained — it changes the number added, not the Spent condition, which reads off the current
  Resolve/Taint comparison after the gain lands.
- What happens when an aligned Exposure's base tier is already major (base 3), the ceiling case
  covered by Acceptance Scenario 3 above?
- What happens for a character whose Fault Line is genuinely broad, matching most Exposure they
  face? Nothing bounds how often the GM may judge alignment — the same is true of Drive invocation
  today, and the cap is per-event (one step), not per-chronicle.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `design/03-rules.md` §4 MUST state that the Fault Line has a mechanical effect on
  Taint gained from Exposure, not only a descriptive one.
- **FR-002**: When an Exposure source's fiction runs with the grain of a character's Fault Line —
  the GM's call, grounded in the fiction, the same judgment already used to invoke a Drive — a
  failed resistance test MUST gain Taint one tier worse than the source's stated base (minor 1 →
  2, moderate 2 → 3, major 3 stays 3).
- **FR-003**: The bias MUST NOT modify the resolution roll used to resist Exposure — it changes
  only the Taint number consumed on a failure, never the percentage chance of failing.
- **FR-004**: The bias MUST apply at most once per Exposure event, mirroring the existing "maximum
  one per check" cap already stated for Invocation.
- **FR-005**: The bias and an Invocation drawn against the same roll MUST be independent — the
  document must state plainly that one changes the Taint gained on failure and the other changes
  the difficulty of the roll, and that applying both to the same event does not compound either
  effect beyond its own stated step.
- **FR-006**: `design/03a-3-transformations.md` MUST remain unchanged in its roll, thresholds, and
  row contents — the Fault Line's effect must not duplicate or fork that table.
- **FR-007**: A check script MUST compute, at real Taint trajectories, how much sooner a character
  facing aligned Exposure crosses the next transformation threshold compared with one facing
  unaligned Exposure at the same starting Taint — not merely assert the difference exists.
- **FR-008**: An ADR MUST record this decision, naming the two rejected alternatives (transformation
  row selection; hidden threshold bias) and why each was set aside.

### Key Entities

- **Fault Line**: an existing field on the player character (`fault_line` in `design/06-state.md`),
  prose naming the direction a character's Taint is taking them. This feature does not change how
  it is set at creation — only that it is now read at Exposure time.
- **Exposure**: the existing Taint-gain route (`design/03-rules.md` §4) — a resisted test with a
  stated base Taint (minor 1, moderate 2, major 3) reduced by degrees of success. This feature adds
  one conditional step to its failure case.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Reading `design/03-rules.md` §4 alone, a GM can determine, for any failed Exposure
  test, exactly what Taint the character gains, without consulting any other document.
- **SC-002**: Two characters at identical starting Taint, one facing Fault-Line-aligned Exposure
  and one facing unaligned Exposure of the same base tier, provably diverge in Taint after one
  failed test — computed, not asserted, by the feature's check script.
- **SC-003**: `design/03a-3-transformations.md` requires zero edits to its roll, table, or
  threshold content as a result of this feature.

## Assumptions

- The Fault Line's *content* (what direction a given character's is, and how creation derives it
  from Drives and Misfortune) is out of scope — this feature only gives an existing field a
  mechanical read, not a new authoring procedure.
- "One tier worse" reuses the three tiers Exposure already names (minor 1, moderate 2, major 3);
  no new tier is introduced.
- The GM's alignment judgment is advisory prose, not a lookup table — consistent with how Drive
  invocation is already specified with no fixed keyword list.
