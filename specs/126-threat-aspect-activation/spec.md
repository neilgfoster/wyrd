# Feature Specification: Threats aspect & activation

**Feature Branch**: `126-threat-aspect-activation`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Threats aspect & activation" (issue #334)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The active set of Threats is a query, not a file (Priority: P1)

The GM needs to know, at any point, which Threats are currently live in the chronicle — to decide
what happens over a game-time span, to check whether a scene should surface one. Since a Threat is
an aspect attached to whichever entity carries it (a character, an organisation or a place), there
is no separate Threat file to read; the active set is derived by scanning entities for a `threat`
block with `imminence > 0`.

**Why this priority**: every other story in this feature (activation, promotion, fading) operates
on "the currently active Threats", so this query is the foundation the rest builds on.

**Independent Test**: given a mixed list of entity dicts, some carrying a `threat` block with
`imminence > 0`, some carrying one with `imminence == 0`, and some carrying none at all, confirm
the active set contains exactly the first group.

**Acceptance Scenarios**:

1. **Given** entities of different types (character, organisation, place) each carrying a
   `threat` block with `imminence > 0`, **When** the active set is queried, **Then** all of them
   are returned regardless of entity type.
2. **Given** an entity whose `threat` block has `imminence == 0`, **When** the active set is
   queried, **Then** that entity is excluded.
3. **Given** an entity with no `threat` block at all, **When** the active set is queried, **Then**
   that entity is excluded.

---

### User Story 2 - A Threat activates on its weekly percentile check (Priority: P1)

Once a game-time week has elapsed, each active Threat gets a chance to act: a d100 roll against
`imminence x 10`. On activation, its `effects` table is rolled to determine what actually
happens — it might grow stronger, spread, or produce an open calamity.

**Why this priority**: this is the mechanic that makes a Threat a "campaign-length antagonist
that acts on its own schedule" rather than inert scenery; without it, imminence is a number with
no consequence.

**Independent Test**: given a Threat with a known `imminence` and a supplied d100 roll (never
generated internally — the caller supplies dice, matching the engine's existing
propose/resolve split), confirm activation is exactly `roll <= imminence * 10`, and that an
activation additionally bands a supplied effects-table roll against the Threat's `effects` table.

**Acceptance Scenarios**:

1. **Given** a Threat with `imminence: 4` and a supplied roll of `40`, **When** activation is
   checked, **Then** it activates (`40 <= 4 * 10`).
2. **Given** a Threat with `imminence: 4` and a supplied roll of `41`, **When** activation is
   checked, **Then** it does not activate.
3. **Given** a Threat with `imminence: 0`, **When** activation is checked with any roll, **Then**
   it never activates.
4. **Given** an activated Threat and a supplied effects-table roll, **When** the effects table is
   resolved, **Then** the matched entry (by its range key) is returned; a roll matching no entry
   is a no-op result, not an error.

---

### User Story 3 - An existing entity is promoted into a Threat (Priority: P2)

Something the character provoked or wronged acquires a `threat` block and an objective naming
them — a conspiracy the player disrupted gains an imminence and turns to face them; a companion
left for dead becomes a nemesis. Nothing new is created: an existing entity gains the aspect.

**Why this priority**: this is what makes a chronicle feel like consequence rather than
content — the mechanism is used less often than activation itself, but it's what the design
explicitly calls out as "the mechanism" (docs/design/19-campaign.md).

**Independent Test**: given an entity dict with no `threat` block, promote it with a supplied
`threat` block and an objective naming the player; confirm the result carries the `threat` block
unchanged and the rewritten objective, and that the entity's other fields are untouched.

**Acceptance Scenarios**:

1. **Given** an entity with no `threat` block, **When** it is promoted with a `threat` block and
   an objective, **Then** the returned entity carries that `threat` block and objective, and every
   other field of the original entity is preserved unchanged.
2. **Given** an entity that already carries a `threat` block, **When** promotion is attempted
   again, **Then** the attempt is rejected rather than silently overwriting the existing block —
   promotion targets an entity that does not yet have one.

---

### User Story 4 - A Threat fades when addressed (Priority: P2)

A Threat's `imminence` may fall when the player addresses a cause, and a Threat whose objective is
satisfied or foreclosed stops being one — its entity and history remain, but it no longer appears
in the active set.

**Why this priority**: without an exit path, every Threat a chronicle ever produces would
accumulate in the active set forever, which contradicts the design's explicit statement that
Threats fade.

**Independent Test**: given an active Threat, lower its `imminence` to `0` and confirm it no
longer appears in the active-set query from User Story 1, while the entity carrying it (and its
`threat` block, for history) is otherwise unchanged.

**Acceptance Scenarios**:

