# Implementation Plan: Holdings: accumulated stakes

**Branch**: `129-holdings-personal-stakes` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/129-holdings-personal-stakes/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/holding.py` module, matching `threat.py`/`thread.py`/`era.py`'s existing
division of labour (plain dicts/lists in, plain dicts out, no I/O): `flag_personal_stakes`, which
annotates a list of Threat entity dicts (as `threat.active_threats` returns) with `personal: bool`
depending on whether each one's `id` appears in a supplied `holdings` list. Holdings themselves
(`gain_holding`/`lose_holding`, kept distinct from `allegiances`) already exist in `economy.py`
(#276-280) — this feature only adds the read-side connection to Threats.

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: none beyond the existing `wyrd` package. No import of `threat.py` is
needed — this module only reads the shape `threat.active_threats` already produces (a list of
entity dicts), keeping the two modules decoupled the way `journey.py`'s `resolve_leg` reads a
`threats` dict passed in by its caller rather than importing `threat.py` directly.

**Storage**: N/A — plain dicts/lists in, plain dicts out.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called wherever the active Threat set is surfaced to the GM
(session/recap machinery, out of scope here).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — a membership check per Threat, not a hot loop.

**Constraints**: ruff-clean repo-wide; no change to `economy.py`'s existing
`gain_holding`/`lose_holding` (already correct and tested per spec.md's Assumptions).

**Scale/Scope**: the personal-stakes flag only. Out of scope: holding creation/loss (already
implemented), what happens in play once a Threat is flagged personal (GM narration).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `holdings`, `personal`, `stakes` are all existing
  engine-neutral terms already in docs/design/19-campaign.md/22-state.md. PASS.
- Deterministic over inference (ADR 0005) — the personal flag is a pure membership check, not
  inferred from narration. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/129-holdings-personal-stakes/
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
└── holding.py             # NEW: flag_personal_stakes

tests/engine/
└── test_holding.py         # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
