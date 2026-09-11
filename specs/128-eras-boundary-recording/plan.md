# Implementation Plan: Eras: named periods and boundary recording

**Branch**: `128-eras-boundary-recording` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/128-eras-boundary-recording/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Extend `state.py`'s chronicle schema with two new optional fields (`eras: []`,
`era_crossings: []`), defaulted and filled in `default_chronicle_state`/`validate_chronicle`
exactly the way `migrations`/`intent` already are. Add a new `engine/wyrd/era.py` module, matching
`chronicle.py`'s (#328) division of labour (pure functions over the relevant sub-fields, no I/O,
caller persists via `save_chronicle`): `ambient_register` (lookup) and `cross_era` (validated
boundary crossing, returning the new pointer plus an append-only crossing record).

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none beyond the existing `wyrd` package (`state`).

**Storage**: `chronicle.yaml`, via `wyrd.state`'s existing `load_chronicle`/`save_chronicle` — this
feature only extends the schema those already read/write; `era.py` itself does no I/O.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library.

**Project Type**: single project (engine library).

**Performance Goals**: N/A — a handful of dict/list operations per crossing, not a hot loop.

**Constraints**: ruff-clean repo-wide; `era_crossings` stays append-only, mirroring `migrations`'s
existing immutability convention exactly (no edit/reorder validation is added here since nothing
in this feature's own functions ever removes or reorders an entry — `state.py`'s existing
`validate_chronicle` `previous_migrations` check is the precedent, not duplicated for crossings
since no caller yet needs to detect tampering with them, per spec.md's scope).

**Scale/Scope**: ambient-register lookup and crossing recording. Out of scope: deciding *when* to
cross (a GM/arc-boundary judgment call), git-tagging the crossing.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `era`, `eras`, `ambient`, `era_crossings` are all
  existing engine-neutral terms already in docs/design/19-campaign.md/22-state.md. PASS.
- Deterministic over inference (ADR 0005) — both functions are pure, deterministic lookups/
  validations over caller-supplied dicts/lists. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/128-eras-boundary-recording/
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
├── state.py              # `eras`/`era_crossings` added to default_chronicle_state/validate_chronicle
└── era.py                # NEW: ambient_register, cross_era

tests/engine/
├── test_state.py          # extended: new fields default/validate correctly
└── test_era.py            # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
