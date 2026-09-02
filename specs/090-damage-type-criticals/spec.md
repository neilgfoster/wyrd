# Feature Specification: Damage-type critical tables

**Feature Branch**: `090-damage-type-criticals`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Damage-type critical tables — extend the existing slashing-only
critical resolution to all four closed damage types (piercing, blunt, searing), each with its own
row table per docs/design/05-criticals.md. Reject any fifth type as a load error. Out of scope:
the Aftermath table, mortal-blow to death-row re-read, Fate spend, recurring-wound combat-start
firing."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reading the correct table for the wound (Priority: P1)

A combatant driven below 0 Stamina by a blow rolls a critical on the table for that blow's damage
type — not always `critical-slashing`, whichever of the four closed damage types the weapon/blow
actually declares.

**Why this priority**: This is the entire feature — the ruleset has told the GM to roll "on the
table for the damage type" since it was written, and only one of the four tables currently exists
in the engine.

**Independent Test**: Stage a critical from a blow of each of the four damage types at a range of
modifiers; confirm each resolves against its own table's rows (not slashing's), with the correct
key, effect, and description at each boundary.

**Acceptance Scenarios**:

1. **Given** a blow of damage type `piercing` that drives its target below 0 Stamina, **When**
   the critical is staged, **Then** it is resolved against `critical-piercing`'s rows, not
   `critical-slashing`'s.
2. **Given** a blow of damage type `blunt` that drives its target below 0 Stamina, **When** the
   critical is staged, **Then** it is resolved against `critical-blunt`'s rows.
3. **Given** a blow of damage type `searing` that drives its target below 0 Stamina, **When** the
   critical is staged, **Then** it is resolved against `critical-searing`'s rows.
4. **Given** a total that falls exactly on a row boundary (e.g. 4/5 on `critical-piercing`, 20/21
   on `critical-blunt`), **When** the critical is staged, **Then** the row selected matches the
   documented range exactly, with no off-by-one drift.
