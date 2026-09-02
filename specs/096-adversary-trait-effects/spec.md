# Feature Specification: Adversary trait effects

**Feature Branch**: `096-adversary-trait-effects`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Adversary trait effects (issue #261): apply an adversary's active
traits to the mechanism each names -- difficulty (shift a named class of test's difficulty in
ladder rungs), damage (add/remove damage dice), damage_type (fix the damage type), stamina_max/
armour_rank (raise/lower those block values), wyrd (widen the Ill Omen/Fair Omen band). Only the
six named effects are supported; nothing beyond the closed vocabulary is invented."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A stamina_max or armour_rank trait retunes the block's own values (Priority: P1)

An adversary's block declares a `stamina_max` or `armour_rank` trait. Something asking for that
adversary's effective Stamina ceiling or armour rank gets the block's base value adjusted by
every such trait, not the raw, undertuned value the bestiary entry alone declares.

**Why this priority**: these are the two effects that retune values already read directly off
the block elsewhere (combat's Stamina/armour checks), so they're the most immediately
load-bearing for anything else that reads an adversary's block.

**Independent Test**: given a block with one `stamina_max: +2` trait, the effective Stamina
ceiling is the block's own `stamina_max` plus 2; given an `armour_rank: -1` trait, the effective
armour rank is one rank below the block's own `armour`.

**Acceptance Scenarios**:

1. **Given** a block with `stamina_max: 7` and a trait `{stamina_max: 2}`, **When** the engine
   computes the effective block, **Then** its Stamina ceiling is 9.
2. **Given** a block with `armour: "modest"` and a trait `{armour_rank: -1}`, **When** the engine
   computes the effective block, **Then** its armour rank is one below modest (light).
3. **Given** a block with `armour: "none"` and a trait `{armour_rank: -1}` (already at the
   floor), **When** the engine computes the effective block, **Then** its armour rank stays
   `none` -- it does not go negative or error.

---

### User Story 2 - A damage or damage_type trait retunes this opponent's blows (Priority: P1)

An adversary's block declares a `damage` trait (adjusting dice count) or a `damage_type` trait
(fixing which critical table a landed blow reads). Something building this opponent's attack
gets the adjusted dice expression and/or the overridden damage type.

**Why this priority**: equally load-bearing as User Story 1 -- both are read at the same moment
(building a combat-attack request) that already exists in `resolution.py`.

**Independent Test**: given a block with `damage: "1d6"` and a trait `{damage: 1}`, the effective
damage expression carries one more die (`2d6`); given a `damage_type` trait, the effective
damage type is the trait's value, not the block's own declared type.

**Acceptance Scenarios**:

1. **Given** a block with `damage: "1d6"` and a trait `{damage: 1}`, **When** the engine computes
   the effective block, **Then** its damage expression is `2d6`.
2. **Given** a block with `damage: "2d6"` and a trait `{damage: -1}`, **When** the engine computes
   the effective block, **Then** its damage expression is `1d6`.
3. **Given** a block with `damage: "1d6"` and a trait `{damage: -1}` (already at one die),
   **When** the engine computes the effective block, **Then** its damage expression stays `1d6`
   -- dice count never drops below one.
4. **Given** a block with `damage_type: "slashing"` and a trait `{damage_type: "searing"}`,
   **When** the engine computes the effective block, **Then** its damage type is `searing`.

---

### User Story 3 - A difficulty trait shifts a test's difficulty by ladder rungs (Priority: P2)

An adversary's block declares a `difficulty` trait. A caller resolving some test against this
adversary (the class of test the trait's own display name and the fiction identify -- this
feature does not itself decide which test a `difficulty` trait applies to) shifts a starting
difficulty step by the trait's stated number of rungs along the existing ladder
(`easy`/`average`/`challenging`/`difficult`/`hard`/`very_hard`), clamped at either end.

**Why this priority**: load-bearing wherever a difficulty step needs adjusting against this
adversary, but -- unlike Stories 1-2 -- there is no single existing read site this feature must
wire into; it is a pure ladder-stepping utility a caller applies at whatever point the fiction
calls for it.

**Independent Test**: given a starting difficulty of `average` and a trait `{difficulty: -1}`,
shifting yields `challenging`; a trait pushing past either end of the ladder clamps rather than
raising an error.

**Acceptance Scenarios**:

1. **Given** a starting difficulty `average` and one trait `{difficulty: -1}`, **When** the
   engine shifts it, **Then** the result is `challenging`.
2. **Given** a starting difficulty `very_hard` and a trait `{difficulty: -1}` (already at the
   ladder's hard end), **When** the engine shifts it, **Then** the result stays `very_hard`.
3. **Given** a starting difficulty `easy` and a trait `{difficulty: 1}` (already at the ladder's
   easy end), **When** the engine shifts it, **Then** the result stays `easy`.

---

### User Story 4 - A wyrd trait widens the Ill/Fair Omen band (Priority: P3)

An adversary's block declares a `wyrd` trait. A test against this adversary reads its Wyrd die
from a wider band of the roll's units digit than the default single value at each end.

**Why this priority**: the most narrowly-scoped of the six effects -- it touches one existing
pure function (`rules._wyrd_die`), and unlike Stories 1-2 it needs one small, additive,
backward-compatible parameter on an existing player-facing function rather than a new
adversary-side computation alone.

**Independent Test**: with the band widened by 1, a roll ending in units digit 1 now also reads
as an Ill Omen (in addition to the existing units-digit-0 case), and a roll ending in 8 also
reads as a Fair Omen (in addition to 9).

**Acceptance Scenarios**:

1. **Given** a Wyrd-die read with width 0 (no widening), **When** a roll's units digit is 0 or 9,
   **Then** it reads `ill_omen`/`fair_omen` exactly as before this feature.
2. **Given** a Wyrd-die read with width 1, **When** a roll's units digit is 0 or 1, **Then** both
   read `ill_omen`; when it is 8 or 9, both read `fair_omen`.

---

### User Story 5 - Multiple traits of the same kind all apply (Priority: P2)

An adversary carries more than one trait naming the same effect (e.g. two separate `stamina_max`
traits, from two different named properties). Both apply -- stacked (summed), not just the
larger or the first one read.

**Why this priority**: the issue's own acceptance criteria name this explicitly ("Multiple
traits on one adversary all apply") as a distinct correctness requirement, mirroring the same
stacking rule the recurring-wound combat-start feature (#254) already established for a
different mechanism.

**Independent Test**: a block with two `stamina_max` traits (`+1` and `+2`) yields an effective
Stamina ceiling three above the block's base value.

**Acceptance Scenarios**:

1. **Given** a block with two traits `{stamina_max: 1}` and `{stamina_max: 2}`, **When** the
   engine computes the effective block, **Then** its Stamina ceiling is the base plus 3.

### Edge Cases

- A block with no `traits` at all: every computation in this feature returns the block's own
  unmodified values (or, for the ladder-shift/band-width utilities, a zero shift/zero width).
- A block whose `traits` list is validated at load time (#259) to hold only the closed six
  effect keys -- this feature never has to reject an unrecognised effect itself; that already
  happened before the block reached here.
- A `damage` trait on a block that declares no `damage` at all (an opponent with no attack):
  the trait's delta is simply not applied to anything -- there is no dice expression to adjust.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST compute an adversary's effective `stamina_max` as its block's own
  value plus the sum of every active `stamina_max` trait effect, never below the block schema's
  minimum.
- **FR-002**: The engine MUST compute an adversary's effective armour rank as its block's own
  `armour` rank shifted along the closed rank order (`none`/`light`/`modest`/`heavy`) by the sum
  of every active `armour_rank` trait effect, clamped at either end.
- **FR-003**: The engine MUST compute an adversary's effective damage expression as its block's
  own `damage` dice count adjusted by the sum of every active `damage` trait effect, never below
  one die, preserving the die size and any flat modifier unchanged.
- **FR-004**: The engine MUST compute an adversary's effective damage type as the value of its
  last active `damage_type` trait, when one is present, overriding the block's own declared
  `damage_type`.
- **FR-005**: The engine MUST provide a way to shift a named difficulty step along the existing
  ladder by a given number of rungs (the sum of every active `difficulty` trait effect),
  clamping at either end of the ladder rather than raising an error.
- **FR-006**: The engine MUST provide a way to read the Wyrd die from a roll with the Ill/Fair
  Omen band widened by a given width (the sum of every active `wyrd` trait effect), where width
  0 reproduces exactly today's behavior.
- **FR-007**: Every computation in this feature MUST stack (sum) multiple traits naming the same
  effect, rather than applying only one.
- **FR-008**: Nothing in this feature introduces a mechanism beyond the six effects already
  named in the closed trait vocabulary (docs/design/12-the-adversary.md section 5) -- no new
  trait-effect key is added.

### Key Entities

- **Adversary block**: the loaded, validated shape #259 produces, including its `traits` list.
  This feature reads `traits` and the fields each effect retunes (`stamina_max`, `armour`,
  `damage`, `damage_type`); it does not change how the block is loaded or validated.
- **Effective block**: a new, computed shape this feature produces -- the adversary block with
  `stamina_max`/`armour`/`damage`/`damage_type` folded in from its active traits. Not persisted;
  computed fresh from the loaded block each time it's needed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For any adversary block carrying `stamina_max`/`armour_rank`/`damage`/
  `damage_type` traits (singly or stacked), the effective block's corresponding value matches
  the block's own value adjusted by the trait(s), for every combination tested.
- **SC-002**: A difficulty step shifted by any rung count, including one that would overshoot
  either end of the ladder, always returns a valid step name -- never an error, never a step
  outside the six named ones.
- **SC-003**: Reading the Wyrd die at width 0 is observably identical to today's unwidened
  behavior for every units digit 0-9 -- no existing caller's behavior changes by this feature
  landing.

## Assumptions

- Which specific test a `difficulty` trait's rungs apply to is decided by the trait's own
  display name and the fiction at the table (docs/design/12-the-adversary.md section 5: "a
  named class of test") -- not something the engine infers mechanically from the trait's data.
  This feature's job is the ladder-stepping utility itself, applied by whichever caller decides
  a `difficulty` trait is in play for the test at hand; it does not wire every existing
  difficulty-selecting call site (e.g. combat's ranged-attack difficulty) to consult it
  automatically, since none of those call sites currently accept "the opponent's traits" as an
  input and adding that plumbing to each is a larger, separate concern than this feature's own
  acceptance criteria describe.
- The Wyrd-die band-widening mechanism (FR-006) is added as a new, optional, backward-compatible
  parameter on the existing `rules._wyrd_die`/`rules.opposed_test` functions, defaulting to 0 (no
  widening) -- not a new parallel dice-reading function -- since the Wyrd die is read in exactly
  one place today and duplicating that logic would be the kind of second implementation this
  repo's process has been corrected for before. This is the one place this feature touches
  `rules.py`; #260's precedent (keeping the adversary baseline path independent of
  `UNTRAINED_SKILL`) was specifically about not sharing that one fallback constant, not a
  blanket rule against ever extending `rules.py`.
- `damage_type` trait effects do not stack the way numeric effects do (there is no meaningful
  way to "add" two damage types) -- the last one present wins, matching how a single override
  is the only sensible reading of "fixes the damage type."
