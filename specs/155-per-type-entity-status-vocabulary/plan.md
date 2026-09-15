# Implementation Plan: Per-type entity status vocabulary

**Branch**: `155-per-type-entity-status-vocabulary` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/155-per-type-entity-status-vocabulary/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`engine/wyrd/entity.py`'s `validate()` checks every entity's `status` field against one global
`STATUSES = ("stub", "drafted", "complete")` tuple. `docs/design/22-state.md` documents two
narrower vocabularies that override this default: a `character` entity with `role: companion`
uses `with-party | away | dead | lost | departed`, and a `thread` entity uses
`open | resolved | cold | never-answered`. Every other entity type — confirmed by reading
`docs/design/22-state.md` and `docs/design/25-entities.md` in full — shares the one default
vocabulary from the common schema, with no type-specific override documented anywhere. The fix
replaces the single global lookup in `validate()` with a per-type (and, for `character`,
per-role) vocabulary lookup, keeping the default as the fallback for every type/role combination
that has no override. `legal_transition()` and `status_counts()` are untouched: neither is called
anywhere outside their own tests, and both only ever make sense against the linear
stub→drafted→complete authoring progression the companion/thread vocabularies aren't shaped like
(no ordering, no "further along" reading) — extending them is a new capability the issue never
asked for, not a gap in this fix.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (existing constraint, `engine/wyrd/entity.py`'s own module docstring)

**Primary Dependencies**: none beyond `wyrd.state` (already imported by `entity.py`)

**Storage**: entity files on disk (markdown + YAML frontmatter), read via `wyrd.state.load_entity` — unchanged by this fix

**Testing**: `unittest` (stdlib), no pytest — `docs/design/27-tooling.md` section 6; existing convention in `tests/engine/test_entity.py`

**Target Platform**: N/A (library code, not a service)

**Project Type**: single project — engine library (`engine/wyrd/`) with a matching `tests/engine/` suite

**Performance Goals**: N/A — a closed-vocabulary membership check, no measurable performance dimension

**Constraints**: `python3 -m ruff check .` and `python3 -m ruff format --check .` must stay clean repo-wide (`CLAUDE.md`)

**Scale/Scope**: one function (`validate()`) in one module, plus a new lookup table; no new files, no schema migration (existing entity files already carry values `validate()` should have always accepted)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, the Constitution Check is evaluated against `CLAUDE.md`
and the accepted ADRs:

- **Capability changes go through the Spec Kit cycle** (`CLAUDE.md`) — this plan exists because
  of that gate; `validate()`'s accepted-vocabulary contract is capability, not documentation.
- **Deterministic over inference** ([ADR 0005](../../docs/adr/0005-deterministic-over-inference.md)) —
  the per-type vocabulary is read directly from `docs/design/22-state.md`/`25-entities.md` and
  the new end-to-end test checks it by loading a real file, not by asserting a claim about it.
- **No setting or system names in `docs/design/` or engine code** — the status values here
  (`with-party`, `open`, etc.) are already the engine's own documented vocabulary, not borrowed
  from a source system; no new vocabulary is introduced by this fix.
- **Rule changes apply forward only, history never recomputed** ([`29-evolution.md`](../../docs/design/29-evolution.md)) —
  N/A: this corrects `validate()` to accept values the design already specified; it does not
  change what any entity's status *means*, and no existing entity file needs rewriting.
- **Design documents describe the present** — `docs/design/22-state.md` and `25-entities.md`
  already document the correct vocabularies; this fix brings the code in line with them, so no
  design document needs editing.

No violations. Nothing in Complexity Tracking below.

## Project Structure

### Documentation (this feature)

```text
specs/155-per-type-entity-status-vocabulary/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

No `contracts/` directory: this feature has no external interface (API, CLI verb, schema) of its
own — `validate(frontmatter: dict) -> dict`'s signature and calling convention are unchanged, only
which status values it accepts.

### Source Code (repository root)

```text
engine/
└── wyrd/
    └── entity.py           # validate(): replace the flat STATUSES check with a per-type/role lookup

tests/
└── engine/
    └── test_entity.py      # new end-to-end tests: real on-disk companion/thread entity files
```

**Structure Decision**: single project (this repo's existing `engine/wyrd/` library +
`tests/engine/` suite). No new directories; the change is confined to `entity.py` and its test
module, matching the issue's own stated scope.

## Complexity Tracking

*No violations — table intentionally omitted.*
