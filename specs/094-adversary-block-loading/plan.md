# Implementation Plan: Adversary block loading and validation

**Branch**: `094-adversary-block-loading` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/094-adversary-block-loading/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `engine/wyrd/adversary.py`: a new module mirroring `character.py`'s per-entity load/validate
shape, that reads a bestiary file's `creatures:` list (via `state.parse_yaml`, the engine's
existing restricted-YAML reader) and validates one entry by id against the same required-field,
unrecognised-field, damage/damage_type pairing, and closed-vocabulary rules
`tools/check_bestiary.py` already enforces at authoring time -- expressed as separate engine code
rather than importing `tools/`, per `engine/` and `tools/` never depending on each other
(`state.py`'s own precedent).

## Technical Context

**Language/Version**: Python 3.11+, standard library only (repo-wide constraint, CLAUDE.md)

**Primary Dependencies**: `engine/wyrd/state.py` (`parse_yaml`, `StateError`) -- no other engine
module needed for this feature

**Storage**: reads a setting's `setting/bestiary.yaml` (or any path the caller passes) from disk;
this feature writes nothing

**Testing**: pytest (new `tests/engine/test_adversary.py`)

**Target Platform**: CLI / library, Linux

**Project Type**: single project (engine library)

**Performance Goals**: N/A -- loading and validating one bestiary entry from a file is not a hot
path

**Constraints**: stdlib-only; validation rules must match `tools/check_bestiary.py`'s rules for
the fields in this feature's scope, without importing `tools/`

**Scale/Scope**: one new module (~1 load function, ~1 validate function, a handful of module-level
constants mirroring `check_bestiary.py`'s); no new persisted schema, no change to existing modules

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): validation is a fixed set of field-presence and
  value-range checks, no inference; a unit test exists for each rejection class.
- **`engine/` and `tools/` must not depend on each other** (precedent: `state.py`'s own
  docstring): this feature's validation logic is a separate implementation in `engine/wyrd/`,
  not an import of `tools/check_bestiary.py`.
- **No setting/system vocabulary**: only existing engine vocabulary (adversary, block, baseline,
  bestiary) is touched; no new label needs this check.
- **Rules changes apply forward only**: not applicable -- this implements previously-specified
  behavior (docs/design/12-the-adversary.md), it does not change a rule.
- No violations requiring the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/094-adversary-block-loading/
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
├── adversary.py       # NEW: load(id, path) -> dict; validate_adversary(entry) -> None (raises)
├── state.py            # parse_yaml (read, unchanged) -- source of the YAML reader this reuses
└── character.py        # load/validate_character (read, unchanged) -- the pattern this mirrors

tests/engine/
└── test_adversary.py  # NEW: load success, each rejection class, ranged default
```

**Structure Decision**: Single project (the existing `engine/wyrd/` library). One new module,
mirroring `character.py`'s existing per-entity load/validate shape. No new top-level directory.

## Complexity Tracking

*No violations -- table omitted.*
