# Implementation Plan: Anti-inflation checks for generated content

**Branch**: `163-anti-inflation-checks` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/163-anti-inflation-checks/spec.md`

## Summary

Add one new engine module implementing the five anti-inflation checks specs/161-adventure-and-
campaign-generation's FR-007 through FR-011 specify — entity-membership, tone/prophecy, danger-
band, scale-drift, and favourable-coincidence — as pure functions that each evaluate a
`GenerationRequest`/candidate pair (from #420's `engine/wyrd/generation.py`) and return a
`{rule, outcome, detail}` check entry matching `GenerationResult.checks`' shape. FR-009 calls the
engine's existing danger-scaling arithmetic (`corpus_scenario.scale_danger`) rather than
reimplementing it. A sixth, thin aggregator function runs all five in order and returns the full
`checks:` list. No persistence, no content generation, no commit-back — those are sibling
features.

## Technical Context

**Language/Version**: Python 3.11 (repo-wide target, per `pyproject.toml`)

**Primary Dependencies**: standard library only, plus `engine/wyrd/corpus_scenario.py`'s
existing `scale_danger` (FR-009 reuse) — matches every other `engine/wyrd/*` module's existing
style

**Storage**: N/A — both the request/candidate inputs and the check-entry outputs are transient
in-memory structures (data-model.md)

**Testing**: stdlib unittest (docs/design/27-tooling.md section 6: "stdlib unittest. No
pytest"), run with `PYTHONPATH=engine`, matching `tests/engine/`'s existing convention

**Target Platform**: same as the rest of the engine — a library called by the (not-yet-built)
generation pipeline, no new runtime target

**Project Type**: single project (existing `engine/wyrd/` library + `tests/engine/` test tree)

**Performance Goals**: N/A — five comparisons against small in-memory structures per call, no
throughput target

**Constraints**: setting-agnostic (no setting/system name in any check's vocabulary or detail
text, per CLAUDE.md); ruff-clean at line length 100, rule sets E/F/I/UP, target 3.11; FR-009 MUST
call the engine's existing danger-scaling arithmetic rather than recompute an equivalent formula
(issue #421's own constraint)

**Scale/Scope**: one new module (~200-300 lines: five check functions + one aggregator + shared
helpers), one new test module covering both a passing and a rejecting/narrowing case per check
(spec.md's own acceptance criteria); no changes to any existing module — `generation.py`'s
`checks:` field stays populated by the caller, not mutated by this module

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled Spec Kit template (placeholder principles, no
project-specific content ratified) — no additional gates beyond this repo's own CLAUDE.md rules,
which are already the standing constraints followed throughout (setting-agnostic naming, ruff
clean, Spec Kit cycle for capability changes, reuse existing arithmetic over reimplementing it).
No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/163-anti-inflation-checks/
├── plan.md               # This file
├── research.md           # Phase 0 output
├── data-model.md          # Phase 1 output — the check-entry shape and candidate contract
├── contracts/             # Phase 1 output — the five check functions' input/output contract
├── quickstart.md          # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md               # Phase 2 output (kord-feature-tasks)
```

specs/161-adventure-and-campaign-generation/spec.md's FR-007 through FR-011 remain the single
source of truth for *what* each rule requires; this feature's own data-model.md/contracts restate
only the additional structural detail (the check-entry shape, the candidate's `threat_updates`
field) needed to implement them mechanically, rather than re-deriving the FR text itself.

### Source Code (repository root)

```text
engine/wyrd/
└── generation_checks.py   # NEW — check_entity_membership, check_prophecy, check_danger_band,
                            #       check_scale_drift, check_favourable_coincidence, run_checks

tests/engine/
└── test_generation_checks.py   # NEW — table-driven tests per spec.md's User Stories 1-3,
                                 #       covering both a passing and a rejecting/narrowing case
                                 #       per check
```

**Structure Decision**: a single new module in the existing `engine/wyrd/` package, tested from
the existing `tests/engine/` tree — matching `generation.py` (#420) and every other feature module
in this codebase, with no new top-level directory and no new dependency. `generation_checks.py`
imports `engine/wyrd/corpus_scenario.py` for FR-009's reuse and `engine/wyrd/threat.py`'s
`validate_connections` for part of FR-010's "no connection" leg; it imports nothing from
`generation.py` itself (the two modules share a data shape by convention, not by import, matching
how `thread.py`/`threat.py` already relate).

## Complexity Tracking

*No Constitution Check violations — this section is not applicable.*
