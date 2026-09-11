# Implementation Plan: Chronicle transaction lifecycle

**Branch**: `125-chronicle-transaction-lifecycle` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/125-chronicle-transaction-lifecycle/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Give `chronicle.yaml`'s `pending` field (round-tripped opaquely by #325) real semantics: resuming
a session from `pending.beat`/`pending.awaiting`, and discarding an open, uncommitted proposal
recorded in `pending.rolled` — automatically at the next Rally if it survived a session boundary,
or explicitly when a live proposal's situation goes moot before `commit`/`discard`. Reuses
`resolution.py`'s existing `propose`/`commit`/`discard` unchanged; adds a small `wyrd.chronicle`
module (new) that owns the `pending` sub-field semantics and reconciles them with `wyrd.session`'s
pre-existing (and now superseded) `set_pending`/`resume_from_pending`/`clear_pending` helpers,
which used a different, ad hoc shape (`{beat_id, action, set_at}`) before `chronicle.yaml`'s actual
schema (`{beat, awaiting, rolled}`, specs/122) existed.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none beyond the existing `wyrd` package (`state`, `session`, `rally`,
`resolution`).

**Storage**: `chronicle.yaml`, via `wyrd.state`'s existing `load_chronicle`/`save_chronicle`.

**Testing**: `pytest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, invoked by the session/Rally loop.

**Project Type**: single project (engine library).

**Performance Goals**: N/A — no roll-frequency or throughput requirement; this is state
bookkeeping, not a hot loop.

**Constraints**: ruff-clean repo-wide (`ruff check .`, `ruff format --check .`); must not invent a
second mechanism alongside `pending` for an open proposal (CLAUDE.md, issue #328).

**Scale/Scope**: one chronicle's `pending` field and the Rally/moot-discard call sites that read
and clear it. Out of scope: invariant cascades (#327) and load-tier resolution (#326), both
already landed as siblings under epic #300.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `pending`, `beat`, `awaiting`, `rolled`, `Rally` are
  all existing engine-neutral terms already in docs/design/16-session.md and 22-state.md. PASS.
- No new mechanism alongside `pending` for an open proposal (`CLAUDE.md`'s explicit constraint on
  this issue) — `pending.rolled` is the only field this plan adds semantics to; no parallel
  registry is introduced. PASS.
- Deterministic over inference (ADR 0005) — Rally-discard and moot-discard are both deterministic
  functions of `pending.rolled`'s current value, not inferred from narration. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/125-chronicle-transaction-lifecycle/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (none — internal engine module, no external contract)
└── tasks.md             # Phase 2 output (kord-feature-tasks, not this command)
```

### Source Code (repository root)

```text
engine/wyrd/
├── chronicle.py         # NEW: pending-field semantics (resume, rally-discard, moot-discard,
│                         #      single-open-proposal-per-actor slot)
├── rally.py              # apply_rally gains an optional pending-discard step
├── session.py             # set_pending/resume_from_pending/clear_pending reconciled onto
│                          # chronicle.py's pending shape (or superseded by it — Phase 1 decides)
└── resolution.py          # unchanged: propose/commit/discard reused as-is

tests/
└── test_chronicle.py     # NEW: resume, rally-discard, moot-discard, single-open-proposal cases
```

**Structure Decision**: single project (existing `engine/wyrd/` package). A new `chronicle.py`
module owns `pending`'s three sub-fields, matching the existing one-module-per-concern layout
(`rally.py` for the Rally, `session.py` for the loop, `resolution.py` for propose/commit/discard)
rather than folding this into any of those three, since `pending` sits at the seam between them
and is the resource this feature genuinely adds.

## Complexity Tracking

*No violations — table intentionally empty.*
