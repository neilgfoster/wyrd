# Feature Specification: Systems of power resolution

**Feature Branch**: `107-systems-of-power`

**Created**: 2026-09-08

**Status**: Draft

**Input**: User description: "Systems of power: engine support — resolution wiring for invoking a
declared system of power (docs/design/09-systems-of-power.md): a d100 test against the setting's
skill, failure-only Strain/Resolve cost, requires_training gating the untrained attempt,
intensity-tier cost/Taint scaling, the Strain-threshold-crossing Trauma check (ADR 0047), and Ill
Omen feeding the existing Taint-accrual/transformation path. Issue #286."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Invoking a plain system of power (Priority: P1)

A player whose character knows a declared system of power (e.g. Ember-craft) attempts to use it.
The engine resolves it as an ordinary test against the character's skill in that system. On
success, nothing is paid. On failure, the declared Strain cost (and Resolve cost, if any) is
applied.

**Why this priority**: This is the mechanism's baseline behaviour — every other rule in this
feature is a modifier layered on top of this one resolution path. Nothing else works without it.

**Independent Test**: Load a setting declaring one untiered system of power with only
`strain_cost`, resolve a failed invocation, and confirm Strain rose by exactly the declared amount
and nothing else changed; resolve a successful invocation and confirm neither Strain nor Resolve
changed.

**Acceptance Scenarios**:

1. **Given** a character with a declared system of power and a failing roll, **When** the
   invocation resolves, **Then** the character's Strain increases by the system's declared
   `strain_cost` and, if declared, Resolve decreases by `resolve_cost`.
2. **Given** the same setup with a succeeding roll instead, **When** the invocation resolves,
   **Then** neither Strain nor Resolve changes.
3. **Given** a system of power with `requires_training: true` and a character with no training in
   its skill, **When** an invocation is attempted, **Then** the engine rejects the attempt outright
   rather than resolving an untrained roll.

---

### User Story 2 - Ambition scales the stakes (Priority: P2)

A player wants a working's outcome to matter more when they attempt something larger. Declaring
an invocation at a higher intensity tier raises both the difficulty the GM sets and, on failure,
the cost paid and the Taint risked — without introducing any new roll or table.

**Why this priority**: Intensity tiers are how the design closes the "ambition costs nothing extra
if it goes wrong" gap; it is a real, separately-testable slice on top of the P1 baseline, but a
setting need not declare tiers at all for the mechanism to work.

