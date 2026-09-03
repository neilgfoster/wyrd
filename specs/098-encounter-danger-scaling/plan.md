---

description: "Implementation plan for encounter danger scaling"
---

# Implementation Plan: Encounter danger scaling

**Branch**: `098-encounter-danger-scaling` | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/098-encounter-danger-scaling/spec.md`

## Summary

Add danger-scaling functions to `engine/wyrd/adversary.py`: effective party size (harmonic-style
sum), the party/`written_for` ratio, `danger_effective`, a scaled opponent count, a skill
adjustment in points, and an adjusted skill. All six are pure functions over plain numbers plus
the already-loaded block (#259) and its baseline-resolution helper (#260); none mutates any
input. The maths is not new -- it reproduces `specs/017-adversary-model/check_adversary.py`'s
`H`/`ratio`/`danger_effective`/`scaled_count`/`adjustment`/`adjusted_skill` exactly, as engine
code rather than a design-programme check script.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`fractions.Fraction`, `math`).

**Storage**: N/A -- pure functions, no state.

**Testing**: `pytest`, `tests/engine/test_adversary.py` (existing file, extended).

**Target Platform**: the engine library (`engine/wyrd/`).

**Project Type**: single project (this repo's engine).

**Performance Goals**: N/A -- these are O(party) sums over at most a handful of bodies.

**Constraints**: stdlib-only; `danger_effective` never rounded mid-calculation (ADR 0024); no
input mutated (docs/design/12-the-adversary.md section 6, "the block is absolute").

**Scale/Scope**: six small functions in one existing module, plus tests.

## Constitution Check

- No new setting/system vocabulary introduced -- every name (`effective_party_size`, `ratio`,
  `danger_effective`, `scaled_count`, `skill_adjustment`, `adjusted_skill`) is descriptive
  English already used by docs/design/03-rules.md section 7 or its neighbours.
- Reuses #259's block shape and #260's `resolve_skill` rather than re-deriving either.
- No new ADR needed: the maths this feature encodes was already settled by ADR 0024; this
  feature is an implementation of that decision, not a new one, and no alternative was rejected
  here that ADR 0024 didn't already weigh.

## Project Structure

### Documentation (this feature)

```
specs/098-encounter-danger-scaling/
|-- spec.md
|-- plan.md
`-- tasks.md
```

### Source Code (repository root)

```
engine/wyrd/adversary.py       # + effective_party_size, ratio, danger_effective,
                                #   scaled_count, skill_adjustment, adjusted_skill
tests/engine/test_adversary.py # + tests for the above
```

**Structure Decision**: extends the existing `adversary.py` module (#259/#260/#261 already live
there) rather than a new module -- these functions are adversary-block-scoped in the same way
`resolve_skill`/`effective_block` already are, and a fourth module for one more block-scoped
computation would split one concept across files for no reason.

## Complexity Tracking

No constitution violation to justify -- table omitted.
