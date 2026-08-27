# Feature Specification: Brake on spamming a failing system-of-power invocation

**Feature Branch**: `163-systems-of-power-spam-brake`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Systems of power's cost structure doesn't discourage spamming failed high-tier invocations (closes #163, found during #151, playtest epic #134). Cost is paid identically win-or-lose, Strain fully resets at a Rally with no cap, and the only persistent cost (Ill Omen Taint) is skill/difficulty/retry-count independent, so a player loses nothing declaring the biggest tier and retrying it repeatedly until a Rally. Needs a real design decision. Operator direction: tie Strain into causing Taint or Trauma, so players can try if they want but repeated failures have a real cost."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Repeated failure of the same declaration has a real, persistent cost (Priority: P1)

A player who fails the same system-of-power invocation over and over, in the same scene, should
pay something that survives the next Rally — not just an unchanged Strain cost that resets away.

**Why this priority**: This is #163's own finding — 26 consecutive failed `major`-tier
invocations produced no consequence beyond a Strain total that vanished at the next Rally.

**Independent Test**: Read `03-rules.md` §5's Trauma-gain list and `09-systems-of-power.md`'s
cost section; confirm a stated, GM-followable rule ties repeated same-power failure to Trauma.

**Acceptance Scenarios**:

1. **Given** a character fails the same system of power twice in a row in one scene, **When** the
   second failure resolves, **Then** it costs 1 Trauma in addition to its stated Strain/Resolve
   cost.
2. **Given** a re-run of a comparable spam sequence to #151's playtest, **When** the new rule is
   applied, **Then** it produces real, non-zero Trauma where the published rule produced none —
   confirming the fix changes the outcome, not just the prose (#163's own acceptance criterion).

### User Story 2 - Ordinary, non-spam play is untouched (Priority: P1)

A character who tries a system of power a normal handful of times per session, and fails once
among successes, should not be punished as if spamming.

**Why this priority**: The operator's own direction — "players can try if they want" — requires
the brake not fire on ordinary use, only on genuine repetition of the same failing declaration.

**Independent Test**: Read the re-run's ordinary-use check; confirm it costs zero Trauma under
the new rule.

**Acceptance Scenarios**:

1. **Given** three invocations of the same power with only one isolated failure among them (the
   design document's own worked "ordinary use" sequence), **When** the new rule is applied,
   **Then** it costs zero additional Trauma.

### Edge Cases

- Does the brake fire on a failure of a *different* system of power right after a failure of
  another? No — the streak is scoped to the same declared system of power; a different power's
  failure starts its own streak, and does not extend the first power's.
- Does the brake apply differently per intensity tier? No — the rule is one flat 1 Trauma per
  consecutive same-power failure, not scaled by `cost_multiplier`; the tier's own multiplier
  already prices ambition on the Strain/Taint side.
- Does this change Strain's own reset-at-a-Rally behaviour, or the Ill Omen consequence? No —
  both are unchanged; this composes alongside them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `03-rules.md` §5 MUST state that a failed system-of-power invocation immediately
  following another failed invocation of the same system of power, in the same scene, costs 1
  Trauma.
- **FR-002**: The first failure of a scene MUST cost nothing extra; a success, or a failure of a
  *different* system of power, MUST reset the streak.
- **FR-003**: `09-systems-of-power.md`'s cost section MUST state the rule where it modifies the
  existing win-or-lose cost text, cross-referencing `03-rules.md` §5.
- **FR-004**: The fix MUST be verified against a re-run of a comparable spam sequence, confirming
  it changes the outcome (non-zero Trauma) rather than only the prose.
- **FR-005**: The fix MUST be verified not to fire on ordinary, non-spam play (an isolated failure
  among successes).
- **FR-006**: A real, workable rejected alternative exists (a Strain cap/threshold; an escalating
  retry cost), so this decision is recorded as an ADR.

### Key Entities

*(none — this feature is a rules addition, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `03-rules.md` §5 and `09-systems-of-power.md` state the new rule.
- **SC-002**: A new ADR records the decision, including the rejected Strain-cap and
  escalating-cost alternatives.
- **SC-003**: `specs/057-systems-of-power-spam-brake/check_spam_brake.py` proves the rule accrues
  real Trauma on a spam sequence (crossing the Affliction threshold) and zero Trauma on ordinary
  play.
- **SC-004**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
  `python3 -m pytest -q` pass.

## Assumptions

- Trauma, not Taint, is the track this brake feeds — Taint already has a dedicated
  systems-of-power channel (the Ill Omen consequence); Strain and Trauma are already the engine's
  two paired mental-harm tiers.
- Documentation-only: no engine code changes; the verification script is a design artefact under
  `specs/`, matching this repo's established precedent.
