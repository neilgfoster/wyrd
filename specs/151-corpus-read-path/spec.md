# Feature Specification: Corpus-build reads extracted text from corpus/, not library/

**Feature Branch**: `151-corpus-read-path`

**Created**: 2026-09-15

**Status**: Draft

**Input**: User description: "Pass 0 and the corpus-build step read extracted text from corpus/, not library/ (issue #393)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Corpus-build step reads extracted text from corpus/ (Priority: P1)

A setting maintainer has run an external extraction tool that writes plain text to `corpus/`,
mirroring `library/`'s relative paths (source suffix changed to `.txt`). Running
`tools/setting_build.py <setting-dir>` builds the four corpus indexes from that extracted text,
never from the source document itself.

**Why this priority**: This is the change the issue exists to make — the corpus-build step's read
path moves off `library/` entirely. Without it, `library/` still has to hold decoded text, which
is the exact hidden assumption the issue reports.

**Independent Test**: Run `setting_build.py` against a fixture setting directory whose `library/`
holds only source documents and whose `corpus/` holds the matching extracted `.txt` files; confirm
the resulting `documents.json`/`nouns.json`/`terms.json`/`tables.json` are built from the `corpus/`
text, and that no code path reads `library/<record.path>` as text.

**Acceptance Scenarios**:

1. **Given** a present catalogue record `core/rulebook.md` with a corresponding
   `corpus/core/rulebook.txt`, **When** `setting_build.py` runs, **Then** the corpus indexes are
   built using the `corpus/core/rulebook.txt` file's text as that document's content.
2. **Given** a setting directory built once already, with nothing added or changed under
   `library/` or `corpus/`, **When** `setting_build.py` runs again, **Then** the corpus-index step
   is skipped exactly as it is today (second run is a no-op).

---

### User Story 2 - A record with no extracted text is reported as a gap, not a crash (Priority: P1)

A present catalogue record exists (its source file was catalogued by Pass 0) but the external
extraction tool has not yet produced its `corpus/` counterpart — for example a freshly-added PDF
that has not been through extraction yet. Running `setting_build.py` must report this cleanly as
"not yet extracted" and continue processing every other record, rather than raising
`UnicodeDecodeError` or any other crash.

**Why this priority**: This is the issue's other named failure mode — today's code assumes every
present record's `library/` file is itself readable text, which is false for a binary source
(PDF) and was previously papered over by writing decoded text into `library/` in place of the
source. Reporting the gap is what makes that workaround unnecessary.

**Independent Test**: Run `setting_build.py` against a fixture setting directory with one present
record that has a `corpus/` counterpart and one present record that does not; confirm the run
completes without raising, the extracted record is indexed, and the un-extracted record is
reported as not-yet-extracted.

**Acceptance Scenarios**:

1. **Given** a present catalogue record with no corresponding `corpus/<path>.txt` file,
   **When** `setting_build.py` runs, **Then** it completes successfully, that record is excluded
   from the built corpus indexes, and the run's report names the record as not-yet-extracted.
2. **Given** the same setting directory is later re-run after the missing `corpus/` file is added,
   **When** `setting_build.py` runs, **Then** the corpus-index step rebuilds (the record is no
   longer a gap) and that record's text is now included.

---

### User Story 3 - Pass 0's own classification is unaffected (Priority: P2)

Pass 0's catalogue/classification step keeps reading `library/` exactly as it does today — kind,
authority tier, subject, and `provides` come from a file's path and front matter, never from
`corpus/`. This story exists only to pin down that Pass 0 itself is explicitly out of scope for
any behavior change, so a reviewer does not need to re-derive that from the diff.

**Why this priority**: Lower than the two behavior changes above because it is a non-change —
included so the feature's boundary is unambiguous rather than left to be inferred.

**Independent Test**: Run the existing Pass 0 test suite unmodified; every test continues to pass
with no reference to `corpus/` anywhere in Pass 0's own code path.

**Acceptance Scenarios**:

1. **Given** the existing Pass 0 fixtures, **When** Pass 0's catalogue step runs, **Then** its
   classification output is unchanged from before this feature, and Pass 0's own code never opens
   a file under `corpus/`.

---

### Edge Cases

- A present record whose `corpus/` counterpart exists but is itself empty (zero-byte `.txt`
  file): treated as extracted text of `""`, not as a gap — the file's presence is the signal, its
  content is not further validated.
