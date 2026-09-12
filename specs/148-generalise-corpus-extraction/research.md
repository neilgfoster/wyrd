# Research: Generalise corpus extraction and indexing for any setting repo

## Decision: orchestration lives in `engine/wyrd/corpus_pipeline.py`, not a new `tools/` script

**Rationale**: #354/#355's builders (`corpus_document.py`, `corpus_terms.py`) are already pure,
setting-agnostic, no-I/O functions per document. The only missing piece is calling them across a
whole document list and merging the results — itself a pure operation, so it belongs beside its
inputs in `engine/wyrd/`, not in `tools/` (which this repo reserves for scripts that read a real
path on disk, e.g. `check_bestiary.py`).

**Alternatives considered**: a `tools/build_corpus_index.py` CLI that reads a directory of `.txt`
files and writes `index/*.json`. Rejected for this pass — #338/#339/#357 (this epic's siblings)
all explicitly scoped a CLI out ("no chronicle-level CLI/session-loop entry point exists yet
anywhere in this codebase"), and adding the first one here, ahead of any other subsystem needing
one, would be new infrastructure this feature doesn't need to introduce to satisfy #101's actual
acceptance criteria (which are about the pipeline's *interface* being setting-agnostic, not about
this repo owning a command-line entry point). A setting repo's own tooling is the natural owner
of the thin, path-reading glue, exactly as it already owns PDF/OCR extraction.

## Decision: PDF/OCR extraction stays entirely out of this repo

**Rationale**: every corpus module in this repo states "Python 3.11+, standard library only."
Extracting text from a PDF (and OCR for scanned pages) requires a real third-party dependency
this repo has never carried, and testing it would require either committing copyrighted fixture
PDFs (CLAUDE.md forbids this outright) or mocking a library so thinly the test would prove
nothing. ADR 0052 confirms this reading directly: "extraction and OCR remain pipeline steps (#101)
run per setting repo, with no shared intermediate repo required" — the "no shared intermediate
repo" phrasing describes exactly this repo's role: it supplies the reusable *indexing* logic, not
the extraction step itself.

**Alternatives considered**: vendoring a pure-Python PDF text extractor (no OCR) as a stdlib-only
approximation. Rejected — even a text-layer-only extractor is still a new dependency and still
needs real PDF fixtures to test meaningfully; the genuine PDF/OCR problem (page layout, OCR
confidence) is exactly the part `docs/design/26-corpus-index.md` already documents as
setting-repo work, and duplicating a fraction of it here without OCR would be worse than not
attempting it.

## Decision: world-building routing is a per-document tag, not a new field on `build_document_record`

**Rationale**: `corpus_document.build_document_record`'s signature and its existing tests
(`tests/engine/test_corpus_document.py`) are already merged and stable. Adding a required field
to it would be a breaking change to an already-shipped, tested API for a concern
(terms/tables routing) that belongs to the orchestration layer, not to a single document's
bibliographic record. `corpus_pipeline.py` instead accepts an optional `world_category` per
document in the list it's given, and uses it only to decide whether to call
`corpus_terms.build_terms_index`/`build_tables_index` for that document — `documents.json` and
`nouns.json` are unaffected either way, matching `docs/design/26-corpus-index.md`'s own
"catalogued and concordance-findable regardless" framing for prose setting material.

**Alternatives considered**: extending `build_document_record`'s `document_type` closed
vocabulary (`rules`/`setting`/`adventure`/`magazine`/`fanzine`) with new world-building values.
Rejected — `document_type` already has a `setting` value that plausibly covers this, and
conflating "what kind of publication is this" with "should mechanical-vocabulary detection run
against it" would make one field do two jobs; a `library`-supplied gazetteer chapter and a
`library`-supplied rules chapter can share one PDF's `document_type` while still needing
different treatment at the paragraph/document-chunk level the orchestration layer already
operates at.

## Decision: the scenario/arcs cache-freshness rule is content-hash + schema-version, both caller-supplied

**Rationale**: `docs/design/26-corpus-index.md` states the fifth index is "regenerated only when
the schema changes," and separately that it's cached per document. Two independent staleness
triggers exist (the document's own text changed; the schema this feature's caller uses to
interpret a generated record changed) and neither is something `corpus_pipeline.py` can compute
itself without either hashing text (an implementation choice #97's own extraction-step fix
already owns — "full-path hashing") or hard-coding a schema-version constant that would need to
change every time a caller's own scenario-record shape does. Accepting both as caller-supplied
values keeps this module honest about which parts it actually decides (staleness *given* a
hash/version comparison) versus which parts remain the caller's own concern.

**Alternatives considered**: hashing the document text internally (e.g. via `hashlib.sha256`).
Rejected for this pass — nothing about *how* to hash is specified anywhere in this issue or
`docs/design/26-corpus-index.md`, and picking one here would be inventing a decision the actual
extraction-step tooling (#97, already landed, out of this repo) already made once; duplicating it
risks the two disagreeing. Accepting a caller-supplied hash string keeps the comparison correct
regardless of which hash the caller's extraction step actually uses.
