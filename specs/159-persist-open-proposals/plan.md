# Implementation Plan: Proposals survive across separate CLI invocations

**Branch**: `159-persist-open-proposals` | **Date**: 2026-09-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/159-persist-open-proposals/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`engine/wyrd/resolution.py`'s `propose_batch`/`commit`/`discard`/`reroll` stage an open proposal
in an in-process dict (`_open_proposals`) that never survives process exit, so a proposal staged
by one `python3 -m wyrd.client propose` invocation is invisible to a `commit`/`discard` run as a
separate later invocation — exactly how every real GM skill actually calls the CLI. The fix:
persist each open proposal's full contents as one JSON file per proposal, under a fixed,
cwd-relative `log/proposals/` directory (mirroring `state.py`'s existing
`DEFAULT_CHRONICLE_PATH` convention and reusing its `write_text_atomic` primitive), replace the
in-process dict entirely so disk is the single source of truth, and switch proposal id generation
from a per-process counter to a random id (research.md Decision 2) so two separate processes can
never mint colliding ids. `docs/design/22-state.md`'s already-specified Rally-clears-a-stale-
proposal policy needs no new code — `rally.py`'s existing `apply_rally` call to
`resolution.discard` starts working correctly the moment `discard` can find the file.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (existing project convention,
docs/design/27-tooling.md).

**Primary Dependencies**: None new — `pathlib`, `json`, `uuid` (stdlib); reuses
`engine/wyrd/state.py`'s existing `write_text_atomic`.

**Storage**: One JSON file per open proposal under a cwd-relative `log/proposals/` directory
(research.md Decision 1) — no database, no new file format beyond plain JSON.

**Testing**: `unittest` (stdlib), matching `tests/engine/test_resolution.py`'s existing
convention; the new regression test additionally uses `subprocess.run` to invoke
`python3 -m wyrd.client` as genuinely separate OS processes.

**Target Platform**: Linux/macOS CLI (wherever `python3 -m wyrd.client` already runs).

**Project Type**: Single project — a CLI tool's own engine library (Option 1 from the template).

**Performance Goals**: N/A — one small JSON file read/write per `propose`/`commit`/`discard`/
`reroll` call, no different in kind from the entity-file reads/writes those calls already do.

**Constraints**: Must not change any existing CLI flag, JSON output shape, or error message for
`propose`/`commit`/`discard`/`reroll` (contracts/cli-propose-commit-discard.md) — every existing
in-process test must keep passing unmodified (SC-003).

**Scale/Scope**: A single chronicle carries at most a handful of open proposals at once (FR-009:
one per actor, and Wyrd is a solo, single-session-at-a-time engine) — no scale concern.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled Spec Kit template (no project-specific
principles have been ratified into it in this repo) — there are no constitution-derived gates to
evaluate. The repo's own binding rules for this work are CLAUDE.md's (ruff-clean, deterministic
over inference, ADR-worthy decisions recorded) and docs/design/27-tooling.md/22-state.md, both
already the basis for research.md's decisions above. **No violations; nothing to justify.**

## Project Structure

### Documentation (this feature)

```text
specs/159-persist-open-proposals/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli-propose-commit-discard.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
engine/
└── wyrd/
    ├── resolution.py    # propose_batch/commit/discard/reroll: disk-backed proposal store
    │                    # replaces the in-process _open_proposals dict; new proposal-id
    │                    # generation (research.md Decision 2)
    └── state.py          # unchanged — write_text_atomic reused as-is, no edit needed

tests/
└── engine/
    └── test_resolution.py   # existing in-process tests, unmodified (SC-003) + new
                              # cross-process regression test (subprocess.run, spec.md
                              # User Story 1's Independent Test)
```

**Structure Decision**: Single project (Option 1) — this feature is entirely internal to
`engine/wyrd/resolution.py`; no new module, no new CLI surface (contracts/
cli-propose-commit-discard.md — every flag and output shape is unchanged). `engine/wyrd/
chronicle.py`, `engine/wyrd/rally.py`, and `engine/wyrd/client.py`/`verbs.py` need no code
changes — `rally.py`'s existing `resolution.discard` call and `client.py`'s existing CLI wiring
both already call through to the functions this feature changes, with the same signatures
(`proposals_dir` is an optional keyword defaulting to the same cwd-relative convention every
other chronicle-scoped call already relies on).

## Complexity Tracking

*No violations — section not applicable.*
