# Implementation Plan: Setting build pipeline — scheduled execution and web augmentation policy

**Branch**: `149-setting-pipeline-scheduling` | **Date**: 2026-09-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/149-setting-pipeline-scheduling/spec.md`

## Summary

Issue #102 asks two questions: can the setting build pipeline (Pass 0, #100; corpus
extraction/indexing, #101) run unattended on a schedule, and under what explicit rule may a
public source supplement a private setting library. Both are **design and policy** questions this
repo can fully answer without shipping a fetch capability or a live scheduled workflow of its
own — per CLAUDE.md's repository table, the actual workflow file and any live web-fetch script
belong in a `wyrd-setting-<name>` repo, not here (the same boundary #101's own spec drew for
PDF/OCR extraction).

The technical approach: extend `docs/design/26-corpus-index.md`'s existing "Build and
maintenance" section — the document that already answers "when does each index get built" — with
a new subsection recommending GitHub Actions' `schedule` trigger, scoped per setting repo, for
the four deterministic indexes plus Pass 0's catalogue/gap-survey, while explicitly excluding the
scenario index's model call from unattended runs (it stays the existing lazy-on-first-need path).
Alongside it, state the public-augmentation policy and define a small, pure `provenance` data
shape — mirroring `corpus_document.build_document_record`'s existing pattern — that a setting
repo's own tooling can attach to any derived fact, recording whether it came from the library or
a public source and, for the latter, a specific checkable reference.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (docs/design/27-tooling.md) — the same
constraint every sibling corpus module (`corpus_document.py`, `corpus_terms.py`,
`corpus_pipeline.py`) already follows.

**Primary Dependencies**: None (stdlib only). No new runtime dependency; no PDF/OCR/web-fetch
library, consistent with CLAUDE.md and with #101's own precedent.

**Storage**: N/A — the provenance shape is a `dict`/JSON-serializable record a caller attaches to
its own derived-fact records; this repo defines the shape, not a store.

**Testing**: stdlib `unittest` (docs/design/27-tooling.md section 6), matching every sibling corpus module's own test suite under `tests/engine/`.

**Target Platform**: Runs anywhere the rest of `engine/wyrd` runs (no platform dependency). The
*design* recommends GitHub Actions as the scheduling mechanism for a setting repo, but that
workflow file is not part of this repo's own deliverable.

**Project Type**: Library module (an addition to `engine/wyrd`) plus a design-document update —
matches the existing `corpus_*` module shape exactly, no new project type.

**Performance Goals**: N/A — the provenance functions are simple record builders/validators, the
same cost class as `corpus_document.build_document_record`.

**Constraints**: No live network call anywhere in this repository's code or tests (FR-006). No
setting-specific reference or copyrighted fixture content (CLAUDE.md).

**Scale/Scope**: One design-document extension (26-corpus-index.md) plus one small pure module
(`engine/wyrd/corpus_provenance.py`) and its test suite — comparable in size to #354/#355's own
per-index modules, not a new subsystem.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

This repository's `.specify/memory/constitution.md` is the unpopulated Spec Kit template — no
project-specific gates are defined there. The effective constitution for this repo is
`CLAUDE.md`, whose relevant gates are:

- **No setting/system names in `docs/design/` or `README.md`** — the design update names no
  setting, no source system, no real-world publisher; every example is generic.
- **No tooling that fetches source material** (CLAUDE.md) — `corpus_provenance.py` performs no
  I/O of any kind; it is a pure record builder, same shape as its `corpus_document.py` sibling.
- **Standard library only** (`27-tooling.md`) — no dependency added.
- **Deterministic over inference** (`27-tooling.md`) — the provenance record and the
  public-augmentation rule are both plain, checkable logic; nothing here calls a model.
- **Design documents are rewritten in place** — this plan extends `26-corpus-index.md` rather
  than adding a competing document describing the same build cadence differently (CLAUDE.md's own
  named fault class #3).

All gates pass; no violations to justify in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/149-setting-pipeline-scheduling/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks — not created by this command)
```

### Source Code (repository root)

```text
docs/design/
└── 26-corpus-index.md          # extended: scheduled-execution design + public-augmentation
                                 # policy, appended to the existing "Build and maintenance" section

engine/wyrd/
└── corpus_provenance.py        # new: pure provenance-record builder + validator

tests/engine/
└── test_corpus_provenance.py   # new: unit tests for the above
```

**Structure Decision**: Single project (this repo's existing flat `engine/wyrd/*.py` +
`tests/engine/test_*.py` layout — every sibling corpus module already follows it, no new
structure needed). No `contracts/` directory: this module has no external service interface, only a
Python function contract documented in `data-model.md` and exercised directly by
`quickstart.md`'s runnable scenario, the same shape #354–357 used for their own no-CLI,
library-level modules.

## Complexity Tracking

*No Constitution Check violations — this section is intentionally empty.*
