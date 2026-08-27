# Feature Specification: Fix the Strain-threshold check so a success cannot erase a Trauma crossing

**Feature Branch**: `178-strain-threshold-catchup-fix`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "new feature, new adr, new playtest to prove, all in the same PR (closes #178). ADR 0045's crossing check compares before/after Strain scoped to one failed invocation; if a success carries Strain past a multiple of maximum Stamina, no failure will ever be charged for that boundary. Fix the check to read cumulative Strain, write a superseding ADR, and correct the sec10/sec14/sec15 playtest figures with real rolls."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A failure always pays for every multiple of maximum Stamina currently outstanding, not just the one it happened to straddle (Priority: P1)

A character who racks up Strain mostly through successes, then finally fails, should pay for the
full backlog — not just whatever fraction of it their own failing roll happened to cross.

**Why this priority**: This is the actual bug #178 found — §15's own attempt 26 failed at 6.3×
maximum Stamina and cost zero Trauma, because the boundary had already been passed for free by
an earlier success.

**Independent Test**: Read ADR 0047 and `check_spam_brake.py`'s new `compare_edge_vs_cumulative`
check; confirm the corrected check never gives less Trauma than the superseded one on the same
rolls, and gives strictly more on the two sequences that found the bug.

**Acceptance Scenarios**:

1. **Given** a run of successes that carries Strain past one or more multiples of maximum
   Stamina, **When** a failure eventually occurs, **Then** it is charged for every multiple
   currently outstanding, not only the span since its own immediately-prior roll.
2. **Given** the exact roll sequences that produced §10/§14's major-tier and §15's minor-tier
   figures, **When** replayed under the corrected check, **Then** both produce real, verifiably
   higher Trauma totals than the superseded check gave on the same rolls.

### User Story 2 - A success still never directly costs Trauma (Priority: P1)

The fix must not turn this into an any-outcome check — a success still costs nothing extra at
the moment it is rolled; only a failure can trigger a charge.

**Why this priority**: This was always the design's stated intent (ADR 0045's own text); the fix
corrects when a failure catches up, not whether a success can itself trigger a charge.

**Independent Test**: Read `check_spam_brake.py`'s consecutive-successes check; confirm Trauma
stays exactly 0 through an arbitrarily long run of successes alone.

**Acceptance Scenarios**:

1. **Given** 26 (and separately 50) consecutive successes with a Strain cost that would cross
   several multiples of maximum Stamina, **When** no failure ever occurs, **Then** Trauma stays
   at 0 throughout.

### Edge Cases

- Does the fix change failure-only gating, the maximum-Stamina modulus, the remainder-carry
  shape, or the disabled-track degradation? No — only how the crossing is detected changes; ADR
  0047 states explicitly what carries over unchanged from ADR 0045.
- Does this edit §10/§14/§15's original text? No — a new §16 states the corrected figures,
  cross-referencing them, per this repo's own convention for a historical record.
- Is ADR 0045 edited in place? No — it is Accepted and merged; a new ADR (0047) supersedes it,
  and 0045 moves to `docs/adr/superseded/` per ADR 0012's convention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The Trauma check on a failed invocation MUST read the character's current,
  cumulative Strain against the maximum-Stamina modulus, not a before/after delta scoped to one
  invocation.
- **FR-002**: A run of successes alone, however long, MUST NOT directly cost Trauma.
- **FR-003**: The first failure following a run of successes MUST be charged for every multiple
  of maximum Stamina currently outstanding, not only a multiple its own increment straddles.
- **FR-004**: ADR 0045 MUST be superseded (moved to `docs/adr/superseded/`, `Status:` line
  updated), not edited in place, per this repo's own ADR convention.
- **FR-005**: `03-rules.md` and `09-systems-of-power.md` MUST restate the rule under the
  corrected check, cross-referencing ADR 0047.
- **FR-006**: `check_spam_brake.py` MUST demonstrate, on the exact roll sequences that found the
  bug (§10/§14's major tier, §15's minor tier), that the corrected check gives strictly more
  Trauma than the superseded one.
- **FR-007**: §10/§14/§15's original playtest text MUST NOT be edited; a new section states the
  corrected figures.

### Key Entities

*(none — this feature is a rules correction plus a playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: ADR 0047 supersedes ADR 0045, stating the corrected check and what is unchanged
  from it.
- **SC-002**: `check_spam_brake.py`'s full assertion suite (real Trauma on spam, zero on ordinary
  play, rotation-immunity, failure-gating, and the new edge-vs-cumulative comparison) passes.
- **SC-003**: A new section in `docs/design/30-playtest-transcript.md` states the corrected
  §10/§14/§15 figures with real seeded rolls, without editing the originals.
- **SC-004**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (no new
  finding class beyond the already-accepted Omen pattern), and `python3 -m pytest -q` pass.

## Assumptions

- Reuses the exact seeds already on record for §10/§14 (`20260842`) and §15 (`20260850`), so the
  corrected figures are directly comparable to the ones the bug produced, not a fresh, unrelated
  sample.
- Documentation-only: no engine code changes.
