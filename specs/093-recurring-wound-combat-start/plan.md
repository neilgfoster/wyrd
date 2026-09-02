# Implementation Plan: The recurring wound's combat-start effect

**Branch**: `093-recurring-wound-combat-start` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/093-recurring-wound-combat-start/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

At the moment a combat scene starts, compute a per-skill penalty from every active recurring
wound the starting combatant carries -- one Challenging-difficulty step (`resolution.
DIFFICULTY_BONUSES["challenging"]`, already exposed in `combat.py` as `CHALLENGING_MODIFIER`) per
wound, stacked where more than one wound bears on the same skill -- and record it on the combat
scene for that combatant, computed once at `start_combat` and never recomputed mid-fight. This
reuses `character.active_wound_effects` to read the wounds rather than a new parallel path.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (repo-wide constraint, CLAUDE.md)

**Primary Dependencies**: none beyond the existing `wyrd` package (`character.py`, `combat.py`,
`resolution.py`, `state.py`)

**Storage**: chronicle state file under `combat` key, via `state.py`'s existing atomic
load/save -- same mechanism `start_combat`/`advance_round` already use

**Testing**: pytest (`tests/engine/test_combat.py`, `tests/engine/test_character.py`)

**Target Platform**: CLI / library, Linux

**Project Type**: single project (engine library)

**Performance Goals**: N/A -- this is per-combat-start bookkeeping over a handful of wound
records, not a hot path

**Constraints**: stdlib-only; the -10 MUST be `resolution.DIFFICULTY_BONUSES["challenging"]` (or
`combat.CHALLENGING_MODIFIER`, which is already defined as that same value), never a new literal
(issue #254's Definition of Done)

**Scale/Scope**: one function (or a small addition to `start_combat`) plus one or two reader
helpers; no new entity type, no new persisted schema field beyond what `combat.py`'s scene dict
already carries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Deterministic over inference** (ADR 0005): the penalty is computed by reading
  `active_wound_effects` and summing a fixed constant per matching wound -- no inference, no
  randomness, checked by a unit test asserting the exact stacked total for a given wound set.
- **No new literal for -10** (CLAUDE.md "Check the maths" / issue #254's Definition of Done):
  satisfied by reusing `combat.CHALLENGING_MODIFIER` / `resolution.DIFFICULTY_BONUSES
  ["challenging"]` rather than writing `-10` again.
- **Rules changes apply forward only** (design/09-evolution.md): not applicable -- this feature
  implements previously-specified behavior (docs/design/06-aftermath.md), it does not change a
  rule.
- **No setting/system vocabulary**: the feature touches only existing engine vocabulary
  (recurring wound, Challenging, skill, combat scene); no new label is introduced that would
  need this check.
- No violations requiring the Complexity Tracking table.

## Project Structure

### Documentation (this feature)

```text
specs/093-recurring-wound-combat-start/
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
├── character.py      # active_wound_effects (read, unchanged) -- source of recurring-wound data
├── combat.py          # start_combat gains the combat-start penalty computation and storage
└── resolution.py      # DIFFICULTY_BONUSES["challenging"] (read, unchanged) -- the reused constant

tests/engine/
├── test_combat.py      # new tests: recurring-wound penalty at combat start, stacking, scoping
└── test_character.py   # unchanged; active_wound_effects already covered here
```

**Structure Decision**: Single project (the existing `engine/wyrd/` library). No new module is
needed -- this is an addition to `combat.py`'s `start_combat` (and a small reader alongside it),
consuming `character.py`'s existing `active_wound_effects` and `resolution.py`'s existing
difficulty constant. No new top-level directory, no new persisted entity type.

## Complexity Tracking

*No violations -- table omitted.*
