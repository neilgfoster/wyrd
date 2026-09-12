# Implementation Plan: Generalise corpus extraction and indexing for any setting repo

**Branch**: `148-generalise-corpus-extraction` | **Date**: 2026-09-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/148-generalise-corpus-extraction/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/corpus_pipeline.py` module: one orchestration function
(`build_setting_corpus_indexes`) that runs #354/#355's already-built per-document index builders
(`corpus_document.build_document_record`/`build_concordance`/`merge_concordances`,
`corpus_terms.build_terms_index`/`build_tables_index`) across a whole document set in one call,
plus a closed world-building-category vocabulary that routes tagged documents away from the
mechanical (`terms`/`tables`) builders while keeping them in `documents`/`nouns`, plus three pure
functions (`scenario_cache_status`, `documents_needing_scenario_generation`,
`build_scenario_index`) that make the fifth index's "lazy, cached" rule
(`docs/design/26-corpus-index.md`) a deterministic, testable mechanism with the actual model call
injected by the caller. Plain dicts/lists in, plain dicts out, no I/O, no CLI (matching
#338/#339/#357's own established precedent for this epic).

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: `wyrd.corpus_document` and `wyrd.corpus_terms` (both already merged,
#354/#355) — this module orchestrates their existing per-document functions across a document
list; it does not duplicate their logic.

**Storage**: N/A — plain dicts/lists in, plain dicts out. No file I/O, no PDF/OCR extraction
(CLAUDE.md; ADR 0052; spec.md's own "Scope note").

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, imported by a setting repo's own tooling (which does the
file I/O against its own `library/`/`corpus/`/`index/`) — the same split
`check_bestiary.py`/`check_gear.py` already use for setting-owned data.

**Project Type**: single project (engine library).

**Performance Goals**: N/A — linear orchestration over an in-memory document list, not a hot
loop; the corpus is tens of millions of words but this module runs once at ingest per
`docs/design/26-corpus-index.md`'s own "Build and maintenance" table.

**Constraints**: ruff-clean repo-wide; no function introduced performs file I/O, network access,
or a model call itself (FR-007); every record produced carries `setting` (FR-008); a same-setting
duplicate document id is a hard error, never a silent overwrite (FR-002, generalising #97's
slug-collision lesson to the indexing step).

**Scale/Scope**: one orchestration function for the four deterministic indexes, one closed
world-building-category vocabulary, three functions for the fifth (scenario/arcs) index's lazy
cache. Out of scope: PDF/OCR extraction itself, any CLI, any live model call, a persistent index
store, and a proof run against a real (private) setting repo — spec.md's Assumptions section
records why each is out of scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `documents`/`nouns`/`terms`/`tables`/`scenarios` and
  `geography`/`factions`/`history`/`daily-life` are the design document's own names, not borrowed
  from any one setting or source system. PASS.
- Deterministic over inference (`docs/design/27-tooling.md`) — every function introduced is a
  pure orchestration/decision function over caller-supplied data; the one place a model is
  genuinely needed (the scenario/arcs thematic record) is never called by this module itself —
  the caller injects the generator, keeping this module's own behaviour fully deterministic and
  testable without any live call. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- Nothing unpublishable enters this repository (CLAUDE.md) — every test in this feature uses
  synthetic fixture text; no PDF/OCR dependency, no extracted source text, no setting-specific
  catalogue is added. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/148-generalise-corpus-extraction/
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
└── corpus_pipeline.py       # NEW: build_setting_corpus_indexes, WORLD_BUILDING_CATEGORIES,
                              #      scenario_cache_status, documents_needing_scenario_generation,
                              #      build_scenario_index

tests/engine/
└── test_corpus_pipeline.py  # NEW: covers every FR/SC in spec.md

docs/design/26-corpus-index.md   # UPDATED in place: document the orchestration layer, the
                                  # world-building-category boundary, and the lazy-cache
                                  # mechanism now that they exist as code, not just description
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