1. **Given** an active Threat, **When** its `imminence` is reduced to `0`, **Then** the entity is
   excluded from the active set, and the `threat` block itself is retained (not deleted) so the
   entity's history stays intact.

### Edge Cases

- A Threat's `effects` table entry may be a single value (e.g. `1`) or a range (e.g. `3-6`), both
  transcribed verbatim from `docs/design/19-campaign.md` — the table lookup must match both key
  shapes, mirroring the existing range-key matching `journey.roll_hazard` already uses for hazard
  tables.
- Promotion supplies an `imminence` of `0` — this is rejected as an invalid Threat block; a
  promoted Threat must be born active (imminence > 0), since a zero-imminence promotion is
  indistinguishable from not promoting at all.
- The active-set query is given an empty list of entities — it returns an empty set, not an
  error.
- Activation is checked for a Threat whose `effects` table is empty — activation itself still
  succeeds or fails on the percentile roll; only the effects-table lookup that follows is
  affected, matching `roll_hazard`'s existing no-op-on-empty-table convention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a query that, given a collection of entities, returns
  exactly those carrying a `threat` block with `imminence > 0` — the active set — regardless of
  the carrying entity's type.
- **FR-002**: The active-set query MUST exclude an entity whose `threat` block has
  `imminence == 0`, and MUST exclude an entity with no `threat` block at all.
- **FR-003**: The engine MUST provide an activation check that takes a Threat's `imminence` and a
  caller-supplied d100 roll (never generated internally) and reports activation exactly when
  `roll <= imminence * 10`.
- **FR-004**: On activation, the engine MUST provide a way to resolve a caller-supplied
  effects-table roll against the Threat's `effects` table, matching both single-value and
  range-value keys, and returning the matched entry (or a no-op result for an unmatched roll).
- **FR-005**: The engine MUST provide a promotion operation that, given an entity with no
  existing `threat` block, a new `threat` block, and an objective, returns the entity with that
  `threat` block and objective attached and every other field unchanged.
- **FR-006**: The promotion operation MUST reject an attempt to promote an entity that already
  carries a `threat` block, and MUST reject a supplied `threat` block whose `imminence` is not
  greater than `0`.
- **FR-007**: The engine MUST NOT delete or otherwise discard a Threat's `threat` block when its
  `imminence` falls to `0` — a faded Threat's history remains on its entity, only its
  active-set membership changes.

### Key Entities

- **`threat` block** (docs/design/19-campaign.md): a dict attached to the frontmatter of any
  entity (`character`, `organisation`, or `place`) — `imminence` (int), `clues` (ordered list),
  `effects` (range-keyed table), `ambient` (list of standing costs), `counters` (list), `weakness`
  (string), `connection` (string), `known_to_player` (`none | rumoured | partial | understood`).
  This feature treats it as a plain dict, matching every other runtime module in `engine/wyrd/`
  (journey.py, economy.py) — no entity/file loading, which stays the setting repo's concern.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given any mix of entities, the active-set query returns exactly the entities with a
  live Threat (`imminence > 0`) — verified by exact-input tests, not eyeballed.
- **SC-002**: The activation check's boundary (`roll == imminence * 10` activates,
  `roll == imminence * 10 + 1` does not) is covered by an explicit test at that exact boundary.
- **SC-003**: A promoted entity's Threat is indistinguishable, from the active-set query's
  perspective, from one seeded at chronicle creation — both are simply entities carrying a
  `threat` block with `imminence > 0`.
- **SC-004**: A faded Threat (`imminence` reduced to `0`) is absent from the active set on the
  very next query, with no separate "clear" or "delete" step required.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts in, plain dicts out, no entity/file
  loading (`engine/wyrd/state.py`/`entity.py` own that layer) — matching `journey.py`'s existing
  division of labour, which already reuses this same activation-roll shape
  (`d100 <= imminence * 10`) for its own hazard check and explicitly notes "No... Threat concept
  has any runtime implementation elsewhere in `engine/wyrd/` yet".
- The weekly cadence itself (rolling every active Threat once per elapsed game-time week) and the
  expected-value roll-generation over a multi-week span are `advance-time`'s concern (#338,
  blocked on this feature) — this feature provides the per-Threat activation check and effects
  lookup that `advance-time` will call once per Threat per elapsed week; it does not implement the
  elapsed-time loop itself.
- `effects` table entries are prose (what actually happens is GM narration), matching
  `journey.py`'s existing separation between mechanical resolution and GM narration
  (docs/design/13-diegesis.md) — this feature surfaces the matched entry, it does not interpret or
  apply it.
- Where a Threat's `ambient` costs route through the material economy is out of scope here,
  matching how `journey.py`'s `resolve_leg` already surfaces (never auto-applies) a crossed
  Threat's `ambient` list.
