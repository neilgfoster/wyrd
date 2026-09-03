# Feature Specification: Affliction table and Trauma-test cascade

**Feature Branch**: `099-affliction-table`

**Created**: 2026-09-03

**Status**: Draft

**Input**: User description: "Implement the affliction table and Trauma-test cascade (issue
#270): docs/design/08-afflictions.md's 1d12 repeatable table, fired when a Trauma test fails at
6+ Trauma (test on every point past the floor), applying each row's declared effect via the
existing points-modifier/difficulty-ladder vocabulary -- mirroring the transformation cascade
already in engine/wyrd/resolution.py."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crossing the Trauma floor stages a test, not an Affliction outright (Priority: P1)

A character whose Trauma reaches exactly 6 does not test and does not roll an Affliction — the
floor itself is free. Only the next point past it, and every point after, stages a Trauma test.

**Why this priority**: docs/design/08-afflictions.md states this explicitly ("6 is the floor,
not itself a further point") and it is the one detail most likely to be got wrong by analogy
with the Taint-threshold cascade, which *does* fire on the crossing itself.

**Independent Test**: propose a mutation taking Trauma from 5 to 6; no Trauma test is staged.
Propose a further mutation taking Trauma from 6 to 7; exactly one Trauma test is staged.

**Acceptance Scenarios**:

1. **Given** a character at Trauma 5, **When** an event raises Trauma to exactly 6, **Then** no
   Trauma test is staged.
2. **Given** a character at Trauma 6, **When** an event raises Trauma to 7, **Then** one Trauma
   test is staged for that point.

---

### User Story 2 - A single event crossing multiple points stages one test per point, in order (Priority: P1)

A "genuinely terrible event" (docs/design/03-rules.md section 5) can add more than one Trauma
point at once. Each point crossed past the floor is tested in turn, in the order gained — not
collapsed into a single test for the whole gain.

**Why this priority**: named explicitly in the design document as the multi-point case, and it
is the shape most likely to be silently flattened if a naive implementation tests the *event*
rather than the *point*.

**Independent Test**: propose a mutation taking Trauma from 5 to 8 in one event; three Trauma
tests are staged (for 6→7, 7→8... wait — the floor is 6, so points past it gained in this event
are 7 and 8 — two tests), each independently resolved.

**Acceptance Scenarios**:

1. **Given** a character at Trauma 5, **When** a single event raises Trauma to 8, **Then** two
   Trauma tests are staged, one for each point past the floor (7, then 8), resolved in that
   order.
2. **Given** a character already at Trauma 9, **When** a further event adds 2 more Trauma,
   **Then** two Trauma tests are staged, one per point gained.

---

### User Story 3 - A failed Trauma test rolls the affliction table and applies its effect (Priority: P1)

Failing a staged Trauma test rolls `1d12` against the affliction table and applies that row's
declared effect via the engine's existing points-modifier/difficulty-ladder vocabulary. A
passed test applies nothing further.

**Why this priority**: this is the cascade's payoff — without it, a Trauma test is inert and the
feature delivers nothing docs/design/03-rules.md section 5 actually promises.

**Independent Test**: force a failing Trauma test; a `1d12` roll against the affliction table
follows in the same cascade, and its row's effect is staged as a mutation. Force a passing test;
no further roll is staged.

**Acceptance Scenarios**:

1. **Given** a staged Trauma test that fails, **When** the cascade resolves, **Then** a
   `1d12` roll against the affliction table follows, and the resulting row's effect is staged,
   along with a flat 6-point reduction to Trauma (docs/design/03-rules.md section 5: "take an
   Affliction and lose 6 Trauma").
2. **Given** a staged Trauma test that passes, **When** the cascade resolves, **Then** no
   affliction roll is staged.

---

### User Story 4 - The affliction table is repeatable: the same row twice is never re-rolled (Priority: P2)

Unlike the transformation table (unique per character), the affliction table is repeatable — a
character can draw the same row more than once, and a duplicate draw stands as rolled rather
than triggering a re-roll.

**Why this priority**: this is the one structural way this family diverges from the
transformation cascade it otherwise mirrors; getting it backwards (treating it as unique) would
silently drop the design document's explicit "repeat draw is not a defect" statement.

**Independent Test**: with a character who has already taken row 3, force another `1d12` roll of
3; the second draw of row 3 is applied, not re-rolled.

**Acceptance Scenarios**:

1. **Given** a character who has already taken affliction row 3, **When** a further failed
   Trauma test rolls row 3 again, **Then** that draw is applied as-is (no re-roll).

### Edge Cases

- A Trauma test's skill is an already-decided caller input (the GM's fictional choice,
  docs/design/08-afflictions.md "the engine names no skill") — this feature does not choose it,
  the same pattern as Exposure's resist test and Fault Line bias.
- Only pass/fail matters for a Trauma test; no Wyrd-die degree reading applies to it (the design
  document states this explicitly, contrasting with the ordinary resolution rule).
- The affliction table carries no severity field and no exhaustion clause (docs/design/08-
  afflictions.md) — the roll itself does not vary its Trauma cost the way a Transformation's
  severity varies its Taint cost, but a flat 6-point Trauma reduction always follows a taken
  Affliction (docs/design/03-rules.md section 5), and there is no "table exhausted" outcome to
  detect.
- A Trauma value that never reaches 6 stages no test at all — the floor is a genuine gate, not
  merely the first tested point.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST stage a Trauma test for each point by which a `trauma` mutation
  crosses past 6 (i.e. for the sequence of integer values strictly greater than 6 that the
  mutation causes `trauma` to pass through or land on), in the order those points are gained,
  mirroring the existing threshold-cascade wiring around `taint`.
- **FR-002**: The engine MUST NOT stage a Trauma test for a mutation that only reaches Trauma 6
  without crossing past it (the floor itself is free).
- **FR-003**: A failed Trauma test MUST stage a further roll of `1d12` against the affliction
  table (key `affliction`), whose resulting row's declared effect is applied via the engine's
  existing points-modifier/difficulty-ladder mutation vocabulary.
- **FR-004**: A passed Trauma test MUST stage no further roll.
- **FR-005**: The affliction table MUST be repeatable — drawing a row a character has already
  taken before is applied as rolled, never re-rolled (contrast with the transformation table's
  unique-per-character re-roll rule).
- **FR-006**: The affliction table MUST carry the twelve rows and effects of
  docs/design/08-afflictions.md, with no severity field; taking a row MUST always reduce Trauma
  by a flat 6 points (docs/design/03-rules.md section 5), regardless of which row was drawn.
- **FR-007**: The Trauma test's skill MUST be accepted as an already-decided caller input, not
  computed or chosen by this feature.
- **FR-008**: The engine MUST expose a `terror` mechanic (docs/design/03-rules.md section 5: "a
  failed Terror test" costs 1 Trauma) as the cascade's entry point — an ordinary pass/fail test
  whose failure stages a `trauma +1` mutation, the same shape `exposure` already is for Taint.
  This is the only Trauma-gain source this feature wires up; the critical-taken and
  power-invocation Trauma sources section 5 also names remain out of scope (see Assumptions).

### Key Entities

- **Trauma**: an existing character-state field (`character.py` CHARACTER_KEYS) already present
  but currently untouched by `resolution.py`; this feature is the first to read/react to its
  mutations.
- **Afflictions**: an existing character-state field (a list of taken rows) already present in
  the schema but currently unpopulated by any cascade.
- **Affliction table**: the twelve-row, `1d12`, repeatable data table from
  docs/design/08-afflictions.md, analogous in structure to the existing
  `TRANSFORMATION_SEVERITIES`/table constants in `resolution.py` but without a severity column.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A mutation taking Trauma from 5 to 6 stages zero Trauma tests; a further mutation
  from 6 to 7 stages exactly one.
- **SC-002**: A single event taking Trauma from 5 to 8 stages exactly two Trauma tests (for
  points 7 and 8), resolved in gained order.
- **SC-003**: A failing Trauma test is always followed, in the same cascade, by exactly one
  `1d12` affliction roll and its effect's application; a passing test is followed by none.
- **SC-004**: A repeated draw of an already-taken affliction row is applied, not re-rolled — the
  full test suite contains at least one case exercising this and it passes.
- **SC-005**: `tools/check_affliction.py`'s existing sawtooth-cadence claim (1-in-6 long-run
  Affliction rate once Trauma is at/above 6, for any skill below ~83%) is unaffected by this
  feature — the check still runs and its figures still match the design document's published
  values.

## Assumptions

- docs/design/03-rules.md section 5 names three Trauma sources: a failed Terror test (1 point),
  a critical taken (1 point), and a failed system-of-power invocation's accumulated Strain
  (multiples of maximum Stamina). This feature wires up only the first, as the cascade's public
  entry point (FR-008) — criticals already stage their own mutations (docs/design/05-criticals.md,
  `resolution.py`'s existing critical tables) and wiring a Trauma point into those, and wiring
  the system-of-power Strain-threshold source, are separate concerns for whichever feature
  implements each of those mechanics; this feature's job is the Trauma-crossing cascade and the
  affliction table themselves, which any future Trauma source can trigger the same way.
- This feature implements the mechanical cascade only: staging the Trauma test(s), rolling the
  table on failure, and applying a row's effect. It does not implement Fault Line alignment
  (`docs/design/07-transformations.md`/`03-rules.md` section 4's row-12 easier-to-invoke
  reference), which — like Exposure's tier and the transformation cascade's Fault Line bias — is
  read as an already-decided input elsewhere in the engine, not computed here.
- The twelve affliction rows' effects are applied using the same mutation vocabulary the
  transformation/critical cascades already use (points modifiers, difficulty-ladder rungs,
  `stamina`/`skill`/`resolve`/`fortune` style fields) rather than inventing new mutation kinds
  per row; where a row's effect is a standing condition rather than an immediate mutation (e.g.
  row 3's "declared category of test is Challenging whenever the trigger is present"), it is
  recorded as a durable entry the caller can read back, the same shape `afflictions` already
  exists in the schema to hold.
