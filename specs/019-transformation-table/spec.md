# Feature Specification: The transformation table

**Feature Branch**: `019-transformation-table`

**Created**: 2026-08-26

**Status**: Draft

**Input**: Issue [#18](https://github.com/neilgfoster/wyrd/issues/18) — define the transformation
table (`docs/design/10-transformations.md`): the Taint thresholds, a severity per row, proof the
threshold re-roll loop terminates, the body-versus-mind split, the hidden threshold, and Dread.

## Why this exists

`docs/design/03-rules.md` §4 makes Transformation the entire consequence layer of Taint and defines
none of it: no threshold values, no table, no severities. Severity is load-bearing in a way most
tables are not — it is what terminates the re-roll loop when a threshold is crossed, and a wrong
severity would not look wrong on the page (`CLAUDE.md`'s fault class 4). Section 4 also reads as
forcing "a Transformation (body) or an Affliction (mind)" at a threshold, which collides with §5:
Afflictions arise only from Trauma reaching 6+, a separate track. That collision (fault class 3 —
two documents, or here two sentences of the same document, describing one thing differently) is
resolved as part of this feature.

Two further mechanics hang off the table and exist only as prose today: the hidden threshold
(rolled secretly, never shown, and what "lost, joins the opposition" concretely does), and Dread
(Taint's social cost).

## Clarifications

None raised — the issue's acceptance criteria, `03-rules.md` §1's Wyrd-die bands, and
`03a-tables.md`'s conventions (#15, already merged) together bound every open question this
feature needed to answer. Where the issue left a numeric scheme unspecified (the exact threshold
spacing, the severity distribution, Dread's magnitude), a concrete choice is made and recorded in
[ADR 0029](../../docs/adr/0029-transformation-thresholds-at-every-three-taint.md) rather than
raised as a clarification question, because a reasonable default existed and the issue asked for a
computed, defensible scheme rather than for a specific one.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A character crosses a Taint threshold (Priority: P1)

A character's Taint rises past a threshold during play (the Bargain, Exposure, or Invocation). The
GM rolls on the transformation table, applies the row's severity against Taint, and re-rolls if
Taint is still at or over the threshold — reading the result's description in the character's own
idiom, never as a raw number.

**Why this priority**: this is the mechanic the issue exists to define; nothing else in scope
functions without it.

**Independent Test**: run `tools/check_transformation.py` and confirm every scanned Taint value
and event-gain combination resolves the loop within the table's row count.

**Acceptance Scenarios**:

1. **Given** a character at Taint 2, **When** Exposure adds 1 Taint (Taint 3), **Then** the
   threshold at 3 is crossed, one roll is made, and its severity drops Taint back below 3.
2. **Given** a character at Taint 5, **When** a 3-point Exposure event adds Taint (Taint 8),
   **Then** the threshold at 6 is crossed, and the GM re-rolls (drawing a new, unique row each
   time) until Taint is back below 6, which the computed worst case bounds at 3 re-rolls.

---

### User Story 2 - The first Transformation sets the hidden threshold (Priority: P2)

The first time a character takes a Transformation, the GM secretly rolls the hidden threshold and
writes it to state once. It is never shown to the player, in any form.

**Why this priority**: it is the mechanic that gives later Transformations their weight, and it
must never leak — a rendering bug here would violate `10-diegesis.md`'s "never shown" class.

**Independent Test**: inspect `chronicle.yaml` after a first Transformation and confirm the hidden
threshold is written once and is absent from every player-facing rendering path.

**Acceptance Scenarios**:

1. **Given** a character taking their first Transformation, **When** it resolves, **Then** the GM
   rolls 1d6+2 once, writes it to state, and it is never re-rolled for that character again.
2. **Given** a character whose Transformation count reaches their hidden threshold, **When** the
   next Transformation would apply, **Then** the character is instead removed from the party and
   becomes an opposition-controlled character.

---

### User Story 3 - A transformed character is seen (Priority: P3)

A transformed character is encountered by someone unfamiliar with their change. Their accumulated
Dread penalises the other party's reaction toward them.

**Why this priority**: this is the social consequence the issue names as Dread's whole purpose,
but it is the third mechanic in the chain and depends on the first two existing.

**Independent Test**: given a character with a known Dread total, confirm a reaction test toward
them by an unfamiliar party applies the stated penalty, clipped the same way every other points
modifier in the engine is.

**Acceptance Scenarios**:

1. **Given** a character with Dread 3, **When** a stranger reacts to them, **Then** the reaction
   test is penalised by 3 points, on the same ladder Taint scaling and difficulty already use.

### Edge Cases

- What happens when a single event's Taint gain is large enough to cross more than one threshold
  at once? Out of scope in practice — the Bargain and Exposure cap a single event at 3 Taint, and
  the threshold spacing (3) means at most one threshold is newly crossed per event; this is stated
  explicitly in `03a-3-transformations.md`.
- What happens when the transformation table itself is exhausted before the hidden threshold is
  reached? Read identically to the hidden threshold running out — the character is lost — though
  the design document notes this is not expected to be reachable given the hidden threshold's
  range (3–8) versus the table's six rows.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The design MUST state concrete numeric Taint threshold values, anchored on the
  Wyrd-die bands already in `03-rules.md` §1.
- **FR-002**: The transformation table MUST carry a severity on every row, following
  `03a-tables.md`'s row schema and roll conventions.
- **FR-003**: The design MUST prove, by computation (a committed script), that the threshold
  re-roll loop terminates, showing expected and worst-case re-roll counts at realistic Taint
  values.
- **FR-004**: The design MUST state, once and unambiguously, that a Taint threshold always forces
  a Transformation and never an Affliction, and that Afflictions arise only from Trauma.
- **FR-005**: The design MUST specify the hidden threshold's roll, its range, that it is written to
  state once and never re-rolled, and what happens to the chronicle when it is exhausted.
- **FR-006**: The design MUST specify Dread's magnitude per Transformation and its effect when a
  transformed character is seen.
- **FR-007**: `docs/design/03-rules.md` §4 MUST be updated in place to match, without changelog
  language.
- **FR-008**: `docs/design/07-tables.md`'s index MUST carry the transformation family's row, no longer
  marked "not yet written".
- **FR-009**: No setting or system name may appear anywhere the change touches in `design/`,
  verified by grep. No row may bake in a tonal register.
- **FR-010**: Nothing produced may require showing the hidden threshold to the player, in any form.

### Key Entities

- **Transformation table**: six rows, each with a range, an effect, a description, and a severity;
  unique per character.
- **Hidden threshold**: a per-character, GM-only integer written once to `chronicle.yaml`.
- **Dread**: a per-character running total, incremented by each Transformation's severity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The re-roll loop's worst case, scanned across Taint 0–20 and every legal single-event
  gain, never exceeds the table's row count (6), and is demonstrated, not asserted.
- **SC-002**: `tools/check_docs.py` and `tools/backlog.py check` both pass after the change.
- **SC-003**: A grep for setting/system vocabulary across the new and changed `design/` files
  returns no unexpected match.

## Assumptions

- The affliction table (#19) has not landed; this document owns the body-versus-mind statement per
  the issue's own instruction that "whichever lands first should own it."
- A concrete threshold-spacing and severity scheme is this feature's to choose, since the issue
  asks for *a* defensible numeric scheme, not a specific one; the choice is recorded in
  [ADR 0029](../../docs/adr/0029-transformation-thresholds-at-every-three-taint.md).
- No engine code exists yet for this family (the engine is design-first, per `07-tooling.md`); this
  feature's deliverable is the design document, its script, and the ADR, matching the shape of
  prior table-family issues (#15's conventions, #17's adversary model).
