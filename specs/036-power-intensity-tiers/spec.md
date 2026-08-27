# Feature Specification: Optional intensity tiers for a system of power

**Feature Branch**: `036-power-intensity-tiers`

**Created**: 2026-08-26

**Status**: Draft

**Input**: User description: "Decide whether a system of power's cost scales with narrative intensity (issue #119)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A setting author declares tiered stakes for a system of power (Priority: P1)

A setting author writing `power.yaml` wants "I warm myself against the chill" and "I burn the
entire city down" to carry different stakes when both are framed as the same system of power.
Today the schema only lets them declare one flat `strain_cost` and one flat `ill_omen_taint`,
so every invocation of that system costs and risks the same regardless of what was attempted.

**Why this priority**: This is the entire feature — without it, nothing changes about how a
system of power behaves, and the loophole the issue raised stays open.

**Independent Test**: Write a `power.yaml` declaring one system of power with an
`intensity_tiers` list of three tiers (minor/moderate/major, each with a distinct
`cost_multiplier` and `ill_omen_taint_bonus`), validate it with `check_power_systems.py`, and
confirm it passes.

**Acceptance Scenarios**:

1. **Given** a system of power with `intensity_tiers` declared, **When** an invocation is
   resolved at a stated tier, **Then** the cost paid is the system's base `strain_cost`/
   `resolve_cost` multiplied by that tier's `cost_multiplier`, and an Ill Omen's Taint gain is
   the base `ill_omen_taint` plus that tier's `ill_omen_taint_bonus`.
2. **Given** a system of power with `intensity_tiers` declared, **When** a tier's `difficulty`
   is read, **Then** it names one of the engine's existing six difficulty-ladder rungs, and the
   GM may still override it from the fiction exactly as any other difficulty.

---

### User Story 2 - A setting author who doesn't need tiers is unaffected (Priority: P1)

A setting author who is happy with the existing flat-cost behaviour declares a system of power
with no `intensity_tiers` field at all, and nothing about how it resolves or validates changes.

**Why this priority**: The issue's own acceptance criteria require this to be additive, not a
breaking change — every setting with a `power.yaml` today must keep validating and resolving
exactly as before.

**Independent Test**: Validate an existing `power.yaml` with no `intensity_tiers` field against
the updated `check_power_systems.py` and confirm it still passes with no new errors or warnings.

**Acceptance Scenarios**:

1. **Given** a system of power with no `intensity_tiers` field, **When** it is validated,
   **Then** validation behaves identically to before this feature existed.
2. **Given** a system of power with no `intensity_tiers` field, **When** it is invoked,
   **Then** cost and Ill Omen Taint gain are exactly the base `strain_cost`/`resolve_cost`/
   `ill_omen_taint` values, unmodified.

---

### User Story 3 - A malformed tier declaration is rejected (Priority: P2)

A setting author makes a mistake authoring a tier — an unrecognised difficulty label, a
non-positive cost multiplier, a negative Taint bonus, or a tier missing its label — and finds
out at validation time rather than at the table.

**Why this priority**: Catches authoring mistakes before they reach play, consistent with how
`check_power_systems.py` already rejects a missing required field or a non-positive base cost.

**Independent Test**: Write a `power.yaml` with one deliberately malformed tier per malformation
type (bad difficulty label, non-positive `cost_multiplier`, negative `ill_omen_taint_bonus`,
missing `label`) and confirm `check_power_systems.py` rejects each with a clear error.

**Acceptance Scenarios**:

1. **Given** a tier whose `difficulty` is not one of the six recognised rungs, **When**
   validated, **Then** validation fails with an error naming the tier and the invalid value.
2. **Given** a tier whose `cost_multiplier` is zero or negative, **When** validated, **Then**
   validation fails with an error naming the tier.
3. **Given** a tier whose `ill_omen_taint_bonus` is negative, **When** validated, **Then**
   validation fails with an error naming the tier.
4. **Given** a tier with no `label`, **When** validated, **Then** validation fails with an error
   naming the system of power and the tier's position in the list.

---

### Edge Cases

- What happens when a system of power declares `intensity_tiers` as an empty list? Treated the
  same as omitting the field entirely — no tiers means the base flat behaviour applies. (An
  empty list is not itself malformed; it simply declares nothing.)
