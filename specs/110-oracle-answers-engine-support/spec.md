# Feature Specification: Oracle answers engine support

**Feature Branch**: `110-oracle-answers-engine-support`

**Created**: 2026-09-09

**Status**: Draft

**Input**: User description: "Oracle answers: engine support — implement docs/design/14-oracle-
answers.md as engine code: given a GM-declared likelihood band and a rolled (or engine-rolled)
1d100, resolve and return the correct oracle answer for that band, reusing the existing Wyrd die
machinery rather than inventing new randomness plumbing. Issue #291."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resolving an oracle-bound question (Priority: P1)

A GM has asked a yes/no question of fact the fiction hasn't settled, and has declared a
likelihood band for it (per docs/design/14-oracle-answers.md's five bands). The GM asks the
engine to resolve the oracle roll and gets back the natural `1d100` roll, the outcome
(`exceptional_yes`, `yes`, `no`, or `exceptional_no`), and the Wyrd die reading from that same
roll's units digit, ready to narrate and record.

**Why this priority**: This is the entire mechanism. Every band shares this same four-row lookup
shape; nothing else in this feature exists without it.

**Independent Test**: Call the lookup for each of the five band names with a roll spanning every
row of that band's table (including every boundary row) and confirm each returns exactly the
outcome docs/design/14-oracle-answers.md declares for that range.

**Acceptance Scenarios**:

1. **Given** a roll of 40, **When** the `Even` band (T=50) is resolved, **Then** the engine
   returns outcome `yes`.
2. **Given** a roll of 1, **When** any band is resolved, **Then** the engine returns
   `exceptional_yes` (every band's row 1-5 is fixed).
3. **Given** a roll of 100, **When** any band is resolved, **Then** the engine returns
   `exceptional_no` (every band's row 96-100 is fixed).
4. **Given** a roll of exactly a band's threshold `T` (e.g. 90 for `Near Certain`), **When** that
   band is resolved, **Then** the engine returns `yes` — the threshold total itself is the last
   `yes` row, not the first `no` row.
5. **Given** a roll of `T+1` for a band, **When** that band is resolved, **Then** the engine
   returns `no` — the first row past the threshold.

---

### User Story 2 - An unrecognized band is a load error (Priority: P2)

A caller asks the engine to resolve a band name that isn't one of the five declared in the
design document (a typo, or a setting mistakenly inventing a sixth band). The engine refuses
rather than silently returning nothing or crashing uninformatively.

**Why this priority**: Matches this engine's existing convention (`resolution.py`'s
`_critical_band`: "an unrecognized damage type is a load error, not a table quietly skipped"),
and the same convention `journey.roll_hazard` and the oracle-prompt lookup already follow —
consistency with sibling table lookups, not new behaviour this feature invents.

**Independent Test**: Call the lookup with a band name not in the closed set of five and confirm
it raises a clear, catchable error rather than returning a value or an unhandled exception.

**Acceptance Scenarios**:

1. **Given** a band name of `"Certain"` (not one of the five), **When** it is resolved, **Then**
   the engine raises an error naming the closed set of valid band names.

---

### Edge Cases

- A roll must be a natural `1d100` result in the range 1-100 inclusive; a value outside that
  range is a caller error (same convention as `journey.roll_hazard` and the oracle-prompt
  lookup).
- The Wyrd die reading (units digit: `0` Ill Omen, `9` Fair Omen, else none) is read from the
  same natural roll, reusing the engine's existing Wyrd-die logic rather than a second read of
  the same digit implemented independently.
- This feature does not write to any entity's persisted state, and does not itself write a beat
  log entry — per the design document's Recording section, the roll/band/outcome/wyrd tuple is
  surfaced for the caller (the GM, or the engine's beat-recording layer) to log, the same
  separation `journey.roll_hazard` already keeps between resolving a table and recording its
  result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a lookup, keyed by one of the five band names declared in
  docs/design/14-oracle-answers.md (`Near Certain`, `Likely`, `Even`, `Unlikely`,
  `Near Impossible`), that maps a natural `1d100` roll to that band's outcome
  (`exceptional_yes`, `yes`, `no`, `exceptional_no`), exactly as the design document's table and
  per-band thresholds declare.
- **FR-002**: Each band's four rows MUST cover 1-100 contiguously with no gaps and no overlaps,
  matching the design document exactly for every one of the five published thresholds
  (`90, 70, 50, 30, 10`) — a property already computed and asserted by
  `tools/check_oracle_answers.py`, which this feature's own data must stay consistent with.
- **FR-003**: The lookup MUST reject a band name outside the closed set of five with a clear
  error, rather than returning an empty/null result or an unhandled exception.
- **FR-004**: The engine MUST expose this lookup as a callable, taking a band name and a natural
  `1d100` roll, and returning the roll, the outcome, and the Wyrd die reading for that same roll
  — reusing the engine's existing Wyrd-die read rather than a second implementation of the
  units-digit rule.
- **FR-005**: The lookup MUST NOT perform its own dice roll; the caller supplies the natural
  `1d100` result, matching this engine's existing split between randomness and banding
  (`resolution.py`, `journey.roll_hazard`).
- **FR-006**: This feature MUST NOT write to any entity's persisted state, and MUST NOT itself
  write a beat log entry; the lookup is a pure function returning content for the caller to
  narrate and record.
- **FR-007**: The lookup MUST be wired into wherever the engine already dispatches other
  table-family rolls (the verb catalog / dispatch pattern the oracle-prompt lookup and other
  recent table families use), so it is reachable the same way sibling families are.

### Key Entities

- **Oracle-answer band**: one of the five band names; four (range, outcome) rows covering 1-100
  contiguously, parameterised by the band's Yes-threshold `T`. Data only — this feature adds no
  new persisted entity type.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For all five band names, every integer roll 1-100 resolves to exactly the outcome
  the design document declares for that range — verified exhaustively, not sampled.
- **SC-002**: `tools/check_oracle_answers.py` runs to completion and passes unchanged.
- **SC-003**: `python3 -m pytest -q` (under `PYTHONPATH=engine`), `python3 -m ruff check .`,
  `python3 -m ruff format --check .`, `python3 tools/check_docs.py`, and `python3
  tools/backlog.py check` are all clean after this feature lands.
