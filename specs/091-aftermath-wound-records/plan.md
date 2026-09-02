# Implementation Plan: The Aftermath table and wound records

**Branch**: `252-aftermath-wound-records` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/091-aftermath-wound-records/spec.md`

## Summary

Add the `aftermath` roll (`d100 + 5 × points_below_zero`) and its 8-row table to
`engine/wyrd/resolution.py`, following the same staging pattern `_stage_critical` already
established for the critical tables landed in #251. A resolved row produces a wound record (where
the row specifies one) via the existing `character.py` wound shape, and records which row was
reached without wiring the non-wound consequences (nemesis/thread entities, companion status,
death-row re-reads) into other subsystems — those are later features in the epic's decomposition.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (existing project constraint)

**Primary Dependencies**: none new — reuses `wyrd.rules.roll_d100`, `wyrd.character.validate_wound`

**Storage**: N/A — wound records are appended to the character's in-memory `wounds` list mutation,
same as criticals already do; persistence is `state.py`'s existing job

**Testing**: `pytest` (existing suite convention: `tests/`)

**Target Platform**: N/A — library code, no platform dependency

**Project Type**: single project (existing `engine/wyrd/` package)

**Performance Goals**: N/A — deterministic table lookups, no performance-sensitive path

**Constraints**: stdlib-only (CLAUDE.md); reuse `character.py`'s wound machinery rather than
duplicating it (driving issue's Definition of Done)

**Scale/Scope**: one new staging function plus its row table, mirroring `_stage_critical`'s
existing shape and size

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Nothing unpublishable: this feature adds no source-derived text — the row table already lives
  in `docs/design/06-aftermath.md`, itself already published. PASS.
- No setting/system names: row keys and descriptions are the engine's own defaults, already
  written in `06-aftermath.md`. PASS.
- Tone stays a setting property: descriptions are copied verbatim from the design doc, which
  itself already frames them as engine defaults a setting may override. PASS.
- Deterministic over inference: the check script (FR-010) computes the 71%/23% figures rather
  than asserting them, matching the design doc's own worked table. PASS.
- Rule changes apply forward only: N/A — this is new functionality, not a change to an existing
  rule. PASS.
- Capability change goes through Spec Kit: this plan. PASS.

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/091-aftermath-wound-records/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/             # Phase 1 output (N/A — internal engine function, no external contract)
└── tasks.md              # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

```text
engine/
├── wyrd/
│   ├── resolution.py     # add AFTERMATH_TABLE, _aftermath_band, _stage_aftermath
│   └── character.py      # unchanged — reused as-is
tests/
└── test_resolution.py    # add aftermath coverage (rows, boundaries, wound-record shape)
tools/
└── check_aftermath_odds.py  # new check script, asserting the 71%/23% figures (FR-010)
```

**Structure Decision**: Single project, extending the existing `engine/wyrd/resolution.py`
module in place — the same file and pattern `_stage_critical`/`CRITICAL_TABLES` already
established for #251. No new module is warranted for one table and one staging function.

## Complexity Tracking

*No violations — table omitted.*
