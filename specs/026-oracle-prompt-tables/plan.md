# Implementation Plan: Oracle prompt tables

**Branch**: `026-oracle-prompt-tables` | **Date**: 2026-08-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/026-oracle-prompt-tables/spec.md`

## Summary

Write `docs/design/15-oracle-prompts.md`: a fixed, small set of genre-neutral prompt families (NPC
objective, why a situation isn't as presented, what a thread turns on, what complicates a scene),
each a table under the existing `oracles` family from `docs/design/04-tables.md`. Every row is checked
against a grim reading and a comic reading, recorded row by row; any row that fails either is
dropped. State when the GM is obliged to roll one, how generated content maps onto
`docs/design/16-session.md` (companion objectives/Tension) and `docs/design/19-campaign.md` /
`docs/design/18-arcs-and-beats.md` (threads/threats), and the setting extension path: `extend:`
(`docs/design/24-authoring-a-setting.md`) gains tables as an extendable kind, alongside its existing
careers/talents/gear/creatures, so a setting can add rows to a prompt table without replacing the
engine's own. Amend `docs/design/04-tables.md`'s existing oracles index row to also link the new
document, and `docs/design/02-architecture.md` / `docs/design/27-tooling.md` if their file-layout mentions
need it.

## Technical Context

**Language/Version**: Markdown design documents; Python 3 for the verification script (matches
existing `tools/*.py` / `specs/*/check_*.py` convention in this repo).

**Primary Dependencies**: None — stdlib only, per existing `check_*.py` scripts in other
`specs/*/` directories.

**Storage**: N/A — this feature produces design prose plus rollable tables, not application state.
No `engine/tables/*.yaml` file, matching every other table family so far — the engine that reads
those files is future work (Stage 13).

**Testing**: `tools/check_oracle_prompts.py` — checks, per table, that every row's range is
contiguous, starts at the family's lowest possible total, and is open at the top
(`docs/design/04-tables.md`'s row-schema rule), and that the document records a grim/comic check for
every row with no row marked as failing either. This is a structural check (row coverage,
duplicate-row detection), not a probability computation — this family's correctness criterion is
qualitative genre-neutrality, not a numeric odds claim (spec Assumptions), so the script's shape
follows `tools/check_bestiary.py`'s structural-validation pattern rather than
`tools/check_oracle_answers.py`'s probability-computation pattern. Plus the repo-wide checks this
change must keep green: `tools/check_docs.py` (reachability) and a grep for setting/system
vocabulary (`CLAUDE.md`).

**Target Platform**: N/A — this repo has no runtime target; it is design documents plus tables
that a future rules engine reads.

**Project Type**: Documentation / design-record change to a single-repo TTRPG engine (`wyrd`).

**Performance Goals**: N/A.

**Constraints**: No setting or system name or borrowed term anywhere in `design/` (`CLAUDE.md`);
no tonal register baked into any row (`docs/adr/0004-tone-belongs-to-the-setting.md`,
`CLAUDE.md`); every row's genre-neutrality check recorded, not merely asserted (`CLAUDE.md`);
design documents rewritten in place, no changelog prose (`CLAUDE.md`).

**Scale/Scope**: One new design document defining a fixed set of prompt families (expected: four,
per the spec's scoped generative gaps), three existing documents amended (`docs/design/04-tables.md`'s
oracles index row, and `docs/design/02-architecture.md` / `docs/design/27-tooling.md` if their filename
mentions go stale), one verification script. No `engine/tables/*.yaml` — consistent with all five
other table families, none of which has one yet.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

This repo has no `.specify/memory/constitution.md`; its governing document is `CLAUDE.md`
(project root). Relevant gates, checked against this plan:

- **Setting-agnostic engine** — no setting/system name in `design/`. Gate: satisfied by design;
  every prompt row is written abstract enough to instantiate in any setting. Verified by grep
  (`quickstart.md`) before this feature is done.
- **Tone is a setting property** (`docs/adr/0004-tone-belongs-to-the-setting.md`) — every row is
  read once grim and once comic before it ships, and the check is recorded in the document, not
  asserted in a sentence. Gate: satisfied by construction — see `data-model.md`'s row-checking
  discipline.
- **Design documents rewritten in place, no changelogs** — `docs/design/04-tables.md`,
  `docs/design/02-architecture.md`, `docs/design/27-tooling.md` are edited to describe the present state
  only.
- **Capability change goes through the Spec Kit cycle, `specs/` committed** — this plan.

No violations requiring the Complexity Tracking table below.

## Project Structure

### Documentation (this feature)

```text
specs/026-oracle-prompt-tables/
├── plan.md                    # This file
├── research.md                # Phase 0 output
├── data-model.md              # Phase 1 output
├── quickstart.md              # Phase 1 output
└── tasks.md                   # Phase 2 output (/speckit-tasks)
```

No `contracts/` — this feature has no external interface (API, CLI surface, wire format); it is a
design document and rollable tables read by the engine's own table-loading rules, already
specified in `docs/design/04-tables.md`.

### Source Code (repository root)

```text
design/
├── 02-architecture.md            # amended only if the oracles file-layout mention goes stale
├── 03a-tables.md                 # amended: oracles index row also links the new document;
│                                  #   "what a setting may replace" gains the extend-a-table path
├── 03a-5-oracle-answers.md       # unchanged — the answer-table sibling this variant sits beside
├── 03a-6-oracle-prompts.md       # new: the prompt families and their tables
├── 07-tooling.md                 # amended only if the oracles file-layout mention goes stale
└── 13-authoring-a-setting.md     # amended: extend: gains tables as an extendable kind,
                                   #   alongside careers/talents/gear/creatures

tools/
└── check_oracle_prompts.py       # new: checks row-range contiguity and grim/comic coverage
```

**Structure Decision**: Follows the pattern set by the five already-defined table families
(`docs/design/05-criticals.md` through `03a-5-oracle-answers.md`, each with a matching
`tools/check_<family>.py`) and mirrors how criticals already holds several variant tables (one per
damage type) under one index row — this feature adds a second variant document under the existing
oracles row rather than a sixth row, per the spec's Clarifications. None of the existing families
has an `engine/tables/*.yaml` file yet (engine implementation is future work, Stage 13), so this
feature does not add one out of step with its siblings.

## Complexity Tracking

No gate violations — table not filled.
