# Feature Specification: Setting build pipeline — Pass 0 catalogue, gap survey and idempotence

**Feature Branch**: `147-setting-pass-0-catalogue`

**Created**: 2026-09-12

**Status**: Draft

**Input**: User description: "Setting build pipeline: Pass 0 catalogue, gap survey and idempotence" (issue #100)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cataloguing a library into an authority-ordered processing list (Priority: P1)

A setting author has dropped a stack of source documents into `library/` — some published core
rules, some expansions, some fan-made material, some scenarios. Before anything is imported or
indexed, Pass 0 walks the library, classifies each document by kind and authority tier, and
produces a single processing order: core rules first, then expansions, then community material,
then scenarios/adventures.

**Why this priority**: every other step in this pipeline (gap survey, idempotent re-runs, the
five-index corpus build downstream) depends on there being a known, ordered list of what exists
and where it sits in the authority hierarchy — nothing else can run meaningfully first.

**Independent Test**: given a directory tree of source files, confirm Pass 0 produces a catalogue
record for every file, each carrying a classified kind and authority tier, and that the tier
values sort into the documented authority order.

**Acceptance Scenarios**:

1. **Given** a `library/` directory containing files of several kinds (rules, expansion,
   community, scenario), **When** Pass 0 runs, **Then** the catalogue lists one record per file,
   each with a classified kind and authority tier.
2. **Given** a catalogue with records at every authority tier, **When** the processing order is
   derived from it, **Then** every core-rules record precedes every expansion record, every
   expansion record precedes every community record, and every community record precedes every
   scenario/adventure record.
3. **Given** a file whose kind cannot be determined from its name/path/front-matter alone,
   **When** Pass 0 classifies it, **Then** it is recorded with an explicit "unclassified" kind
   and the lowest authority tier, rather than silently dropped or guessed into a specific tier.

---

### User Story 2 - The engine gap report (Priority: P1)

A setting author wants to know, before doing any further work, what the engine expects a setting
to supply that this library does not yet cover — an entry career, a bestiary, a names table, and
so on. Pass 0 produces a gap report comparing what the setting-authoring contract
(docs/design/24-authoring-a-setting.md) requires against what the catalogue found.

**Why this priority**: this is the feature's other named deliverable, and the one issue #100
explicitly calls out as not existing anywhere today — each setting has had to discover its own
gaps ad hoc.

**Independent Test**: given a catalogue that is missing evidence of a required setting file (e.g.
no bestiary-shaped material anywhere in the library), confirm the gap report names that
requirement as unmet, and that a catalogue covering every requirement produces an empty gap
report.

**Acceptance Scenarios**:

1. **Given** a catalogue with no record classified as bestiary-shaped material, **When** the gap
   report is built, **Then** it names the bestiary requirement as a gap.
2. **Given** a catalogue whose records cover every requirement the setting-authoring contract
   lists, **When** the gap report is built, **Then** it reports no gaps.
3. **Given** a gap report, **When** it is produced, **Then** each entry names the specific
   requirement that is unmet in language a setting author can act on, not just a count.

---

### User Story 3 - Idempotent re-runs by content hash (Priority: P2)

A setting author adds three new files to an already-catalogued `library/` and re-runs Pass 0.
Only those three files are processed; every previously-catalogued, unchanged file is left alone,
because Pass 0 recorded a content hash per source and per derived artefact on the prior run.

**Why this priority**: issue #100's own Definition of Done requires Pass 0 to be "cheap enough to
re-run whenever material is added" — without idempotence, every re-run reprocesses the whole
library, which defeats that requirement as the library grows.

**Independent Test**: run Pass 0 twice against the same unchanged library and confirm the second
run reports zero files processed; then add one new file and confirm the third run processes
exactly that one file, leaving every other catalogue record's hash and content untouched.

**Acceptance Scenarios**:

1. **Given** a library Pass 0 has already catalogued, **When** Pass 0 is re-run with no changes
   to the library, **Then** it reprocesses no file and reports zero changes.
2. **Given** an already-catalogued library, **When** one existing file's content changes and Pass
   0 is re-run, **Then** only that file's catalogue record and hash are updated, and every other
   record is left byte-for-byte unchanged.
3. **Given** an already-catalogued library, **When** one new file is added and Pass 0 is re-run,
   **Then** only the new file gets a catalogue record; every existing record's hash is unchanged.
4. **Given** a file is removed from the library, **When** Pass 0 is re-run, **Then** the catalogue
   marks that file's record as no longer present rather than silently deleting the record (so a
   later authority conflict or gap-report change stays explainable).

