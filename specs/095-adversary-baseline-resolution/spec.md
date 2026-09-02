# Feature Specification: Adversary baseline skill resolution

**Feature Branch**: `095-adversary-baseline-resolution`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Adversary baseline skill resolution (issue #260): when an opposed
test names a skill an adversary's block does not list, resolve that test at the adversary's
baseline percentage rather than any untrained/fallback constant. A skill the block does list is
resolved at its listed value, unaffected by baseline. The baseline must never be confused with or
substituted by the untrained-10% constant."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An adversary is tested on a skill its block doesn't list (Priority: P1)

Something asks an adversary to resist a shove, spot a liar, or run down a fleeing party --
none of which its bestiary entry explicitly lists. The engine resolves that test at the
adversary's `baseline` value rather than treating the adversary as untrained.

**Why this priority**: this is the entire feature's purpose -- docs/design/12-the-adversary.md
section 3 exists specifically because a block cannot list every skill a setting declares.

**Independent Test**: given a loaded adversary block and a skill name absent from its `skills`
mapping, resolving a percentage for that skill returns the block's `baseline` value.

**Acceptance Scenarios**:

1. **Given** an adversary block with `baseline: 35` and `skills: {blade: 55}`, **When** the
   engine resolves the adversary's percentage for `tracking` (not listed), **Then** it returns
   35.

---

### User Story 2 - An adversary is tested on a skill its block does list (Priority: P2)

The adversary's block already names the skill in question. The engine resolves the test at that
skill's own listed value; the baseline plays no part.

**Why this priority**: docs/design/12-the-adversary.md section 3 is explicit that "the baseline
is not a floor under a listed skill" -- a skill written below the baseline stays where it was
written, so this is a correctness boundary the feature must not blur.

**Independent Test**: given the same block, resolving a percentage for `blade` (listed) returns
55, not 35 -- even where the listed value is lower than the baseline.

**Acceptance Scenarios**:

1. **Given** an adversary block with `baseline: 35` and `skills: {blade: 55}`, **When** the engine
   resolves the adversary's percentage for `blade`, **Then** it returns 55.
2. **Given** an adversary block with `baseline: 60` and `skills: {stealth: 20}` (a listed skill
   below the baseline), **When** the engine resolves the adversary's percentage for `stealth`,
   **Then** it returns 20, not 60 -- the baseline is not a floor.

---

### User Story 3 - The untrained-10% path stays untouched (Priority: P3)

A player character with no relevant skill still resolves at the existing untrained rate
(`engine/wyrd/rules.py`'s `UNTRAINED_SKILL`). This feature's new adversary path must share no
constant or code path with that one, so a future change to either never silently drags the
other along.

**Why this priority**: the issue's own Definition of Done makes this an explicit non-negotiable
("must never be confused with or substituted by the untrained-10% constant"), not merely a nice
property.

**Independent Test**: confirm the adversary-baseline resolution function and
`select_group_skill`/`UNTRAINED_SKILL` are independent -- changing one's constant does not affect
the other's behavior, verified by a test exercising each path with values that would collide if
they were accidentally shared.

**Acceptance Scenarios**:

1. **Given** an adversary with `baseline: 10` (coincidentally equal to `UNTRAINED_SKILL`),
   **When** its percentage for an unlisted skill is resolved, **Then** the result is exactly the
   adversary's own `baseline` field value, read from the block -- not the shared constant.
2. **Given** a player-side group test with a member who has no relevant skill, **When**
   `select_group_skill` resolves that member, **Then** it still returns `UNTRAINED_SKILL`,
   unaffected by anything this feature adds.

### Edge Cases

- A block whose `skills` mapping is empty is already rejected at load time (#259's
  `validate_adversary`: `skills` must be a non-empty mapping) -- this feature does not need to
  handle an empty-skills adversary as a distinct case.
- A skill name resolved case-sensitively or with surrounding whitespace: out of scope --
  matching is exact-string, the same convention the loaded block's `skills` mapping already uses
  (no normalization happens at load time either).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a way to resolve the percentage an adversary tests a named
  skill at, given its loaded block.
- **FR-002**: If the named skill is present in the adversary's `skills` mapping, the resolved
  percentage MUST be that skill's own listed value.
- **FR-003**: If the named skill is absent from the adversary's `skills` mapping, the resolved
  percentage MUST be the adversary's `baseline` value.
- **FR-004**: The baseline MUST NOT act as a floor under a listed skill -- a listed skill's value
  below the baseline is returned unchanged, not raised to the baseline.
- **FR-005**: This resolution path MUST NOT read or depend on `UNTRAINED_SKILL` or
  `select_group_skill`, and MUST NOT be read by them -- the two fallback rates stay fully
  independent code paths, even where their values happen to coincide.

### Key Entities

- **Adversary block**: the loaded, validated shape #259 already produces (`baseline`, `skills`,
  and the rest). This feature reads `baseline` and `skills` from it; it does not change how the
  block is loaded or validated.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For any loaded adversary block and any skill name absent from its `skills`
  mapping, resolving that skill's percentage returns exactly the block's `baseline` value, for
  every block tested.
- **SC-002**: For any loaded adversary block and any skill name present in its `skills` mapping,
  resolving that skill's percentage returns exactly that skill's listed value, regardless of how
  it compares to the block's `baseline`.
- **SC-003**: Changing `UNTRAINED_SKILL`'s value in isolation does not change any adversary
  baseline-resolution test's outcome, and vice versa -- verified by tests that would fail if the
  two paths shared state.

## Assumptions

- "Resolve that test at the adversary's baseline percentage" is implemented as a small, pure
  accessor function (analogous to how `rules.select_group_skill` selects a percentage for a
  group test) that other engine code (resolution, combat) will call when it needs an adversary's
  effective skill value -- this feature provides that accessor; wiring every call site that
  currently assumes a character's skill into using it for an adversary is out of this feature's
  scope unless the issue's own acceptance criteria require it (they describe the accessor
  behavior itself, not every caller).
- This lives in `engine/wyrd/adversary.py` alongside the block-loading code from #259, since both
  concern only the adversary block and its fields, rather than in `engine/wyrd/rules.py` (which
  holds the player-facing resolution machinery this feature must stay independent from, per
  FR-005).
