# Implementation Plan: Corpus index retrieval queries (wyrd find)

**Branch**: `136-corpus-retrieval` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/136-corpus-retrieval/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/corpus_find.py` module: `find_noun`, `find_rule`, `find_table`,
`find_scenario`, `find_doc` — five query functions over the index shapes #354/#355/#356 already
build. Plain dicts/lists in, plain dicts out; no CLI wiring (matching #338/#339's precedent).

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none — operates purely on the dict/list shapes `corpus_document.py`
(#354), `corpus_terms.py` (#355), `corpus_scenario.py` (#356) already produce; no import of
those modules is required since this module only reads their output shape.

**Storage**: N/A — plain dicts/lists in, plain dicts out.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called by a setting's own tooling or a future session-loop
integration (out of scope here).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — linear scans over already-built in-memory indexes, not a hot loop.

**Constraints**: ruff-clean repo-wide; no result ever carries a loaded text passage (FR-007).

**Scale/Scope**: five query functions. Out of scope: building the indexes themselves (#354/#355/
#356), CLI wiring, a persistent index store.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `find_noun`/`find_rule`/`find_table`/
  `find_scenario`/`find_doc` are the design document's own retrieval names. PASS.
- Deterministic over inference (ADR 0005) — every query is a pure filter/lookup over
  caller-supplied data. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/136-corpus-retrieval/
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
└── corpus_find.py          # NEW: find_noun, find_rule, find_table, find_scenario, find_doc

tests/engine/
└── test_corpus_find.py      # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
