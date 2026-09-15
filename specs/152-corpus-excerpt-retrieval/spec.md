# Feature Specification: Corpus excerpt retrieval — a bounded read at a doc+offset

**Feature Branch**: `152-corpus-excerpt-retrieval`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Corpus excerpt retrieval: read a bounded passage at a doc+offset (issue #397)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A query result carries its own excerpt, not just coordinates (Priority: P1)

`corpus_find.py`'s five query functions (#357) each return `{doc, offset}` pairs. A caller — the
GM-contract engine, or an agent populating/playing a setting — needs the actual surrounding text
at that offset, not just its address, to avoid loading a whole extracted document into context to
find one passage.

**Why this priority**: this is the entire reason `docs/design/26-corpus-index.md` designed
`doc + offset` results in the first place — "the next step is always a bounded read of the
surrounding passage rather than loading a whole book into context. That bounded read is the
point." Without it, every query result is a dead end that still requires manually opening and
searching the source file.

**Independent Test**: given a setting's real `documents.json` and its corpus text on disk, resolve
a known `doc` id to its corpus file, read a window of text around a known `offset`, and confirm
the returned excerpt actually contains the expected passage.

**Acceptance Scenarios**:

1. **Given** a `documents.json` record naming a document's corpus path, and that file's text on
   disk, **When** an excerpt is requested at an offset known to fall inside a specific sentence,
   **Then** the returned excerpt contains that sentence.
2. **Given** the same inputs, **When** an excerpt is requested twice at the same doc+offset+window,
   **Then** both calls return identical text (deterministic).
3. **Given** a `documents.json` record for setting `A`, **When** an excerpt is requested with
   `setting="B"`, **Then** no excerpt is returned — the document is not resolved outside its own
   setting, matching every other `corpus_find.py` function's setting-scoping rule (#364).

---

### User Story 2 - An excerpt request outside the document's real bounds is a valid, quiet outcome (Priority: P1)

An offset can be stale (the document changed since the index was built), the doc id can be wrong,
or the setting can be wrong. None of these should raise — `corpus_find.py`'s five query functions
already never raise on an unmatched query, and this function must not become the first exception
to that rule.

**Why this priority**: a crash on a malformed or stale query is worse than an empty result,
because it takes down whatever loop is walking a batch of query results rather than just skipping
one bad entry.

**Independent Test**: call the excerpt function with an unknown doc id, an unknown setting, and an
offset past the end of a real document's text; confirm each returns the function's designated
"nothing found" value rather than raising.

**Acceptance Scenarios**:

1. **Given** a `documents.json` with no record for a given `doc` id, **When** an excerpt is
   requested for that id, **Then** the function returns `None` rather than raising `KeyError` or
   any other exception.
2. **Given** a real document whose extracted text is `N` characters long, **When** an excerpt is
   requested at `offset >= N`, **Then** the function returns `None` rather than raising an
   indexing error.
3. **Given** a real `doc`/`offset` but a `setting` that does not match the document's own setting,
   **Then** the function returns `None` — same outcome as an unknown doc id, never a partial or
   cross-setting excerpt.

---

### User Story 3 - `wyrd find`'s own output already carries the excerpt (Priority: P2)

Today, calling any of `corpus_find.py`'s query functions through whatever surfaces them (the
`wyrd find` entry point named in `docs/design/26-corpus-index.md`'s "Retrieval" section) returns
coordinates the caller must still resolve by hand. Once User Story 1/2 exist, wiring them into
that entry point removes that manual step for the common case.

**Why this priority**: valuable, but the excerpt function itself (User Stories 1-2) is useful on
its own even before every call site is updated — this is the integration, not the capability.

**Independent Test**: run a `wyrd find` query against a real setting and confirm each result in
its output already includes a resolved excerpt field alongside `doc`/`offset`, with no separate
manual step required.

**Acceptance Scenarios**:

1. **Given** a `wyrd find noun`/`rule`/`table` query against a real setting with results,
   **When** the query runs, **Then** each result carries an excerpt alongside its `doc`/`offset`.
2. **Given** the same query against a setting whose corpus text for a matched document is
   missing on disk (index present, extraction not yet run or since removed), **When** the query
   runs, **Then** that result's excerpt is `None`/absent rather than the whole query failing.

### Edge Cases

- A `doc` id present in `documents.json` but whose corpus text file is missing from disk (e.g.
  extraction not yet run, or the file was deleted after indexing) returns `None`, the same as an
  unknown `doc` id — a missing file is not raised as an I/O error to the caller.
- An `offset` of `0` is a valid start-of-document offset, not treated as falsy/missing.
- A negative `offset` is invalid input and returns `None`, consistent with "never raise, never
  return a wrong-but-plausible-looking excerpt."
- `window` of `0` returns a valid (possibly empty or minimal) excerpt rather than raising —
  this feature does not mandate a minimum window size, only a sensible default when unspecified.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a function that, given a `documents.json`-shaped index, a
  `setting`, a `doc` id, and an `offset`, resolves the document's corpus text file and returns a
  bounded window of text centred on that offset.
- **FR-002**: The function MUST require `setting` as a mandatory argument and only resolve a
  document whose own record matches that setting — never across settings — matching the
  setting-scoping rule every other `corpus_find.py` function already follows (#364).
- **FR-003**: The function MUST accept a `window` size controlling how much text surrounds the
  offset, with a sensible default when the caller does not specify one.
- **FR-004**: The function MUST return `None` (never raise) for: an unknown `doc` id, a `doc`
  that does not belong to the given `setting`, an `offset` at or past the end of the document's
  text, a negative `offset`, or a document whose corpus text file cannot be found on disk.
- **FR-005**: The function MUST be deterministic — the same `documents.json`, `setting`, `doc`,
  `offset`, and `window` always produce the same returned excerpt.
- **FR-006**: `wyrd find`'s existing query output MUST be extended to include the resolved
  excerpt for each result that carries a `doc`/`offset` pair, alongside those coordinates
  unchanged.
- **FR-007**: This feature MUST NOT change what the four deterministic index builders (#354/#355)
  or the `scenarios` index (#356) write, and MUST NOT require rebuilding any already-built
  setting's indexes.

### Key Entities

- No new persisted entity — this feature reads the existing `documents.json` record shape (#354)
  and the corpus text files a setting repository's own extraction pipeline already produces
  (`docs/design/26-corpus-index.md`); it introduces no new index or on-disk schema.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a real setting's `documents.json` and corpus text, an excerpt requested at a
  known offset contains the expected passage — verified against at least one of
  `wyrd-setting-titan`'s or `wyrd-setting-darkfuture`'s real indexes, not only synthetic fixtures.
- **SC-002**: Every named failure mode (unknown doc, wrong setting, offset past end, negative
  offset, missing corpus file) returns `None` rather than raising, verified explicitly for each.
- **SC-003**: A `wyrd find` query's output already contains a resolved excerpt for every result
  that has a `doc`/`offset`, with no separate manual read step required by the caller.
- **SC-004**: Retrieving an excerpt from a real, previously 10,000+ line corpus document no
  longer requires reading or grepping the whole file — the excerpt call alone is sufficient to
  confirm a specific passage.

## Clarifications

### Session 2026-09-15

- Q: Does `documents.json`'s existing record shape already carry a field this feature can use
  to locate a document's corpus text file, or does the schema need extending first? → A:
  Confirmed by reading `engine/wyrd/corpus_document.py`'s `build_document_record` — every record
  already carries a `path` field. No schema change, and FR-007's "additive only, no forced
  rebuild" holds without qualification.

## Assumptions

- A setting repository's corpus text layout (one `.txt` file per source document, mirroring
  `library/`'s relative paths, per `docs/design/26-corpus-index.md` and the `create-setting`
  skill's Phase 0) is already stable and does not change as part of this feature.
- `documents.json`'s existing record shape already carries a `path` field (confirmed above) that
  locates a document's corpus text file — no schema change or index rebuild is needed (FR-007).
- "A sensible default" window (FR-003) is a fixed constant chosen during planning/implementation
  and documented in code, not user-configurable at first; a caller with an unusual need can pass
  an explicit `window` value.
- The `wyrd find` entry point named throughout `docs/design/26-corpus-index.md`'s "Retrieval"
  section already exists as some callable surface over `corpus_find.py`'s functions (even if not
  literally a shipped CLI binary yet) that this feature can extend; if no such surface exists yet
  at implementation time, User Story 3's scope is the addition of that minimal surface, not a
  redesign of one.
