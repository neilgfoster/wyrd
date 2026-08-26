# Implementation Plan: The dangling-mechanic check

**Branch**: `028-dangling-mechanic-check` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/028-dangling-mechanic-check/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `tools/check_dangling_mechanics.py`: a stdlib-only script that scans every `design/**.md`
file for mechanic **definitions** (headings, table rows, glossary entries) and mechanic
**references** (prose/table uses of a name outside its own definition), and fails when a
reference has no matching definition anywhere under `design/`. Follows the exact shape of
`tools/check_docs.py` — same argparse CLI (`--format json`), same `Problem(str)` pattern, same
`find_problems(root) -> list[Problem]` entry point, tested the same way: `tools/test_check_dangling_mechanics.py`
builds each fixture as a temporary tree per test (no on-disk fixtures), including one test per
historical instance from issue #59.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`design/07-tooling.md` section 2)

**Primary Dependencies**: None — `pathlib`, `re`, `argparse`, `json`, `sys` only, matching `check_docs.py`

**Storage**: N/A — reads `design/**.md` from the filesystem, writes nothing

**Testing**: stdlib `unittest`, run via `python3 -m unittest discover -s tools -p 'test_*.py'` (matches `test_check_docs.py`'s own header)

**Target Platform**: Linux/macOS dev environment, CLI invocation — same as every other `tools/` script

**Project Type**: single-file CLI tool, following the `tools/check_docs.py` / `tools/backlog.py` pattern

**Performance Goals**: N/A — `design/` is on the order of tens of files; a full scan must complete well under a second, same order as `check_docs.py`

**Constraints**: No third-party dependencies, no daemon/server, auditable top to bottom (`design/07-tooling.md` section 2)

**Scale/Scope**: One new script (`tools/check_dangling_mechanics.py`) plus its test module (`tools/test_check_dangling_mechanics.py`); no changes to existing scripts or design documents required for the check itself to exist and pass

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo** — the check reads only `design/`, already public content; no source-text extraction. **Pass.**
- **No setting or system names in `design/`/`README.md`** — this feature adds a script, not a design document; it does not touch design content. **Pass** (N/A to this change).
- **Tone is a setting property** — N/A, no mechanic content authored here. **Pass.**
- **Deterministic over inference** (ADR 0005) — this is precisely a script replacing what prose review has twice failed to catch. **Pass, this is the point of the feature.**
- **Rule changes apply forward only** — N/A, no gameplay rule changes. **Pass.**
- **Design documents rewritten in place; ADRs never edited** — no design document edits are needed to build the checker itself (FR-007 requires it pass against the *existing* design tree, not that the tree be changed to satisfy it). **Pass.**
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** — this plan is that cycle. **Pass.**

No violations. Complexity Tracking table is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/028-dangling-mechanic-check/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/            # Phase 1 output (CLI contract, since this is a CLI tool not a library/API)
└── tasks.md              # Phase 2 output (/speckit-tasks — not created by this command)
```

### Source Code (repository root)

```text
tools/
├── check_dangling_mechanics.py       # the check: find_problems(root) -> list[Problem], argparse CLI
└── test_check_dangling_mechanics.py  # unittest, temp-tree fixtures per test (no fixtures/ dir)
```

**Structure Decision**: Single project, single new script pair in `tools/`, matching the
existing `check_docs.py` / `test_check_docs.py` pair exactly. No `src/`, no `frontend/`,
no `contracts/` in the REST-API sense — "contracts" here means the CLI's argument/output
contract (documented in Phase 1's `contracts/cli.md`), since this tool is a CLI, not a service.

## Complexity Tracking

*No violations — table not needed.*
