# Feature Specification: Generalise corpus extraction and indexing for any setting repo

**Feature Branch**: `148-generalise-corpus-extraction`

**Created**: 2026-09-12

**Status**: Draft

**Input**: User description: issue #101, "Generalise corpus extraction and indexing for any setting repo"

## Orientation

Wyrd is a setting-agnostic tabletop engine (this repo). A setting repo (`wyrd-setting-*`,
separate, often private — CLAUDE.md's repository table) supplies documents under its own
`library/` and, once extracted, its own `corpus/` and `index/`. #354–#357 (specs/133–136,
merged) already built four of the five corpus indexes' *per-document* building blocks as pure,
no-I/O functions (`corpus_document.py`, `corpus_terms.py`, `corpus_scenario.py`,
`corpus_find.py`) — each one already takes `setting` as an explicit, mandatory argument and
never hard-codes anything about a specific setting. What does not yet exist is the layer that
actually **runs those functions together across a whole setting's document set** — the thing
issue #101 calls "a pipeline any `wyrd-setting-*` repo can run against its own `library/`."

This is that orchestration layer.

## Scope note — reconciling with CLAUDE.md, and with #354–357's own precedent

Three things fix this feature's boundary, and each is load-bearing:

1. **CLAUDE.md**: "Nothing unpublishable may enter this repository... no tooling that fetches
   source material." This repo carries no PDF/OCR library today (every corpus module states
   "Python 3.11+, standard library only") and adding one — plus fixture PDFs to test it against
   — would mean either a real third-party dependency this repo has never needed, or copyrighted
   fixture content. Neither is acceptable here. **PDF/OCR extraction itself — turning bytes in
   `library/` into plain text — stays a setting repo's own concern**, unchanged from today.
