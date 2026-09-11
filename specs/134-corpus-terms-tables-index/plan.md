# Implementation Plan: Curated term and structural table indexes (terms.json, tables.json)

**Branch**: `134-corpus-terms-tables-index` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/134-corpus-terms-tables-index/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/corpus_terms.py` module: `build_terms_index` (curated-vocabulary postings
ranked definition-vs-mention by heading proximity) and `build_tables_index` (structural dice-table
detection by row-shape run, with dice-type inference and a caption guess). Plain strings/dicts
in, plain dicts out — matching #354's `corpus_document.py` convention exactly.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`re`).

**Primary Dependencies**: none.

**Storage**: N/A — plain strings/dicts in, plain dicts out.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called by a setting's own ingest tooling (out of scope).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — one pass per document, not a hot loop.

**Constraints**: ruff-clean repo-wide; curated vocabulary closed and fixed in source (not
setting-configurable in this feature); heading/row heuristics documented as such, not a
layout-aware parser.

**Scale/Scope**: term-posting ranking and table detection. Out of scope: table-proximity ranking
for terms (deferred, spec.md's Assumptions), `documents.json`/`nouns.json` (#354, separate).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — the curated terms themselves (Fear, Terror, taint,
  transformation, critical, career exit, trauma, Fate) are already named in
  docs/design/26-corpus-index.md's own worked example, not invented here. PASS.
- Deterministic over inference (ADR 0005) — both indexes are pure pattern-matching functions,
  no model call. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/134-corpus-terms-tables-index/
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
└── corpus_terms.py        # NEW: build_terms_index, build_tables_index

tests/engine/
└── test_corpus_terms.py    # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