---

### User Story 4 - Authority conflicts are recorded, never silently resolved (Priority: P2)

Two documents at different authority tiers both bear on the same topic — say, a community
supplement that restates a rule the core book already covers, differently. Pass 0's processing
order determines which is authoritative, but does not let the lower-authority material overwrite
the higher-authority material's record; instead it records that a conflict exists, for a human to
resolve.

**Why this priority**: issue #100 states this explicitly as a constraint ("later material must
not silently overwrite higher-authority material; conflicts are recorded, not resolved by run
order") — getting it wrong corrupts the very thing Pass 0 exists to make trustworthy.

**Independent Test**: given two catalogued documents at different authority tiers whose declared
subject overlaps, confirm Pass 0's output records the conflict (naming both documents and the
overlap) without either document's own catalogue record being altered by the other.

**Acceptance Scenarios**:

1. **Given** two documents in the library that a shared classification signal (e.g. a declared
   topic or document type) shows both bear on, **When** Pass 0 catalogues them, **Then** it
   records a conflict entry naming both documents, rather than dropping or merging either one.
2. **Given** a recorded conflict, **When** the catalogue is inspected, **Then** each of the two
   documents' own catalogue records is unchanged by the other's presence — the conflict is a
   separate record, not a mutation of either document's entry.

### Edge Cases

- An empty `library/` directory produces an empty catalogue and a gap report listing every
  setting-authoring requirement as unmet, rather than an error.
- A file Pass 0 cannot read at all (corrupt, unreadable) is recorded with an explicit
  "unreadable" status rather than silently skipped, so it surfaces the same way an unclassified
  file does.
- Re-running Pass 0 against a library that has not changed at all, more than once in a row, is
  stable: the second and third no-op runs report identically zero changes.
- A document that could plausibly classify as more than one kind (e.g. a book with both core rules
  and a bundled scenario) is classified as its single dominant kind by a documented, deterministic
  rule, and the ambiguity itself is recorded rather than silently discarded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Pass 0 MUST enumerate every file under a setting's `library/` directory and produce
  one catalogue record per file.
- **FR-002**: Each catalogue record MUST carry a classified document kind and an authority tier,
  using a closed, documented vocabulary for both.
