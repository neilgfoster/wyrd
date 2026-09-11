# Implementation Plan: Bibliographic and concordance indexes (documents.json, nouns.json)

**Branch**: `133-corpus-document-nouns-index` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/133-corpus-document-nouns-index/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/corpus_document.py` module: `build_document_record` (bibliographic
metadata + a stdlib-only OCR-confidence heuristic) and `build_concordance` (proper-noun
extraction: capitalised, non-sentence-initial, stop-listed tokens, mapped to
document/count/offsets). Plain strings/dicts in, plain dicts out — this tooling never touches
source files itself, matching every other engine module's no-I/O convention.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`re` for tokenization/sentence
boundaries).

**Primary Dependencies**: none — no third-party dictionary/NLP library, per this repo's
stdlib-only constraint.

**Storage**: N/A — plain strings/dicts in, plain dicts out. Persisting `documents.json`/
`nouns.json` themselves is a setting-repo/caller concern, out of scope.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called by a setting's own ingest tooling (out of scope
here).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — this is a one-pass-per-document build step, not a hot loop; no
specific throughput target for this feature (a real corpus is tens of millions of words, but
optimising that is #28-maintenance's `wyrd optimise` concern, not this feature's).

**Constraints**: ruff-clean repo-wide; no third-party dependency; `ocr_confidence` is
documented honestly as a heuristic, not a real dictionary lookup (spec.md's Assumptions).

**Scale/Scope**: document-record building and concordance building. Out of scope: file I/O,
`documents.json`/`nouns.json` persistence, a real dictionary-word-ratio implementation.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `document_type`, `extraction_method`,
  `ocr_confidence`, `concordance` are all existing engine-neutral terms already in
  docs/design/26-corpus-index.md. PASS.
- Nothing unpublishable enters the repo — no source text, no tooling that fetches source
  material; this module operates on caller-supplied text (CLAUDE.md). PASS.
- Deterministic over inference (ADR 0005) — both builders are pure, deterministic functions of
  their input text; `ocr_confidence` is a fixed formula, not a model call. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/133-corpus-document-nouns-index/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (none — internal engine module, no external contract)
└── tasks.md             # Phase 2 output (kord-feature-tasks, not this command)
```

### Source Code (repository root)

```text
engine/wyrd/
└── corpus_document.py     # NEW: build_document_record, build_concordance

tests/engine/
└── test_corpus_document.py  # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
