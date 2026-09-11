# Implementation Plan: Chronicle intent's lethality is validated against the mortality vocabulary

**Branch**: `140-lethality-validation` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/140-lethality-validation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

`state.py` gains a local `_LETHALITY_LEVELS = frozenset({"low", "standard", "high"})` constant
and `validate_chronicle` rejects an out-of-vocabulary `intent.lethality`, raising `StateError`.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none — no import of `creation.py`/`resolution.py` (would cycle).

**Storage**: N/A — a validation rule inside the existing `validate_chronicle` function.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library (`state.validate_chronicle`).

**Project Type**: single project (engine library).

**Performance Goals**: N/A.

**Constraints**: ruff-clean repo-wide; no import cycle; existing valid chronicles unaffected
(FR-003).

**Scale/Scope**: one validation rule. No schema change beyond validating a field that already
exists.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `low`/`standard`/`high` already exist in
  `creation.py`/`resolution.py`. PASS.
- Deterministic over inference (ADR 0005) — a closed-set membership check. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/140-lethality-validation/
├── plan.md, research.md, data-model.md, quickstart.md, tasks.md
└── contracts/ (none)
```

### Source Code (repository root)

```text
engine/wyrd/state.py         # validate_chronicle gains the lethality check
tests/engine/test_state.py   # extended: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