**Independent Test**: Load a setting declaring one system of power with `intensity_tiers`
(minor/moderate/major, per the design doc's worked example), resolve a failed invocation declared
at each tier, and confirm the paid cost and the Taint applied on an Ill Omen both scale by that
tier's multiplier/bonus while the base (untiered) figures are unaffected when no tier is declared.

**Acceptance Scenarios**:

1. **Given** a system of power with `intensity_tiers` and a failed invocation declared at a tier
   with `cost_multiplier: 4`, **When** the invocation resolves, **Then** the applied Strain/Resolve
   cost is the system's base cost multiplied by 4.
2. **Given** the same system and a natural roll reading Ill Omen at a tier with
   `ill_omen_taint_bonus: 3`, **When** the invocation resolves, **Then** the Taint applied is the
   system's base `ill_omen_taint` plus 3.
3. **Given** a system of power with no `intensity_tiers` declared, **When** any invocation
   resolves, **Then** cost and Ill Omen Taint are exactly the system's base declared values, with
   no scaling applied.

---

### User Story 3 - Consequences that accumulate (Priority: P3)

A character who keeps failing invocations of a system of power — whether the same one or several
different ones — is at growing risk: enough accumulated Strain crosses into Trauma, and an Ill
Omen on the roll risks a lasting transformation, exactly as any other Taint-feeding event already
does.

**Why this priority**: This closes the loop into the engine's existing consequence machinery
(Trauma, Taint accrual, the transformation table) — necessary for the feature to be complete, but
it reuses existing engine paths rather than introducing new ones, and is naturally tested last
since it depends on the invocation resolution from User Story 1 already working.

**Independent Test**: Resolve a sequence of failed invocations that pushes a character's
cumulative Strain across a multiple of their maximum Stamina, and confirm Trauma is applied
exactly once per multiple crossed, using the character's total accumulated Strain rather than a
delta scoped to one invocation; separately, resolve an invocation whose natural roll reads Ill
Omen and confirm the resulting Taint gain routes through the same accrual path other Taint sources
use, including triggering a transformation roll when a threshold is crossed.

**Acceptance Scenarios**:

1. **Given** a character whose accumulated Strain, after a failed invocation, crosses one or more
   multiples of their maximum Stamina, **When** the invocation resolves, **Then** Trauma is applied
   using `(strain − 1) // max_stamina` read against the cumulative total, not a before/after delta
   scoped to that one invocation.
2. **Given** a character retrying the same system of power after a prior failure left Strain just
   under a Stamina multiple, and a character rotating between two different systems of power
   reaching the same cumulative Strain, **When** each next failure crosses the multiple, **Then**
   both apply Trauma identically — the check depends only on total Strain and maximum Stamina, not
   which system of power produced the failure.
3. **Given** any invocation (win or lose) whose natural roll's units digit reads Ill Omen, **When**
   it resolves, **Then** the system's declared `ill_omen_taint` (plus any tier bonus) is applied
   through the existing Taint-accrual path, and a transformation-table roll follows immediately
   if that gain crosses a threshold.
4. **Given** a setting that has disabled Strain and/or Trauma, or disabled Taint, **When** an
   invocation would otherwise apply the disabled track's consequence, **Then** that consequence is
   skipped entirely rather than substituted with anything else, while the base d100 resolution and
   any still-enabled cost fields are unaffected.

### Edge Cases

- What happens when a system of power declares `requires_training: false` and an untrained
  character attempts it? The standard untrained-10% rule applies — the invocation resolves exactly
  like any other untrained skill test, with no power-specific exception.
- What happens when an invocation is declared at an intensity tier but the setting's
  `intensity_tiers` list doesn't include that label? The invocation is rejected as an invalid
  declaration — there is no fallback tier to guess at.
- What happens when a success occurs at a natural roll reading Ill Omen? The Ill Omen consequence
  still applies (it is read from the Wyrd die on any roll, win or lose) even though the cost
  fields, which apply only on failure, are skipped.
- What happens when a character has no Resolve field/track available (e.g. an adversary or a
  setting without Resolve)? Only the fields the system declares and the character's sheet actually
  carries are applied; nothing is invented for a track that doesn't exist there.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST resolve an invocation of a declared system of power as an ordinary
  test against the character's skill in the system's declared `skill`, using the same core roll,
  degree-of-success, and Wyrd-die reading already used for every other test.
- **FR-002**: The engine MUST reject an invocation attempt outright, with no roll, when the
  system's `requires_training: true` and the character has no training in its skill.
- **FR-003**: On a failed invocation, the engine MUST apply the system's declared `strain_cost` to
  the character's Strain and, if declared, `resolve_cost` to Resolve; on a successful invocation,
  the engine MUST apply neither.
- **FR-004**: When the invocation is declared at one of the system's `intensity_tiers`, the engine
  MUST multiply the applied `strain_cost`/`resolve_cost` by that tier's `cost_multiplier` before
  applying FR-003, and MUST add that tier's `ill_omen_taint_bonus` to the base `ill_omen_taint`
  before applying FR-006.
- **FR-005**: After applying a failure's cost, the engine MUST check the character's total,
  cumulative Strain against their maximum Stamina using `(strain − 1) // max_stamina`, and apply
  that many further Trauma gains — read from the cumulative total each time, not a before/after
  delta scoped to the one invocation that just resolved.
- **FR-006**: On any invocation whose natural roll reads Ill Omen, win or lose, the engine MUST
  apply the system's declared `ill_omen_taint` (plus any tier bonus per FR-004) through the
  engine's existing Taint-accrual path, and MUST trigger a transformation-table roll if that gain
  crosses a threshold — reusing the existing transformation chain rather than a power-specific one.
- **FR-007**: When the acting setting has disabled Strain and/or Trauma (`overrides.disable`), the
  engine MUST skip FR-003's cost and FR-005's Trauma check entirely rather than substituting any
  other consequence.
- **FR-008**: When the acting setting has disabled Taint, the engine MUST skip FR-006's
  Taint-accrual application entirely, while still resolving the base roll and any still-enabled
  cost fields.
- **FR-009**: The engine MUST NOT introduce a second dice mechanic, a second table, or any
  power-specific consequence chain — every rule above composes with the engine's existing
  resolution, Strain/Resolve, Taint-accrual, and transformation machinery unchanged.

### Key Entities

- **System of power**: A setting-declared configuration (`id`, `name`, `skill`, `strain_cost`,
  `requires_training`, optionally `resolve_cost`, `ill_omen_taint`, `description`,
  `intensity_tiers`) already validated by the existing schema checker; this feature is what makes
  an invocation of one actually resolve at runtime.
- **Intensity tier**: A named point within a system of power's optional `intensity_tiers` list
  (`label`, `difficulty`, `cost_multiplier`, `ill_omen_taint_bonus`) that a player declares when
  invoking, scaling that one invocation's stakes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both worked examples from the design document (Ember-craft with tiers,
  Signal-attunement without) resolve through the engine exactly as their narrated worked-example
  outcomes describe, verified by automated tests.
- **SC-002**: 100% of the acceptance scenarios above pass as automated tests before this feature is
  considered complete.
- **SC-003**: A setting author can add a wholly new system of power to `power.yaml` and have it
  resolve correctly with zero engine code changes — confirming the mechanism is genuinely
  data-driven, not hard-coded per system.

## Assumptions

- The engine already exposes the primitives this feature composes: a core d100 test resolver, a
  Strain/Resolve track, a Taint-accrual path, a transformation-table roll, and an
  `overrides.disable` mechanism for Strain/Trauma/Taint — this feature wires a new entry point into
  them, it does not build any of them from scratch.
- `tools/check_power_systems.py` already validates that a setting's declared systems of power
  conform to the schema before this feature's resolution path ever sees them; this feature assumes
  well-formed input and is not responsible for re-validating schema shape at resolution time.
- "Character" throughout includes any entity the resolution engine already treats as capable of
  testing a skill (a player character or, where a setting allows it, an adversary/companion) —
  this feature does not restrict systems of power to player characters specifically, since the
  design document does not either.
