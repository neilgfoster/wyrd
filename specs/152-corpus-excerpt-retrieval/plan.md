# Implementation Plan: Corpus excerpt retrieval — a bounded read at a doc+offset

**Branch**: `152-corpus-excerpt-retrieval` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/152-corpus-excerpt-retrieval/spec.md`

## Summary

`corpus_find.py`'s five query functions (#357) return `{doc, offset}` coordinates but never the
text itself, leaving every caller to open and search a whole extracted document by hand — the
exact gap `docs/design/26-corpus-index.md` promised a "bounded read" would close. This feature
adds that bounded read: a function that resolves a `documents.json` record's `path` field to its
`corpus/` text file (mirroring `tools/setting_build.py`'s own `corpus_text_path` derivation) and
returns a windowed excerpt around a given offset, plus a thin `wyrd find` CLI surface (new —
none exists today) that wires the five query functions and this excerpt reader together.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (repo-wide convention, CLAUDE.md)

**Primary Dependencies**: None new — `pathlib`, stdlib only

**Storage**: Reads plain-text files under a setting repo's own `corpus/` directory; no new
on-disk schema

**Testing**: stdlib `unittest`, no pytest (`docs/design/27-tooling.md` section 6), matching
`tests/engine/test_corpus_find.py`'s existing style

**Target Platform**: Linux/macOS CLI (matches `engine/wyrd/client.py`'s existing `wyrd` verbs)

**Project Type**: Library + CLI verb, single project (this repo's existing `engine/` + `tools/`
layout)

**Performance Goals**: N/A — a single bounded file read per call, not a hot path

**Constraints**: Deterministic (same inputs, same excerpt); never raises on a malformed/stale
query, matching `corpus_find.py`'s existing "never an error" contract

**Scale/Scope**: One new I/O-performing function plus a `find` CLI verb; no change to any index
builder or existing setting's already-built indexes

## Constitution Check

*Evaluated against CLAUDE.md and the accepted ADRs (`.specify/memory/constitution.md` is a
pointer to these, not a separate authority).*

- **Nothing unpublishable enters this repo**: this feature touches only `engine/`/`tools/`
  code and this repo's own tests/specs — no corpus text, no setting-specific content. **Pass.**
- **No setting/system names in `design/`/`README.md`**: this feature adds no design document and
  changes no existing one; its own spec/plan (`specs/`) may reference real setting repos
  (`wyrd-setting-titan`, `wyrd-setting-darkfuture`) for verification, which is normal spec
  content, not `design/` prose. **Pass.**
- **Deterministic over inference**: the excerpt reader is a pure string-slice operation once the
  file is read — no model call, no inference. **Pass.**
- **Capability changes go through the Spec Kit cycle**: this plan is that cycle. **Pass.**
- **Setting-scoped corpus queries** (`docs/design/21-parallel-chronicles.md`): the excerpt
  function requires `setting` and only resolves a document belonging to that setting, matching
  every existing `corpus_find.py` function (#364). **Pass.**

No violations; Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/152-corpus-excerpt-retrieval/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/            # Phase 1 output — CLI contract for the new `find` verb
└── tasks.md              # Phase 2 output (kord-feature-tasks — not created here)
```

### Source Code (repository root)

```text
engine/wyrd/
├── corpus_find.py        # existing (#357) — unchanged; stays pure, no I/O
└── corpus_excerpt.py      # NEW — read_excerpt(), the one I/O-performing function this feature adds

tools/
└── (no change — this feature does not touch the extraction/index-build pipeline)

engine/wyrd/client.py       # extended — a new `find` verb wiring corpus_find + corpus_excerpt

tests/engine/
├── test_corpus_find.py    # existing — unchanged
└── test_corpus_excerpt.py # NEW — unit tests against fixture text files
```

**Structure Decision**: `corpus_excerpt.py` is a new, separate module rather than an addition to
`corpus_find.py`, because `corpus_find.py`'s own docstring states it is "deliberately no I/O" —
resolving a `path` field to an actual file read is I/O by definition. This keeps `corpus_find.py`
importable and testable with zero filesystem access, exactly as it is today, while the new
module owns the one filesystem-touching operation this feature adds. `client.py`'s `find` verb is
the integration point: it calls `corpus_find.py`'s query functions for coordinates, then
`corpus_excerpt.py`'s `read_excerpt` for each result's text.
