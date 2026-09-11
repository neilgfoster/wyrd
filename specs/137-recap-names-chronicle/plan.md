# Implementation Plan: Recap names its chronicle and setting

**Branch**: `137-recap-names-chronicle` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/137-recap-names-chronicle/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`loadtier.generate_recap` stops discarding its `chronicle` parameter: reads `chronicle["name"]`
and `chronicle["setting"]["repo"]`, falling back to the existing `_RECAP_PLACEHOLDER` convention
when either is absent, and adds a new "## Chronicle" section naming both.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none beyond the existing `wyrd` package (`loadtier.py` itself).

**Storage**: N/A — `generate_recap` is already a pure function; this feature reads one more
field from its existing `chronicle` parameter.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library (`loadtier.generate_recap`, called by `recap_close_step`).

**Project Type**: single project (engine library).

**Performance Goals**: N/A.

**Constraints**: ruff-clean repo-wide; every existing `GenerateRecapTest` case must continue to
pass unchanged (FR-004).

**Scale/Scope**: one new recap section, reading two existing chronicle fields. No schema change.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced. PASS.
- No schema change — reads fields `state.default_chronicle_state` already produces. PASS.
- Deterministic over inference (ADR 0005) — a pure string-formatting read of existing dict
  fields. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/137-recap-names-chronicle/
├── plan.md, research.md, data-model.md, quickstart.md, tasks.md
└── contracts/  (none — internal engine module, no external contract)
```

### Source Code (repository root)

```text
engine/wyrd/loadtier.py   # generate_recap gains a "## Chronicle" section
tests/engine/test_loadtier.py  # extended: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
