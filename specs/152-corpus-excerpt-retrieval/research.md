# Phase 0 Research: Corpus excerpt retrieval

No `NEEDS CLARIFICATION` markers remained after `/speckit-clarify` (one architectural question
was resolved by reading `engine/wyrd/corpus_document.py` directly — see spec.md's
Clarifications section). The decisions below were made during planning.

## Decision: a new `corpus_excerpt.py` module, not an addition to `corpus_find.py`

**Rationale**: `corpus_find.py`'s own docstring states it is "deliberately no I/O" and
"deliberately no import of #354/#355/#356" — a query layer over an already-loaded index shape,
never a file reader. Resolving a `documents.json` record's `path` field to an actual corpus text
file and reading it is I/O by definition. Keeping it in a separate module preserves
`corpus_find.py`'s existing zero-filesystem-access testability untouched.

**Alternatives considered**: adding `read_excerpt` directly to `corpus_find.py`. Rejected —
would silently break that module's own documented invariant for every future reader of its
docstring, for no benefit (nothing forces the two functions to live in the same file; nothing in
this feature's five query functions needs to call the excerpt reader internally).

## Decision: reuse `tools/setting_build.py`'s existing path-derivation rule

**Rationale**: `tools/setting_build.py`'s `corpus_text_path(setting_dir, record_path)` already
defines exactly the mapping this feature needs: a document's corpus text lives at the same
relative path under `setting_dir / "corpus"` as its `library/`-relative `path` field, with the
suffix changed to `.txt`. `documents.json`'s `path` field (`engine/wyrd/corpus_document.py`'s
`build_document_record`) is that same `library/`-relative path, caller-supplied and unchanged by
this feature. Re-deriving this mapping independently in a second module would create the "two
lists describing the same thing" drift CLAUDE.md warns about; instead `corpus_excerpt.py`
reimplements the same one-line rule as a pure helper (`corpus_text_path`-equivalent) rather than
importing `tools/` from `engine/` (the reverse of this repo's existing dependency direction —
`engine/` is imported by `tools/`, never the other way around, confirmed by grep: no existing
`engine/wyrd/*.py` imports anything from `tools/`).

## Decision: default window size

**Decision**: 400 characters either side of the offset (800 total), a paragraph-scale window —
plenty to show the sentence/paragraph containing a matched noun/term/table caption without
approaching "load the whole document" territory. Configurable via an optional `window` parameter
per FR-003.

**Rationale**: `docs/design/26-corpus-index.md` describes the goal as "the surrounding passage,"
not a fixed line/sentence count; 400 characters is roughly 60-80 words each side, comfortably
covering a full sentence or two of context in the extracted prose this repo's corpus text
consists of. Computed directly against `wyrd-setting-titan`'s real corpus text (`corpus/01 -
publications/05 - Titan.txt`): average line length 42.8 characters, so a 400-character window
covers roughly 9 lines of that document's wrapped text either side of the offset.

**Alternatives considered**: a line-count window. Rejected — corpus text is extracted from PDFs
with irregular line-wrapping (OCR'd gamebooks wrap unpredictably), so a character-count window is
a more stable, format-independent measure than a line count.

## Decision: `wyrd find` as a new `client.py` verb

**Rationale**: `docs/design/26-corpus-index.md`'s "Retrieval" section names `wyrd find noun`,
`wyrd find rule`, etc. as the intended surface, but no such verb exists in `engine/wyrd/client.py`
today (confirmed by grep — zero references to `corpus_find` anywhere outside `corpus_find.py`
itself and its test). This feature adds the minimal `find` verb (with `noun`/`rule`/`table`
sub-shapes, matching `corpus_find.py`'s own function names) rather than redesigning the CLI —
per spec.md's Assumptions, "if no such surface exists yet at implementation time, User Story 3's
scope is the addition of that minimal surface, not a redesign of one."

**Alternatives considered**: deferring the CLI wiring entirely to a follow-up issue, shipping
only `corpus_excerpt.py`'s library function. Rejected as the primary scope, but the tasks below
still let `read_excerpt` land and be fully tested before the CLI wiring, so a partial delivery
remains useful if the CLI piece needs to split off later.
