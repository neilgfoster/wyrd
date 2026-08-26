# Implementation Plan: Fleet rollout of engine and template changes

**Branch**: `032-fleet-rollout` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/032-fleet-rollout/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

A single stdlib script, `tools/fleet_rollout.py`, following `tools/backlog.py`'s shape: a
read-only `status` verb that discovers the fleet by listing repos matching `wyrd-setting-*` /
`wyrd-setting-template` / `wyrd-chronicle-template`, reads each one's `.wyrd-version` marker
file, and reports current/behind/unversioned/diverged/unreachable against a **change manifest**
committed in the source repos (`wyrd-setting-template`, `wyrd-chronicle-template`, and this
engine repo). A `rollout` verb reads the same manifest and opens one PR per behind repo,
bundling every outstanding change since its recorded SHA, built from the manifest entries'
declared class (additive: copy new paths in; structural: apply the entry's migration script).
No content is ever read from a target repo's `library/`, `corpus/`, or `index/` directories.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (`design/07-tooling.md` §2)

**Primary Dependencies**: none — `gh` CLI invoked via `subprocess`, same as `tools/backlog.py`

**Storage**: none — state lives in each repo's `.wyrd-version` file and the source repos'
`rollout/changes/*.yaml` manifest entries; no local cache or database

**Testing**: `stdlib unittest`, captured-fixture based (no network in tests), matching
`tools/test_backlog.py`'s pattern — `python3 -m unittest discover -s tools -p 'test_*.py'`

**Target Platform**: Linux/macOS CLI, run by the maintainer or a scheduled job with `gh` auth

**Project Type**: single CLI tool (extends the existing `tools/` catalog)

**Performance Goals**: N/A — fleet is ~18 repos; a full status read completing in well under a
minute is more than sufficient

**Constraints**: never pushes directly to a repo's default branch; never reads a target repo's
`library/`, `corpus/`, or `index/` content; must work identically against private repos

**Scale/Scope**: sixteen `wyrd-setting-*` repos today, plus `wyrd-setting-template` and
`wyrd-chronicle-template`; designed to keep working as the fleet grows without a code change

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo** — the tool never reads a setting repo's
  `library/`/`corpus/` content (copyrighted material lives there); it only reads/writes a small
  version-marker file and structural files the template itself owns. **Pass.**
- **No setting or system names in `design/` or `README.md`** — this feature adds no design
  document that names one; `tools/fleet_rollout.py`'s own docstring stays generic. **Pass.**
- **Deterministic over inference** (`design/07-tooling.md` §1, ADR 0005) — repo discovery,
  version comparison, and change classification are all script-computed from committed data
  (the manifest), never inferred from a diff. **Pass.**
- **Rule changes apply forward only** (`design/09-evolution.md`) — out of scope by the spec's
  own boundary (live chronicle state migration is excluded); this feature only propagates
  repo/template file changes, which is a different axis. **Pass, not applicable to chronicle
  state.**
- **Capability changes go through the Spec Kit cycle** — this plan is that cycle. **Pass.**
- **Python 3.11+, stdlib only, zero-dependency** (`design/07-tooling.md` §2) — `gh` CLI only,
  no packages. **Pass.**

No violations; Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/032-fleet-rollout/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
tools/
├── fleet_rollout.py          # status + rollout verbs, argparse dispatch (like backlog.py)
├── test_fleet_rollout.py     # unittest, fixture-driven, no network
└── fixtures/
    └── fleet.json            # captured gh repo-list / contents output for tests
```

**Structure Decision**: Single project, extending the existing `tools/` script catalog — the
same shape `tools/backlog.py` and `tools/check_docs.py` already use. No new top-level directory,
no package, no service: one script with two verbs (`status`, `rollout`), a fixture-backed test
file, and a fixture directory. `wyrd-setting-template` and `wyrd-chronicle-template` each gain a
`rollout/changes/` directory (out of this repo, in those repos — recorded in this repo only as
documentation of the manifest schema, not as code that ships there).

## Complexity Tracking

*No violations — table omitted.*
