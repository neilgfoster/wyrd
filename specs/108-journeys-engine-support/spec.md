# Feature Specification: Journeys: engine support

**Feature Branch**: `108-journeys-engine-support`

**Created**: 2026-09-08

**Status**: Draft

**Input**: User description: "Journeys: engine support" (issue #287)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolve a journey's legs by declared mode (Priority: P1)

A GM running a journey arc needs each leg resolved the way its author declared: a `mode:
played` leg runs as an ordinary beat resolution, a `mode: summarised` leg advances through
elapsed-time. The engine must not invent a third behaviour or pick the mode itself.

**Why this priority**: Without leg-mode dispatch there is no journey subsystem at all — this is
the entry point every other capability in this feature builds on.

**Independent Test**: Given a journey arc with one `mode: played` leg and one `mode: summarised`
leg, resolving each leg produces the outcome shape appropriate to its mode, and a leg's mode is
read from its own record, never inferred.

**Acceptance Scenarios**:

1. **Given** a journey with no `pace`, **When** it is resolved, **Then** it runs as a single leg
   covering the whole route.
2. **Given** a journey with a `pace`, **When** it is resolved, **Then** its declared children are
   treated as its ordered legs.
3. **Given** a leg with `mode: played`, **When** it is resolved, **Then** the engine reports it as
   an ordinary beat resolution (no hazard-roll-specific shape imposed on it beyond the hazard
   check itself).
4. **Given** a leg with `mode: summarised`, **When** it is resolved, **Then** the engine reports
   it as an elapsed-time advance over that leg's span.

---

### User Story 2 - Hazard roll and sub-table match (Priority: P1)

A GM needs the once-per-leg hazard check to fire at the documented probability, match the
correct row of the journey's `hazards` table, and resolve that row through the core roll
against its named skill and difficulty — introducing no second resolution mechanic.

**Why this priority**: The hazard roll is the mechanical heart of a journey; without it a
journey is indistinguishable from ordinary narrated travel, which defeats the feature's purpose.

**Independent Test**: Given a journey with a known `hazard_rating` and `hazards` table and a
fixed die sequence, resolving one leg produces a deterministic activation/no-activation result,
and — on activation — a deterministic sub-table match resolved via the core roll.

**Acceptance Scenarios**:

1. **Given** a journey with `hazard_rating: 4`, **When** a leg is resolved, **Then** the hazard
   check activates when the roll is `≤ 40` and does not activate otherwise.
2. **Given** a journey with `hazard_rating: 0` (the default), **When** a leg is resolved, **Then**
   no hazard roll occurs.
3. **Given** an activated hazard and a non-empty `hazards` table, **When** the sub-table roll
   lands in one of its ranges, **Then** that entry is selected and, if it names a skill, resolved
   through the core roll against its skill and difficulty.
4. **Given** an activated hazard whose matched entry has no skill, **When** it resolves, **Then**
   it is reported as narration, not a test.
5. **Given** an activated hazard and an empty `hazards` table, **When** it resolves, **Then** the
   activation is a no-op — reported, but with no further mechanical effect.

---

### User Story 3 - Early ending and Threat's reach (Priority: P2)

A GM needs a journey that is abandoned, rerouted, or interrupted to apply consequences only for
the legs actually reached, and needs a leg that crosses an active Threat's reach to apply that
Threat's `ambient` cost — without a separate journey-versus-Threat resolution path.

**Why this priority**: Both are documented, testable edge behaviours of the same subsystem, but
neither blocks the core leg/hazard resolution above, so they land after it.

**Independent Test**: Given a journey with three legs and only the first two resolved, ending it
early is verified to report consequences for exactly those two legs. Given a leg flagged as
passing through an active Threat's reach, resolving it is verified to apply that Threat's
`ambient` cost alongside its own outcome.

**Acceptance Scenarios**:

1. **Given** a three-leg journey with only legs 1-2 reached, **When** the journey ends early,
   **Then** consequences are reported for legs 1-2 only, and leg 3 is reported as not reached.
2. **Given** a leg marked as passing through an active Threat's reach, **When** it resolves,
   **Then** the Threat's `ambient` cost is applied in addition to the leg's own resolution.
3. **Given** a leg with no Threat's reach crossing, **When** it resolves, **Then** no `ambient`
   cost is applied.

### Edge Cases

- A journey whose `hazards` table has gaps in its ranges (e.g. `1-2` and `6` but nothing for
  `3-5`): a sub-table roll landing in the gap is a no-op, the same as an empty table.
- A `mode: summarised` leg's elapsed-time advance passes through more than one active Threat:
  each is handled by the existing elapsed-time mechanism this feature reuses, not reworked here.
- A journey with `roles` declared: the engine carries the list as data only and does not gate or
  bonus anything from it (per `20-journeys.md`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST recognise a journey record (`scale: journey`) and derive its
  ordered legs from its declared children — a single implicit leg spanning the whole route when
  no `pace` is present, or its `children` in order when `pace` is present.
- **FR-002**: The engine MUST resolve a `mode: played` leg as an ordinary beat resolution and a
  `mode: summarised` leg as an elapsed-time advance, reading `mode` from the leg's own record —
  never selecting it from pacing, hazard state, or any other runtime signal.
- **FR-003**: The engine MUST roll the hazard check once per leg when the journey's
  `hazard_rating` is above zero, activating on `d100 ≤ hazard_rating × 10`, and MUST perform no
  hazard roll at all when `hazard_rating` is `0` (the default).
- **FR-004**: On activation, the engine MUST roll against the journey's `hazards` sub-table and
  select the matching entry; a roll matching no entry (including on an empty table) MUST be
  reported as a no-op with no further mechanical effect.
- **FR-005**: A matched hazard entry naming a `skill` MUST be resolved through the engine's
  existing core-roll mechanism against that skill and its stated `difficulty`; an entry with no
  skill MUST be reported as narration only, never as a test.
- **FR-006**: Ending a journey before all its legs are resolved MUST apply consequences only for
  the legs actually reached; legs not reached MUST be reported as such and MUST NOT contribute
  consequences.
- **FR-007**: A leg reported as passing through an active Threat's reach MUST have that Threat's
  `ambient` cost applied through the existing material economy, in addition to the leg's own
  outcome; a leg with no such crossing MUST NOT have any `ambient` cost applied.
- **FR-008**: The engine MUST NOT introduce a second resolution mechanic, and MUST NOT introduce
  any per-item inventory or logistics ledger, for any journey behaviour in this feature.
- **FR-009**: All consequences produced by this feature (hazard effects, early-ending, Threat
  crossing) MUST be routed through the engine's existing material-economy handling rather than a
  journey-specific ledger.

### Key Entities

- **Journey**: an arc (`scale: journey`) with `from`/`to` place references, an optional `pace`,
  an optional `hazard_rating` (default `0`), an optional `hazards` sub-table (default empty), an
  optional `roles` list (default empty, carried as data only), and an ordered list of legs.
- **Leg**: an ordinary arc or beat, a child of a journey, that additionally carries the
  `mode: played | summarised` field already defined for beats — the unit the hazard roll and
  Threat-crossing check apply to.
- **Hazard entry**: one row of a journey's `hazards` sub-table — a matched numeric range, an
  optional `skill`/`difficulty` pair, and an `effect`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A journey with no `pace` resolves as exactly one leg, and a journey with `pace`
  resolves each declared child as its own leg, in every test run.
- **SC-002**: Across a large sample of hazard rolls at a fixed `hazard_rating`, the observed
  activation rate matches `hazard_rating × 10`% within ordinary sampling tolerance, verified by a
  deterministic test using fixed die values rather than statistical sampling at runtime.
- **SC-003**: 100% of hazard activations against an empty or gap-matching `hazards` table produce
  a no-op result with no consequence applied.
- **SC-004**: 100% of early-ended journeys in test coverage report consequences for exactly the
  legs reached, never for legs beyond the ending point.
- **SC-005**: 100% of legs flagged as crossing an active Threat's reach apply that Threat's
  `ambient` cost; 100% of legs with no such flag do not.

## Assumptions

- Neither arcs, beats, Threats, nor the elapsed-time (`wyrd advance-time`) machinery have any
  runtime implementation in `engine/wyrd/` yet — this feature introduces the minimal slice of
  each (arc/leg record shape, `mode` dispatch, an active-Threat's `ambient` lookup, and an
  elapsed-time advance stub) needed to resolve a journey, rather than a general-purpose
  arc/campaign engine. Building the full campaign layer is out of scope; only what a journey's
  own resolution needs is implemented, and it is implemented so a later general arc/beat/Threat
  feature can extend it rather than replace it.
- "The core roll" refers to the engine's existing `resolution.propose`/`commit` mechanism
  (`docs/design/03-rules.md`); a hazard entry with a skill is resolved by constructing an
  ordinary test request against that mechanism, not a new one.
- "The existing material economy" refers to the engine's existing Standing/coin/condition
  handling (`economy.py` and related); this feature calls into it rather than re-implementing
  consequence application.
- Journey, leg, and Threat records are passed to the engine as plain data (dicts) by the caller,
  consistent with every other module in `engine/wyrd/` — this feature does no file/entity
  loading from a setting repository, matching the engine's existing separation between engine
  and setting content.
- A "leg passing through a Threat's reach" is caller-declared input (a flag or reference on the
  leg record), not something this feature computes from geography — the engine has no spatial
  model to derive reach-crossing from.
