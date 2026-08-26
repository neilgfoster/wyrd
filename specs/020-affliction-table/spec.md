# Feature Specification: The affliction table

**Feature Branch**: `020-affliction-table`

**Created**: 2026-08-26

**Status**: Draft

**Input**: Issue [#19](https://github.com/neilgfoster/wyrd/issues/19) — define the affliction
table (`docs/design/11-afflictions.md`): the test at 6+ Trauma, a table large enough to survive a
chronicle measured in years, what happens on a repeat draw, the Taint-threshold route, and the
sawtooth rate computed at real accrual figures.

## Why this exists

`docs/design/03-rules.md` §5 specifies the Affliction *track* precisely (test on every Trauma point at
6+, lose 6 Trauma on a failure, sawtooths across years) and its *contents* not at all — no table,
no named test, no target number. It also carries the engine's sharpest presentation constraint for
this family: "an Affliction is never described as an Affliction — it is described as behaviour," so
a row phrased as a diagnosis is a defect, not a style choice.

The body-versus-mind collision §4 used to read ("a Transformation (body) or an Affliction (mind)"
at a Taint threshold) is already resolved: `docs/design/10-transformations.md` (#18, merged) states
that a Taint threshold always forces a Transformation and never an Affliction, and that Afflictions
are Trauma's business alone. This feature does not reopen that; it inherits it and defines the
Trauma-side table the resolution promised.

Because this track sawtooths rather than terminating, it carries a requirement most tables in this
engine do not: it has to stay interesting across a chronicle that rolls on it repeatedly for years,
which means it must be **large enough not to repeat quickly** and must say what a repeat draw does.

## Clarifications

None raised — `03-rules.md` §5's accrual rates (1 Trauma per critical, 1 per failed Terror test),
`03a-tables.md`'s conventions (#15, merged), and `03a-3-transformations.md`'s already-settled
body/mind split (#18, merged) together bound every open question this feature needs to answer.
Two numeric choices this feature must still make — the test target for "test on every further
point," and the table's size/repeat-draw rule — have no value stated anywhere upstream; concrete,
defensible choices are made here and recorded in an ADR if a real alternative was rejected, per
`CLAUDE.md`'s bar for when a decision earns one.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A character's Trauma crosses 6 and keeps rising (Priority: P1)

A character's Trauma reaches 6 (from a critical taken or a failed Terror test) and continues to
rise. On every further point, the GM calls for a test; on a failure, the character rolls on the
affliction table, takes the row's behaviour, and Trauma drops by 6.

**Why this priority**: this is the mechanic the issue exists to define; nothing else in scope
functions without it.

**Independent Test**: run the feature's check script and confirm the sawtooth rate is computed
(not asserted) at the accrual rates §5 already specifies, at real Trauma trajectories a character
could plausibly reach across a chronicle.

**Acceptance Scenarios**:

1. **Given** a character at Trauma 5, **When** a critical taken raises Trauma to 6, **Then** no
   test fires yet — 6 is the floor, not itself a further point.
2. **Given** a character at Trauma 6, **When** a failed Terror test raises Trauma to 7, **Then**
   the test at the stated target fires; on a failure the character rolls on the affliction table
   and Trauma drops to 1.

---

### User Story 2 - A character draws an Affliction they already carry (Priority: P2)

The unique-per-character convention (`03a-tables.md`) means a repeat draw needs a stated
resolution, the same way the transformation table needed one.

**Why this priority**: the sawtooth means this will happen in any chronicle long enough to matter;
an undefined repeat draw is a table that stops working exactly when it is depended on most.

**Independent Test**: given a character already holding every row up to some count, confirm the
document states — and the check script exercises — what a duplicate roll does, and what happens if
the table is ever exhausted.

**Acceptance Scenarios**:

1. **Given** a character who already holds the row a fresh roll lands on, **When** the roll
   resolves, **Then** the stated repeat-draw rule applies (a defined re-roll, deepen, or
   equivalent — not silence).
2. **Given** a character who holds every row the table has, **When** a further Affliction test is
   failed, **Then** the stated exhaustion outcome applies.

---

### User Story 3 - The table is read against the rest of the mental-harm chain (Priority: P3)

Strain, Trauma and Afflictions are three tiers of one chain (§5); a failed Terror test feeds
Trauma, which feeds this table. The numbers have to compose without silently double-counting or
leaving a gap.

**Why this priority**: the issue calls this out explicitly as a maths check, not a detail — a wrong
composition here is exactly `CLAUDE.md`'s "tables are where staleness hides" fault class, because
each individual number reads as a small, plausible claim.

**Independent Test**: the check script computes, at the accrual rates already specified, how often
a character reaches 6+ Trauma and how many Afflictions a long chronicle produces, and the design
document states that computed figure rather than an intuited round number.

**Acceptance Scenarios**:

1. **Given** the accrual rates in §5 (1 per critical, 1 per failed Terror test), **When** the
   sawtooth rate is computed across a plausible chronicle length, **Then** the resulting cadence
   is stated in the design document as a computed figure, and is neither implausibly frequent
   ("one every two sessions") nor implausibly rare ("one every ten years") without that being
   called out as a finding.

### Edge Cases

- What happens when a character's Trauma is pushed from below 6 to well above it in one jump (a
  GM-discretion "genuinely terrible event" adding more than 1)? §5 allows the GM discretion to add
  more than 1 Trauma for such events; this document must state whether that still tests once or
  once per point crossed, since the base rule ("test on every further point") implies the latter.
- What happens when a table result is drawn while Trauma is already below what a single test's
  6-point drop would leave non-negative? Trauma cannot go below 0; the design document states the
  floor explicitly.
- What happens when the affliction table is exhausted (every row already held) and a further test
  is failed? Must be stated — plausibly reachable in a long chronicle, unlike the transformation
  table's hidden threshold, since this track has no analogous hard cap on total draws.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The design MUST name the test made "on every further point" past 6 Trauma —
  what is rolled and what it is tested against — following the resolution conventions already in
  `03-rules.md` §1.
- **FR-002**: The affliction table MUST carry rows large enough that a chronicle measured in years
  does not repeat quickly at the computed sawtooth rate, following `03a-tables.md`'s row schema.
- **FR-003**: Every row MUST be phrased as behaviour the character exhibits, never as a named
  condition or diagnosis, and MUST carry a mechanical effect the engine can apply without reading
  the prose.
- **FR-004**: The design MUST state what happens when a roll draws an Affliction the character
  already holds (`03a-tables.md`'s uniqueness convention), and what happens if the table is ever
  exhausted.
- **FR-005**: The design MUST restate — matching, not re-deriving — `03a-3-transformations.md`'s
  settled body/mind split: a Taint threshold never produces an Affliction, and Afflictions arise
  only from Trauma reaching 6+.
- **FR-006**: The design MUST compute, by a committed script, the sawtooth rate at the accrual
  rates §5 already specifies (1 Trauma per critical, 1 per failed Terror test), and state the
  resulting figure — flagged as a finding if implausibly frequent or rare.
- **FR-007**: `docs/design/03-rules.md` §5 MUST be updated in place to match, without changelog
  language.
- **FR-008**: `docs/design/07-tables.md`'s index MUST carry the affliction family's row, no longer
  marked "not yet written".
- **FR-009**: No setting or system name may appear anywhere the change touches in `design/`,
  verified by grep. No row may bake in a tonal register or presume a particular moral reading of
  mental harm.

### Key Entities

- **Affliction table**: N rows (sized against the computed sawtooth rate), each with a range, an
  effect, and a description phrased as behaviour; unique per character.
- **Trauma test**: the named test fired on every Trauma point past 6, with its target number.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The sawtooth rate — Afflictions per chronicle-year at the specified accrual rates —
  is demonstrated by a committed script, not asserted.
- **SC-002**: `tools/check_docs.py` and `tools/backlog.py check` both pass after the change.
- **SC-003**: A grep for setting/system vocabulary across the new and changed `design/` files
  returns no unexpected match.

## Assumptions

- The transformation table (#18) has already landed and owns the body/mind split; this feature
  restates it in `03a-4-afflictions.md` for a reader who starts there, rather than re-arguing it.
- No engine code exists yet for this family (the engine is design-first, per `07-tooling.md`); this
  feature's deliverable is the design document, its check script, and an ADR if the numeric choices
  made (test target, table size, repeat-draw rule) reject a real alternative worth recording.
- A chronicle "measured in years" is read, for sizing purposes, against the session cadence and
  advancement rate already implied by §6 (1–3 advances per session), giving the check script a
  concrete session-per-year figure to compute against rather than an unstated one.
