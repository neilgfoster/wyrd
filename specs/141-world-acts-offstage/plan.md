# Implementation Plan: world_acts_offstage gates threat activation while the character is elsewhere

**Branch**: `141-world-acts-offstage` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/141-world-acts-offstage/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`advance_time.advance_time` gains `world_acts_offstage: bool = True` and `witnessed: bool =
True` keyword parameters. When both are `False`, every Threat's activation is suppressed
(`activation_count: 0`, `effects: []`, no roll drawn, no offset consumed) while the calendar
still advances normally.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: unchanged (`wyrd.threat`, `wyrd.rules`).

**Storage**: N/A — plain dicts/lists/bools in, plain dicts out.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library (`advance_time.advance_time`).

**Project Type**: single project (engine library).

**Performance Goals**: N/A.

**Constraints**: ruff-clean repo-wide; default parameters reproduce #338's exact prior
behaviour (FR-004); no roll consumed when suppressed (FR-005).

**Scale/Scope**: two new parameters on one existing function. Out of scope: deciding what
counts as "witnessed" (caller's judgment), reading `chronicle["intent"]` itself (caller's job).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `world_acts_offstage`/`witnessed` are the design
  document's own terms. PASS.
- Deterministic over inference (ADR 0005) — a pure boolean gate on an already-deterministic
  computation. PASS.
- Backward-compatible additive change (FR-004) — no existing caller's behaviour changes unless
  it opts in. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/141-world-acts-offstage/
├── plan.md, research.md, data-model.md, quickstart.md, tasks.md
└── contracts/ (none)
```

### Source Code (repository root)

```text
engine/wyrd/advance_time.py        # advance_time gains two parameters
tests/engine/test_advance_time.py  # extended: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
