# Implementation Plan: Chronicle Entity Loader Layout

**Branch**: `170-chronicle-entity-loader-layout` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/170-chronicle-entity-loader-layout/spec.md`

## Summary

`resolution._load_chronicle_entities` globs entity files as flat, top-level `*.md` under
`setting/`, `overlay/`, and `entities/`. Real bootstrapped chronicles nest entity files one level
down under a per-type subdirectory, as `.yaml`. The fix widens the glob to also walk
`<dir>/<type>/*.yaml` (with `setting/`'s entities specifically under `setting/entities/<type>/`),
while keeping the old flat `*.md` glob for back-compat (FR-004). No parsing change is needed —
`state.load_entity` is already extension-agnostic (research.md) — and no special-case guard
against non-entity files is needed either, since the corrected glob simply stops matching them
(research.md).

## Technical Context

**Language/Version**: Python 3.11+, standard library only (existing repo convention)

**Primary Dependencies**: none new — reuses `wyrd.state.load_entity`/`wyrd.entity.load`/
`wyrd.entity.load_set`/`wyrd.entity.resolve_entity`, all unchanged

**Storage**: chronicle repo filesystem layout (`setting/`, `overlay/`, `entities/` directories) —
no database, no new file format

**Testing**: pytest, run via `PYTHONPATH=engine python3 -m pytest tests/engine/...`
(existing repo convention)

**Target Platform**: N/A — pure Python library function, platform-independent

**Project Type**: single project (engine library)

**Performance Goals**: N/A — no performance-sensitive path; one additional glob pass per
directory is negligible against typical chronicle sizes

**Constraints**: `python3 -m ruff check .` and `python3 -m ruff format --check .` must stay clean
repo-wide (CLAUDE.md)

**Scale/Scope**: single function (`_load_chronicle_entities`) plus its private helper surface in
`engine/wyrd/resolution.py`; no other module changes required (verbs.py already delegates to this
function rather than duplicating the glob, confirmed by reading its source)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No `.specify/memory/constitution.md` exists in this repo; the operative governance document is
this repo's own `CLAUDE.md`. Relevant gates checked:

- **Capability change goes through the Spec Kit cycle** (CLAUDE.md) — satisfied: this plan is
  that cycle's plan phase, following `kord-feature-specify` and `kord-feature-clarify`.
- **The engine is setting-agnostic** (CLAUDE.md) — satisfied: the fix reads entity-type directory
  names generically (whatever `entity.ENTITY_TYPES` or the chronicle's own directories name them),
  introduces no setting-specific vocabulary.
- **Deterministic over inference** (CLAUDE.md) — satisfied: the canonical layout is confirmed by
  reading real on-disk chronicles and setting output directly (research.md), not assumed; the
  overlay-side shape is recorded as a deliberate decision (spec.md Clarifications) precisely
  because it could not be confirmed by inspection.
- **Design documents rewritten in place, ADRs for genuine alternatives rejected** — this feature
  does not warrant a new ADR: no real alternative was rejected that would have produced a
  different engine (the flat-vs-nested question is "what does bootstrap already produce," not a
  design choice between two workable engine behaviours) except the one genuine decision already
  resolved by clarification (overlay's per-type subdirectory) — too narrow to be its own ADR, and
  it will be recorded in docs/design/22-state.md's rewritten description (FR-006) instead.

No violations. Gate passes.

## Project Structure

### Documentation (this feature)

```text
specs/170-chronicle-entity-loader-layout/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output (no new entities — documents the layout change)
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── _load_chronicle_entities.md   # Phase 1 output
└── tasks.md              # Phase 2 output (/speckit-tasks — not created by this command)
```

### Source Code (repository root)

```text
engine/
├── wyrd/
│   ├── resolution.py    # _load_chronicle_entities, _find_chronicle_root -- fix lands here
│   ├── entity.py         # load/load_set/resolve_entity -- read-only reference, unchanged
│   ├── state.py           # load_entity/parse_entity -- read-only reference, unchanged
│   └── verbs.py          # load_effective_entities -- delegates to resolution.py, unchanged
tests/
└── engine/
    └── test_resolution.py   # new tests for the nested-layout + back-compat + non-entity-file cases

docs/
└── design/
    └── 22-state.md       # updated to name the confirmed layout (FR-006)
```

**Structure Decision**: Single project, existing engine library layout. The entire fix is
contained in `engine/wyrd/resolution.py` (one function and, if needed, its directory-discovery
helper); no new module, no new top-level directory. Tests extend the existing
`engine/tests/engine/test_resolution.py`. Documentation update lands in the existing
`docs/design/22-state.md`, not a new document.

## Complexity Tracking

*No Constitution Check violations — table omitted.*