5. **Given** a total high enough to land in the table's open-ended top row (e.g. 19+ on
   `critical-piercing`), **When** the critical is staged, **Then** the row's `effect` is exactly
   `mortal`, staging no further wound-record mutation (unchanged behaviour from
   `critical-slashing`'s existing mortal handling).

### User Story 2 - A weapon may only declare a damage type the engine knows (Priority: P2)

A weapon or blow that names a damage type outside the closed set of four fails to load, rather
than silently resolving against no table or the wrong one.

**Why this priority**: The design is explicit that the set of four is closed and that a fifth
type is a load error, not a table quietly skipped — this is the guard that keeps the engine's
promise to the setting-authoring surface honest.

**Independent Test**: Attempt to stage a critical for a damage type not among
`{slashing, piercing, blunt, searing}`; confirm it raises the engine's existing load-error
exception rather than resolving.

**Acceptance Scenarios**:

1. **Given** a blow declaring damage type `"acid"` (not one of the four), **When** the critical
   is staged, **Then** the engine raises a load error naming the unrecognized type.
2. **Given** a blow declaring no damage type at all where one is required, **When** the critical
   is staged, **Then** the engine raises the same class of load error.

### Edge Cases

- What happens at each table's lowest possible total (2 for every table)? It resolves against
  that table's first row — every table's first row is required to start at 2
  ([`04-tables.md`](../../docs/design/04-tables.md)).
- What happens when the same combatant takes two criticals of different damage types in one
  fight? Each is staged and resolved independently, against its own blow's table — this feature
  does not change the "once per critical taken" behaviour already in place for slashing.
- What happens to existing `critical-slashing` behaviour? It is unchanged — this feature adds the
  other three tables alongside it, and does not alter slashing's rows, keys, effects, or the
  existing wound-record mutation it already stages.
- What happens when a `combat-attack` request supplies no `damage_type` at all (every existing
  caller/test today)? It resolves against `critical-slashing`, exactly as before this feature
  (FR-001b) — omission is not a load error, only an unrecognized non-empty value is.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST resolve a critical roll against the row table matching the blow's
  own damage type — one of `critical-slashing`, `critical-piercing`, `critical-blunt`, or
  `critical-searing` — never a fixed table regardless of damage type.
- **FR-001a**: The system MUST accept `damage_type` as a caller-supplied parameter of a
  `combat-attack` request, threaded the same way `weapon_dice`/`armour_dice` already are — through
  `resolution.propose`/`propose_batch`, `combat.py`'s existing `crowd_attack`/`resolve_ranged_attack`
  callers, `verbs.py`, the CLI (`client.py`), and the MCP tool schema (`catalog.py`) — since no such
  parameter exists anywhere in the request chain today.
- **FR-001b**: The system MUST default a `combat-attack` request with no `damage_type` supplied to
  `slashing`, preserving every existing caller's behaviour unchanged (FR-005).
- **FR-002**: The system MUST implement `critical-piercing`'s six rows exactly as specified in
  `docs/design/05-criticals.md` (ranges, keys, effects, descriptions).
- **FR-003**: The system MUST implement `critical-blunt`'s six rows exactly as specified in
  `docs/design/05-criticals.md`.
- **FR-004**: The system MUST implement `critical-searing`'s six rows exactly as specified in
  `docs/design/05-criticals.md`.
- **FR-005**: The system MUST leave `critical-slashing`'s existing rows, resolution, and staged
  wound-record mutation unchanged.
- **FR-006**: The system MUST reject a blow declaring a damage type outside the closed set of
  four as a load error, distinguishable from a normal resolution failure.
- **FR-007**: For every non-mortal row across all four tables, the system MUST stage the same
  shape of wound-record mutation `critical-slashing` already stages (one wound record carrying
  the row's `effect`, keyed to the step), using the row's own effect rather than a fixed one.
- **FR-008**: For the mortal row of any of the four tables, the system MUST stage no further
  wound-record mutation, matching `critical-slashing`'s existing `mortal` handling (ADR 0023: a
  critical never kills during the fight).

### Key Entities

- **Damage type**: one of the closed set `{slashing, piercing, blunt, searing}`, named for the
  shape of the wound rather than a weapon or element. Already a property blows/weapons carry
  elsewhere in the engine; this feature is the first place that value selects between multiple
  row tables rather than being ignored.
- **Critical table**: a `04-tables.md`-shaped family, one per damage type, sharing the same die
  (`1d6`), modifier (`+ points below zero`), and row schema, differing only in row content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four tables' rows match `docs/design/05-criticals.md` exactly, verified by a
  scripted check comparing every row's range/key/effect against the design doc's own tables.
- **SC-002**: A boundary total on either side of every row transition in all four tables resolves
  to the documented row on each side, with zero off-by-one mismatches, verified by a scripted
  check.
- **SC-003**: check_criticals.py (or its extension) asserts the design doc's own computed
  per-table percentages (nothing lasting / lasting mark / mortal, from the "What each table
  weighs" table) hold for all four tables, not just slashing.
- **SC-004**: A blow declaring an unrecognized damage type fails to resolve, verified by a
  scripted check that it raises a load error rather than returning a result.

## Assumptions

- No `damage_type` parameter exists anywhere in the request chain today (`resolution.py`,
  `combat.py`, `verbs.py`, `client.py`, `catalog.py`'s MCP schema all currently thread only
  `weapon_dice`/`armour_dice`). This feature introduces it as a new caller-supplied parameter,
  following the exact existing pattern those two already establish, and defaults it to `slashing`
  when omitted so every existing caller and test keeps behaving exactly as it does today
  (FR-001a/b).
- The Aftermath table (`docs/design/06-aftermath.md`), the mortal-blow-forces-death-row
  mechanism, Fate's re-read of a death result, and the recurring wound's combat-start firing are
  explicitly out of scope — each is a separate feature under the same parent epic (#213), tracked
  as #252, #253, and #254 respectively.
- The load-error mechanism for an unrecognized damage type reuses whatever exception class the
  engine already raises for other closed-set/load-time violations elsewhere in the codebase,
  rather than introducing a new exception type.
