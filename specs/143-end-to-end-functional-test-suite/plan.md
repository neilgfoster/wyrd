# Implementation Plan: End-to-end functional test suite across the whole engine

**Branch**: `143-end-to-end-functional-test-suite` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/143-end-to-end-functional-test-suite/spec.md`

## Summary

Add one new integration test module, `tests/engine/test_integration.py`, that constructs a
single player character via `engine/wyrd/creation.py` inside a temporary chronicle directory,
then drives that character through the eleven subsystem areas named in the spec's FR-002 using
each subsystem's own existing public entry points (the same functions/CLI verbs their own unit
suites already call), asserting at each handoff that the next subsystem's state reflects a
concrete value the previous subsystem produced.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: none beyond the standard library and `engine/wyrd/*` (repo convention,
docs/design/27-tooling.md)

**Storage**: flat files under a `tempfile.TemporaryDirectory()`-backed chronicle root, exactly as
`state.py`/`chronicle.py` already require and as `tests/engine/test_client.py`,
`tests/engine/test_resolution.py` etc. already do for their own fixtures

**Testing**: stdlib `unittest`, `PYTHONPATH=engine`, matching every existing file under
`tests/engine/`

**Target Platform**: Linux server / CI-less local run (`python3 -m pytest` or `python3 -m
unittest`)

**Project Type**: library (engine module) plus its test suite

**Performance Goals**: N/A — a single deterministic in-process run, no throughput target

**Constraints**: no new engine capability (spec FR-007); no third-party test dependency (FR-005);
ruff-clean under the repo's existing config (FR-006); deterministic across repeated runs (SC-004)

**Scale/Scope**: one new test file (plus, if needed, a small shared fixture helper reused only by
that file) exercising eleven existing subsystem areas in one sequential test method

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

This repo has no `.specify/memory/constitution.md` populated with project-specific gates beyond
CLAUDE.md's own ground rules, which this plan already satisfies: stdlib-only, ruff-clean,
Spec-Kit-cycled (this document is that cycle), and adds no setting-specific vocabulary. No
violation to justify — Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/143-end-to-end-functional-test-suite/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (skipped — no external interface added)
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

```text
engine/wyrd/            # existing subsystem modules — read-only for this feature, no new
                         # capability added to any of them (spec FR-007)

tests/engine/
├── test_integration.py # NEW — the single end-to-end sequence and its handoff assertions
└── ...                 # every existing per-module unit suite, unchanged
```

**Structure Decision**: Single project (this is a library/engine repo, not a client/server
split). The new artifact is exactly one test module under the existing `tests/engine/` tree,
following the same `sys.path.insert(... "engine")` + `from wyrd import ...` pattern every sibling
test file in that directory already uses. No production code under `engine/wyrd/` is modified.

## Complexity Tracking

Not applicable — no Constitution Check violation.
