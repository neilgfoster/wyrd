# Implementation Plan: Scenario index schema and deterministic selection (scenarios.json)

**Branch**: `135-scenario-index-schema` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/135-scenario-index-schema/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/corpus_scenario.py` module: `validate_scenario_record` (closed
`scale`/`season` vocabularies), `scale_danger` (reuses `adversary.danger_effective` unchanged),
`check_requirements` (`needs_access`/`needs_capability` reported met/unmet, never filtered),
`check_helped_by` (informational only), `is_eligible_for_setting` (the one genuine hard gate:
`settings` membership).

## Technical Context

**Language/Version**: Python 3.11+, standard library only.

**Primary Dependencies**: `wyrd.adversary` (`danger_effective`) for danger scaling — no new
formula.

**Storage**: N/A — plain dicts/lists in, plain dicts out.

**Testing**: stdlib `unittest`, run with `PYTHONPATH=engine`.

**Target Platform**: engine library, called by scenario selection (`scenario_selection.py`,
#339) and retrieval (`corpus_terms`/#357, out of scope here).

**Project Type**: single project (engine library).

**Performance Goals**: N/A — a handful of dict operations per scenario record.

**Constraints**: ruff-clean repo-wide; no second danger-scaling formula (FR-004); needs_access/
needs_capability/helped_by never filter (FR-005, FR-006, FR-007).

**Scale/Scope**: schema validation, danger scaling, requirement/helped-by reporting, setting
eligibility. Out of scope: thematic fields, thread-graph matching (#339), the LLM extraction
step that produces `tone`/`themes`/`shape`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced — `scale`, `season`, `needs_access`,
  `needs_capability`, `helped_by` are all existing engine-neutral terms already in
  docs/design/26-corpus-index.md. PASS.
- No second danger-scaling mechanism (FR-004) — reuses `adversary.danger_effective` unchanged,
  the same discipline #339's `scale_encounters` already kept toward `adversary.scaled_count`.
  PASS.
- "Almost nothing gates" (docs/design/26-corpus-index.md) — only `settings` membership is a hard
  exclusion; everything else is informational. PASS.
- Deterministic over inference (ADR 0005) — every function here is a pure, deterministic
  validation/lookup. PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan. PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/135-scenario-index-schema/
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
└── corpus_scenario.py     # NEW: validate_scenario_record, scale_danger, check_requirements,
                            #      check_helped_by, is_eligible_for_setting

tests/engine/
└── test_corpus_scenario.py # NEW: covers every FR/SC in spec.md
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
