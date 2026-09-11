# Feature Specification: Chronicle state invariants: passive validation and active cascades

**Feature Branch**: `327-chronicle-state-invariants`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Chronicle state invariants: passive validation and active cascades — enforce docs/design/22-state.md's full invariant set on commit: passive checks that reject a bad write outright, active cascades already staged for taint/trauma/transformation crossings, and Spent computed at read time."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A malformed commit is rejected before it touches disk (Priority: P1)

A GM tool stages a proposal whose mutations would produce a duplicate entity id, a broken
`[[link]]`/`parent`/`overlay_of` reference, `fortune.current` above `fate.max`, or a tracker
`value` outside `0..max`. Committing that proposal must fail outright, with nothing written to
any entity file.

**Why this priority**: without this, `commit()` silently writes broken state that downstream
reads (tiering, rendering, further proposals) have no way to detect or recover from — the
foundational guarantee the rest of the engine assumes already holds.

**Independent Test**: build a proposal whose mutations, if applied, would violate exactly one of
the four passive rules; call `commit`; assert it raises and that the target entity file(s) on
disk are byte-identical to before the call.

**Acceptance Scenarios**:

1. **Given** a proposal that would create an entity id already present among the chronicle's
   other entities, **When** `commit` is called, **Then** it raises and no entity file changes.
2. **Given** a proposal that would set a `parent` value that does not resolve to any known
   entity, **When** `commit` is called, **Then** it raises and no entity file changes.
3. **Given** a proposal that would set `parent` such that the parent chain now cycles back to the
   entity itself, **When** `commit` is called, **Then** it raises and no entity file changes.
4. **Given** a proposal that would raise `fortune.current` above the entity's current
   `fate.max`, **When** `commit` is called, **Then** it raises and no entity file changes.
5. **Given** a proposal that would push a tracker's `value` below `0` or above its own `max`,
   **When** `commit` is called, **Then** it raises and no entity file changes.
6. **Given** a proposal whose mutations violate none of the four rules, **When** `commit` is
   called, **Then** it succeeds exactly as it does today.

---

### User Story 2 - Active cascades stay staged inside the same proposal (Priority: P2)

Taint crossing a multiple of 3, Trauma reaching or passing the floor, and a Transformation count
reaching a character's `hidden_threshold` already spawn their further rolls inside `propose()`
(`resolution.py`'s `_cascade_from_mutation` / `_stage_transformation_chain` /
`_stage_trauma_test_chain`). This story is about confirming — and protecting with a regression
test at the level of the whole invariant, not just the individual functions — that none of these
three cascades can be bypassed by a `commit()` that starts enforcing the User Story 1 passive
checks: a cascade must still be staged (and, if it fails a passive check itself, rejected) inside
the *same* proposal as the crossing write, never as a follow-up.

