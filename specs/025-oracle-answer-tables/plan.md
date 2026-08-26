# Implementation Plan: Oracle answer tables

**Branch**: `025-oracle-answer-tables` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/025-oracle-answer-tables/spec.md`

## Summary

Write `design/03a-5-oracle-answers.md`: define what an oracle is, when the GM must use one, and
the `oracle-answer` table — five likelihood bands over a reused `1d100` roll, each with an
Exceptional Yes / Yes / No / Exceptional No degree, whose odds are computed and checked by script
rather than asserted. State the oracle roll's relationship to the existing Wyrd die (reused
verbatim, no new mechanism) and what an oracle roll records to the beat log. Amend
`design/01-principles.md` so the GM contract states the same obligation. Update
`design/03a-tables.md`'s index row, and `design/02-architecture.md` / `design/07-tooling.md` if
their file-layout mentions need it.

## Technical Context

**Language/Version**: Markdown design documents; Python 3 for the verification script
(matches existing `tools/*.py` / `specs/*/check_*.py` convention in this repo).

**Primary Dependencies**: None — stdlib only, per existing `check_*.py` scripts in other
`specs/*/` directories.

**Storage**: N/A — the "data" this feature produces is design prose plus a YAML table
(`engine/tables/oracle-answer.yaml`), not application state.

**Testing**: `tools/check_oracle_answers.py` (probability/contiguity maths), matching the
`tools/check_<family>.py` convention already used by `check_affliction.py`,
`check_transformation.py`, and `check_fault_line.py`; plus the repo-wide checks this change must
keep green: `tools/check_docs.py` (reachability) and a grep for setting/system vocabulary
(`CLAUDE.md`).

**Target Platform**: N/A — this repo has no runtime target; it is design documents plus data
tables that a future rules engine reads.

**Project Type**: Documentation / design-record change to a single-repo TTRPG engine (`wyrd`).

**Performance Goals**: N/A.

**Constraints**: No setting or system name or borrowed term anywhere in `design/`
(`CLAUDE.md`); every probability claim computed and checked, not asserted (`CLAUDE.md`); design
documents rewritten in place, no changelog prose (`CLAUDE.md`).

**Scale/Scope**: One new design document, three existing documents amended
(`design/01-principles.md`, `design/03a-tables.md`'s index row, and `design/02-architecture.md` /
`design/07-tooling.md` if their filename mentions go stale), one verification script. No engine
data file — the engine implementation (and `engine/tables/*.yaml`) does not exist yet for any of
the four already-defined families either; each family's document is the sole deliverable until
Stage 13 builds the engine that reads it.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

This repo has no `.specify/memory/constitution.md`; its governing document is `CLAUDE.md`
(project root). Relevant gates, checked against this plan:

- **Setting-agnostic engine** — no setting/system name in `design/`. Gate: satisfied by design;
  every example question and row description in the new document is generic. Verified by grep
  (`quickstart.md`) before this feature is done.
- **Deterministic over inference / compute the maths** — every probability claim is computed by
  `check_oracle_answer.py`, not asserted. Gate: satisfied — see `research.md`, whose numbers this
  script already reproduces.
- **Design documents rewritten in place, no changelogs** — `design/01-principles.md`,
  `design/03a-tables.md`, `design/02-architecture.md`, `design/07-tooling.md` are edited to
  describe the present state only.
- **Capability change goes through the Spec Kit cycle, `specs/` committed** — this plan.

No violations requiring the Complexity Tracking table below.

## Project Structure

### Documentation (this feature)

```text
specs/025-oracle-answer-tables/
├── plan.md                    # This file
├── research.md                # Phase 0 output
├── data-model.md              # Phase 1 output
├── quickstart.md              # Phase 1 output
└── tasks.md                   # Phase 2 output (/speckit-tasks)
```

No `contracts/` — this feature has no external interface (API, CLI surface, wire format); it is a
design document and a data table read by the engine's own table-loading rules, already specified
in `design/03a-tables.md`.

### Source Code (repository root)

```text
design/
├── 01-principles.md              # amended: GM's obligation to consult an oracle
├── 02-architecture.md            # amended only if the oracles file-layout mention goes stale
├── 03a-tables.md                 # amended: index row for Oracles, linked and rolled
├── 03a-5-oracle-answers.md       # new: what an oracle is, the oracle-answer table, the odds
└── 07-tooling.md                 # amended only if the oracles file-layout mention goes stale

tools/
└── check_oracle_answers.py       # new: computes and asserts the row widths/odds table
```

**Structure Decision**: Follows the existing pattern set by the four already-defined table
families (`design/03a-1-criticals.md` through `03a-4-afflictions.md`, each with a matching
`tools/check_<family>.py`) — this feature adds the fifth in the same shape, plus the
design-document amendments the issue's scope names. None of the four existing families has an
`engine/tables/*.yaml` file yet either (the engine implementation is future work, Stage 13), so
this feature does not add one out of step with its siblings.

## Complexity Tracking

No gate violations — table not filled.
