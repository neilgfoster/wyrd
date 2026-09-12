# Implementation Plan: Setting build pipeline — Pass 0 catalogue, gap survey and idempotence

**Branch**: `147-setting-pass-0-catalogue` | **Date**: 2026-09-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/147-setting-pass-0-catalogue/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `tools/setting_pass0.py`: a stdlib-only, mostly-scripted pass that walks a setting's
`library/` directory, classifies each file by kind and authority tier (core rules / expansions /
community material / scenarios-adventures / unclassified), derives an authority-ordered
processing list, records a content hash per source file, persists a catalogue at
`<setting-dir>/index/catalogue.json` (the `index/` location docs/design/24-authoring-a-setting.md
already reserves for corpus indexes), compares catalogue coverage against the
setting-authoring contract to build a gap report, and detects same-subject conflicts across
authority tiers without ever letting one document's record overwrite another's. A re-run diffs
against the persisted catalogue by hash and touches only what changed. Like `tools/backlog.py`
and `tools/check_settings_catalogue.py`, this is a CLI tool with pure, testable functions
underneath — it does not depend on or write to any real `wyrd-setting-*` repository; tests run it
against fixture library trees.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none — `hashlib` for content hashes, `json` for the catalogue/gap-report
artefacts, `pathlib` for traversal. No third-party YAML dependency; where a document declares
front-matter, it is read with `check_bestiary.py`'s existing small restricted-subset YAML reader
rather than a new one.

**Storage**: a JSON catalogue file at `<setting-dir>/index/catalogue.json` (plus a
`gap_report.json` alongside it) — the persisted state idempotence diffs against. This is the one
piece of local state the feature owns; everything else is pure functions over it.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`, driven against fixture library trees
under `tools/fixtures/pass0/` (this repo's own test fixtures — never a real setting repo's
content, per CLAUDE.md's repository table).

**Target Platform**: CLI tool, run by a setting author or by a later pipeline stage against that
setting repo's own `library/`.

**Project Type**: single project — one CLI script plus its test module, in this repo's existing
`tools/` layout.

**Performance Goals**: N/A — Pass 0 is explicitly the cheap, pre-import pass (issue #100); no
throughput target beyond "cheap enough to re-run whenever material is added" (idempotence is what
delivers that, not raw speed).

**Constraints**: ruff-clean repo-wide; no third-party dependency; classification and conflict
detection are deterministic and signal-based (docs/design/27-tooling.md), never a model call —
Pass 0 explicitly precedes the model-assisted `scenarios` index build
(docs/design/26-corpus-index.md) rather than duplicating it.

**Scale/Scope**: catalogue, processing order, gap report, idempotent hash-diffed re-run, and
conflict recording. Out of scope: extracting document text, building any of the five corpus
indexes themselves (#133-#136), and touching any specific setting repo's content.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — "core rules", "expansions", "community material",
  "scenarios/adventures" are issue #100's own engine-neutral authority-tier names; document kinds
  stay in the same closed, descriptive vocabulary. PASS.
- Nothing unpublishable enters the repo — this feature ships tooling and fixture text this repo
  authors itself; it never fetches, stores, or reproduces any real setting's source material
  (CLAUDE.md). PASS.
- Deterministic over inference (docs/design/27-tooling.md) — classification, authority ordering,
  gap comparison, hashing, and conflict detection are all pure, deterministic functions of their
  input; nothing here is a model call. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- Engine-repo scope boundary (CLAUDE.md's repository table) — Pass 0 is design/tooling that will
  later run against any `wyrd-setting-*` repo; this feature itself never populates or touches one.
  Enforced by testing exclusively against fixtures under `tools/fixtures/pass0/`. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/147-setting-pass-0-catalogue/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI contract — this is a script, not a network API)
└── tasks.md             # Phase 2 output (kord-feature-tasks, not this command)
```

### Source Code (repository root)

```text
tools/
├── setting_pass0.py       # NEW: classify, order, catalogue, gap-report, hash-diff, conflicts, CLI
├── test_setting_pass0.py  # NEW: covers every FR/SC in spec.md
└── fixtures/pass0/        # NEW: small fixture library trees (never real setting content)
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
