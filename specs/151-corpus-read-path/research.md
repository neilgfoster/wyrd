# Phase 0 Research: Corpus-build reads extracted text from corpus/, not library/

No unresolved `NEEDS CLARIFICATION` markers came out of Phase 0 for this feature — the driving
issue (#393) and the existing code (`tools/setting_build.py`, `tools/setting_pass0.py`) together
were specific enough to settle every open question directly. Recorded here for the record, in the
issue's own decision/rationale/alternatives shape:

## Decision: mirrored relative path, suffix changed to `.txt`

**Decision**: A present record's extracted text lives at
`corpus/<record.path with its suffix replaced by .txt>` — e.g. `library/core/rulebook.pdf` maps to
`corpus/core/rulebook.txt`. Implemented with `Path(record.path).with_suffix(".txt")`.

**Rationale**: This is exactly what issue #393 specifies verbatim ("same relative path <->
corpus/foo/bar.txt"), and it is the mapping `wyrd-setting-template`'s extraction tool already
needs to target once it stops writing into `library/` (per the issue's own context paragraph).
`Path.with_suffix` is a single stdlib call, keeping the change minimal and dependency-free.

**Alternatives considered**: Appending `.txt` after the original suffix (`rulebook.pdf.txt`) was
rejected — it does not match the issue's own stated mapping and would leave two dots in every
extracted filename for no benefit. A separate manifest file mapping paths explicitly was rejected
as unnecessary indirection; the mirrored-path convention is deterministic and needs no extra state.

## Decision: missing corpus file is a gap, not an exception

**Decision**: `run_corpus_step` checks `corpus_file.is_file()` per present record before reading
it. A record with no corresponding file is added to a `not_yet_extracted` list and excluded from
`documents`; no `read_text` call is ever made against a nonexistent or binary path.

**Rationale**: This is FR-002 and the issue's explicit "reported as a gap, not a crash" acceptance
criterion. Checking existence up front (rather than try/except around `read_text`) makes the
"nothing was read" case explicit and keeps the not-yet-extracted list accurate even if a future
change wants to distinguish "missing" from "unreadable" without changing this check's shape.

**Alternatives considered**: Catching `UnicodeDecodeError`/`OSError` around the read was rejected
as the primary mechanism — it would still attempt to open a file that by design (per the issue)
usually doesn't exist yet in the common case (extraction hasn't run), making the exists-check the
correct-by-construction primary path; a broad except would also risk masking a genuinely corrupt
`corpus/` text file's error rather than a merely-absent one (out of scope per spec.md's edge
cases, which explicitly declines to add new handling for a corrupt `corpus/` file).

## Decision: idempotence keys off the corpus/ text file's hash

**Decision**: `corpus_step_needed`'s comparison dict changes from
`{record.path: record.content_hash for record in present}` (Pass 0's `library/`-file hash) to
`{record.path: pass0.hash_file(corpus_file) for record in present if corpus_file.is_file()}` — the
`corpus/` text file's own hash. The cache's `documents` field is written from this same dict after
a build, so a later run detects a changed `corpus/` file, a newly-appeared one, or a removed one,
independent of whether the `library/` source itself changed.

**Rationale**: FR-003/FR-004/FR-005 and the issue's "idempotence must still hold ... keyed off the
corpus/ text file's hash where extraction has happened, same guarantee as today, just relocated."
Reusing `pass0.hash_file` (already imported into `setting_build.py` as `pass0`) keeps the hash
algorithm and prefix (`sha256:...`) identical to Pass 0's own, so nothing new is introduced.

**Alternatives considered**: Continuing to key off Pass 0's `content_hash` (the `library/` file's
hash) was rejected outright — it is exactly the coupling the issue reports as wrong: a `corpus/`
file could change (re-extraction with better OCR) without the `library/` source changing at all,
and the old key would never notice. Hashing both and combining them was considered and rejected as
unneeded complexity; the `corpus/` file is the sole input the corpus-build step now reads, so only
its hash needs to be the staleness signal.

## Decision: a removed corpus/ file reverts to not-yet-extracted, not a stale cache hit

**Decision**: Because `corpus_step_needed`'s current dict never includes a path that has no
`corpus/` file (see above), a removed extraction naturally drops out of `current`, differs from
the cache's `documents`, and triggers a rebuild in which that record is now reported as
not-yet-extracted again.

**Rationale**: FR-005 and spec.md's edge case explicitly calling this out — no separate code path
is needed since the "gap detection" and "cache key" mechanisms are the same underlying check.

**Alternatives considered**: None seriously considered — this falls out of the chosen design for
free rather than requiring separate handling, which is itself a point in the design's favor.

## Decision: Pass 0 is untouched

**Decision**: No changes to `tools/setting_pass0.py`. Its catalogue step keeps calling
`library_dir.rglob("*")` and classifying by front matter/path only.

**Rationale**: FR-006, and explicitly out of scope per the issue ("setting_pass0.py's catalogue
step continues to enumerate library/ for classification ... this does not change"). Pass 0 never
reads file content for anything beyond a front-matter parse attempt (`classify_document`), so
there is no coupling to relocate.

**Alternatives considered**: None — this is a stated non-goal, not a design choice with
alternatives.
