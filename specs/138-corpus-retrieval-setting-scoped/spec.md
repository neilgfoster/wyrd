# Feature Specification: Corpus retrieval is scoped to a setting, never unfiltered

**Feature Branch**: `138-corpus-retrieval-setting-scoped`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Corpus retrieval is scoped to a setting, never unfiltered" (issue #364)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A query can never return another setting's material (Priority: P1)

Every `corpus_find.py` (#357) query function now requires the caller to state which setting it's
querying for, and filters every result to that setting before applying any other criterion — so
an index that happens to carry records from more than one setting can never leak a cross-setting
result into a chronicle that has no business seeing it.

**Why this priority**: docs/design/21-parallel-chronicles.md states this as a GM-contract MUST —
"the corpus is queried with the setting as a filter, never unfiltered" — and #357's original
five functions had no such filter at all.

**Independent Test**: given an index containing records from two different settings, confirm a
query for setting A never returns a record whose own `setting` (or `settings` membership, for
scenarios) is B, even when every other criterion would otherwise match.

**Acceptance Scenarios**:

1. **Given** a concordance/term/table/document index containing postings/records from settings
   `A` and `B`, **When** any query names `setting="A"`, **Then** no result carrying `setting: "B"`
   is ever returned, regardless of whether the query's other criteria would match it.
2. **Given** a scenario index whose records each carry a `settings` list, **When** a query names
   `setting="A"`, **Then** only records whose `settings` list contains `"A"` are returned.
3. **Given** a query with `setting` omitted, **When** the call is made, **Then** it is rejected
   at the language level (a required argument, not an optional filter) — there is no way to call
   any of the five functions unscoped.

### Edge Cases

- A record missing a `setting` (or `settings`) field entirely is never returned by any query —
  treated the same as belonging to no setting, never matched by any `setting` value including an
  empty string.
- An index containing only one setting's records still requires `setting` to be passed — there
  is no "skip the filter, there's only one setting anyway" shortcut, since a caller cannot always
  know that in advance and the invariant this feature enforces is structural, not situational.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `find_noun`, `find_rule`, `find_table`, `find_doc` MUST each require a `setting`
  argument and filter every candidate posting/record to `posting["setting"] == setting` (or
  `record["setting"] == setting`) before applying any other criterion.
- **FR-002**: `find_scenario` MUST require a `setting` argument and filter every candidate
  record to `setting in record.get("settings", [])` before applying any other criterion —
  replacing the prior optional `setting_in` keyword filter with this now-mandatory one.
- **FR-003**: Omitting `setting` on any of the five functions MUST be a call-time error (a
  required parameter), not a silently-unfiltered query.
- **FR-004**: A record with no `setting`/`settings` field at all MUST never match any query,
  regardless of the `setting` value passed.

### Key Entities

- No new entities — this feature changes the five existing query functions' signatures (#357),
  it introduces no new record shape.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every one of the five functions, a query against a mixed-setting index never
  returns a result from a setting other than the one requested — verified by exact-input tests
  covering all five.
- **SC-002**: Calling any of the five functions without `setting` raises `TypeError` (Python's
  own missing-required-argument error) — verified explicitly, not assumed.
- **SC-003**: A record with no `setting` field is excluded from every query, verified explicitly.

## Assumptions

- This is a breaking change to #357's already-merged signatures, made deliberately and
  documented as such — the issue's own scope note ("this feature changes its signatures") calls
  it out; there is no other caller of `corpus_find.py` in this repo yet to migrate (grep-verified
  before implementation).
- `find_scenario`'s prior `setting_in` keyword is removed entirely, folded into the now-mandatory
  `setting` positional/keyword argument — a caller no longer has a choice between an optional
  membership filter and an unfiltered query; there is only the one, mandatory, membership-based
  filter.
- This feature does not change what `corpus_document.py`/`corpus_terms.py`/`corpus_scenario.py`
  (#354/#355/#356) write onto each record — every record they already produce already carries a
  `setting`/`settings` field for exactly this purpose (docs/design/26-corpus-index.md: "every
  record names its setting").
