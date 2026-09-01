# Implementation Plan: Engine scaffolding

**Branch**: `221-engine-scaffolding` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/075-engine-scaffolding/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Stand up `engine/` with three load-bearing pieces the rest of the engine build depends on: a
deterministic d100 dice primitive (principle 1, "the dice bind the GM"), an atomic
save/load for chronicle state (principle 2, "persist before narrate"), and a minimal CLI entry
point later features attach their own commands to. Python 3.11+, standard library only, per
`docs/design/27-tooling.md`.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: None — standard library only (`docs/design/27-tooling.md`)

**Storage**: Plain files on disk (YAML state files), no database

**Testing**: stdlib `unittest`, no pytest — `docs/design/27-tooling.md` section 6 states this
explicitly, and `tools/test_*.py` already follows it repo-wide.

**Target Platform**: Any platform with Python 3.11+ (local CLI, no server)

**Project Type**: CLI / library (single project — `engine/` is a Python package, no
frontend/backend split)

**Performance Goals**: Not performance-sensitive — a single interactive user, one command at a
time. No specific latency target beyond "instant" at terminal scale.

**Constraints**: Stdlib-only, zero-dependency, zero-backend, no daemon, no database
(`docs/design/27-tooling.md`). Setting-agnostic: nothing under `engine/` may name a specific
setting or system (`CLAUDE.md`).

**Scale/Scope**: Single chronicle, single active session at a time (`docs/design/02-architecture.md`'s
"two chronicles never share a repository" guarantee) — no concurrency handling required.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, checked against `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repository** — N/A, this feature adds only original code
  and tests, no extracted source material. PASS.
- **No setting or system names in `design/` or `README.md`** — N/A, this feature touches
  `engine/` and `specs/`, not `docs/design/` or `README.md`. The code itself must still avoid
  setting-specific vocabulary (spec FR-011). PASS.
- **Tone is a setting property** — N/A, this feature has no tone-bearing content (it is
  infrastructure: dice, state, CLI). PASS.
- **Deterministic over inference** (ADR 0005) — this feature *is* the deterministic-over-inference
  guarantee for dice and state; nothing here is inferred by a model. PASS.
- **Rule changes apply forward only; history never recomputed** — N/A, no existing rule is being
  changed; this is new infrastructure. PASS.
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** — satisfied
  by this very plan; `specs/075-engine-scaffolding/` is being committed alongside the code.

No violations. Nothing to record in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/075-engine-scaffolding/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

`docs/design/27-tooling.md` section 3 already specifies this package's exact shape — a single
tool catalog (`TOOLS`) driving both `describe` (discovery) and argparse dispatch, so they can
never drift, plus structured JSON output by default. This feature builds the four modules that
shape requires and nothing needs later, leaving `tables.py`, `calendar.py`, and `campaign.py` for
the features that actually need them (#222+):

```text
engine/
└── wyrd/
    ├── __init__.py
    ├── catalog.py       # TOOLS — pure data: the "roll" verb's name, description, annotations, inputSchema
    ├── client.py         # entry point; argparse dispatch built FROM catalog.py; `describe` verb
    ├── verbs.py           # the "roll" operation: calls rules.roll_d100, then state.save
    ├── rules.py            # roll_d100(seed=None) -- pure, no I/O
    ├── state.py             # load/save/validate chronicle state; atomic writes
    └── render.py             # JSON (default) / --format text output

tests/
└── engine/
    ├── test_rules.py
    ├── test_state.py
    ├── test_verbs.py
    └── test_client.py
```

**Structure Decision**: Single project — `engine/wyrd/` is a plain Python package at the repo
root, following `docs/design/27-tooling.md` section 3's specified layout exactly (not a
scaffolding-feature invention: the doc names these module files and their responsibilities
already). `tables.py`/`calendar.py`/`campaign.py` from that same section are out of scope here —
this feature has no tables or calendar work yet — and are left as directories/files a later
feature adds. Tests live under `tests/engine/`, mirroring the module layout, using stdlib
`unittest` per section 6 of the same document.
