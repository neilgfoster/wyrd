# Implementation Plan: Generation Pipeline

**Branch**: `165-generation-pipeline` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/165-generation-pipeline/spec.md`

## Summary

Add one new engine module, `generation_pipeline.py`, implementing specs/161's FR-016 through
FR-020 (plus FR-021, this feature's own wiring requirement) as four pure functions plus one
documented call sequence: `select_grounding` (FR-016, no model — reuses `arc_selection.select`'s
thread-subset-match/`leads_to`-fallback primitive over a caller-supplied candidate pool),
`compute_structural_fields` (FR-017, no model — reuses `generation_checks.check_danger_band`'s
own `corpus_scenario.scale_danger` arithmetic and `generation_checks`'s scale-drift constants
rather than recomputing either), `assemble_pacing` (FR-018, Haiku tier — takes the model's
structured response as an injected argument), and `write_prose` (FR-019, capable tier — takes the
model's free-form prose as an injected argument, applies FR-007's entity-membership/labelling
convention, and returns a finished `GenerationResult` via `generation.new_result`). `run_pipeline`
wires all four in order and hands its result straight to `generation_checks.run_checks`, matching
FR-021. No content generation logic beyond field assembly, no persistence, and no live model call
anywhere in this module — an out-of-process caller injects both model responses.

## Technical Context

**Language/Version**: Python 3.11 (repo-wide target, per `pyproject.toml`)

**Primary Dependencies**: standard library only, plus the existing `engine/wyrd/generation.py`
(`GenerationRequest`/`GenerationResult` shapes, `new_result`), `engine/wyrd/generation_checks.py`
(`check_danger_band`'s arithmetic and scale-drift constants, `run_checks`), and `engine/wyrd/
arc_selection.py` (`select`, `entity.resolve_wikilink`-based `leads_to` fallback) — no new
dependency.

**Storage**: none — this module performs no I/O; `generation_commit.py` (already merged) owns
the write path for whatever `GenerationResult` this pipeline produces.

**Testing**: stdlib unittest (docs/design/27-tooling.md section 6), run with `PYTHONPATH=engine`,
matching `tests/engine/`'s existing convention.

**Target Platform**: same as the rest of the engine — a library a future `/wyrd-*` skill or
`create-setting`'s Q3 path calls, supplying both model responses itself; no new runtime target.

**Project Type**: single project (existing `engine/wyrd/` library + `tests/engine/` test tree).

**Performance Goals**: N/A — pure in-memory field assembly, no throughput target.

**Constraints**: setting-agnostic (no setting/system name in any field, label, or detail text,
per CLAUDE.md); ruff-clean at line length 100, rule sets E/F/I/UP, target 3.11; no live model call
performed anywhere in this module (issue #423's explicit out-of-scope boundary) — FR-018/FR-019's
model-derived input always arrives as an ordinary function argument; FR-020 verified by test via
each function's own signature (no model-response parameter on the no-model steps, a structured
mapping only on the Haiku-tier step, free-form text only on the capable-tier step); FR-016/FR-017
reuse `arc_selection`/`generation_checks`'s existing arithmetic rather than recomputing either,
verified the same way #422 verified its own reuse constraint (a test asserting the identical
function/constant is used).

**Scale/Scope**: one new module (~180-220 lines: four pipeline functions plus `run_pipeline`), one
new test module covering each function in isolation, the FR-020 signature/tier assertions, and one
end-to-end pipeline-to-checks composition test per scale (beat/arc/campaign-spine); no changes to
any of the three already-merged sibling modules.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled Spec Kit template (placeholder principles, no
project-specific content ratified) — no additional gates beyond this repo's own CLAUDE.md rules,
already the standing constraints followed throughout this epic (setting-agnostic naming, ruff
clean, Spec Kit cycle for capability changes, reuse existing arithmetic/matching over
reimplementing it, no live model call from engine code). No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/165-generation-pipeline/
├── plan.md               # This file
├── research.md           # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/
│   └── generation-pipeline.md
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (/speckit-tasks — not created by /speckit-plan)
```

### Source Code (repository root)

```text
engine/wyrd/
└── generation_pipeline.py     # NEW — select_grounding, compute_structural_fields,
                                #        assemble_pacing, write_prose, run_pipeline

tests/engine/
└── test_generation_pipeline.py  # NEW
```

**Structure Decision**: single project, matching every sibling `engine/wyrd/*` module in this
epic (#420/#421/#422) — one new module, one new test module, no changes elsewhere.

## Complexity Tracking

*No entries — no constitution violation to justify.*
