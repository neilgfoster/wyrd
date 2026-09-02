# Implementation Plan: Propose/commit/discard core

**Branch**: `235-propose-commit-discard-core` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/082-propose-commit-core/spec.md`

## Summary

Adds `engine/wyrd/resolution.py`: a process-local proposal store plus `propose`/`commit`/
`discard`, implementing `docs/design/31-action-resolution.md`'s "Propose, then commit" (ADR
0050) for the single-step case. `propose` looks up an actor's (and optional target's) state,
resolves one roll via the engine's existing `rules.py` primitives, computes any mutation a
mechanic's rule implies, and returns it all under a proposal id without writing anything.
`commit` applies the staged mutations atomically via `state.py`'s existing atomic-write
primitive; `discard` writes nothing. Both invalidate the id. A small closed mechanic registry
(initially `ordinary-test` and `exposure`, the two the design doc's own worked examples use)
maps a resolved outcome to its mutation. `client.py`/`verbs.py` gain matching `propose`/`commit`/
`discard` CLI verbs, per `docs/design/02-architecture.md`'s existing CLI sketch.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (existing repo convention,
`docs/design/27-tooling.md`).

**Primary Dependencies**: none beyond stdlib — reuses `engine/wyrd/rules.py` (dice/degrees),
`engine/wyrd/state.py` (atomic YAML read/write), `engine/wyrd/character.py` (entity schema).

**Storage**: the existing restricted-YAML entity files `state.py`/`character.py` already
read/write (per-character frontmatter files). Proposals themselves are never persisted — an
in-memory dict for the lifetime of the process, consistent with the engine having no
backend/daemon.

**Testing**: `pytest` (existing `tests/engine/` suite), plus `ruff check .` and
`ruff format --check .` (existing repo gates).

**Target Platform**: CLI / library, same as the rest of `engine/wyrd/`.

**Project Type**: single project (library + thin CLI), matching the existing `engine/wyrd/`
layout — no new project structure.

**Performance Goals**: N/A — no stated throughput requirement; a single roll resolves in
negligible time on any modern machine.

**Constraints**: `propose` MUST NOT write to state under any code path (SC-002); `commit`/
`discard` MUST invalidate their proposal id atomically with respect to any concurrent read of
the proposal store within the same process.

**Scale/Scope**: single-step resolution only (this feature's own FR-009) — no cascading, no
reroll, no Omen carryover; those are separate sibling features (#236, #237, #238).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting or system names introduced — `ordinary-test`/`exposure` are the engine's own
  closed mechanic vocabulary per `docs/design/31-action-resolution.md`, not a setting borrowing.
- Nothing unpublishable enters the repo — no source text, no setting content.
- Deterministic over inference — the mechanic → mutation mapping is a Python function per
  mechanic, not inferred at runtime; every worked example in `docs/design/31-action-resolution.md`
  is reproduced by a test using its disclosed seed.
- This is a capability change (new engine module) — goes through the Spec Kit cycle, `specs/`
  committed. Not a design-only change, so no design document is edited by this feature (the
  design already exists at `docs/design/31-action-resolution.md`); this feature implements it.
- No real rejected alternative surfaced beyond what ADR 0050 already recorded when the design
  was specified (#193) — no new ADR from this feature.

**PASS** — no violations, nothing to justify in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/082-propose-commit-core/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
engine/wyrd/
├── rules.py          # existing: dice, degrees, Wyrd die (reused, unchanged)
├── state.py          # existing: atomic YAML save/load (reused, unchanged)
├── character.py       # existing: entity schema, validation (reused, unchanged)
├── resolution.py      # NEW: Proposal store, propose(), commit(), discard(), mechanic registry
├── verbs.py           # gains: propose/commit/discard wrappers matching existing verb style
└── client.py          # gains: `propose`/`commit`/`discard` CLI subcommands

tests/engine/
└── test_resolution.py # NEW: unit tests, incl. both worked examples from
                        # docs/design/31-action-resolution.md (seed 20260852; the Taint-
                        # threshold-cascade worked example is NOT reproduced here since its
                        # cascade step is out of scope for this feature — only its single
                        # `exposure` roll/mutation is)
```

**Structure Decision**: Extends the existing single-project `engine/wyrd/` + `tests/engine/`
layout — no new top-level directory. `resolution.py` sits alongside `rules.py`/`state.py` as a
new pure-ish module (it reads/writes via `state.py`'s existing primitives rather than touching
files directly), matching the repo's established layering: `rules.py` (pure functions) →
`resolution.py` (orchestrates rules + state) → `verbs.py` (public call shape) → `client.py`
(CLI).

## Complexity Tracking

*No violations — table omitted.*
