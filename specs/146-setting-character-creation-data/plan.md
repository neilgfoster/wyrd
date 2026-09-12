# Implementation Plan: Setting-Level Character Creation Data

**Branch**: `146-setting-character-creation-data` | **Date**: 2026-09-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/146-setting-character-creation-data/spec.md`

**Note**: `.specify/memory/constitution.md` is the unfilled Spec Kit template in this repo — this
repo's actual governing document is [`CLAUDE.md`](../../CLAUDE.md), consulted directly below.

## Summary

Document the schema of five setting files character creation needs but has never had a schema
for (`loyalties.yaml`, `drives.yaml`, `misfortunes.yaml`, `names.yaml`, and optional
`ancestries.yaml`) in `docs/design/24-authoring-a-setting.md`, alongside the existing
`careers.yaml`/`gear.yaml` schemas; then write one validator,
`tools/check_character_creation_data.py`, that checks a setting directory's full
character-creation surface — including `careers.yaml`, which is schema'd today but has never had
a validator — against those schemas. Populating any actual setting's files (including
`wyrd-setting-template`) is out of scope here per the repository table in `CLAUDE.md`.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`docs/design/27-tooling.md`).

**Primary Dependencies**: None — reuses `tools/check_bestiary.py`'s existing small YAML reader
(`read_yaml`/`YamlError`), the same restricted-subset reader `check_gear.py` and `check_setting.py`
already import rather than adding a second one.

**Storage**: N/A — reads setting YAML files from a path the caller supplies; writes nothing.

**Testing**: `pytest`, following `tools/test_check_setting.py`'s existing pattern (fixture
directories under a temp path, one test per rejected-shape class).

**Target Platform**: CLI tool, run from a developer's shell or another script, same as every
other `tools/check_*.py`.

**Project Type**: Single project — this repo's existing `tools/` CLI-validator layout.

**Performance Goals**: N/A — validates a handful of small YAML files; no throughput target.

**Constraints**: Must not add a third-party dependency (`docs/design/27-tooling.md` section 2).
Must report every failure found, not just the first (matches `check_bestiary.py`/`check_gear.py`).

**Scale/Scope**: One new validator script, one new test file, one doc section addition. No engine
runtime code changes — this is setting-data validation tooling, not a new engine mechanism.

## Constitution Check

*No project-specific constitution is filled in for this repo (see Note above); `CLAUDE.md` is
the operative governance document. Relevant checks:*

- **Engine is setting-agnostic** (`CLAUDE.md`): the new schemas and validator name no setting or
  system — they generalize the same shape `careers.yaml`/`gear.yaml` already use. PASS.
- **Deterministic over inference** (`docs/design/27-tooling.md`): a validator script replaces what
  was previously left to an author's or GM's judgement. PASS — this is the entire point of the
  feature.
- **The engine is setting-agnostic; a setting may never add a mechanism** (`24-authoring-a-setting.md`):
  this feature adds no new mechanism — Loyalty relations (ADR 0015), Drives/Misfortunes/Names/
  ancestries (`11-character-creation.md` §3-4) already exist as engine concepts; this only gives
  their setting-side data a schema and a check. PASS.
- **No unpublishable content enters this repository** (`CLAUDE.md`): all new files are schemas and
  a generic validator; no setting's actual data is added here. PASS.

No violations; Complexity Tracking table is empty.

## Project Structure

### Documentation (this feature)

```text
specs/146-setting-character-creation-data/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
└── tasks.md              # Phase 2 output (kord-feature-tasks)
```

No `contracts/` directory: this feature has no network-facing or inter-service interface. Its one
"contract" is the YAML schema itself, which is documented in `data-model.md` and
`docs/design/24-authoring-a-setting.md` directly, and enforced by the validator script rather than
a separate machine-readable contract file — the same pattern every existing `check_*.py` in this
repo already follows (no `openapi.yaml`/JSON-schema file backs `check_gear.py` either; the Python
validator function *is* the contract).

### Source Code (repository root)

```text
docs/design/
├── 24-authoring-a-setting.md   # add loyalties.yaml/drives.yaml/misfortunes.yaml/names.yaml/
│                                # ancestries.yaml schema sections
└── 11-character-creation.md    # §4 table: link each requirement to its schema

tools/
├── check_character_creation_data.py   # new validator (careers, loyalties, drives,
│                                       # misfortunes, names, optional ancestries)
└── test_check_character_creation_data.py   # new tests, fixture-per-failure-class
```

**Structure Decision**: Single project, matching every existing `tools/check_*.py` +
`tools/test_check_*.py` pair in this repo. No new top-level directory; the feature is one script,
one test file, and two doc edits.
