# Feature Specification: Cascading resolution

**Feature Branch**: `236-cascading-resolution`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Cascading resolution — a resolved step spawns a further step inside the same proposal whenever the mechanic's own rule calls for one, per docs/design/31-action-resolution.md 'Cascading resolution'. Two trigger shapes: a mutation crossing a threshold, and a roll's own outcome calling for a further roll. Worked examples: the combat resolution chain (attack -> damage -> armour -> critical), and a Taint-threshold-into-Transformation chain. Depends on #235 (propose/commit/discard core). Closes #236, part of #211."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A landed attack resolves its full chain in one call (Priority: P1)

A caller resolves a combat attack and, without a further call, gets back the weapon damage, the
armour reduction, the resulting Stamina mutation, and — if that mutation crosses below zero — the
critical roll and its wound-record mutation, all staged in one proposal.

**Why this priority**: This is the combat chain `docs/design/31-action-resolution.md` names as
its own worked example — the clearest instance of the outcome-triggered cascade shape, and the
one every future combat feature depends on.

**Independent Test**: Given an actor and target with known skills/armour/weapon dice, calling
`propose` for a `combat-attack` that lands a telling blow taking the target below 0 Stamina
returns a proposal with four dependent steps (attack, weapon-damage, armour, critical) and
mutations that, once committed, leave the target's Stamina and wound record exactly as a
hand-worked resolution would.

**Acceptance Scenarios**:

1. **Given** an attack roll that lands (target's defence fails, or the attacker's own roll
   succeeds against the mechanic in play), **When** `propose` resolves it, **Then** a
   `weapon-damage` step and an `armour` step are staged, both depending on the attack step.
2. **Given** the weapon-damage and armour rolls, **When** they combine into the Stamina mutation,
   **Then** that mutation is exactly `max(1, damage - armour)` subtracted from the target's
   current Stamina.
3. **Given** the combined Stamina mutation crosses below 0, **When** `propose` checks it against
   Stamina's own threshold, **Then** a `critical` step is staged, depending on that mutation, and
   its own mutation (a wound record) is included in the proposal.
4. **Given** the attack roll reads a telling blow (`degrees >= 6`), **When** the weapon-damage
   step resolves, **Then** its damage is doubled before combining with armour.
5. **Given** an attack that does not land, **When** `propose` resolves it, **Then** no further
   step is staged — a single, non-cascading step, exactly as #235 already handles.

---

### User Story 2 - A Taint mutation crossing a threshold forces a Transformation, cascaded (Priority: P1)

A caller resolves an Exposure test that fails and, without a further call, gets back the
Transformation roll a crossed Taint threshold forces — including the case where the
Transformation's own Taint reduction leaves the character still at or over the threshold, forcing
a re-roll, all inside the same proposal.

**Why this priority**: This is the second worked example `docs/design/31-action-resolution.md`
names, and the clearest instance of the threshold-crossing cascade shape.

