# Feature Specification: Scenario index schema and deterministic selection (scenarios.json)

**Feature Branch**: `135-scenario-index-schema`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Scenario index schema and deterministic selection (scenarios.json)" (issue #356)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A scenario record's deterministic fields are validated (Priority: P1)

A scenario record (`id`, `scale`, `region`, `danger`, `written_for`, `length`, `season`,
`needs_access`, `needs_capability`, `helped_by`, `settings`) is checked against the schema
before anything downstream (selection, scaling) trusts it — a closed vocabulary for `scale` and
`season`, and sane types for the rest.

**Why this priority**: every other function in this feature reads these fields — nothing else
can safely run against a record whose shape hasn't been checked.

**Independent Test**: given a record with an out-of-vocabulary `scale` value, confirm it is
rejected; given a fully valid record, confirm it passes unchanged.

**Acceptance Scenarios**:

1. **Given** a record whose `scale` is one of the nine documented values (`village`, `town`,
   `city`, `wilderness`, `underground`, `waterway`, `road`, `ship`, `fortress`), **When** it is
   validated, **Then** it passes.
2. **Given** a record whose `scale` is outside that vocabulary, **When** it is validated,
   **Then** it is rejected, naming the offending field.
3. **Given** a record whose `season` is `any` or one of `winter`/`harvest`/`festival`, **When**
   it is validated, **Then** it passes; any other value is rejected.

---

### User Story 2 - Party size scales danger; it never gates (Priority: P1)

"Almost nothing gates. Most things modulate." A scenario's `danger` is scaled against the actual
party through the engine's existing formula — never used to exclude the scenario outright.

**Why this priority**: this is the design document's own central claim about this index — the
library is too valuable to filter aggressively — and it is the one rule easiest to get backwards
(treating `written_for` as a minimum party size rather than a scaling input).

**Independent Test**: given a scenario's `danger`/`written_for` and an actual party size, confirm
the scaled result matches `adversary.danger_effective` exactly for the same inputs — never a
different formula, and never a rejection based on party size alone.

**Acceptance Scenarios**:

1. **Given** a scenario written for 4, played by a party of 6, **When** danger is scaled,
   **Then** the result equals `adversary.danger_effective(danger, 6, 4)` exactly.
2. **Given** a scenario played by a party of 1, **When** danger is scaled, **Then** it still
   produces a scaled value (via the existing effective-party-size arithmetic) — never a
   rejection for being "too small a party."

---

### User Story 3 - Access and capability are checked as requirements, never as filters (Priority: P2)

`needs_access`/`needs_capability` are things that must be supplied by someone — the player
character, a companion, or hired help — and obtaining them may itself become play. `helped_by`
is a flag only. None of the three excludes a scenario from selection.

**Why this priority**: this is the design's second explicit warning against over-filtering — a
low-status character can still be smuggled into a scenario that lists `needs_access` they don't
have; excluding it outright would silently discard "the better scenario" the design calls out.

**Independent Test**: given a scenario whose `needs_access`/`needs_capability` are not currently
met by a party, confirm the check reports which are unmet — informational, never a rejection —
and that `helped_by` is reported the same informational way regardless of whether it's met.

**Acceptance Scenarios**:

1. **Given** a scenario requiring `needs_access: [temple]` and a party with no listed access,
   **When** requirements are checked, **Then** the result reports `temple` as unmet, and the
   scenario itself is still returned (not filtered out).
2. **Given** a scenario's `helped_by` list and a party that meets none of it, **When**
   requirements are checked, **Then** the result still reports which `helped_by` entries are met
   (possibly none) — `helped_by` is reported, never used to exclude.

### Edge Cases

- A scenario record whose `settings` list does not include the caller's target setting is the
  one genuine hard exclusion this feature implements — matching the design's own "the genuine
  exclusions are few: wrong setting" statement.
- A record with empty `needs_access`/`needs_capability`/`helped_by` lists reports all
  requirements trivially met, never an error.
- `adaptation: rewrite`'s cost-not-worth-paying judgment (the design's second named exclusion) is
  explicitly a GM call, not automated by this feature (spec.md's Assumptions) — this feature
  reports `adaptation` unchanged for the caller to weigh, never excludes on it itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST validate a scenario record's `scale` against a closed, nine-member
  vocabulary (village/town/city/wilderness/underground/waterway/road/ship/fortress).
- **FR-002**: The engine MUST validate a scenario record's `season` against `any` or one of
  `winter`/`harvest`/`festival`.
- **FR-003**: The engine MUST reject a record failing either check, naming the offending field.
- **FR-004**: The engine MUST provide a way to scale a scenario's `danger` against an actual
  party size via `adversary.danger_effective`, unchanged — no second scaling formula.
- **FR-005**: Scaling MUST NOT reject or exclude a scenario for any party size — a party size is
  always a valid scaling input.
- **FR-006**: The engine MUST provide a way to check a scenario's `needs_access`/
  `needs_capability` against a party's currently-available access/capability, reporting each as
  met or unmet — never filtering the scenario out.
- **FR-007**: The engine MUST provide a way to report which of a scenario's `helped_by` entries
  a party currently satisfies — informational only, never a filter.
- **FR-008**: The engine MUST provide a way to check a scenario's `settings` list against a
  target setting, as the one genuine hard exclusion this feature implements.

### Key Entities

- **Scenario record** (docs/design/26-corpus-index.md § "5. scenarios.json"): this feature's
  own concern is its deterministic fields only — `id`, `settings`, `scale`, `region`, `danger`,
  `written_for`, `length`, `season`, `needs_access`, `needs_capability`, `helped_by`,
  `adaptation`. The model-generated fields (`tone`, `themes`, `shape`) and the graph fields
  (`requires_threads`, `emits_threads`, `chain`) are read/passed through unchanged, never
  validated or interpreted by this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the nine `scale` values and all four `season` values validates
  correctly; every out-of-vocabulary value is rejected — verified by exact-input tests.
- **SC-002**: Scaled danger always exactly equals `adversary.danger_effective`'s own output for
  the same inputs, across a range of party sizes including a party of one.
- **SC-003**: A requirement check never removes a scenario from consideration — only annotates
  it — verified across met, unmet, and empty-requirement cases.
- **SC-004**: The setting check correctly separates an eligible scenario from an ineligible one
  by `settings` membership alone.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts/lists in, plain dicts out, no I/O —
  matching #354/#355's `corpus_document.py`/`corpus_terms.py` convention.
- The thematic fields (`tone`, `themes`, `shape`) are model-generated elsewhere ("Haiku-tier",
  docs/design/26-corpus-index.md) — out of scope here entirely; this feature never reads or
  validates them.
- Thread-graph matching (`requires_threads`/`emits_threads` against currently-hot threads) is
  already implemented by `scenario_selection.py` (#339) — this feature does not duplicate that
  machinery; it only validates/scales/checks the scenario record's own deterministic fields that
  feed into it.
- `adaptation: rewrite`'s "not worth paying today" judgment is explicitly a GM call the design
  document itself frames as judgment, not a deterministic rule — this feature passes `adaptation`
  through unchanged rather than encoding a threshold for when a rewrite is "worth it."
- Party size never gates scaling (FR-005) even at a party of one, since
  `adversary.danger_effective`'s own effective-party-size arithmetic (`1 + 1/2 + ... + 1/n`,
  #98) already produces a sensible ratio at any positive party size; a party of `0` is out of
  scope here (matches `adversary.danger_ratio`'s own existing behaviour, unchanged).
