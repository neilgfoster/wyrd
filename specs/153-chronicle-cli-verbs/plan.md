# Implementation Plan: Chronicle CLI Verbs

**Branch**: `153-chronicle-cli-verbs` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/153-chronicle-cli-verbs/spec.md`

## Summary

Wire the eleven chronicle-level CLI verbs docs/design/02-architecture.md lists
(`session-context`, `get`, `find`, `party`, `threads`, `threats`, `log`, `save`/`load`/
`validate`, `recap`, `advance-time`, `threat-check`; `doctor`/`optimise` deferred) into
`engine/wyrd/catalog.py`'s `TOOLS` registry and `client.py`'s dispatch, following the
`find-noun`/`find-rule`/`find-table` pattern from #397/PR #398. Research (research.md) found
that most of the underlying logic already exists as pure functions in `loadtier.py`,
`entity.py`, `threat.py`, `advance_time.py`, `party.py`, and `state.py` — this feature adds
thin `verbs.py` wrappers over them, plus a small number of genuinely new pure functions where
no existing one covers a verb (`find`'s general filter, the full `threads` query, and the
`log` reader/writer, since `log/` has no reader today).

## Technical Context

**Language/Version**: Python 3.11+, standard library only (matches the rest of `engine/wyrd/`).

**Primary Dependencies**: None beyond the existing `wyrd` package modules this feature wires
together (`session`, `chronicle`, `state`, `era`, `thread`, `threat`, `entity`, `loadtier`,
`advance_time`, `party`).

**Storage**: Flat files under a chronicle directory (`chronicle.yaml`, `setting/`, `overlay/`,
`entities/`, `log/`, `recap.md`) — unchanged storage model, per docs/design/22-state.md.

**Testing**: stdlib `unittest`, no pytest (docs/design/27-tooling.md §6), matching every
existing file under `tests/engine/`.

**Target Platform**: Linux/CLI, same as the rest of the `wyrd` engine.

**Project Type**: Single project — CLI verbs added to an existing package (`engine/wyrd/`).

**Performance Goals**: N/A — this feature is CLI plumbing over small, in-memory entity sets;
no new performance-sensitive path is introduced.

**Constraints**: ruff clean repo-wide (line length 100, rule sets E/F/I/UP, target 3.11); no
setting or system names in `docs/design/`; each verb reuses existing pure functions where one
exists (spec.md FR-014).

**Scale/Scope**: Eleven CLI verbs, thin wrappers plus a handful of small new pure functions
(`find`'s filter, full `threads` query, `log` read/write) — no new subsystem.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, evaluated against `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repository**: this feature touches only engine code and
  design references already in this repo; no source-text extraction or setting-specific content
  is added. Pass.
- **No setting or system names in `docs/design/` or `README.md`**: this feature does not modify
  `docs/design/` (it implements what 02-architecture.md, 16-session.md, 19-campaign.md,
  22-state.md, 28-maintenance.md already specify); verb names (`session-context`, `get`, `find`,
  `party`, `threads`, `threats`, `log`, `save`/`load`/`validate`, `recap`, `advance-time`,
  `threat-check`) are all descriptive English, none borrowed from a source system. Pass.
- **Tone is a setting property**: none of these verbs bake in tone; they return structured data,
  never player-facing prose (spec.md FR-012). Pass.
- **Deterministic over inference**: `advance-time` and `threat-check` both draw dice via the
  existing seeded `rules.roll_d100`/dice tool, reproducible from a given seed — no verb infers a
  result an existing deterministic function could compute. Pass.
- **Rule changes apply forward only**: this feature adds CLI plumbing, not a rule change; no
  history is recomputed. N/A.
- **Design documents rewritten in place; ADRs never edited**: no ADR is touched; no design
  document changes (this feature implements existing design, it does not change it). If a design
  document turns out to need a correction during implementation, it will be edited in place, not
  changelog-appended. Pass (no violation anticipated).
- **Capability changes go through the Spec Kit cycle**: this plan is exactly that — `specs/153-
  chronicle-cli-verbs/` is committed. Pass.

No violations requiring the Complexity Tracking table below.

## Project Structure

### Documentation (this feature)

```text
specs/153-chronicle-cli-verbs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/
│   └── cli-verbs.md      # Phase 1 output
└── tasks.md              # Phase 2 output (/speckit-tasks, not this command)
```

### Source Code (repository root)

```text
engine/wyrd/
├── catalog.py        # TOOLS registry — add 11 new entries (this feature)
├── client.py          # argparse dispatch built from TOOLS — add per-verb subparsers + _run_* (this feature)
├── verbs.py            # thin wrapper functions the CLI calls — add 11 new functions (this feature)
├── loadtier.py         # existing: always_tier, lookup, generate_recap, recap_close_step (reused)
├── entity.py            # existing: resolve_entity, load_set (reused)
├── threat.py             # existing: active_threats, check_activation (reused)
├── advance_time.py        # existing: advance_time (reused)
├── party.py                # existing: roster (reused)
├── state.py                 # existing: save_chronicle, load_chronicle, validate_chronicle (reused)
└── log.py                    # NEW: log entry read (--last/--since) and append, per research.md

tests/engine/
├── test_verbs.py       # extend: one test class per new verb
├── test_loadtier.py     # extend: session-context/get/recap coverage if the wrapper logic warrants it
├── test_threat.py        # extend: threat-check coverage
├── test_advance_time.py   # extend: advance-time verb-level coverage
└── test_log.py             # NEW: log.py's own read/append functions
```

**Structure Decision**: Single project, extending the existing `engine/wyrd/` package and its
`tests/engine/` suite in place — no new top-level directory. This matches how #397/PR #398 added
`find-noun`/`find-rule`/`find-table` and every other verb this repo has added to `catalog.py`.

## Complexity Tracking

*No Constitution Check violations — table intentionally empty.*
