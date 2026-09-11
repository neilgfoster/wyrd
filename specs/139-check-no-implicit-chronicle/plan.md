# Implementation Plan: Check: no implicit current-chronicle global state

**Branch**: `139-check-no-implicit-chronicle` | **Date**: 2026-09-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/139-check-no-implicit-chronicle/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `tools/check_no_implicit_chronicle.py`: `ast`-parses every `engine/wyrd/*.py` file, finds
module-level assignments whose value is an empty mutable container, and flags any whose
immediately preceding comment lines don't contain `"process-local"` — the exact justification
language `resolution._open_proposals` (the one existing, allowed exception) already uses.
Matches `check_dangling_mechanics.py`'s CLI/exit-code/test-suite conventions exactly.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`ast`, `pathlib`, `argparse`).

**Primary Dependencies**: none.

**Storage**: N/A — reads the filesystem, writes nothing.

**Testing**: stdlib `unittest`, matching `test_check_dangling_mechanics.py`'s "scratch tree per
test, no fixtures on disk" convention.

**Target Platform**: repo-maintenance CLI tool (`tools/`), run on demand.

**Project Type**: single project (repo tooling, not the engine).

**Performance Goals**: N/A — a handful of files, one `ast.parse` each.

**Constraints**: ruff-clean repo-wide; no CI to wire into (this repo has none); must pass clean
against the real repo today (SC-001).

**Scale/Scope**: `engine/wyrd/*.py` only. Out of scope: `tools/`, `specs/`, tests, any
CI wiring.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- No setting/system vocabulary introduced. PASS.
- Deterministic over inference (ADR 0005) — `ast`-based structural detection, not a guess.
  PASS.
- Matches this repo's established deterministic-check convention
  (`check_docs.py`/`check_dangling_mechanics.py`). PASS.
- Capability change goes through the Spec Kit cycle, `specs/` committed — this plan (matching
  `check_dangling_mechanics.py`'s own `specs/028-dangling-mechanic-check` precedent for a
  `tools/` check). PASS.
- No gate violations to justify; Complexity Tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/139-check-no-implicit-chronicle/
├── plan.md, research.md, data-model.md, quickstart.md, tasks.md
└── contracts/ (none — a CLI tool, no library API contract)
```

### Source Code (repository root)

```text
tools/check_no_implicit_chronicle.py       # NEW
tools/test_check_no_implicit_chronicle.py  # NEW
```

## Complexity Tracking

*No entries — no constitution gate was violated.*