**Why this priority**: the cascades already work; what's missing is proof they keep working once
User Story 1's checks sit in front of every commit, and that a passive check on a
cascade-produced mutation (e.g. an Affliction roll's own tracker bounds) is enforced exactly the
same way as on a directly-requested one.

**Independent Test**: propose a mutation that crosses a taint multiple of 3 (or the trauma floor,
or the hidden_threshold), assert the returned proposal already contains the further roll's steps
before `commit` is ever called, then commit it and assert every staged mutation — original and
cascaded — landed together.

**Acceptance Scenarios**:

1. **Given** a taint mutation that crosses a multiple of 3, **When** `propose` stages it,
   **Then** the same proposal already contains a Transformation roll's steps, and `commit`
   applies both the taint change and the transformation's mutations in one call.
2. **Given** a trauma mutation that crosses past the floor, **When** `propose` stages it,
   **Then** the same proposal already contains the gating test (and, on a failed test, an
   Affliction roll), and `commit` applies all of it together.
3. **Given** a transformation mutation that brings the count to `hidden_threshold`, **When**
   `propose` stages it, **Then** the same proposal already sets `status: lost`, and `commit`
   applies it in the same call as the crossing mutation.

---

### User Story 3 - Spent is read, never written (Priority: P3)

A caller asks whether a character is Spent (`resolve.current ≤ max(taint, trauma)`, each axis
exempted at `0`, per ADR 0049). The answer is computed from the character's current `resolve`,
`taint` and `trauma` fields at the moment of the read; nothing writes a `spent` field to the
entity, on commit or otherwise.

**Why this priority**: lowest-risk of the three — nothing currently writes a `spent` field, so
this story is additive (an accessor) rather than a change to an existing write path — but it
closes the last unaddressed invariant.

**Independent Test**: construct character states at each side of the Spent boundary (including
the `0`-exemption on each axis) and assert the accessor's answer against each, independent of
`commit`/`propose`.

**Acceptance Scenarios**:

1. **Given** a character with `resolve.current` at or below `max(taint, trauma)`, and neither
   `taint` nor `trauma` at `0`, **When** the Spent accessor is called, **Then** it reports Spent.
2. **Given** a character with `taint == 0` (or `trauma == 0`) so that axis is exempted, **When**
   the Spent accessor is called with `resolve.current` at or below the *other* axis alone,
   **Then** it reports according to the non-exempted axis only, per ADR 0049's exemption rule.
3. **Given** a character with `resolve.current` above `max(taint, trauma)`, **When** the Spent
   accessor is called, **Then** it reports not Spent.
4. **Given** any character entity file, **When** it is loaded from disk, **Then** it carries no
   `spent` field, before or after any commit.

### Edge Cases

- A proposal touching more than one entity, where only one entity's mutations violate a passive
  check: `commit` must raise for the whole proposal and leave *every* touched entity's file
  unchanged — the existing "atomic per entity file" guarantee `commit`'s own docstring already
  states must not degrade into a partial multi-entity write.
- A cascade-produced mutation (e.g. a Transformation roll's own field write) that itself would
  violate a passive check (out-of-range tracker) must be rejected exactly like a directly
  requested mutation — cascades get no exemption from User Story 1's rules.
- `fortune.current ≤ fate.max` must be checked against the value *after* all of a proposal's
  mutations to that entity are applied, not the value at the moment fortune is first touched —
  matching how `commit` already applies a proposal's mutations as one entity-scoped batch.
- An entity that has no `fate`/`fortune` fields at all (a non-character entity) must not be
  checked against the fortune/fate rule — it only applies where the fields exist.
- A `parent` cycle introduced across *two different entities* in the same multi-entity proposal
  (A's mutation points to B, B's mutation points to A) must be caught the same as a single-entity
  self-cycle.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `commit` MUST reject the entire proposal, applying no mutation to any entity file,
  if any staged mutation (direct or cascade-produced) would result in a duplicate entity `id`
  among the chronicle's known entities.
- **FR-002**: `commit` MUST reject the entire proposal, applying no mutation to any entity file,
  if any staged mutation would leave any `[[link]]`, `parent`, or `overlay_of` reference
  unresolved.
- **FR-003**: `commit` MUST reject the entire proposal, applying no mutation to any entity file,
  if any staged mutation would introduce a cycle in the `parent` chain, whether within one entity
  or across the entities touched by the same proposal.
- **FR-004**: `commit` MUST reject the entire proposal, applying no mutation to any entity file,
  if any staged mutation would leave an entity's `fortune.current` greater than that entity's
  `fate.max`, checked after all of that entity's mutations in the proposal are applied. Entities
  with no `fortune`/`fate` fields are exempt from this rule.
- **FR-005**: `commit` MUST reject the entire proposal, applying no mutation to any entity file,
  if any staged mutation would leave a tracker's `value` outside `0..max` for that tracker.
- **FR-006**: The passive checks in FR-001 through FR-005 MUST apply identically to a
  cascade-produced mutation (Transformation, trauma-test, Affliction) and a directly requested
  one — no mutation is exempt because of how it was staged.
- **FR-007**: A `commit` rejected by any of FR-001 through FR-005 MUST leave every entity file the
  proposal touches byte-identical to its state before the call — the existing per-entity
  atomicity guarantee extends to reject-as-a-whole, not partial application across entities.
- **FR-008**: Taint crossing a multiple of 3, trauma reaching or passing the floor (gating
  further gain behind a test, and a failed test spawning an Affliction roll), and a
  transformation count reaching `hidden_threshold` (setting `status: lost`) MUST continue to be
  staged inside the same proposal as the crossing write — this is existing, already-implemented
  behavior (`resolution.py`) that this feature must not regress once FR-001 through FR-007 are
  layered in front of `commit`.
- **FR-009**: A new accessor MUST compute whether a character is Spent
  (`resolve.current ≤ max(taint, trauma)`, each axis exempted at `0`, per ADR 0049) from the
  character's current state at call time. No commit path may write a `spent` field to any entity.
- **FR-010**: The generic tracker-reaching-`max` immediate-write path (`wyrd track`) is explicitly
  out of scope for this feature and MUST NOT be altered.
- **FR-011**: The pending/transaction lifecycle (`chronicle.yaml`'s `pending.rolled`, an
  interrupted-session's uncommitted proposal) is explicitly out of scope for this feature and MUST
  NOT be altered.

### Key Entities

- **Proposal**: the in-memory, uncommitted result of `propose()` — a list of staged steps, each
  carrying zero or more mutations against one or more entities. This feature adds a validation
  pass that runs once, across every mutation in the proposal, immediately before `commit` applies
  any of them.
- **Entity**: a chronicle file with YAML frontmatter (character, companion, thread, tracker,
  place, …), per `25-entities.md`. The passive checks in this feature are checked against the
  full set of entities a proposal's mutations touch, resolved against the chronicle's other known
  entities for id-uniqueness and reference resolution.
- **Tracker**: an entity of type `tracker`, holding `value` and `max` (party Tension is one
  instance). FR-005's bounds check applies to every entity carrying `value`/`max` tracker fields,
  not only entities of type `tracker`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the four passive rules (duplicate id, unresolved reference, parent
  cycle, fortune > fate.max, tracker out of bounds) has at least one automated test proving a
  violating commit is rejected and leaves disk state unchanged.
- **SC-002**: The three existing active cascades (taint→Transformation, trauma→test→Affliction,
  transformation-count→lost) continue to pass their existing test coverage unchanged, plus one
  new test each proving the cascade still lands correctly when staged alongside a proposal that
  also exercises the new passive checks.
- **SC-003**: The Spent accessor is exercised by a test at each of the four boundary conditions
  named in User Story 3, and no test anywhere in the suite finds a `spent` field written to an
  entity file.
- **SC-004**: `ruff check .` and `ruff format --check .` both report clean, repo-wide, after this
  feature lands.

## Assumptions

- "Reject the entire proposal" means `commit` raises `ProposalError` (or a new, equally explicit
  exception) before applying any mutation — consistent with `commit`'s existing behavior for an
  already-closed proposal, and with the design document's "rejects a write outright" language.
  This feature does not introduce a partial-commit or best-effort mode.
- "The chronicle's other known entities," for id-uniqueness and reference resolution, means the
  effective entity set `entity.py`'s existing `load_set`/`resolve_entity`/`check_containment`
  machinery already assembles (setting + overlay + chronicle-invented entities) — this feature
  reuses that machinery rather than inventing a second way to enumerate entities.
- A tracker's `value`/`max` fields are read by the same field-path convention
  `_apply_mutation`/`_get_nested` already use elsewhere in `resolution.py` (dotted paths like
  `stamina.current`), not a new schema.
- The passive-check pass runs once per `commit()` call, after all of a proposal's cascades have
  already been staged by `propose()` — it validates the proposal's final shape, not each
  intermediate staging step.
- When a proposal's entities live outside a full chronicle directory layout (no discoverable
  `entities/`/`overlay/`/`setting/` root above them — the case most of this engine's own unit
  tests already exercise), the passive checks fall back to validating only the entities the
  proposal itself touches, rather than failing every such commit outright for a layout it was
  never asked to assume. Duplicate-id and unresolved-reference checks against entities *outside*
  the proposal only run when a chronicle root is actually found.
