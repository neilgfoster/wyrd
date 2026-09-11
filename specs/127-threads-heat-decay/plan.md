# Implementation Plan: Threads: open-loop tracking, heat and decay

**Branch**: `127-threads-heat-decay` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/127-threads-heat-decay/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/thread.py` module, matching `threat.py` (#334) and `journey.py`'s existing
division of labour (plain dicts in and out, no entity/file I/O): `new_thread` (creation with a
validated 0-5 starting heat), `touch` (raises heat by one, capped at 5), and `decay` (lowers heat
by one point per whole elapsed game-year, closing the thread with a recorded reason once decay is
applied again while already at the floor).

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none beyond the existing `wyrd` package.

**Storage**: N/A — plain dicts in, plain dicts out.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine` (docs/design/27-tooling.md section 6,
matching `tests/engine/test_threat.py`'s and `tests/engine/test_journey.py`'s own convention).

**Target Platform**: engine library, called by scenario selection (#339, blocked on this feature)
and `advance-time` (#338, for the decay step).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — a handful of dict operations per thread per elapsed span.

**Constraints**: ruff-clean repo-wide; a thread stays the existing `entity.ENTITY_TYPES` member
(`"thread"`, already present) — this feature adds no new type, only the heat/decay mechanic.

**Scale/Scope**: thread creation, touch, and decay. Out of scope: the elapsed-time loop deciding
*when* to call `decay` (`advance-time`, #338), and scenario selection's hook-matching/consumption
(#339).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `thread`, `heat`, `hooks`, `opened` are all existing
  engine-neutral terms already in docs/design/19-campaign.md. PASS.
- No new entity type — `"thread"` already exists in `entity.ENTITY_TYPES`; this plan adds no
  eleventh member. PASS.
- Deterministic over inference (ADR 0005) — `decay`'s year-stepping is a pure function of a
  caller-supplied elapsed-days integer, not inferred from narration. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/127-threads-heat-decay/
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
└── thread.py              # NEW: new_thread, touch, decay

tests/engine/
└── test_thread.py          # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
