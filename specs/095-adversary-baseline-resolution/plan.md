# Implementation Plan: Adversary baseline skill resolution

**Branch**: `095-adversary-baseline-resolution` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/095-adversary-baseline-resolution/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `resolve_skill(block: dict, skill: str) -> int` to `engine/wyrd/adversary.py`: returns
`block["skills"][skill]` if present, else `block["baseline"]`. A small, pure accessor, kept in
`adversary.py` (not `rules.py`) and sharing no code or constant with `rules.UNTRAINED_SKILL`/
`select_group_skill`, per the issue's explicit non-negotiable.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (repo-wide constraint, CLAUDE.md)

**Primary Dependencies**: none beyond the adversary block shape #259 already produces (this
function takes a plain `dict`, no import of `character.py`/`rules.py` needed)

**Storage**: N/A -- pure function, no I/O

**Testing**: pytest (`tests/engine/test_adversary.py`, extending #259's test module)

**Target Platform**: CLI / library, Linux

**Project Type**: single project (engine library)

**Performance Goals**: N/A -- a dict lookup

**Constraints**: stdlib-only; must not import or reuse `rules.UNTRAINED_SKILL`/
`select_group_skill` (FR-005)

**Scale/Scope**: one function, ~5 lines, in an existing module; a handful of tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): a pure dict lookup with one fallback branch; no
  inference, no randomness.
- **No shared fallback constant** (issue #260's own Definition of Done): satisfied by keeping
  this function in `adversary.py`, reading only the block's own `baseline` field, with a test
  that sets `baseline` equal to `UNTRAINED_SKILL`'s value and confirms the result still traces to
  the block's field, not the shared constant.
- **No setting/system vocabulary**: only existing engine vocabulary (adversary, baseline, skill)
  is touched.
- **Rules changes apply forward only**: not applicable -- implements previously-specified
  behavior (docs/design/12-the-adversary.md section 3), does not change a rule.
- No violations requiring the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/095-adversary-baseline-resolution/
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
├── adversary.py       # gains resolve_skill(block, skill) -> int
└── rules.py             # UNTRAINED_SKILL/select_group_skill (read, unchanged; must stay independent)

tests/engine/
└── test_adversary.py  # gains tests for resolve_skill
```

**Structure Decision**: Single project. One new function in the existing `engine/wyrd/adversary.py`
module (from #259); no new module, no new top-level directory.

## Complexity Tracking

*No violations -- table omitted.*
