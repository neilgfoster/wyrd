# Feature Specification: Playtest minor-tier systems-of-power spam, the typical caster-in-an-encounter case

**Feature Branch**: `176-minor-tier-spam-playtest`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Add another playtest - the same systems of power, but with the player spamming minor tier instead of major - a typically situation for a magic focussed character in an encounter (closes #176, part of the playtest epic #134). §10/§14's major-tier spam sequence has strain_cost (8) exceeding a starting character's maximum Stamina (6), so ADR 0045's threshold crosses on nearly every failure at that tier -- check whether minor tier (strain_cost 2, well under maximum Stamina) behaves as originally intended with real play."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The Trauma threshold's rate at a realistic, non-maximal tier is checked with real play (Priority: P1)

A magic-focused character's typical encounter play is spamming their bread-and-butter *minor*
invocation repeatedly, not the most ambitious tier a schema allows. Someone wants to know whether
ADR 0045's threshold still behaves as "occasional crossings, not automatic" at that realistic
tier, or whether the major-tier near-certainty generalises.

**Why this priority**: The major-tier near-certainty was noticed in conversation after §14
landed, not checked against real play — this pass is that check.

**Independent Test**: Read the new section's per-attempt table and Findings; confirm the
crossing rate is computed from real rolls and compared directly against §10/§14's major-tier
figures.

**Acceptance Scenarios**:

1. **Given** a 26-attempt minor-tier spam sequence with real seeded rolls, **When** the failure
   and Trauma-crossing counts are tallied, **Then** the crossing rate is stated as a fraction of
   actual failures, not assumed from the arithmetic alone.
2. **Given** that rate, **When** compared to §10/§14's major-tier crossing rate, **Then** the
   pass states plainly whether the threshold behaves as intended (a materially lower rate) or
   shows the same degeneracy.

### Edge Cases

- Does this pass make a new design decision? No — it checks how the already-decided rule (ADR
  0045) performs at a different tier; it does not change it.
- Does this pass check moderate tier too? No — out of scope, stated explicitly as unproven by
  this pass rather than assumed to sit between the two endpoints.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A new section MUST be added to `docs/design/30-playtest-transcript.md` playing a
  26-attempt minor-tier spam sequence with real seeded rolls, matching the transcript's existing
  discipline (every attempt disclosed).
- **FR-002**: The section MUST state the fraction of actual failures that crossed the Trauma
  threshold, and compare it directly against §10/§14's major-tier figure.
- **FR-003**: The section MUST call out a more realistic single-encounter length (the first
  ~12 attempts) separately from the full 26, since 26 is chosen for direct comparison, not
  realism.
- **FR-004**: The section MUST NOT propose or make a new design decision, whatever the rate
  found.

### Key Entities

*(none — this feature is a playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section with a full 26-attempt
  minor-tier spam sequence, every roll traced to a real seeded draw.
- **SC-002**: The section states the minor-tier Trauma-crossing rate as a fraction of failures,
  contrasted explicitly against the major-tier rate from §10/§14.
- **SC-003**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (no new
  finding class), and `python3 -m pytest -q` pass.

## Assumptions

- Kester (the same character from §10/§14) is reused rather than inventing a new one, since the
  comparison is specifically against his own prior major-tier sequence.
- No new ADR — this is a confirmatory playtest pass, not a decision.