- A present record whose `corpus/` counterpart previously existed and was later deleted (the
  extraction was retracted): on the next run, that record is no longer found under `corpus/` and
  is reported as not-yet-extracted rather than reusing stale text from a previous build's cache.
- A `corpus/` file that cannot be decoded as UTF-8 (extraction wrote something malformed): out of
  scope for this feature to invent new recovery behavior for — the corpus-build step already
  requires readable UTF-8 text from its source; this feature only relocates that expectation from
  `library/` to `corpus/`, it does not add new handling for a corrupt `corpus/` file.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The corpus-build step MUST read each present catalogue record's extracted text from
  `corpus/<record's relative library path, with its suffix changed to .txt>`, never from
  `library/<record.path>`.
- **FR-002**: A present catalogue record with no corresponding `corpus/` text file MUST be
  excluded from the built corpus indexes and reported in the run's output as not-yet-extracted,
  without raising an exception.
- **FR-003**: The corpus-index build step's idempotence (a second run with nothing changed does no
  rebuild work) MUST continue to hold, keyed off each `corpus/` text file's own content hash
  rather than the source `library/` file's content hash.
- **FR-004**: When a previously-missing `corpus/` text file appears (extraction has since
  happened), the next `setting_build.py` run MUST detect the change and rebuild the corpus
  indexes to include that record.
- **FR-005**: When a previously-present `corpus/` text file is removed, the next
  `setting_build.py` run MUST treat that record as not-yet-extracted again (report it as a gap,
  exclude it from the indexes) rather than reusing a stale cached result.
- **FR-006**: Pass 0's catalogue/classification step MUST NOT change — it continues to enumerate
  and classify `library/` exactly as before, using only path and front-matter signals, and never
  reads from or reasons about `corpus/`.
- **FR-007**: The existing fixture trees under `tools/fixtures/pass0/` and
  `tools/fixtures/setting_build/` MUST gain a `corpus/` counterpart tree so their existing tests
  keep passing under the new read path, and at least one fixture MUST exercise the
  not-yet-extracted case (a present record with no `corpus/` counterpart).

### Key Entities

- **Catalogue record** (existing, from Pass 0): a cataloged `library/` file's classification —
  path, kind, authority tier, subject, content hash, status. Unchanged by this feature.
- **Extracted text file**: a `.txt` file under `corpus/`, at the same relative path as its source
  `library/` file (suffix changed). Its presence, absence, and content hash now drive the
  corpus-build step's read and idempotence logic in place of the source file's own hash.
- **Corpus-build report**: the `corpus` sub-object `setting_build.py` returns/prints — gains a
  field naming which present records had no corresponding `corpus/` text file this run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `setting_build.py` against a setting directory whose `library/` holds only
  binary source documents (no decoded text ever written there) still produces a complete,
  correct set of corpus indexes, provided `corpus/` holds the matching extracted text.
- **SC-002**: A present record with no extracted text never causes `setting_build.py` to exit with
  an unhandled exception; it is reported as a named gap in the run's output instead.
- **SC-003**: Running `setting_build.py` twice in a row with nothing added or changed does no
  rebuild work on the second run, exactly as before this feature.
- **SC-004**: Every existing test in `tools/test_setting_pass0.py` and `tools/test_setting_build.py`
  continues to pass, plus new tests covering both the "extracted text present" and "not yet
  extracted" cases.

## Assumptions

- `corpus/` text files are UTF-8 plain text, the same encoding assumption the corpus-build step
  already made of `library/` files before this change — this feature relocates that assumption,
  it does not relax or generalize it.
- The relative-path mirroring rule is exactly "same relative path under `corpus/` as under
  `library/`, with the file's suffix changed to `.txt`" — e.g. `library/core/rulebook.pdf` maps to
  `corpus/core/rulebook.txt`. No other renaming or nesting convention is introduced.
- The PDF/OCR extraction tool itself (what writes into `corpus/`) is out of scope, per the issue's
  own "Out of scope" note — this feature only changes where `setting_build.py` reads from.
- `tools/setting_pass0.py`'s gap-report content (the ten setting-authoring requirements) is
  unaffected — this feature does not add "extraction" as a new requirement category there; a
  not-yet-extracted record is reported only in `setting_build.py`'s own corpus report, not in
  Pass 0's gap report.
