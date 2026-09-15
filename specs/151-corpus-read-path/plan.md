# Implementation Plan: Corpus-build reads extracted text from corpus/, not library/

**Branch**: `151-corpus-read-path` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/151-corpus-read-path/spec.md`

## Summary

`tools/setting_build.py`'s `run_corpus_step` currently reads each present catalogue record's text
straight from `library/<record.path>`. That changes to read from
`corpus/<record.path with suffix changed to .txt>` instead. A present record with no matching
`corpus/` file is excluded from the built indexes and named in the run's `corpus` report as
not-yet-extracted, rather than raising `UnicodeDecodeError`. The idempotence cache
(`corpus_build_cache.json`) switches from keying on Pass 0's `content_hash` (the `library/` file's
hash) to a hash of the `corpus/` text file itself, computed the same way (`pass0.hash_file`,
already imported). `tools/setting_pass0.py` is untouched — its catalogue step never reads file
content beyond front matter and keeps enumerating `library/` exactly as before.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (docs/design/27-tooling.md).

**Primary Dependencies**: `tools/setting_pass0.py` (imported as a module, unchanged — reused only
for `hash_file` and its existing `CatalogueRecord`/`Catalogue` types) and
`engine.wyrd.corpus_pipeline` (unchanged).

**Storage**: plain JSON files under the target setting directory's `index/` — no database. This
feature adds no new file, only changes what `corpus_build_cache.json`'s `documents` values mean
(a `corpus/` text file's hash instead of the `library/` source's hash) and adds one new field
(`not_yet_extracted`) to the `corpus` report sub-object `run_corpus_step` returns.

**Testing**: `pytest`, run with `PYTHONPATH=engine`, against fixture setting directories under
`tools/fixtures/pass0/` and `tools/fixtures/setting_build/`, each gaining a `corpus/` counterpart
tree.

**Target Platform**: any POSIX environment `tools/setting_build.py` already runs on.

**Project Type**: single CLI script, `tools/` convention (existing sibling: `tools/setting_pass0.py`).

**Performance Goals**: not applicable — same scale as #388 (tens-to-low-hundreds of documents per
setting), no profiling concerns.

**Constraints**: stdlib only; no network access; must never read/write any file outside the given
setting directory; must not fetch or embed source material (CLAUDE.md); Pass 0's own gap-report
content (the ten setting-authoring requirements) must not change in meaning.

**Scale/Scope**: one setting directory per invocation, same as #388.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project-specific `.specify/memory/constitution.md` gates apply beyond this repo's own
CLAUDE.md rules, which this plan satisfies directly:
- Engine-repo work only; no setting content populated or touched (only fixtures under
  `tools/fixtures/`), and no extracted source text or copyrighted quotes enter this repo — fixture
  "extracted text" is the same kind of placeholder fixture prose the existing fixtures already use.
- No source-fetching or extraction tooling added — this feature only relocates a read path.
- Reuses #100/#388's existing, unmodified functions (`pass0.hash_file`, `CatalogueRecord`,
  `corpus_pipeline.build_setting_corpus_indexes`) rather than adding new extraction/indexing logic.
- Python 3.11+, stdlib only, ruff-clean.

No violations to track in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/151-corpus-read-path/
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
├── setting_pass0.py                  # existing (#100), unmodified
├── setting_build.py                  # MODIFIED: run_corpus_step's read path + cache key
├── test_setting_pass0.py             # unmodified
├── test_setting_build.py             # MODIFIED: new corpus/-present and not-yet-extracted tests
└── fixtures/
    ├── pass0/basic/
    │   ├── library/                   # existing, unmodified
    │   └── corpus/                    # NEW: extracted-text counterpart for every present record
    └── setting_build/
        ├── basic/
        │   ├── library/                # existing, unmodified
        │   └── corpus/                 # NEW: extracted-text counterpart for both present records
        ├── world_building/
        │   ├── library/                # existing, unmodified
        │   └── corpus/                 # NEW: extracted-text counterpart for gazetteer.md
        └── partial_extraction/         # NEW fixture: one extracted record, one not-yet-extracted
            ├── library/
            └── corpus/                 # only the extracted record's .txt file
```

**Structure Decision**: Single project, `tools/` CLI-script convention already established by
#100/#388. No new top-level directory; the only additions are `corpus/` counterparts under
existing fixture trees plus one new fixture directory (`partial_extraction`) purpose-built to
exercise the not-yet-extracted path without disturbing the existing `basic`/`world_building`
fixtures' other test coverage.

## Complexity Tracking

*No violations — table omitted per template instructions.*
