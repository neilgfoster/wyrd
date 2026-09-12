# Phase 0 Research: Setting build pipeline — Pass 0

No `NEEDS CLARIFICATION` markers remained in the Technical Context — this feature reuses this
repo's established stdlib-only, deterministic tooling conventions rather than introducing new
ones. The open questions worth recording a decision for are the classification and
idempotence mechanics themselves.

## Decision: classification is signal-based, not content-extraction-based

**Decision**: A document's kind and authority tier are classified from cheap signals available
without extracting or reading the full document body: filename, path segment under `library/`,
and an optional sidecar/front-matter block a setting author may supply (`kind:`, `authority:`).
A `.pdf` or other binary source with no such signal is classified `unclassified`.

**Rationale**: issue #100 states Pass 0 must be "cheap, and running before anything is imported."
Full-text extraction is docs/design/26-corpus-index.md's job, and duplicating it here would erase
the cost distinction the design document draws between Pass 0 and corpus indexing.

**Alternatives considered**: full-text keyword classification (rejected — expensive, and belongs
to `terms.json`/`scenarios.json` downstream, not Pass 0); a required front-matter block on every
file (rejected — real libraries are messy scans; requiring metadata on ingest would make Pass 0
unusable on day one, and #100 asks for something "cheap enough to re-run whenever material is
added," implying it must tolerate an unannotated library too).

## Decision: idempotence via a persisted catalogue keyed by relative path, diffed by content hash

**Decision**: `catalogue.json` stores one record per relative path under `library/`. A re-run
hashes every currently-present file, compares against the stored hash, and only reclassifies a
file whose hash differs from its last-recorded value or that has no prior record at all. A file
previously recorded but no longer found on disk is marked `present: false` rather than deleted
from the catalogue.

**Rationale**: this is the simplest mechanism that satisfies FR-006/FR-007/FR-011 and matches how
this repo's own idempotence precedent works elsewhere (content hashing, not mtime — mtime is
unreliable across a git checkout / re-clone, per general engineering practice this repo also
follows for reproducibility). SHA-256 via stdlib `hashlib` needs no dependency.

**Alternatives considered**: mtime-based staleness (rejected — not reproducible across a fresh
checkout, and issue #100 explicitly asks for hash-based idempotence); re-hashing everything but
only *reporting* what changed without skipping reclassification work (rejected — this satisfies
FR-006's "MUST reprocess only files whose content hash has changed" more weakly than actually
skipping the reclassification step).

## Decision: gap report is derived from a fixed table of setting-authoring requirements

**Decision**: the gap report checks catalogue coverage against a small, fixed list of
requirements mirrored from docs/design/24-authoring-a-setting.md's "What a setting repository
contains" table (`voice.md`, `careers.yaml`, `gear.yaml`, `bestiary.yaml`, `names.yaml`, etc.) —
detected the same signal-based way document kind is (front-matter `provides:` list, or filename
matching the setting-authoring contract's own expected filenames when material has already been
authored as those files directly, rather than raw library source).

**Rationale**: docs/design/24-authoring-a-setting.md is the existing, authoritative statement of
what a setting must supply; re-deriving that list here would create the kind of "two documents
describing one thing differently" drift CLAUDE.md's recurring-faults section warns about. Pass 0
reads that document's table as data instead.

**Alternatives considered**: a Pass-0-owned, separately maintained requirements list (rejected —
duplicates 24-authoring-a-setting.md and will drift from it, the exact fault class CLAUDE.md
names).

## Decision: conflict detection compares (kind, declared-subject) pairs across tiers

**Decision**: two catalogued documents are flagged as a conflict when they share both a
classified `kind` and an optional `subject`/`topic` signal (front-matter, or a shared filename
stem after normalisation) *and* sit at different authority tiers. Same-tier overlaps are not
flagged as conflicts (issue #100's authority-ordering constraint is specifically about a lower
tier silently overwriting a higher one — same-tier duplication is a different, out-of-scope
concern).

**Rationale**: matches FR-008 and User Story 4 exactly, stays deterministic (no semantic
comparison of document bodies), and scopes the check to the actual risk the issue names.

**Alternatives considered**: full-text similarity comparison (rejected — expensive, and not what
issue #100 asks for; it asks that authority ordering never silently resolve a conflict, not that
Pass 0 detect every possible topical overlap in the library).
