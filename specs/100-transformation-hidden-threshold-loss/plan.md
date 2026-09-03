# Implementation Plan: Transformation count reaching the hidden threshold

**Branch**: `100-transformation-hidden-threshold-loss` | **Date**: 2026-09-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/100-transformation-hidden-threshold-loss/spec.md`

## Summary

`_stage_transformation_chain` (`engine/wyrd/resolution.py`) already rolls the hidden threshold
once and reduces Taint/raises Dread per Transformation, but never records the Transformation on
the character's `transformations` field and never checks the running count against
`hidden_threshold`. This feature adds both: an append mutation on `transformations` for every
Transformation staged, and — once the resulting count reaches `hidden_threshold` — one further
mutation setting `status: lost`, staged on the same step and ending that character's re-roll loop.
Fate is never touched. No new visibility/rendering machinery is needed: existing "never shown"
handling for `hidden_threshold` already covers this path, since the new step's roll data carries
no threshold value.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only (existing repo constraint)

**Primary Dependencies**: none new — extends `engine/wyrd/resolution.py`,
`engine/wyrd/character.py`

**Storage**: `chronicle.yaml`/character frontmatter files, via the existing `state.py`/mutation
machinery — unchanged by this feature

**Testing**: pytest, `tests/engine/test_resolution.py` (existing conventions:
`ResolutionTestBase`, `TransformationCascadeTest`)

**Target Platform**: engine library, no platform dependency

**Project Type**: single project (Python library, `engine/wyrd`)

**Performance Goals**: N/A — bounded per-cascade work, same order as the existing re-roll loop

**Constraints**: stdlib-only; `hidden_threshold`'s numeric value must never leak to a rendered
view, including as unease

**Scale/Scope**: one function (`_stage_transformation_chain`) gains two mutation types; no schema
migration, since `transformations` and `status`-equivalent fields already exist in
`PLAYER_CHARACTER_FIELDS`/companion frontmatter

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Nothing unpublishable enters the repo: no source text involved. **Pass.**
- No setting/system names: all vocabulary (`hidden threshold`, `lost`, `with-party`) is already
  established engine vocabulary from `docs/design/07-transformations.md` and
  `docs/design/22-state.md`; nothing new is coined. **Pass.**
- Tone: this feature stages a state transition only; no narrative/tone content is added.
  **Pass.**
- Deterministic over inference: the count-vs-threshold comparison is exact integer comparison,
  nothing probabilistic beyond the rolls the cascade already makes. No new check script is needed
  — there is no probability claim to verify, only a comparison. **Pass.**
- Rule changes apply forward only: this feature does not touch historical mutation records.
  **Pass.**
- Capability change, so it goes through the Spec Kit cycle (this plan) and `specs/100-.../` is
  committed. **Pass.**

No violations. Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/100-transformation-hidden-threshold-loss/
├── plan.md              # This file
├── data-model.md         # Phase 1 output — the two fields/transition this feature touches
└── checklists/
    └── requirements.md
```

No `research.md`: nothing in the Technical Context needed resolving (no NEEDS CLARIFICATION —
the design documents already specify the trigger, the field, and the resulting state).
No `contracts/`: this is a pure internal-engine change with no external interface (no CLI/API
surface added or altered). No `quickstart.md`: the existing pytest suite under
`tests/engine/test_resolution.py` (run with `PYTHONPATH=engine python3 -m pytest -q`) is already
the validation path for this module; a separate quickstart would duplicate it.

### Source Code (repository root)

```text
engine/wyrd/
├── resolution.py     # _stage_transformation_chain gains the append + threshold-loss mutations
└── character.py       # no field-list change needed; transformations/status already listed

tests/engine/
└── test_resolution.py  # TransformationCascadeTest / MultiRerollTransformationTest gain cases
                         # for: transformations recorded, player-character loss, companion loss
```

**Structure Decision**: Single project, existing layout unchanged. All work lands inside
`engine/wyrd/resolution.py`'s existing `_stage_transformation_chain`, with test coverage added to
the existing `tests/engine/test_resolution.py` file rather than a new module — this is one
function gaining two mutation types, not a new subsystem.

## Complexity Tracking

*No Constitution Check violations — table omitted.*
