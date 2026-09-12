# Implementation Plan: Setting Build Command

**Branch**: `150-setting-build-command` | **Date**: 2026-09-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/150-setting-build-command/spec.md`

## Summary

Add `tools/setting_build.py`, a thin orchestration entry point that runs Pass 0
(`tools/setting_pass0.py`) then the corpus pipeline (`engine/wyrd/corpus_pipeline.py`) against one
setting directory, in order, idempotently, reporting what it processed and skipped. It adds no new
extraction or indexing logic — it imports and calls both pieces' existing functions, does the
document-dict construction and index-file I/O the pure `corpus_pipeline` module deliberately
leaves to its caller, and reuses Pass 0's own catalogue `content_hash` as the sole per-document
freshness signal for the corpus-index step (a small per-document cache file records which content
hash each corpus index was last built from).

## Technical Context

**Language/Version**: Python 3.11+, standard library only (docs/design/27-tooling.md).

**Primary Dependencies**: `tools/setting_pass0.py` (imported as a module) and
`engine.wyrd.corpus_pipeline` / `engine.wyrd.corpus_document` (already on `PYTHONPATH=engine` per
this repo's test convention).

**Storage**: plain JSON files under the target setting directory's `index/` — no database.

**Testing**: `pytest`, run with `PYTHONPATH=engine`, against fixture setting directories under
`tools/fixtures/` (mirroring `tools/fixtures/pass0/`).

**Target Platform**: any POSIX environment `tools/setting_pass0.py` already runs on (this repo's
own CI-equivalent: `python3 -m ruff check .`/`ruff format --check .`/`pytest`).

**Project Type**: single CLI script, `tools/` convention (existing sibling: `tools/setting_pass0.py`).

**Performance Goals**: not applicable — a setting's library is small enough that Pass 0 and the
four deterministic indexes already run in one pass without profiling concerns (per #100/#101).

**Constraints**: stdlib only; no network access; must never read/write any file outside the given
setting directory; must not fetch or embed source material (CLAUDE.md).

**Scale/Scope**: one setting directory per invocation; document counts in the tens-to-low-hundreds
range typical of a `wyrd-setting-*` repo's `library/`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project-specific `.specify/memory/constitution.md` gates apply beyond this repo's own
CLAUDE.md rules, which this plan satisfies directly:
- Engine-repo work only; no setting content populated or touched (only fixtures under
  `tools/fixtures/`).
- No source-fetching tooling added.
- Reuses #100/#101's existing, unmodified functions rather than adding new extraction/indexing
  logic.
- Python 3.11+, stdlib only, ruff-clean.

No violations to track in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/150-setting-build-command/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── cli.md            # Phase 1 output
└── tasks.md              # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

```text
tools/
├── setting_pass0.py           # existing (#100), imported unmodified
├── setting_build.py           # NEW: this feature's entry point
└── fixtures/
    ├── pass0/                 # existing fixtures, reused
    └── setting_build/         # NEW: fixtures exercising the combined command

engine/wyrd/
├── corpus_pipeline.py         # existing (#101), imported unmodified
├── corpus_document.py         # existing, imported unmodified
└── corpus_provenance.py       # existing (#102) — not called by this feature (no public
                                # augmentation performed by this command)

tools/
└── test_setting_build.py      # NEW: unit + idempotence (run-twice) tests, alongside the script
                                # (mirrors tools/test_setting_pass0.py's existing convention)
```

**Structure Decision**: Single-project, `tools/` CLI-script convention — same shape as
`tools/setting_pass0.py` and its sibling `tools/test_setting_pass0.py` / `tools/fixtures/pass0/`.
No new top-level project or package.

## Complexity Tracking

*No Constitution Check violations — this section is empty by design.*
