# Implementation Plan: Scenario selection by thread heat and hooks

**Branch**: `131-scenario-selection` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/131-scenario-selection/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/scenario_selection.py` module, matching the epic's existing division of
labour (plain dicts/lists in, plain dicts out, no I/O): `rank_by_heat` (stable descending sort),
`select_scenario` (best hook/thread-heat match, deterministic tie-break), `scale_encounters`
(reuses `adversary.scaled_count` unchanged), and `record_source` (attaches provenance).

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: `wyrd.adversary` (`scaled_count`) for encounter scaling — no new
scaling formula.

**Storage**: N/A — plain dicts/lists in, plain dicts out. `scenarios/*/scenario.yaml` file
loading and setting-filtering are a caller/setting-repo concern (spec.md's Assumptions).

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called at arc start / scenario close (session-orchestration
code, out of scope here, same boundary every sibling module in this epic keeps).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — a handful of set/sum operations over a small candidate list.

**Constraints**: ruff-clean repo-wide; no second danger-scaling formula introduced (FR-005).

**Scale/Scope**: thread ranking, hook-match selection, encounter scaling, provenance recording.
Out of scope: loading `scenario.yaml` files, setting-eligibility filtering, the full scenario
schema.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `hooks`, `heat`, `source`, `danger_rating` are all
  existing engine-neutral terms already in docs/design/19-campaign.md/03-rules.md. PASS.
- Deterministic over inference (ADR 0005) — selection is a pure deterministic best-match/
  tie-break computation, not inferred. PASS.
- No second danger-scaling mechanism (FR-005) — reuses `adversary.scaled_count` unchanged, the
  same discipline #338 kept toward `threat.resolve_effects`. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/131-scenario-selection/
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
└── scenario_selection.py   # NEW: rank_by_heat, select_scenario, scale_encounters, record_source

tests/engine/
└── test_scenario_selection.py  # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
