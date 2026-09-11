# Feature Specification: Corpus index retrieval queries (wyrd find)

**Feature Branch**: `136-corpus-retrieval`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Corpus index retrieval queries (wyrd find)" (issue #357)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A GM asks a question by its shape and gets a bounded read (Priority: P1)

Five different question shapes (proper noun, mechanical term, structural table, thematic
scenario, bibliographic lookup) each have their own index (#354, #355, #356); this feature is
the query layer a GM (or the engine, on their behalf) actually calls. Every result names a
document and an offset — never a whole loaded passage — so the next step is always a bounded
read of the surrounding text.

**Why this priority**: this is the entire point of building five indexes instead of one full-text
search — the retrieval layer is what actually answers "what exists, what kind of thing it is,
and which of forty mentions is the one that matters."

**Independent Test**: given each index's already-built shape (from #354/#355/#356) and a query,
confirm the matching query function returns exactly the matching entries, each naming a document
identifier and — where the index has one — an offset.

**Acceptance Scenarios**:

1. **Given** a concordance containing a name's postings across two documents, **When** the name
   is looked up, **Then** every occurrence in both documents is returned, each with its own
   `doc`/`offset`.
2. **Given** a term index containing both a `definition`-ranked and a `mention`-ranked posting
   for the same term, **When** the term is looked up, **Then** the `definition` posting is
   returned first.
3. **Given** a table index containing records of different dice types, **When** a lookup filters
   by `dice="d100"`, **Then** only the matching dice type's records are returned.
4. **Given** a table index, **When** a lookup filters by `about="<a word from a caption>"`,
   **Then** only records whose `caption` contains that word (case-insensitively) are returned.
5. **Given** a scenario index, **When** a lookup filters by `scale` and/or `setting`, **Then**
   only matching scenario records are returned.
6. **Given** a document index, **When** a lookup filters by `work`/`issue`, **Then** only the
   matching document record(s) are returned, identified by `doc` — bibliographic lookup has no
   in-document offset to report.

### Edge Cases

- A query against an empty index, or one with no matching entries, returns an empty result —
  never an error (this issue's own acceptance criterion).
- A query with no filters at all (every optional argument left unset) returns every entry in the
  index unchanged — an unconstrained query is a valid query, not a mistake.
- `find_table`'s `about` filter matching against a `None` caption (a table with no caption
  guess) never raises — it simply doesn't match.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide `find_noun`, returning every posting for a given name
  across every document, each with `doc` and `offset`.
- **FR-002**: The engine MUST provide `find_rule`, returning every posting for a given curated
  term, with `definition`-ranked postings ordered before `mention`-ranked ones.
- **FR-003**: The engine MUST provide `find_table`, filterable by `dice` and/or `about`
  (case-insensitive substring match against `caption`), returning matching table records
  unchanged.
- **FR-004**: The engine MUST provide `find_scenario`, filterable by any of the scenario
  record's deterministic fields (at minimum `scale`, `season`, `setting`), returning matching
  scenario records unchanged.
- **FR-005**: The engine MUST provide `find_doc`, filterable by `work` (matched against a
  document's `system`) and/or `issue` (matched against `edition`), returning matching document
  records' `doc` identifiers.
- **FR-006**: Every query function MUST return an empty result (never raise) against an empty
  index or a query matching nothing.
- **FR-007**: No query function MUST return a loaded passage of text — only a document
  identifier and, where the underlying index carries one, a character offset.

### Key Entities

- **Query result**: for `find_noun`/`find_rule`, `{doc, offset, rank?}`; for `find_table`, the
  matching table record from #355 unchanged; for `find_scenario`, the matching scenario record
  from #356 unchanged; for `find_doc`, `{doc}` — the bibliographic index has no in-document
  offset (Edge Cases).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every query function returns exactly the matching entries for a constructed test
  index, verified by exact-input tests.
- **SC-002**: `find_rule`'s ordering (definition before mention) is asserted explicitly, not
  incidental to dict/list ordering.
- **SC-003**: Every query function is exercised against an empty index and confirmed to return
  an empty result without raising.
- **SC-004**: No test result for any query function carries a loaded text passage — only
  identifiers/offsets/already-built records.

## Assumptions

- This feature is a runtime-logic slice only: plain dicts/lists in, plain dicts out, no I/O —
  matching every sibling module in this epic (#354, #355, #356).
- No CLI wiring: no chronicle-level CLI/session-loop entry point exists yet anywhere in this
  codebase for any sibling feature (#338/#339's own established scope narrowing, reused here
  verbatim) — the design document's `wyrd find ...` notation is read as naming these library
  query functions, not a literal CLI-argument-parsing requirement.
- `find_doc`'s `work`/`issue` filters match against a document record's `system`/`edition`
  fields respectively (#354's `build_document_record` shape) — the design's own worked example
  (`--work "<periodical>" --issue 98`) matches #354's own worked example
  (`system: "a periodical"`, `edition: "98"`) field-for-field.
- `find_scenario` reuses #356's already-validated scenario records as-is; it does not re-run
  `validate_scenario_record`/`scale_danger`/`check_requirements` itself — those remain the
  caller's own next step once a candidate record is found, matching the design's own separation
  between "find" (a lookup) and "select" (`scenario_selection.py`, #339, which further ranks and
  scales a found candidate).
