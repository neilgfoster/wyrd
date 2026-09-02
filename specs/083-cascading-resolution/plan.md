# Implementation Plan: Cascading resolution

**Branch**: `236-cascading-resolution` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/083-cascading-resolution/spec.md`

## Summary

Extends `engine/wyrd/resolution.py` (#235) so a proposal can hold more than one dependent step.
`propose` gains a `_STEP` record (`step_id`, `mechanic`, `roll`, `mutations`, `depends_on`) and
two cascade triggers: a threshold-crossing check (registered for `taint` → `transformation`) run
against every staged mutation, and an outcome-triggered check for `combat-attack` (staging
`weapon-damage` + `armour`, whose combined Stamina mutation is itself threshold-checked, staging
`critical` on a crossing below zero). New mechanics: `combat-attack`, `weapon-damage`, `armour`,
`critical` (slashing table only), `transformation`. `commit`/`discard` are unchanged in shape —
they already apply/discard a proposal's `mutations` list, which now may be the concatenation of
several steps' mutations rather than one step's.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only.

**Primary Dependencies**: none beyond stdlib — extends `engine/wyrd/resolution.py` (#235),
`rules.py`, `state.py`/`character.py`.

**Storage**: unchanged from #235 — proposals stay process-local/in-memory; commit writes via the
existing atomic entity-file path.

**Testing**: `pytest`, `ruff check .`, `ruff format --check .`.

**Target Platform**: CLI/library, same as `engine/wyrd/`.

**Project Type**: single project, extending the existing `engine/wyrd/` layout.

**Performance Goals**: N/A.

**Constraints**: A cascade must terminate within the same call — no unbounded recursion. The
Transformation cascade's termination is already proven by `tools/check_transformation.py`
(6-row ceiling); this feature's implementation must not exceed that bound either.

**Scale/Scope**: Exactly the two triggers spec.md's Assumptions name — no Strain/Trauma/
Affliction cascade, no gear-lookup integration, `critical-slashing` only.

## Constitution Check

- No setting/system names — `combat-attack`/`weapon-damage`/`armour`/`critical`/`transformation`
  are the engine's own closed mechanic vocabulary, matching `docs/design/31-action-resolution.md`
  and `docs/design/05-criticals.md`/`07-transformations.md`.
- Deterministic over inference — every worked example is reproduced or freshly computed with a
  disclosed seed (`research.md`), never asserted.
- Capability change — goes through the Spec Kit cycle, `specs/` committed.
- No new ADR: this feature implements what `docs/design/31-action-resolution.md` (design already
  landed, #193) and the two referenced tables already specify; no new rejected alternative
  surfaces here.

**PASS** — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/083-cascading-resolution/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
engine/wyrd/
├── resolution.py      # extended: Step record, depends_on, threshold-rule registry,
│                       # combat-attack/weapon-damage/armour/critical/transformation mechanics
├── verbs.py            # propose's existing wrapper is unchanged in signature
└── client.py           # propose's existing CLI subcommand is unchanged in signature

tests/engine/
└── test_resolution.py  # extended with cascade test classes
```

**Structure Decision**: No new files beyond continuing to extend `resolution.py` and its test
module — this is additive to #235's existing structure, not a new layer.

## Complexity Tracking

*No violations — table omitted.*