- What happens when only `resolve_cost` is declared (no base `resolve_cost` — some systems draw
  on Strain alone, per the existing worked examples)? A tier's `cost_multiplier` only has
  anything to multiply where the corresponding base cost is declared; there is nothing to scale
  on a cost the system never charges.
- What happens when two tiers share the same `label`? Not restricted by this feature — labels
  are free text for the GM/player to reference at the table, and duplicate labels are a setting
  authoring choice, not a validation concern this feature takes on.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The systems-of-power schema MUST support an optional `intensity_tiers` field on a
  system of power, as a list of zero or more tiers.
- **FR-002**: Each declared tier MUST specify a `label` (free text, required), a `difficulty`
  (one of the engine's six difficulty-ladder rungs), a `cost_multiplier` (a positive number), and
  an `ill_omen_taint_bonus` (a non-negative integer).
- **FR-003**: A system of power with no `intensity_tiers` field MUST resolve and validate
  identically to how it does today — this field is purely additive.
- **FR-004**: `docs/design/09-systems-of-power.md` MUST document `intensity_tiers` as an
  optional field, including a worked example showing a tiered invocation and how
  `cost_multiplier`/`ill_omen_taint_bonus` apply at resolution.
- **FR-005**: `tools/check_power_systems.py` MUST validate `intensity_tiers` when present: reject
  a tier with an unrecognised `difficulty` label, a non-positive `cost_multiplier`, a negative
  `ill_omen_taint_bonus`, or a missing `label`.
- **FR-006**: `tools/check_power_systems.py` MUST continue to validate a `power.yaml` with no
  `intensity_tiers` field exactly as it did before this feature (no regression for existing
  setting data).
- **FR-007**: The documented resolution rule MUST state that at an invocation declared at a
  given tier, the cost paid is the system's base `strain_cost`/`resolve_cost` multiplied by that
  tier's `cost_multiplier`, and an Ill Omen's Taint gain is the base `ill_omen_taint` plus that
  tier's `ill_omen_taint_bonus` — both still paid/applied exactly per the existing win-or-lose
  and Taint-accrual rules, never a new resolution path.
- **FR-008**: This feature MUST NOT change the existing required/default semantics of
  `strain_cost`, `resolve_cost`, or `ill_omen_taint` — `intensity_tiers` composes with them, it
  does not replace them.

*Out of scope*: whether a character is discouraged from always reaching for a power skill over a
mundane one in general. That pressure is already governed by Strain's Rally-gated scarcity and by
a character's skill points being zero-sum across a career build, and is orthogonal to whether
cost scales with declared intensity within a single invocation — this feature does not add
anything addressing it.

### Key Entities

- **Intensity tier**: an optional, named point a system of power can declare, carrying a
  difficulty rung, a cost multiplier, and an Ill Omen Taint bonus. Declared once per setting
  (in `power.yaml`), referenced at the table when a player/GM frames an invocation at that tier.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A setting author can express three-tiered stakes (e.g. minor/moderate/major) for
  one system of power using only fields this feature adds, with no change to any other system of
  power's declaration.
- **SC-002**: Every existing `power.yaml` in the repository continues to validate cleanly with no
  changes required to it.
- **SC-003**: A malformed tier of each of the four kinds in User Story 3 is rejected at
  validation time, with an error that names which system of power and which tier is at fault.
- **SC-004**: `docs/design/09-systems-of-power.md` states, in prose a reader can act on without
  consulting anything else, that `intensity_tiers` is optional and does not require any existing
  declared system of power to change.

## Assumptions

- The "six difficulty-ladder rungs" are exactly the six named in
  `docs/design/03-rules.md` §1 (Easy, Average, Challenging, Difficult, Hard, Very Hard); this
  feature introduces no new difficulty scale.
- `cost_multiplier` and `ill_omen_taint_bonus` are declared once per tier and apply uniformly —
  there is no per-invocation negotiation of these numbers beyond choosing which declared tier
  applies.
- Choosing which tier an invocation is framed at is a declaration made at the table (by the
  player, subject to the GM's usual authority over plausibility), the same way any other
  declaration specificity is — this feature does not define a new procedural step for choosing a
  tier, it only defines what a tier is and how it modifies resolution once chosen.
- No existing `power.yaml` in this repository currently declares `intensity_tiers` (the field is
  new), so SC-002 is satisfiable by construction.
