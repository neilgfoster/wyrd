# Implementation Plan: Session-context resolves the player character from pc.yaml

**Branch**: `160-session-context-reads-pc-yaml` | **Date**: 2026-09-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/160-session-context-reads-pc-yaml/spec.md`

## Summary

`session-context`'s `player_character` field is always `null` against a real chronicle, because
the shared entity set `session-context`/`get`/`find`/`party` all read
(`verbs.load_effective_entities`) globs only `setting/*.md`, `overlay/*.md`, and
`entities/*.md` — never `pc.yaml`, which is where the player character actually lives at the
chronicle root, per `wyrd-chronicle-template`'s deployed layout and the already-merged
`/wyrd-bootstrap` skill (specs/156). The fix loads `pc.yaml` (when present) into that same
effective-entity dict, using the existing single-entity-file loader (`entity.load`), rather than
adding a second, `session-context`-only code path or asking any chronicle-writing skill to
duplicate the character into `entities/`.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (existing engine convention)

**Primary Dependencies**: None new — reuses `engine/wyrd/entity.py` (`entity.load`) and
`engine/wyrd/state.py`, already used by every other entity-loading path.

**Storage**: Chronicle-repo files — adds one more file this repo's engine reads directly
(`<chronicle_dir>/pc.yaml`), alongside `setting/*.md`, `overlay/*.md`, `entities/*.md`,
`chronicle.yaml`.

**Testing**: `pytest`, `PYTHONPATH=engine` (existing convention; see
`tests/test_verbs.py`/`tests/test_loadtier.py`).

**Target Platform**: N/A (library/CLI engine, cross-platform Python).

**Project Type**: Single project — engine library (`engine/wyrd/`) with a thin CLI (`client.py`).

**Performance Goals**: N/A — one additional file read per chronicle-verb call, negligible
against existing glob-and-parse cost.

**Constraints**: Must not touch `engine/wyrd/resolution.py` (issue #414 may be landing
concurrently against that file in a sibling batch member — different files, but avoid touching it
regardless). Must not require any chronicle-writing skill (outside this repo) to change.

**Scale/Scope**: One function (`verbs.load_effective_entities`) plus its test coverage; no new
CLI verb, no schema change.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled Spec Kit template (no project-specific
principles recorded) — no gates apply. This repo's own `CLAUDE.md` supplies the effective
constraints instead (ruff-clean, engine setting-agnostic, docs reachable from README, Spec Kit
cycle for capability changes) and is followed directly rather than through this section.

## Project Structure

### Documentation (this feature)

```text
specs/160-session-context-reads-pc-yaml/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

```text
engine/wyrd/
├── verbs.py             # load_effective_entities gains the pc.yaml read (the actual fix)
├── entity.py            # unchanged; entity.load() is reused as-is
└── loadtier.py           # unchanged; always_tier already handles role: player generically

tests/engine/
└── test_verbs.py        # new regression test: real chronicle layout, pc.yaml at root only
```

**Structure Decision**: Single project, no new module. The fix is a small, additive change to
`verbs.load_effective_entities` — the one place `session-context`/`get`/`find`/`party` already
share their entity set — plus a new test in the existing `tests/engine/test_verbs.py`. No new
files beyond the Spec Kit artifacts under `specs/`.

## Complexity Tracking

*No Constitution Check violations — this section is not applicable.*
