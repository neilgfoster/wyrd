# Implementation Plan: Commit-Back Path for Accepted Generated Content

**Branch**: `164-commit-back-path-for-generated-content` | **Date**: 2026-09-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/164-commit-back-path-for-generated-content/spec.md`

## Summary

Add one new engine module implementing specs/161-adventure-and-campaign-generation's FR-012
through FR-015 — the accept/reject path for a `GenerationResult` (#420, `generation.py`) that has
been run through the five anti-inflation checks (#421, `generation_checks.py`). `accept_result`
writes the candidate as an ordinary `arc`/`beat` entity at `status: drafted` via
`entity.py`/`state.py`'s existing schema and I/O, records provenance as a new, additive
`sources.generated` shape, and consumes/emits whatever thread and threat changes the candidate
declares by calling `thread.py`'s `new_thread`/`touch` and `threat.py`'s
`promote`/`check_activation`/`resolve_effects` directly — never a parallel reimplementation.
`reject_result` (covering both an explicit decline and a `checks` list carrying any `reject`
entry, or an empty/unevaluated `checks` list) performs no I/O and calls no mutation function at
all. No content generation and no persistence-layer changes beyond the one additive `sources`
field — those are this feature's explicit boundaries per spec.md's Assumptions.

## Technical Context

**Language/Version**: Python 3.11 (repo-wide target, per `pyproject.toml`)

**Primary Dependencies**: standard library only, plus the existing `engine/wyrd/entity.py`
(schema/validation), `engine/wyrd/state.py` (`save_entity`, atomic file I/O), `engine/wyrd/
thread.py` (`new_thread`, `touch`), and `engine/wyrd/threat.py` (`promote`, `check_activation`,
`resolve_effects`) — no new dependency

**Storage**: the filesystem entity store `state.py`/`entity.py` already write to — one new entity
file per accepted result, at a path the caller supplies; no new file, table, or schema beyond one
additive `sources.generated` shape

**Testing**: stdlib unittest (docs/design/27-tooling.md section 6), run with `PYTHONPATH=engine`,
matching `tests/engine/`'s existing convention

**Target Platform**: same as the rest of the engine — a library called by the (not-yet-built)
generation pipeline (#422's sibling), no new runtime target

**Project Type**: single project (existing `engine/wyrd/` library + `tests/engine/` test tree)

**Performance Goals**: N/A — one file write plus a handful of in-memory dict mutations per call,
no throughput target

**Constraints**: setting-agnostic (no setting/system name in any field or detail text, per
CLAUDE.md); ruff-clean at line length 100, rule sets E/F/I/UP, target 3.11; FR-013 MUST call
`thread.py`/`threat.py`'s existing functions rather than recompute equivalent behaviour (issue
#422's own constraint, verified by a test asserting the identical function is invoked); FR-015
MUST leave zero filesystem writes and zero thread/threat mutation on any non-accepted path,
verified by a filesystem/state assertion rather than a return-value check alone; FR-014 (`29-
evolution.md` "the past is a fact") means this feature adds no update/rewrite path for an entity
already written — `accept_result` only ever creates a new file, never opens an existing one

**Scale/Scope**: one new module (~150-200 lines: `accept_result`, `reject_result`, a small
`_apply_thread_and_threat_changes` helper that dispatches to the existing functions), one new
test module covering an accepted write, a declined/rejected no-write case, and the
identical-function-call assertion (spec.md's own acceptance criteria); one small additive change
to `entity.py`'s `validate_source` to accept the `{generated, mode, consumed}` shape alongside the
existing `{work, pages, licence, path}` shape, since FR-012 requires this without replacing the
existing shape — no other existing module changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unfilled Spec Kit template (placeholder principles, no
project-specific content ratified) — no additional gates beyond this repo's own CLAUDE.md rules,
which are already the standing constraints followed throughout (setting-agnostic naming, ruff
clean, Spec Kit cycle for capability changes, reuse existing mutation functions over
reimplementing them, "the past is a fact" — no retcon path). No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/164-commit-back-path-for-generated-content/
├── plan.md               # This file
├── research.md           # Phase 0 output
├── data-model.md          # Phase 1 output — the sources.generated shape and accept/reject
│                           # outcome contract
├── contracts/             # Phase 1 output — accept_result/reject_result's input/output contract
├── quickstart.md          # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md               # Phase 2 output (kord-feature-tasks)
```

specs/161-adventure-and-campaign-generation/spec.md's FR-012 through FR-015 remain the single
source of truth for *what* the commit-back path requires; this feature's own data-model.md/
contracts restate only the additional structural detail (the `sources.generated` field shape,
the accept/reject outcome record) needed to implement them mechanically, rather than re-deriving
the FR text itself.

### Source Code (repository root)

```text
engine/wyrd/
├── generation_commit.py   # NEW — accept_result, reject_result, and the thread/threat dispatch
│                           # helper
└── entity.py               # MODIFIED — validate_source accepts the additive
                             # {generated, mode, consumed} sources[] shape

tests/engine/
└── test_generation_commit.py   # NEW — covers an accepted write (User Story 1), a declined/
                                 # rejected no-write case with a filesystem assertion (User Story
                                 # 2), and a test asserting the accept path calls thread.py's/
                                 # threat.py's own functions (FR-003)
```

**Structure Decision**: a single new module in the existing `engine/wyrd/` package, tested from
the existing `tests/engine/` tree — matching `generation.py` (#420) and `generation_checks.py`
(#421). It imports `entity`, `state`, `thread`, and `threat` directly (all existing modules); it
takes a `GenerationResult` (#420's shape) as a plain dict, matching every sibling module's
convention of sharing shapes by structure, not by a shared base class. No new top-level
directory, no new dependency, no new persisted schema beyond `entity.py`'s one additive
`sources.generated` variant.

## Complexity Tracking

*No Constitution Check violations — this section is not applicable.*
