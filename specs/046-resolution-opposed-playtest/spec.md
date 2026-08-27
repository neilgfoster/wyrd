# Feature Specification: Resolution and opposed-tests playtest

**Feature Branch**: `046-resolution-opposed-playtest`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Resolution and opposed-tests playtest (closes #147, part of the playtest epic #134). Extends specs/014-r3-prove-ruleset-on-paper's precedent (a single creation + combat exchange) to the ordinary-test shape and opposed tests specifically, in isolation from combat's fixed two-sided form."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader trusts the resolution rule plays as designed, not just as computed (Priority: P1)

Someone who has read `tools/check_probability_coverage.py`'s computed claims about resolution
wants confidence the rule also survives being *played* — real dice, real declared attempts, real
edge cases — the way #14/R3 proved for creation and one combat exchange.

**Why this priority**: This is #134's own stated purpose: CLAUDE.md records the one existing
playtest correcting the resolution mechanic three times inside two rolls, "none of it visible on
paper." Individual computed checks don't exercise the same failure mode a played sequence does.

**Independent Test**: Read the new playtest section in `docs/design/30-playtest-transcript.md`
and confirm every attempt resolves against `03-rules.md` §1's stated formulas without an invented
judgement call.

**Acceptance Scenarios**:

1. **Given** a real, seeded random-number sequence (not a curated one, per the existing #14/R3
   precedent's own discipline), **When** every difficulty tier, declaration quality, an untrained
   attempt, an assisted attempt, and the player-facing opposed-test shape are each played through
   at least once, **Then** every result matches what `03-rules.md` §1 and #139's reworked
   untrained-attempt table already state.
2. **Given** an attempt already impossible before the die is thrown (e.g. Very Hard on a barely
   trained skill), **When** it is reached in the sequence, **Then** no die is drawn for it — the
   same "no die drawn here is thrown away" discipline #14/R3's combat exchange established, held
   to for the inverse case too (no die drawn that shouldn't have been).

### User Story 2 - Any fault found is corrected or explicitly justified (Priority: P1)

If the playtest surfaces a genuine gap or contradiction (the shape #14/R3 found in character
creation), it gets fixed in place or recorded as an explicit, deliberate non-issue — never left
implicit.

**Why this priority**: #134's own Definition of Done requires this discipline for every child.

**Independent Test**: Read the new section's Findings subsection; confirm it states plainly
whether anything was found, and if so, what was done about it.

**Acceptance Scenarios**:

1. **Given** the playtest run, **When** it completes, **Then** its Findings subsection states
   either "no fault found" or names each fault and its resolution.

### Edge Cases

- A natural roll of 100 came up during this playtest (Difficult, effective% 15). Does the
  resolution rule need a special case for it? No — confirmed during play: "at or under" already
  fails a 100 against any skill under 100 (skills never reach 100% given the 70% career cap), and
  its units digit (0) reads as an Ill Omen with no exception needed.
- Does a failed roll report degrees? No — confirmed against `03-rules.md` §1's own wording
  ("degrees of success") and #14/R3's own combat exchange, which already established "No degrees
  (degrees only exist on a success)." This playtest follows that same convention rather than
  computing a negative degrees figure for failures.
- The two-player-controlled-entities contest (no NPC/opponent side) — does it need its own roll
  formula? No — `03-rules.md` §1 already states it resolves as one ordinary test on whichever side
  the GM names, or two separate ordinary tests; playing it through confirms nothing further is
  needed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The playtest MUST use a real, seeded random-number sequence, not a curated
  sequence chosen to hit interesting cases — matching #14/R3's own established discipline.
- **FR-002**: The playtest MUST exercise every difficulty tier from the ladder, at least one
  attempt at each of the three declaration-bonus levels, at least one untrained attempt at each
  legal difficulty (per #139's reworked table), at least one assisted attempt, and the
  player-facing opposed-test shape.
- **FR-003**: No die MUST be drawn for an attempt already impossible before it is thrown.
- **FR-004**: Degrees MUST be reported only on a success, per `03-rules.md` §1's own convention.
- **FR-005**: The playtest record MUST state its Findings explicitly — either no fault found, or
  each fault and its resolution — never left implicit.
- **FR-006**: Any correction to `docs/design/` found necessary MUST land through the ordinary
  Spec Kit / ADR discipline (per #134's Definition of Done), not silently folded into this
  feature's own diff unless it is a trivial in-place fix of the same shape #14/R3 made.

### Key Entities

*(none — this feature is a worked playtest record, no new data)*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/design/30-playtest-transcript.md` gains a new section covering resolution and
  opposed tests, following the existing document's established structure and tone.
- **SC-002**: Every attempt in the new section's tables is traceable to a real `python3 random`
  draw, seeded, in a stated fixed order.
- **SC-003**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py` pass,
  with no new finding class introduced (pre-existing false-positive patterns for difficulty-tier
  names and character names are expected and tolerated, per repo convention).
- **SC-004**: `python3 -m pytest -q` passes with no regression.

## Assumptions

- This feature does not create a `specs/` subdirectory with the depth #14/R3 itself used (that
  feature had none at all — it was a direct commit against `docs/design/`) but follows this
  session's own established practice of writing spec/plan/tasks artifacts for traceability,
  consistent with every other feature driven this session.
- Documentation-only: the playtest itself found no fault requiring a design correction (see
  Findings in the new section), so this feature carries no ADR and no capability change — only
  #134's own coverage requirement is being met.
- Extended tasks, the Bargain, and Fortune's spend options are explicitly out of scope for this
  feature — they belong to other playtest-epic children (#150 for economy-adjacent mechanics;
  none currently scoped for Fortune specifically, noted as a residual gap in the new section's own
  "what this pass does not prove").