- **FR-003**: Pass 0 MUST derive a processing order from the catalogue in which every record at a
  higher authority tier precedes every record at a lower authority tier (core rules, then
  expansions, then community material, then scenarios/adventures — issue #100's stated order).
- **FR-004**: Pass 0 MUST produce an engine gap report comparing the catalogue's coverage against
  the setting-authoring contract's declared requirements (docs/design/24-authoring-a-setting.md),
  naming each unmet requirement individually.
- **FR-005**: Pass 0 MUST record a content hash per source file and per derived artefact
  (catalogue record, gap report) it produces.
- **FR-006**: On a re-run, Pass 0 MUST reprocess only files whose content hash has changed since
  the last run, plus any file newly present; it MUST NOT reprocess a file whose hash is unchanged.
- **FR-007**: A re-run against an unchanged library MUST produce zero changes to the catalogue or
  gap report.
- **FR-008**: When two catalogued documents at different authority tiers are detected as bearing
  on the same subject, Pass 0 MUST record the conflict as its own entry, and MUST NOT let the
  lower-authority document's content alter the higher-authority document's own catalogue record
  (or vice versa).
- **FR-009**: A file Pass 0 cannot classify MUST be recorded with an explicit "unclassified" kind
  at the lowest authority tier, never silently omitted from the catalogue.
- **FR-010**: A file Pass 0 cannot read MUST be recorded with an explicit "unreadable" status,
  never silently omitted from the catalogue.
- **FR-011**: A file previously catalogued but no longer present in `library/` MUST be marked in
  the catalogue as no longer present, rather than having its record deleted outright.
- **FR-012**: Pass 0 MUST be runnable as a script against any `wyrd-setting-*`-shaped `library/`
  directory, without depending on or modifying any specific setting repository's content — this
  repository's own test fixtures stand in for a real setting's library.
- **FR-013**: Pass 0's catalogue output MUST record enough per-document metadata (id, source
  path, classified kind, authority tier, content hash) for later pipeline passes — including the
  corpus indexing work of docs/design/26-corpus-index.md — to build on it without re-deriving the
  same classification.

### Key Entities

- **Catalogue record**: one entry per source file — id, source path, classified kind, authority
  tier, content hash, and presence status (present / removed).
- **Processing order**: the catalogue's records sorted by authority tier, the order later passes
  should process them in.
- **Gap report**: one entry per setting-authoring requirement the catalogue does not evidence
  coverage for, naming the requirement and why it is considered unmet.
- **Conflict record**: one entry per detected same-subject overlap between two catalogued
  documents at different authority tiers, naming both documents.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running Pass 0 against a setting's library produces a catalogue, an
  authority-ordered processing list, and a gap report in a single invocation, with no manual
  classification step required for a well-formed library.
- **SC-002**: A second Pass 0 run against an unchanged library reprocesses zero files and
  completes without modifying any previously-produced artefact.
- **SC-003**: Adding N new files to an already-catalogued library and re-running Pass 0 processes
  exactly those N files, regardless of total library size.
- **SC-004**: Every gap report entry names a specific, actionable setting-authoring requirement —
  never a bare count or an unexplained failure.
- **SC-005**: No authority conflict between two catalogued documents ever results in either
  document's catalogue record being silently overwritten by the other.

## Assumptions

- "Enumerate the library" means every regular file under `library/`, recursively; directory
  structure within `library/` carries no special meaning Pass 0 depends on (a setting author may
  organise it however they like).
- The authority-tier vocabulary is closed and fixed at four values, matching issue #100's stated
  order exactly: core rules, expansions, community material, scenarios/adventures — plus the
  "unclassified" fallback kind at the lowest tier for material Pass 0 cannot place.
- Document-kind classification is signal-based (filename, path segment, optional front-matter or
  sidecar metadata a setting author supplies) rather than requiring full-text extraction — Pass 0
  is explicitly a cheap, pre-import pass (issue #100: "cheap, and running before anything is
  imported"), not the corpus-extraction work of docs/design/26-corpus-index.md.
- "Same subject" for conflict detection is judged from the same classification signals Pass 0
  already computes (declared kind plus a shared topic/subject signal where available), not a
  full semantic comparison of document contents — that stays a cheap, deterministic check
  consistent with docs/design/27-tooling.md's deterministic-over-inference rule.
- This feature is engine-repo tooling only: it operates against a `library/`-shaped directory
  (exercised in tests against fixtures under this repo), and never reads, writes, or otherwise
  touches any actual `wyrd-setting-*` repository's content, per this repo's CLAUDE.md repository
  table.
- Pass 0's output is consumed by later, separately-tracked pipeline stages (issue #100 references
  #30's gap-survey work and this design's corpus indexing, #133-#136); this feature defines and
  implements only the catalogue/gap-report/idempotence/authority-ordering pass itself, not those
  downstream consumers.
