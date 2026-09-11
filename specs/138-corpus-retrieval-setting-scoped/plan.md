# Implementation Plan: Corpus retrieval is scoped to a setting, never unfiltered

**Branch**: `138-corpus-retrieval-setting-scoped` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/138-corpus-retrieval-setting-scoped/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Change all five `corpus_find.py` (#357) functions to require a `setting` argument, filtering
every candidate to that setting (equality for postings/documents, membership for scenarios)
before applying any other criterion. Removes `find_scenario`'s prior optional `setting_in`
keyword, folding it into the now-mandatory `setting`.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none (unchanged).

**Storage**: N/A — plain dicts/lists in, plain dicts out (unchanged).

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library (unchanged).

**Project Type**: single project (engine library).

**Performance Goals**: N/A.

**Constraints**: ruff-clean repo-wide; `setting` is a required argument on every one of the five
functions (FR-003) — no default value that would silently permit an unscoped call.

**Scale/Scope**: signature changes to five existing functions. No new module. No other repo
caller to migrate (grep-verified).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced. PASS.
- Deterministic over inference (ADR 0005) — the setting filter is a pure equality/membership
  check. PASS.
- Isolation invariant enforced structurally (docs/design/21-parallel-chronicles.md) rather than
  left to caller discipline — a required parameter, not an optional one. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/138-corpus-retrieval-setting-scoped/
├── plan.md, research.md, data-model.md, quickstart.md, tasks.md
└── contracts/ (none — internal engine module, no external contract)
```

### Source Code (repository root)

```text
engine/wyrd/corpus_find.py        # all five functions gain a required setting argument
tests/engine/test_corpus_find.py  # rewritten fixtures/tests for the new mandatory filter
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