2. **ADR 0052** (accepted the same day as this pass, superseding ADR 0051): "#101 proceeds
   unchanged except that its second proof run (against `wyrd-research`'s corpus) is dropped —
   one real setting repo is enough to prove genericity," and "extraction and OCR remain pipeline
   steps (#101) run per setting repo, with no shared intermediate repo required." Read together
   with point 1, this feature's own genericity proof is a test suite run against synthetic
   fixture text in *this* repo, not a live run against a private setting repo this repo cannot
   reach.
3. **#354–357's own established precedent** (specs/136's own Assumptions, verbatim): "No CLI
   wiring: no chronicle-level CLI/session-loop entry point exists yet anywhere in this codebase
   for any sibling feature." This feature follows the same line — it is a library-level
   orchestration module a setting repo's own tooling imports and calls with the text it has
   already extracted, not a new CLI this repo would have to build, test, and maintain ahead of
   any other subsystem having one.

Net: this feature takes each already-extracted document's **plain text plus its bibliographic
metadata** as a plain in-memory input (exactly what `corpus_document.build_document_record`
already accepts), and produces the four deterministic indexes for a whole document set in one
call — the piece #354–357 stopped short of.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build a whole setting's deterministic indexes in one call (Priority: P1)

A setting repo has already extracted its `library/` into plain text per document (its own,
existing concern, unchanged by this feature). Today it would have to call
`corpus_document.build_document_record`/`build_concordance` and `corpus_terms.build_terms_index`/
`build_tables_index` once per document and merge the results by hand. This feature gives it one
orchestration call that takes the whole document set and returns the four merged, setting-scoped
indexes (`documents`, `nouns`, `terms`, `tables`) ready to write to that setting's own `index/`.

**Why this priority**: this is the entire generalisation issue #101 asks for — the same call
works for any `wyrd-setting-*` repo's document set, with no setting-specific code inside it.

**Independent Test**: given a list of synthetic documents (varied `setting` values, some sharing
one, some not) and their already-extracted text, confirm the orchestration call returns the four
indexes with every record correctly scoped to its own document's `setting`, matching what calling
each #354/#355 builder by hand and merging would have produced.

**Acceptance Scenarios**:

1. **Given** three documents belonging to two different settings, **When** the pipeline builds
   indexes for them in one call, **Then** every returned `documents`/`nouns`/`terms`/`tables`
   record carries the `setting` of the document it came from, and a query scoped to one setting
   (via #357's `corpus_find` functions) never returns the other setting's records.
2. **Given** a document set with two documents sharing the same `id`, **When** the pipeline is
   called, **Then** it raises naming the colliding id, rather than silently letting the second
   overwrite the first (the fault #97 fixed for the extraction step, generalised here to the
   indexing step: a silent collision must never again cost a document its indexing).
3. **Given** an empty document set, **When** the pipeline is called, **Then** it returns four
   empty indexes rather than raising.

---

### User Story 2 - World-building content stays out of the mechanical indexes (Priority: P2)

A setting's `library/` mixes rules text (Fear rules, transformation tables) with prose
world-building material (a regional gazetteer, a faction write-up, a history). Per
`docs/design/26-corpus-index.md`'s closing section, prose world-building material is deliberately
**not** run through curated-term/table detection — those passes exist for mechanical vocabulary,
and a gazetteer has none — but it must still be catalogued (`documents.json`) and made
concordance-findable by name (`nouns.json`), which is how such material is actually reached in
play ("not 'tell me about Ostland' but 'what is this place the player just mentioned?'").

**Why this priority**: this is issue #101's own second acceptance criterion — "the world-building
corpus is produced and kept distinct from mechanical content in the index" — and getting the
boundary wrong either pollutes `terms.json`/`tables.json` with false-positive matches against
prose, or silently drops world-building material from the concordance that makes long chronicles
work.

**Independent Test**: given one document tagged as world-building content and one tagged
mechanical, both containing text that would trip the terms/tables detectors if run, confirm the
world-building document contributes to `documents`/`nouns` but zero postings to `terms`/`tables`,
while the mechanical document contributes to all four.

**Acceptance Scenarios**:

1. **Given** a document marked with a world-building category (geography, factions, history, or
   daily life) whose text contains a curated term (e.g. "Fear") and a table-shaped run of lines,
   **When** the pipeline builds indexes, **Then** that document contributes no `terms.json` or
   `tables.json` postings, but does contribute a `documents.json` record and its proper nouns to
   `nouns.json`.
2. **Given** a document with no world-building category set, **When** the pipeline builds
   indexes, **Then** it is treated as mechanical content and indexed by all four builders exactly
   as #354/#355 already do per-document.
3. **Given** a world-building category value outside the closed vocabulary (geography, factions,
   history, daily life), **When** the pipeline is called, **Then** it raises naming the invalid
   value, rather than silently accepting an open-ended category.

---

### User Story 3 - The thematic (arcs/scenario) index is generated lazily and cached (Priority: P3)

Per `docs/design/26-corpus-index.md`, the fifth index (`scenarios.json`, the model-generated
thematic layer the issue calls "the arcs index") is the one index needing a model call, and is
**lazy** — "an adventure gets its thematic record the first time anything asks for it, not up
front... Rebuilding is a `wyrd optimise` function, and regenerated only when the schema changes."
This feature makes that caching decision itself a pure, deterministic, and therefore testable
function, with the actual model call injected by the caller rather than hard-coded — this repo
makes no live model calls in its own test suite.

**Why this priority**: without a deterministic cache-staleness rule, "lazy and cached" is just a
description, not a mechanism a setting repo's tooling can actually rely on — and getting it wrong
either regenerates every document's thematic record on every run (defeating "lazy") or never
regenerates a stale one after the schema changes (defeating "cached... regenerated only when the
schema changes").

**Independent Test**: given a cache with one fresh entry, one entry whose stored content hash no
longer matches its document's current text, one entry whose stored schema version is older than
the current one, and one document with no cache entry at all, confirm the pipeline calls the
injected generator only for the three non-fresh cases and leaves the fresh entry untouched.

**Acceptance Scenarios**:

1. **Given** a document with no existing cache entry, **When** the pipeline builds the scenario
   index, **Then** the injected generator is called for that document and its result is cached
   under the document's current content hash and schema version.
2. **Given** a document whose cache entry's content hash matches its current text and whose
   schema version matches the current schema version, **When** the pipeline builds the scenario
   index, **Then** the injected generator is **not** called for that document, and its cached
   record is reused unchanged.
3. **Given** a document whose cache entry's content hash no longer matches its current text (the
   document was re-extracted or corrected), **When** the pipeline builds the scenario index,
   **Then** the injected generator is called again for that document, and the cache is updated.
4. **Given** a document whose cache entry's schema version is older than the pipeline's current
   schema version, **When** the pipeline builds the scenario index, **Then** the injected
   generator is called again for that document, even though its content hash is unchanged.

### Edge Cases

- A document set containing zero documents produces empty indexes for all three user stories'
  functions, never an error.
- Two documents in **different** settings sharing the same `id` is not a collision — id
  uniqueness is scoped per setting, matching every other per-setting corpus record.
- The generator function injected for User Story 3 raising an exception for one document does not
  corrupt the cache entries already computed for other documents in the same call.
- A world-building document (User Story 2) is still eligible for the scenario index (User Story
  3) — the world-building/mechanical distinction is orthogonal to whether a document ever gets a
  thematic record; a gazetteer can still be the seed for a scenario.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST provide a function that takes a list of documents (each carrying
  the fields `corpus_document.build_document_record` already accepts, plus the document's
  extracted `text`) and returns the four deterministic indexes (`documents`, `nouns`, `terms`,
  `tables`) built by orchestrating #354/#355's existing per-document builders across the whole
  list, merged exactly as `corpus_document.merge_concordances` already merges per-document
  concordances.
- **FR-002**: That function MUST raise naming the offending id when two documents in the same
  call share both `id` and `setting` — a same-setting duplicate is always an error, never a
  silent overwrite.
- **FR-003**: The engine MUST provide a closed vocabulary of world-building categories
  (`geography`, `factions`, `history`, `daily-life`) and accept an optional category tag per
  document; a document carrying one of these MUST NOT contribute any `terms.json`/`tables.json`
  postings, while still contributing to `documents.json`/`nouns.json` exactly as an untagged
  document does.
- **FR-004**: Passing a world-building category value outside the closed vocabulary MUST raise
  naming the offending value.
- **FR-005**: The engine MUST provide a pure function deciding, for a given document's current
  content hash and the pipeline's current schema version against a cache entry (or its absence),
  whether that document's thematic (scenario/arcs) record is fresh, stale, or missing.
- **FR-006**: The engine MUST provide an orchestration function for the scenario/arcs index that
  calls an injected generator callable only for documents whose cache status (FR-005) is stale or
  missing, reuses the cached record unchanged for fresh documents, and returns both the updated
  scenario records and the updated cache.
- **FR-007**: No function introduced by this feature MUST perform file I/O, network access, or
  any model call itself — every model call a caller needs happens through the injected callable
  from FR-006, matching #354–357's own "pure, no I/O" convention.
- **FR-008**: Every function introduced by this feature MUST require `setting` (directly on each
  document, as #354–357's own functions already do) rather than accepting or producing any
  record with no setting — matching `docs/design/26-corpus-index.md`'s "indexes are scoped to a
  setting" rule and #357's existing enforcement pattern.

### Key Entities

- **Document input**: an in-memory record combining `corpus_document.build_document_record`'s
  existing fields (`id`, `path`, `system`, `edition`, `document_type`, `page_count`,
  `extraction_method`, `setting`) with its extracted `text` and an optional `world_category`.
- **Index bundle**: `{"documents": [...], "nouns": {...}, "terms": {...}, "tables": [...]}` — the
  same per-index shapes #354/#355 already define, merged across a whole document set.
- **Scenario cache entry**: `{"content_hash", "schema_version", "record"}` per document id,
  keyed by `(setting, doc id)`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a constructed multi-setting, multi-document fixture, the orchestration
  function's output is asserted, record for record, against what calling each #354/#355 builder
  by hand and merging would produce — proving the orchestration adds no setting-specific logic.
- **SC-002**: A document tagged with each of the four world-building categories, whose text
  contains both a curated term and a table-shaped run, is asserted to produce zero `terms`/
  `tables` postings while still producing `documents`/`nouns` entries.
- **SC-003**: For a scenario-cache fixture covering all four freshness cases in User Story 3's
  Independent Test, the injected generator's call count is asserted to be exactly the number of
  stale-or-missing documents — never more, never fewer.
- **SC-004**: Every function this feature introduces is exercised against an empty document list
  and an empty cache, and confirmed to return empty results without raising.
- **SC-005**: `python3 -m ruff check .` and `python3 -m ruff format --check .` both report clean
  across the whole repository after this feature lands (CLAUDE.md's standing requirement).

## Assumptions

- **No CLI is built by this feature**, matching specs/133–136's own established precedent (no
  chronicle-level CLI entry point exists yet anywhere in this codebase). A setting repo's own
  tooling is expected to extract its `library/` into plain text (unchanged, existing concern),
  read each document's text, call this feature's orchestration functions, and write the returned
  indexes to its own `index/` directory — the same "engine provides pure logic, a setting-scoped
  script does the I/O" split `check_bestiary.py`/`check_gear.py` already use for setting data.
- **The issue's "arcs index" and `docs/design/26-corpus-index.md`'s `scenarios.json` name the
  same fifth index.** The design document is the engine's authoritative description of what that
  index is (Haiku-tier, lazy, cached); this feature does not introduce a sixth index.
- **A document's content hash (FR-005) is supplied by the caller**, not computed by this feature
  — hashing algorithm choice is an extraction-step concern (#97's own "full-path hashing" fix),
  out of scope here; this feature only compares whatever hash string it is given against the
  cache's stored one.
- **The pipeline's current schema version (FR-005/FR-006) is a caller-supplied value**, not a
  constant this feature owns — the caller (a setting repo's tooling) is the one that knows when
  its own scenario record schema has changed and needs to bump it.
- **#97 is closed** and its fixes (full-path hashing, correct puller path, retry/cleaning-pass
  logic) already landed in the (now-retired, per ADR 0052) extraction tooling; this feature does
  not re-implement or re-verify them, only builds the indexing layer #101 scoped to run after
  extraction.
