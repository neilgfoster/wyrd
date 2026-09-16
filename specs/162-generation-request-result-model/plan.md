# Implementation Plan: Generation request/result data model and mode validation

**Branch**: `162-generation-request-result-model` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/162-generation-request-result-model/spec.md`

## Summary

Add one new engine module implementing the `GenerationRequest`/`GenerationResult` shapes and
mode-validation functions specified by specs/161-adventure-and-campaign-generation's FR-001
through FR-006 (and specified in detail by this feature's own spec.md/data-model.md, inherited
unchanged from specs/161's data-model.md and contracts/generation-request.md). Pure, side-effect
free functions only — no persistence, no anti-inflation checks, no content generation.

## Technical Context

**Language/Version**: Python 3.11 (repo-wide target, per `pyproject.toml`)

**Primary Dependencies**: none beyond the standard library — matches every other `engine/wyrd/*`
module's existing style (plain functions/dataclasses, no external validation library)

**Storage**: N/A — both shapes are explicitly transient (data-model.md)

**Testing**: pytest, run with `PYTHONPATH=engine`, matching `tests/engine/`'s existing convention

**Target Platform**: same as the rest of the engine — a library invoked by the CLI/session layer,
no new runtime target

**Project Type**: single project (existing `engine/wyrd/` library + `tests/engine/` test tree)

**Performance Goals**: N/A — validation of small in-memory structures, no throughput target

**Constraints**: setting-agnostic (no setting/system name in the shape or validation logic, per
CLAUDE.md); ruff-clean at line length 100, rule sets E/F/I/UP, target 3.11

**Scale/Scope**: one new module (~150-250 lines), one new test module; no changes to any existing
module — this feature has no persistence and no caller yet (the three sibling features wire it up)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled Spec Kit template (placeholder principles, no
project-specific content ratified) — no additional gates beyond this repo's own CLAUDE.md rules,
which are already the standing constraints followed throughout (setting-agnostic naming, ruff
clean, Spec Kit cycle for capability changes). No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/162-generation-request-result-model/
├── plan.md              # This file
├── data-model.md         # Phase 1 output — inherited unchanged from specs/161 (see below)
├── contracts/            # Phase 1 output — inherited unchanged from specs/161 (see below)
├── quickstart.md         # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md              # Phase 2 output (kord-feature-tasks)
```

Phase 1's `data-model.md` and `contracts/generation-request.md` are **not regenerated** here —
they already exist, complete and unchanged, at
`specs/161-adventure-and-campaign-generation/data-model.md` and
`specs/161-adventure-and-campaign-generation/contracts/generation-request.md`, and this feature's
own spec.md's Key Entities section restates the same two shapes at this feature's own scope
(FR-001-006 only). Duplicating them verbatim into this feature's directory would create two
documents describing one thing — the exact drift CLAUDE.md's "Recurring faults" section warns
against — so this plan references the specs/161 originals directly rather than copying them.

### Source Code (repository root)

```text
engine/wyrd/
└── generation.py          # NEW — GenerationRequest, GenerationResult, validate_request(),
                            #        validate_campaign_spine_alias(), structured rejection reasons

tests/engine/
└── test_generation.py     # NEW — table-driven tests per spec.md's User Stories 1-3 and FR-006's
                            #        mode-boundary invariant
```

**Structure Decision**: a single new module in the existing `engine/wyrd/` package, tested from
the existing `tests/engine/` tree — matching every other feature in this codebase (e.g.
`thread.py`, `threat.py`) with no new top-level directory, no new dependency, and no change to
`engine/wyrd/__init__.py` beyond adding the new module (no re-export needed since nothing calls
this module yet).

## Complexity Tracking

*No Constitution Check violations — this section is not applicable.*
