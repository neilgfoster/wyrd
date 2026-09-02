# Implementation Plan: Adversary trait effects

**Branch**: `096-adversary-trait-effects` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/096-adversary-trait-effects/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add to `engine/wyrd/adversary.py`: `effective_block(block)` (folds `stamina_max`/`armour_rank`/
`damage`/`damage_type` trait effects into a new block dict, stacking same-key traits) and
`shift_difficulty(base, rungs)` (steps a difficulty name along the existing ladder, clamped).
Add one small, additive, backward-compatible `omen_width: int = 0` parameter to
`rules._wyrd_die`/`rules.opposed_test` for the `wyrd` trait's band-widening.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (repo-wide constraint, CLAUDE.md)

**Primary Dependencies**: `engine/wyrd/resolution.py` (`DIFFICULTY_BONUSES`, for the ladder
order) and `engine/wyrd/rules.py` (`_wyrd_die`/`opposed_test`, extended additively)

**Storage**: N/A -- pure functions, no I/O

**Testing**: pytest (`tests/engine/test_adversary.py`, `tests/engine/test_rules.py`)

**Target Platform**: CLI / library, Linux

**Project Type**: single project (engine library)

**Performance Goals**: N/A -- small pure computations over a handful of trait entries

**Constraints**: stdlib-only; only the six closed trait-effect keys are handled (FR-008); the
`rules.py` change must be additive and backward-compatible (SC-003)

**Scale/Scope**: two new functions in `adversary.py`, one new module-level constant
(`ARMOUR_RANKS` already exists there from #259), one small additive parameter change across two
functions in `rules.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): every computation is a pure sum/clamp/lookup; a
  test exists for each rule and each clamp boundary.
- **No new mechanism** (docs/design/12-the-adversary.md section 5, FR-008): only the six closed
  effect keys are read; nothing else is invented.
- **Backward compatibility for the `rules.py` change** (SC-003): `omen_width` defaults to 0,
  reproducing exactly today's `_wyrd_die` behavior for every existing caller.
- **No setting/system vocabulary**: only existing engine vocabulary is touched.
- **Rules changes apply forward only**: not applicable -- implements previously-specified
  behavior (docs/design/12-the-adversary.md section 5), does not change a rule.
- No violations requiring the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/096-adversary-trait-effects/
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
├── adversary.py       # gains effective_block(block), shift_difficulty(base, rungs)
├── resolution.py       # DIFFICULTY_BONUSES (read, unchanged) -- source of the ladder order
└── rules.py             # _wyrd_die/opposed_test gain an additive omen_width: int = 0 parameter

tests/engine/
├── test_adversary.py  # gains tests for effective_block, shift_difficulty
└── test_rules.py        # gains tests for omen_width
```

**Structure Decision**: Single project. Two new functions in the existing `adversary.py` module;
one small additive change to `rules.py`'s existing dice-reading function. No new module.

## Complexity Tracking

*No violations -- table omitted.*
