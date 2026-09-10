# Implementation Plan: Lazy Conversion Lifecycle

**Branch**: `121-lazy-conversion-lifecycle` | **Date**: 2026-09-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/121-lazy-conversion-lifecycle/spec.md`

## Summary

Add the deterministic bookkeeping functions the stub/drafted/complete lifecycle needs, on top of
`engine/wyrd/entity.py`'s existing `STATUSES` tuple and `validate()`: stub-sufficiency checking,
`sources` schema checking, a legal-transition predicate, and a pure stub-ratio report. No new
module — these are additional functions in `entity.py`, following the existing pattern of pure
functions over passed-in frontmatter/entity-set data.

## Technical Context

**Language/Version**: Python 3.11, stdlib only

**Primary Dependencies**: none beyond what `entity.py` already imports (`pathlib`, `wyrd.state`)

**Storage**: N/A — pure functions over in-memory frontmatter dicts

**Testing**: pytest, run as `PYTHONPATH=engine python3 -m pytest -q`

**Target Platform**: engine library, setting-agnostic

**Project Type**: library (single project)

**Performance Goals**: N/A — in-memory, no I/O

**Constraints**: ruff-clean (E/F/I/UP, line length 100); stdlib-only; no source-fetching tooling

**Scale/Scope**: four new functions in one existing module

## Constitution Check

No `.specify/memory/constitution.md` exists in this repo — CLAUDE.md carries the equivalent rules
(setting-agnostic engine, deterministic-over-inference, ruff-clean, stdlib-only). This feature:

- Adds no setting-specific vocabulary (field/function names are descriptive English).
- Adds no source-fetching tooling (pure functions over already-loaded data).
- Follows the existing engine module pattern (setting-supplied data passed as arguments).

No violations; no complexity to track.

## Project Structure

### Documentation (this feature)

```text
specs/121-lazy-conversion-lifecycle/
├── plan.md              # This file
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

No `data-model.md`/`contracts/` — the "data model" is entirely the existing entity frontmatter
schema (`docs/design/25-entities.md`), extended by this feature's `sources` field; no new
resource/API contracts are introduced.

### Source Code (repository root)

```text
engine/wyrd/
└── entity.py             # add: sources schema constant, check_stub_sufficiency(),
                           #      validate_source(), legal_transition(), status_counts()

tests/engine/
└── test_entity.py        # add test cases for each new function
```

**Structure Decision**: Single project (existing `engine/wyrd/` library + `tests/engine/`). All
four new functions land in `entity.py` beside `STATUSES`/`validate()`, since they operate on the
same frontmatter shape and the module's docstring already frames it as "common-schema and
per-type validation."

## Complexity Tracking

No violations — table omitted.
