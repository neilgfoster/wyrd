# Feature Specification: Brake on spamming a failing system-of-power invocation

**Feature Branch**: `163-systems-of-power-spam-brake`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Systems of power's cost structure doesn't discourage spamming failed high-tier invocations (closes #163, found during #151, playtest epic #134). Cost is paid identically win-or-lose, Strain fully resets at a Rally with no cap, and the only persistent cost (Ill Omen Taint) is skill/difficulty/retry-count independent, so a player loses nothing declaring the biggest tier and retrying it repeatedly until a Rally. Needs a real design decision. Operator direction, worked through iteratively: (1) tie Strain into causing Taint or Trauma so repeated failures have a real cost, resolved to Trauma; (2) a first same-power-failure-streak design was re-playtested and found defeated outright by a character rotating between two known systems of power (closes #172); (3) redirected to a Strain-threshold trigger, failure-only, with the threshold tied to an existing per-character stat rather than a fixed number -- resolved to the character's maximum Stamina, verified to be immune to the rotation exploit by construction since it never reads which power failed; (4) considered whether a setting could defeat the brake by overriding strain_cost to 0 (not possible, schema-enforced positive) or by disabling the Strain/Trauma tracks entirely (possible and accepted, matching the existing Taint-disable precedent -- stated explicitly rather than patched around)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Repeated failure has a real, persistent cost, scaled to the character (Priority: P1)

A player who fails system-of-power invocations repeatedly, in the same scene, should pay
something that survives the next Rally — sized to their own character, not an arbitrary
engine-wide number.

**Why this priority**: This is #163's own finding — 26 consecutive failed `major`-tier
invocations produced no consequence beyond a Strain total that vanished at the next Rally.

**Independent Test**: Read `03-rules.md` §5's Trauma-gain bullet and `09-systems-of-power.md`'s
cost section; confirm a stated, GM-followable rule ties a failed invocation crossing a multiple
of maximum Stamina to Trauma.

**Acceptance Scenarios**:

1. **Given** a failed invocation whose resulting Strain crosses a multiple of the character's
   maximum Stamina, **When** it resolves, **Then** it costs 1 Trauma per multiple crossed, with
   Strain carrying forward at its remainder.
2. **Given** a re-run of a comparable spam sequence to #151's playtest, **When** the new rule is
   applied at every realistic maximum-Stamina value, **Then** it produces real, non-zero Trauma
   (crossing the Affliction threshold) where the published rule produced none.

### User Story 2 - The brake cannot be defeated by rotating between known systems of power (Priority: P1)

A first design (a same-power failure streak) was found, by re-playtesting, to be defeated
outright by a character who knows two systems of power and alternates between them — identical
outcomes, zero Trauma (#172). The adopted design must not repeat that failure mode.

**Why this priority**: A brake a player can switch off by knowing two spells is not a brake; this
was found by direct re-playtest, not by inspection, and the fix needed a mechanism immune to it
by construction rather than a patched special case.

**Independent Test**: Read `check_spam_brake.py`'s rotation-immunity check; confirm an identical
roll sequence run as single-power spam and as two-power rotation produces identical Trauma.

**Acceptance Scenarios**:

1. **Given** an identical sequence of failed rolls, **When** run once against one system of power
   spammed and once against two systems of power alternated, **Then** both produce identical
   Trauma, at every maximum-Stamina value tested.

### User Story 3 - Ordinary and mostly-successful play are untouched (Priority: P1)

A character who tries a system of power a normal handful of times, or who mostly succeeds, should
not be punished as if spamming.

**Why this priority**: The operator's own stated intent — "repeated failures have a real cost" —
requires the brake to be failure-gated, not volume-gated; a naive any-outcome trigger was
considered and rejected specifically because it would also tax legitimate, mostly-successful use.

**Independent Test**: Read `check_spam_brake.py`'s ordinary-use and mixed-outcome checks; confirm
zero Trauma for isolated failure among successes, and strictly less Trauma under failure-only
gating than a naive any-outcome variant on identical rolls.

**Acceptance Scenarios**:

1. **Given** three invocations of the same power with only one isolated failure among them (the
   design document's own worked "ordinary use" sequence), **When** the new rule is applied,
   **Then** it costs zero additional Trauma.
2. **Given** a mostly-successful mixed-outcome sequence, **When** compared against a naive
   any-outcome variant on the same rolls, **Then** failure-only gating produces strictly less
   Trauma.

### Edge Cases

- Can a setting defeat the brake by declaring `strain_cost: 0`? No — the existing schema
  validator (`tools/check_power_systems.py`) already rejects a non-positive `strain_cost`.
- Can a setting defeat the brake by disabling the Strain and/or Trauma tracks entirely? Yes — both
  are already in the engine's published disable-able set (`24-authoring-a-setting.md`). This is
  accepted, not patched around: the brake states plainly that it applies no consequence when its
  feeding track(s) are disabled, mirroring the existing behaviour already stated for a
  Taint-disabled setting's Ill Omen consequence. Inventing a substitute consequence for a
  deliberately-disabled track would itself be a new mechanism (ADR 0036).
- Does the brake apply differently per intensity tier? No — a bigger `strain_cost` per attempt
  simply reaches the threshold sooner; no separate scaling rule is needed.
- Does this change Strain's own reset-at-a-Rally behaviour, or the Ill Omen consequence? No —
  both are unchanged; this composes alongside them.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `03-rules.md` §5 MUST state that a failed system-of-power invocation that pushes
  accumulated Strain past a multiple of the character's maximum Stamina costs 1 Trauma per
  multiple crossed.
- **FR-002**: A success that crosses the same multiple MUST cost nothing extra — the brake is
  failure-gated.
- **FR-003**: Strain MUST carry forward at its remainder past the last multiple crossed, not
  reset to zero outright.
- **FR-004**: `09-systems-of-power.md`'s cost section MUST state the rule where it modifies the
  existing win-or-lose cost text, cross-referencing `03-rules.md` §5, and MUST state the
  disabled-track degradation explicitly.
- **FR-005**: The fix MUST be verified against a re-run of a comparable spam sequence at every
  realistic maximum-Stamina value, confirming it changes the outcome (non-zero Trauma).
- **FR-006**: The fix MUST be verified immune to the two-power rotation exploit that defeated the
  first (superseded) design — identical Trauma for single-power spam and two-power rotation on
  identical rolls.
- **FR-007**: The fix MUST be verified not to fire on ordinary, non-spam play, and to produce
  strictly less Trauma under failure-only gating than a naive any-outcome variant on
  mostly-successful play.
- **FR-008**: A real, workable rejected alternative exists (the same-power-streak design; a flat
  engine-wide threshold; an any-outcome trigger; a disabled-track fallback), so this decision is
  recorded as an ADR, including the superseded first draft.

### Key Entities

*(none — this feature is a rules addition, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `03-rules.md` §5 and `09-systems-of-power.md` state the max-Stamina-threshold rule
  and its disabled-track degradation.
- **SC-002**: ADR 0045 records the decision, including the superseded same-power-streak first
  draft and the rejected flat-threshold, any-outcome, and disabled-track-fallback alternatives.
- **SC-003**: `specs/057-systems-of-power-spam-brake/check_spam_brake.py` proves the rule
  accrues real Trauma on a spam sequence (crossing the Affliction threshold) across the realistic
  maximum-Stamina range, is immune to the rotation exploit, and stays failure-gated on
  ordinary/mostly-successful play.
- **SC-004**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`, and
  `python3 -m pytest -q` pass.

## Assumptions

- Trauma, not Taint, is the track this brake feeds — Taint already has a dedicated
  systems-of-power channel (the Ill Omen consequence); Strain and Trauma are the engine's paired
  mental-harm tiers.
- Maximum Stamina, not current Stamina, is the modulus — stable and not subject to a perverse
  incentive to manipulate current Stamina via an unrelated subsystem (combat harm) to change the
  threshold.
- Documentation-only: no engine code changes; the verification script is a design artefact under
  `specs/`, matching this repo's established precedent.
