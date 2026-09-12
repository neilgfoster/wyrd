# Feature Specification: Setting Build Command

**Feature Branch**: `150-setting-build-command`

**Created**: 2026-09-12

**Status**: Draft

**Input**: User description: "Wire Pass 0 and the corpus pipeline into one end-to-end setting-build command" (GitHub issue #388)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build a setting's indexes with one command (Priority: P1)

A setting author has a `wyrd-setting-<name>` repository with a populated `library/`. Today they
must run `tools/setting_pass0.py` by hand, then separately wire up `corpus_pipeline` themselves
with no guidance on ordering. They want one command that catalogues the library, surveys gaps,
and builds the deterministic corpus indexes, in the right order, in a single invocation.

**Why this priority**: This is the feature's entire purpose — epic #28's Definition of Done is
literally "one command, run twice, second run a no-op." Without this story there is no feature.

**Independent Test**: Run the new command against a fixture setting directory with a `library/`
of a few documents. Assert `index/catalogue.json`, `index/gap_report.json`, and the four
deterministic corpus index files exist and contain records for every present library document.

**Acceptance Scenarios**:

1. **Given** a setting directory with an unindexed `library/`, **When** the command runs,
   **Then** it produces a Pass 0 catalogue, a gap report, and `documents`/`nouns`/`terms`/`tables`
   corpus indexes on disk, and reports what it built.
2. **Given** a setting directory where Pass 0's catalogue already exists but a library file has
   changed since the catalogue's content hash was recorded, **When** the command runs, **Then**
   Pass 0's own catalogue step rebuilds only that file's record (unchanged records are left
   byte-for-byte alone, per #100); the corpus-index step detects the changed hash and rebuilds
   its whole four-index set from every present document (research.md's whole-set-rebuild
   decision, since `build_setting_corpus_indexes` is not an incremental, per-document API).

---

### User Story 2 - A second run is a no-op (Priority: P1)

A setting author reruns the command (by hand, or from a scheduled job per
`docs/design/26-corpus-index.md`'s "Scheduled execution" section) after nothing in `library/` has
changed. They need confidence that this does not silently redo work, corrupt state, or produce a
spurious diff.

**Why this priority**: This is epic #28's own explicit acceptance test, named verbatim in the
issue. It is not optional polish; it is the feature's defining property.

**Independent Test**: Run the command twice in a row against the same unmodified fixture setting
directory. Assert the second run processes zero documents, writes no files (or writes
byte-identical files), and its report says so explicitly.

**Acceptance Scenarios**:

1. **Given** a setting directory the command has already fully processed, **When** the command
   runs again with no changes to `library/`, **Then** it makes no writes and its report states
   that every document was already up to date (skipped, and why).

---

### User Story 3 - The command reports what it did and skipped (Priority: P2)

A setting author (or an unattended scheduled job) needs to know, after a run, which documents were
newly catalogued or reclassified, which were left alone because unchanged, which were removed, how
many requirement gaps remain, and how many authority conflicts exist — without reading raw JSON.

**Why this priority**: Named directly in the issue's acceptance criteria ("reports what it
skipped and why") and matches Pass 0's own existing reporting convention (`tools/setting_pass0.py`
already reports processed/removed/gaps/conflicts counts) — this story extends that convention to
cover the corpus-index step too, rather than leaving it silent.

**Independent Test**: Run the command against a fixture with a mix of new, unchanged, and removed
library files; capture its output and assert it names both what changed and what was skipped, with
a reason for each skip.

**Acceptance Scenarios**:

1. **Given** a run that processes some documents and skips others, **When** it finishes, **Then**
   its report distinguishes "processed" from "skipped (unchanged)" and states the corpus-index
   document/term/table counts alongside Pass 0's own gap/conflict counts.
2. **Given** `--format json` (mirroring `setting_pass0.py`'s own existing flag), **When** the
   command runs, **Then** its machine-readable output carries the same distinction.

### Edge Cases

- A setting directory with no `library/` at all: the command fails the same way
  `tools/setting_pass0.py` already does today (clear error, non-zero exit), rather than partially
  running the corpus step against nothing.
- A library file that fails Pass 0's classification (unreadable/binary): it is catalogued as
  `unclassified`/`unreadable` by Pass 0 exactly as today; this command excludes any
  non-`present`-status record from the corpus-index step rather than trying to extract text from
  it.
- `world_category`: `corpus_pipeline.build_setting_corpus_indexes` accepts an optional
  `world_category` per document and, when set, excludes that document from `terms`/`tables`. Pass
  0's own `CatalogueRecord` (#100, unmodified per FR-002) does not carry this field today, so this
  command always passes `world_category=None` — every document is treated as ordinary mechanical
  material for `terms`/`tables` purposes. Threading a setting's own `world_category` signal through
  Pass 0's catalogue is future work, not this feature's (see Assumptions).
- Two documents that collide on `(setting, id)`: `corpus_pipeline.build_setting_corpus_indexes`
  already raises `ValueError` for this; the command surfaces that error clearly rather than
  swallowing it, and makes no partial index writes for that run.
- The scenarios/arcs (fifth, model-driven) index: explicitly out of scope for this command, per
  `docs/design/26-corpus-index.md`'s "Scheduled execution" section, which excludes it from the
  scheduled/deterministic run by design.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a single command-line entry point, in this repo's
  `tools/` directory, that accepts one setting directory path and runs Pass 0's catalogue/gap-
  report step followed by the corpus pipeline's index-building step against that same directory,
  in that order.
- **FR-002**: The command MUST reuse `tools/setting_pass0.py`'s existing catalogue-building and
  gap-report logic unmodified (by importing/calling it), and MUST reuse
  `engine/wyrd/corpus_pipeline.py`'s `build_setting_corpus_indexes` unmodified — this feature adds
  no new extraction or indexing logic of its own.
- **FR-003**: For each catalogue record with `status == "present"` after the Pass 0 step, the
  command MUST read that file's text from disk and construct the document dict
  `build_setting_corpus_indexes` requires (`id`, `path`, `system`, `edition`, `document_type`,
  `page_count`, `extraction_method`, `text`, `setting`; `world_category` always `None`, per the
  Edge Cases section), then pass the resulting document list to `build_setting_corpus_indexes`.
- **FR-004**: The command MUST write the returned `documents`, `nouns`, `terms`, and `tables`
  indexes to the setting directory's `index/` subdirectory, as separate JSON files alongside
  Pass 0's own `catalogue.json` and `gap_report.json`.
- **FR-005**: A second invocation of the command against an unchanged setting directory MUST make
  no writes to `index/catalogue.json`, `index/gap_report.json`, or any corpus index file it
  produced on the first run, and MUST report that nothing needed to be redone.
- **FR-006**: The command MUST use Pass 0's own per-document `content_hash` (from the catalogue) as
  the sole signal for whether a document's corpus-index contribution is stale — it MUST NOT
  compute or store a second, independent hash for this purpose.
- **FR-007**: The command MUST report, per run, what it processed (new or changed documents) and
  what it skipped (unchanged documents, and any documents excluded because their catalogue status
  is not `present`), each skip naming its reason.
- **FR-008**: The command MUST support both a human-readable text report and a `--format json`
  machine-readable report, mirroring `tools/setting_pass0.py`'s existing `--format` flag.
- **FR-009**: The command MUST NOT build the scenarios/arcs (fifth) index — that index's model-
  driven, lazy-on-first-need build stays out of this command's scope per
  `docs/design/26-corpus-index.md`'s "Scheduled execution" section.
- **FR-010**: The command MUST NOT fetch, embed, or otherwise introduce any source material of its
  own — it only ever reads files already present under the given setting directory's `library/`.
- **FR-011**: This repository's own tests for the command MUST run only against fixture setting
  directories checked into this repo (e.g. under `tools/fixtures/`) — never against any actual
  `wyrd-setting-*` repository's content.
- **FR-012**: When `corpus_pipeline.build_setting_corpus_indexes` raises (e.g. a duplicate
  `(setting, id)` or an invalid `world_category`), the command MUST propagate a clear error and
  MUST NOT write partial corpus-index output for that run.

### Key Entities

- **Setting directory**: the on-disk root the command is pointed at; holds `library/` (input) and
  `index/` (all output: `catalogue.json`, `gap_report.json`, plus the corpus indexes).
- **Catalogue record**: Pass 0's existing per-document record (`id`, `path`, `kind`,
  `authority_tier`, `subject`, `content_hash`, `status`, `provides`) — this command's sole source
  of truth for which files exist, their identity, and their staleness.
- **Corpus document dict**: the in-memory shape `build_setting_corpus_indexes` requires per
  document; this command's own construction step, derived from a catalogue record plus that
  record's file's text content.
- **Run report**: the command's own output — processed documents, skipped documents (each with a
  reason), and the resulting gap/conflict/document/term/table counts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A setting repository with a loaded library can be fully indexed — catalogue, gap
  report, and all four deterministic corpus indexes — by running exactly one command.
- **SC-002**: Running that same command a second time, with no changes to the setting directory in
  between, performs zero writes and completes reporting that everything was already up to date.
- **SC-003**: After a run, an author can determine — from the command's own report alone, without
  opening any JSON file — which documents were newly processed, which were skipped and why, and
  how many requirement gaps and authority conflicts remain.

## Assumptions

- A setting's library documents are extractable as UTF-8 text directly from their files under
  `library/` (as `tools/setting_pass0.py`'s own fixtures already are) — this feature does not
  perform PDF/OCR extraction; any such conversion is a setting repository's own separate tooling
  concern, unchanged from today.
- `system`, `edition`, `document_type`, `page_count`, and `extraction_method` — fields
  `build_setting_corpus_indexes`'s document dict requires but Pass 0's catalogue record does not
  itself carry — are filled with reasonable, documented defaults (e.g. `document_type` from Pass
  0's own `kind`, `page_count` left unset/0 when unknown) since deriving them precisely is outside
  both #100's and #101's own delivered scope and no other current source supplies them.
- The command lives at `tools/setting_build.py`, following this repo's existing `tools/`
  single-purpose-script convention (e.g. `tools/setting_pass0.py`, `tools/backlog.py`).
- "Idempotent" and "no-op" are judged at the level of `index/`'s file contents and the run report,
  not at the level of incidental metadata such as a `generated_at` timestamp Pass 0 already
  treats as unchanged-when-nothing-changed.