**Independent Test**: Given an actor whose Taint mutation from a failed Exposure test crosses a
multiple of 3, calling `propose` returns a proposal with a `transformation` step depending on the
Exposure step, whose own mutations (Taint reduced by the rolled severity, Dread increased by the
same amount, and — on the character's first Transformation — the hidden threshold set once) are
included.

**Acceptance Scenarios**:

1. **Given** a failed Exposure test whose Taint mutation crosses a multiple of 3, **When**
   `propose` resolves it, **Then** a `transformation` step is staged, depending on the Exposure
   step.
2. **Given** the Transformation roll's severity, **When** its mutation is computed, **Then** Taint
   is reduced by exactly that severity and Dread is increased by the same amount.
3. **Given** this is the character's first Transformation, **When** the transformation step
   resolves, **Then** a `hidden_threshold` mutation (`set`, a fresh `1d6 + 2` roll) is staged
   alongside it; on a later Transformation, no such mutation is staged.
4. **Given** the Transformation's own Taint reduction leaves Taint still at or over the crossed
   threshold, **When** `propose` resolves the chain, **Then** a further `transformation` step is
   staged, depending on the first, drawing a different (unique-per-character) table row, and this
   repeats until Taint clears the threshold.
5. **Given** a mutation that does not cross any threshold, **When** `propose` resolves it,
   **Then** no `transformation` step is staged.

---

### User Story 3 - A deferred consequence never cascades into the same proposal (Priority: P2)

A caller resolving a combat chain that produces a mortal critical does not get an Aftermath step
in the same proposal — Aftermath is deliberately rolled after the fight, not immediately.

**Why this priority**: `docs/design/31-action-resolution.md` states this explicitly as a
boundary on cascading resolution; getting it wrong would silently roll a consequence at the wrong
narrative moment.

**Independent Test**: A critical roll's own mutation (a wound record, however severe) never
stages a further step in the same proposal.

**Acceptance Scenarios**:

1. **Given** a critical roll lands on a mortal-band result, **When** `propose` resolves the
   chain, **Then** the proposal contains the critical step and its wound-record mutation, and
   nothing further.

### Edge Cases

- What happens when a cascade would stage a step for an unregistered field/mechanic combination
  (e.g. a Strain or Trauma threshold, which this feature does not implement)? → No step is
  staged; only the two triggers this feature actually wires up (Stamina→critical inside the
  combat chain, and Taint→Transformation) fire. This is not silent data loss — it is this
  feature's explicitly stated scope boundary (see Assumptions).
- What happens when the Transformation table's six rows are all taken (exhausted) mid-cascade? →
  Out of scope for this feature (not reachable by either worked example); left as a documented
  follow-up, matching `docs/design/07-transformations.md`'s own note that this is not expected to
  be reachable in play.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every proposal step MUST record what it `depends_on` — the list of step ids whose
  resolution caused it to be staged.
- **FR-002**: `propose` MUST check every staged mutation against its field's own threshold rule
  (this feature wires up exactly one: Taint, every multiple of 3) and, on a crossing, stage the
  further step(s) that rule calls for, depending on the mutation's own step — recursively, since
  the further step's own mutation can cross another threshold in turn.
- **FR-003**: `propose` MUST support a mechanic whose own resolved outcome calls for a further
  step regardless of any mutation crossing a threshold (this feature wires up exactly one: a
  landed `combat-attack`, staging `weapon-damage` and `armour`).
- **FR-004**: The combat chain MUST combine weapon-damage and armour into a Stamina mutation as
  `max(1, damage - armour)`, doubling weapon damage first when the attack step read a telling
  blow (`degrees >= 6`).
- **FR-005**: The combined Stamina mutation from FR-004 MUST itself be checked against Stamina's
  own threshold (crossing below 0) under the same rule as FR-002, staging a `critical` step when
  crossed.
- **FR-006**: The `critical` step MUST roll `1d6 + points below zero` against the
  `critical-slashing` table (`docs/design/05-criticals.md`) and stage the resulting wound-record
  mutation (or a `mortal` marker, per that table's `21+` row).
- **FR-007**: The `transformation` step MUST roll `1d6` against the Transformation table
  (`docs/design/07-transformations.md`), consuming a severity value unique per character (no row
  repeats until the table would need to for that character), reduce Taint by that severity,
  increase Dread by the same amount, and — only on that character's first Transformation — stage
  a `hidden_threshold` mutation from a fresh `1d6 + 2` roll.
- **FR-008**: If, after a `transformation` step's own Taint reduction, Taint is still at or over
  the threshold just crossed, `propose` MUST stage a further `transformation` step depending on
  the first, repeating until Taint clears the threshold (bounded by the table's own 6 rows, per
  `docs/design/07-transformations.md`'s termination proof).
- **FR-009**: A step's own mutation MUST NOT stage a further step for a consequence its own rule
  states is deferred (e.g. Aftermath) — cascading resolution only stages what the triggering
  rule itself says happens immediately.
- **FR-010**: All of this MUST happen inside a single `propose` call, staged but not written,
  exactly like #235's single-step case — `commit` applies every staged mutation from every
  cascaded step atomically; `discard` writes nothing.

### Key Entities

- **Step**: extends #235's implicit single roll into an explicit record — `step_id`, `kind`
  (`roll`), `mechanic`, the resolved roll data, its own `mutations` (each tagged
  `produced_by_step`), and `depends_on` (a list of step ids).
- **Threshold rule**: a registered mapping from a mutation's field name to the further mechanic a
  crossing stages (this feature registers exactly `taint` → `transformation`, and, only inside
  the combat chain's own combining step, `stamina.current` → `critical`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `propose` for the combat chain reproduces the combat-resolution worked example in
  `docs/design/31-action-resolution.md` ("Senna Vask's Round 2 defence roll") exactly: telling
  blow, doubled damage, armour reduction, Stamina crossing below 0 at the same value, and the
  `critical-slashing` `6–9` band result.
- **SC-002**: `propose` for the Taint-threshold chain, given a real seeded scenario constructed
  for this feature (not asserted, computed and disclosed — see `research.md`), reproduces the
  same shape as `docs/design/31-action-resolution.md`'s own worked example: Taint reduced back
  below the threshold, Dread increased by the same severity, hidden threshold set once on first
  Transformation.
- **SC-003**: A cascade that would need more than one Transformation re-roll to clear a threshold
  (a constructed scenario, since neither worked example needs one) resolves correctly within one
  `propose` call, and never repeats a table row for the same character within that cascade.
- **SC-004**: A mortal critical does not stage any further step (User Story 3).
- **SC-005**: `ruff check . && ruff format --check . && python3 -m pytest -q` is clean.

## Assumptions

- This feature wires up exactly the two threshold/outcome triggers both of
  `docs/design/31-action-resolution.md`'s own worked examples need: Stamina→critical (inside the
  combat chain) and Taint→Transformation. Strain→Trauma and Trauma→Affliction cascades
  (mentioned in `docs/design/31-action-resolution.md`'s own prose as further instances of the
  same shape) are out of scope — no engine code for Strain/Trauma/Affliction exists yet, and
  adding it is a separate feature, not implied by this one.
- Only the `critical-slashing` damage-type table is implemented (matching the combat chain's own
  worked example); `critical-piercing`/`critical-blunt`/`critical-searing` are a documented
  follow-up, not required by either of this feature's worked examples.
- ADR 0044 (telling blow via a failed defence roll's own virtual-roll formula) is not
  reimplemented here — this feature's `combat-attack` mechanic reads telling directly off the
  attack step's own `degrees >= 6`, matching `docs/design/31-action-resolution.md`'s own
  statement of the rule ("no separate roll decides telling blow; it is read directly off the
  attack ... crossing 6"), and does not attempt the defence-roll-specific symmetry ADR 0044
  separately proves. A `combat-defence` mechanic reading a landed-but-failed roll the same way is
  a documented follow-up.
- Weapon/armour dice are supplied by the caller as explicit `NdM` strings (no gear-lookup
  integration yet — `engine/wyrd/` has no gear-entity reader), consistent with #235's own
  Assumption that plumbing not yet present in `state.py`/`character.py` is in scope to add, but a
  full gear system is not.
