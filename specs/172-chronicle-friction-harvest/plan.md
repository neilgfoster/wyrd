# Implementation Plan: Chronicle friction harvest

**Branch**: `172-chronicle-friction-harvest` | **Date**: 2026-09-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/172-chronicle-friction-harvest/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `tools/harvest_friction.py`: a stdlib-only Python script that reads one or more chronicle
repos' `log/friction.md` files (the format `docs/design/16-session.md` settles), applies that
document's own triage line to separate a genuine engine gap from setting-local color, checks each
surviving candidate against `wyrd`'s existing issues via kord's `github-issue-dedup-check`
primitive (shelling to kord's `client.py`, the same pattern `kord-template-harvest` already
uses), and prints a reviewable list of proposed issues — new proposals distinct from likely
duplicates — without filing anything itself. Filing is a separate, explicit operator step (`gh
issue create`, or the existing `github-issue-recurrence-comment` primitive for a duplicate),
mirroring the propose-then-confirm posture `kord-template-harvest` already establishes for its own
output epic.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only (per `CLAUDE.md`'s `tools/` convention and issue
#95's own Definition of Done), except for shelling out to `gh` (to read a chronicle repo's
`log/friction.md` when no local checkout is given) and to kord's `client.py` (for
`github-issue-dedup-check`) — the same two allowances the issue's DoD names explicitly.

**Primary Dependencies**: None beyond the Python standard library and the two external CLIs
above (`gh`, and kord's `client.py` invoked as a subprocess, exactly as `tools/backlog.py`
already shells to `gh`).

**Storage**: Reads `log/friction.md` (Markdown, per `docs/design/16-session.md`) from each named
chronicle repo. Writes nothing — no local cache, no "already seen" ledger (Assumptions /
FR-010): re-invocation safety comes from the dedup check against `wyrd`'s live issues, not from
local state that could drift from what is actually on the board.

**Testing**: `python3 -m unittest discover -s tools -p 'test_*.py'` — `docs/design/27-tooling.md`
§6 states "stdlib unittest. No pytest," and `tools/test_backlog.py` already follows it; this
feature's tests use the same `unittest.TestCase` shape against fixture `log/friction.md` files
(mirroring `tools/fixtures/`'s existing use for other checkers), with the two GitHub-calling
functions (`gh` read, `github-issue-dedup-check` call) isolated behind an injectable callable so
tests substitute a fake instead of shelling out for real.

**Target Platform**: Linux/CLI, run manually by an operator from this repo (or any environment
with `python3`, `gh`, and access to kord's `client.py`), consistent with every other `tools/`
script here.

**Project Type**: Single CLI script inside the existing `tools/` tree — no new top-level
project, no library boundary; matches `backlog.py`'s own shape (a script that shells to `gh` and
prints a report for an operator to act on).

**Performance Goals**: N/A — a friction log is small (dozens of entries at most per chronicle
per session cadence); no throughput or latency target applies.

**Constraints**:
- Never file an issue itself (FR-003) — output is a proposal list, filing is an explicit
  follow-up command the operator runs.
- Never let narrative content cross into a proposal (FR-005, `CLAUDE.md` "Nothing unpublishable
  may enter this repository") — a proposal's body is built only from the friction entry's
  `mechanic` field plus a restatement of `what happened`/`what the GM did`, never other text from
  the chronicle repo.
- Must not error on a chronicle with no `log/friction.md` (FR-006).
- Must skip and separately report a malformed entry (missing field) rather than guess or drop it
  silently (FR-008).

**Scale/Scope**: One new script (`tools/harvest_friction.py`), one new test module
(`tools/test_harvest_friction.py`), fixture friction-log files under `tools/fixtures/`, and this
feature's own `specs/172-chronicle-friction-harvest/` artifacts. No changes to
`docs/design/16-session.md` — that document is #94's territory and already states the format and
triage line this feature consumes as-is.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` in this repo is the unfilled Spec Kit template — as with the
sibling feature (#171/PR #442), this repo's actual governing document for design and build work
is `CLAUDE.md`. Gates checked against it directly:

- **Nothing unpublishable enters `wyrd`** (`CLAUDE.md` "The repositories"): PASS by construction
  — FR-005 and the Constraints above bound every proposal to the friction entry's own mechanical
  fields; Phase 1's data model and quickstart both include an explicit check for this before
  reporting done.
- **Deterministic over inference** (`CLAUDE.md`, `docs/design/27-tooling.md`): PASS — the triage
  line is applied as an explicit, checkable rule (spec FR-002, the same three conditions
  `docs/design/16-session.md` already enumerates), and duplicate detection reuses the existing
  deterministic `github-issue-dedup-check` primitive rather than an LLM similarity judgment.
- **The code is linted and formatted** (`CLAUDE.md`): PASS as a gate to satisfy before PR —
  `ruff check .` / `ruff format --check .` run over the new script and test module as part of
  this feature's own validation, same as every other `tools/` addition.
- **ADR discipline** (`CLAUDE.md` "Decisions are recorded"): No ADR raised. The design choices
  here (stdlib script, `gh`/`client.py` shell-outs, dedup via the existing primitive, propose-
  don't-file) are direct reads of issue #95's own stated Definition of Done and of the pattern
  `kord-template-harvest` already established — not a contested fork with a rejected alternative
  a future reader would plausibly re-propose.
- **Work is tracked as GitHub issues, via kord** (`CLAUDE.md`): This plan is itself produced
  through that cycle (`kord-feature-specify` → `clarify` → `plan` → `tasks` → `implement`) against
  issue #95, child of epic #93.

No violations. Complexity Tracking table below is empty accordingly.

## Project Structure

### Documentation (this feature)

```text
specs/172-chronicle-friction-harvest/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

No `/contracts/` — this feature's external interface is a CLI invocation (`tools/harvest_friction.py
--chronicle <path-or-owner/repo> [...]`), which `quickstart.md` documents directly rather than as
a separate contract file, consistent with `tools/backlog.py` and its siblings having no
`contracts/` of their own either.

### Source Code (repository root)

```text
tools/
├── harvest_friction.py          # new: the harvest script this feature adds
├── test_harvest_friction.py     # new: its test module
└── fixtures/
    └── friction/                # new: sample log/friction.md fixtures for tests
        ├── qualifying.md
        ├── color_only.md
        └── malformed.md
```

**Structure Decision**: A single script added to the existing `tools/` tree, following the
established `tools/check_*.py` / `tools/backlog.py` shape (a stdlib CLI, its own `test_*.py`
module, shared `tools/fixtures/` for sample input) — none of the template's web/mobile project
layouts apply.

## Complexity Tracking

*No entries — Constitution Check reported no violations.*
