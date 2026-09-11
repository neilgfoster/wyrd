# Implementation Plan: Threats aspect & activation

**Branch**: `126-threat-aspect-activation` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/126-threat-aspect-activation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/threat.py` module, matching `journey.py`'s existing division of labour
(plain dicts in and out, no entity/file I/O, caller-supplied dice): an active-set query over a
collection of entities, an activation check (`roll <= imminence * 10`, reusing the exact formula
`journey.py` already documents as belonging to Threats), a range-keyed effects-table lookup
(mirroring `journey.roll_hazard`'s existing sub-table matching), and a promotion operation that
attaches a new `threat` block and objective to an entity that doesn't yet carry one.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none beyond the existing `wyrd` package. No new dependency on
`entity.py`/`state.py` — this feature stays at the pure-function layer those modules sit below,
matching `journey.py`, `economy.py`, `advancement.py`.

**Storage**: N/A — plain dicts in, plain dicts out; nothing here loads or saves
`chronicle.yaml`/entity files.

**Testing**: `pytest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called by `advance-time` (#338, blocked on this feature) and
eventually by scenario/succession machinery (#339, #340).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — a handful of dict operations per Threat per elapsed week, not a hot
loop.

**Constraints**: ruff-clean repo-wide (`ruff check .`, `ruff format --check .`); a Threat stays an
aspect, never a tenth `ENTITY_TYPES` entry (docs/design/19-campaign.md, spec.md's Key Entities).

**Scale/Scope**: the per-Threat active-set query, activation check, effects lookup, and promotion
operation. Out of scope: the weekly elapsed-time loop and multi-week expected-value roll
generation (`advance-time`, #338), the material economy routing of `ambient` costs (already
deferred the same way by `journey.py`), and entity/file loading (`entity.py`/`state.py`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `threat`, `imminence`, `clues`, `effects`, `ambient`,
  `counters`, `weakness`, `connection` are all existing engine-neutral terms already in
  docs/design/19-campaign.md. PASS.
- Threat stays an aspect, not a new entity type — this plan adds no ninth/tenth member to
  `entity.ENTITY_TYPES`; it operates on whatever dict the caller passes in. PASS.
- Deterministic over inference (ADR 0005) — activation and effects-lookup are pure functions of a
  caller-supplied roll, not inferred from narration; matches `journey.roll_hazard`'s existing
  convention exactly. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/126-threat-aspect-activation/
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
└── threat.py             # NEW: active_threats, check_activation, resolve_effects, promote

tests/
└── test_threat.py         # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
