# Implementation Plan: Character, downtime and session-close skills

**Branch**: `154-session-close-skills` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/154-session-close-skills/spec.md`

## Summary

This feature spans two repositories, per the Clarifications section of spec.md:

1. **`wyrd` (this repo)** — wire the missing CLI verbs `downtime` (Upkeep, the Undertaking
   choice gate, Mend) and `rally` (recovery, advance award, commit) into
   `engine/wyrd/catalog.py`/`verbs.py`/`client.py`, following the exact wrapper pattern
   #402/PR #407 used for `save`/`recap`/etc. — thin CLI wrappers over the existing pure
   functions in `engine/wyrd/downtime.py` and `rally.py`, adding no new arithmetic.
2. **`wyrd-chronicle-template`** — a separate deliverable (own PR, own repo, no Spec Kit
   substrate there) building the three prompt-level skills
   (`.claude/skills/wyrd-character/SKILL.md`, `wyrd-downtime/SKILL.md`,
   `wyrd-end-session/SKILL.md`) that call the CLI verbs from part 1 (plus the already-existing
   `spend-advance`, `character-load`, `session-context`, `save`, `recap`), presenting the
   player's own choices (Undertaking, Upkeep trade, whether/how to spend an advance) as prose
   decisions and reporting only the numbers those verbs return.

This plan (and `tasks.md`) covers part 1 in full engineering detail, since that is the capability
change this repo's Spec Kit gate applies to. Part 2 is scoped here (its own tasks are listed) but
implemented and delivered as a second PR against `wyrd-chronicle-template`, referencing this same
tracking issue (neilgfoster/wyrd#404) from that repo.

## Technical Context

**Language/Version**: Python 3.11+, standard library only, for part 1 (matches
`engine/wyrd/`). Part 2 is prompt-level Markdown (`SKILL.md` files, per docs/adr/0013) with no
runtime of its own.

**Primary Dependencies**: Part 1 reuses `engine/wyrd/downtime.py`, `rally.py`, `advancement.py`,
`chronicle.py`, `resolution.py` — all already present, no new dependency.

**Storage**: Flat files under a chronicle directory (`chronicle.yaml`, `pc.yaml`, `party.yaml`,
`recap.md`), unchanged storage model (docs/design/22-state.md).

**Testing**: stdlib `unittest` for part 1, matching every existing file under `tests/engine/`
(docs/design/27-tooling.md §6, no pytest). Part 2 has no automated test harness of its own (no
CI in `wyrd-chronicle-template`); its `quickstart.md` documents a manual walkthrough instead.

**Target Platform**: Linux/CLI for part 1. Claude Code, inside a bootstrapped chronicle, for
part 2.

**Project Type**: Single project for part 1 (CLI verbs added to an existing package). Part 2
adds a `.claude/skills/` directory to a repo that has none yet.

**Performance Goals**: N/A — thin CLI plumbing over small in-memory character/chronicle state.

**Constraints**: ruff clean repo-wide (line length 100, rule sets E/F/I/UP, target 3.11) for
part 1; no setting or system names in either part's prose; neither part reimplements arithmetic
an existing pure function already performs (spec.md FR-009).

**Scale/Scope**: Two new CLI verb families (`downtime`, `rally`) in part 1; three `SKILL.md`
files in part 2.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md` (unfilled template in this repo) evaluated against
`CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repository**: part 1 touches only engine code and design
  references already in `wyrd`; no source-text extraction, no setting-specific content. Part 2
  lands in `wyrd-chronicle-template`, not here. Pass.
- **No setting or system names in `docs/design/` or `README.md`**: neither part modifies
  `docs/design/`; verb names (`downtime`, `rally`) and skill names (`wyrd-character`,
  `wyrd-downtime`, `wyrd-end-session`) are all descriptive English already used by
  02-architecture.md/16-session.md, none borrowed from a source system. Pass.
- **Tone is a setting property**: neither part bakes in tone; the CLI verbs return structured
  data, and the skills' own prose stays in the engine's descriptive vocabulary (Undertaking,
  Upkeep, Rally, advance), never a setting's register. Pass.
- **Deterministic over inference**: every numeric outcome in both parts traces to an existing
  pure function's return value (spec.md FR-009, SC-004); no verb or skill infers a number an
  existing function already computes. Pass.
- **Rule changes apply forward only**: this feature adds CLI plumbing and prompt-level skills,
  not a rule change; no history is recomputed. N/A.
- **Design documents rewritten in place; ADRs never edited**: no ADR is touched; no design
  document changes (this feature implements what 02-architecture.md and 16-session.md already
  specify — it does not change their content). Pass.
- **Capability changes go through the Spec Kit cycle**: this plan is exactly that for part 1 —
  `specs/154-session-close-skills/` is committed in `wyrd`. Part 2 is not a `wyrd`-repo
  capability change and `wyrd-chronicle-template` has no Spec Kit substrate installed; this
  spec/plan/tasks set is the design record for both parts. Pass.
- **docs/adr/0013 (engine names no game-mechanic skill)**: the three `SKILL.md` files are
  Claude Code skills (prompt-level instructions), never redefined as a game mechanic of the
  engine's own — the engine's vocabulary (Downtime, Rally, advance) is invoked, not renamed.
  Pass.

No violations requiring the Complexity Tracking table below.

## Project Structure

### Documentation (this feature)

```text
specs/154-session-close-skills/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── cli-verbs.md      # Phase 1 output — part 1's downtime/rally verb contracts
│   └── skills.md          # Phase 1 output — part 2's three SKILL.md contracts
└── tasks.md              # Phase 2 output (/speckit-tasks, not this command)
```

### Source Code (repository root)

```text
# Part 1 — this repo (wyrd)
engine/wyrd/
├── catalog.py         # TOOLS registry — add downtime/rally verb entries (this feature)
├── client.py           # argparse dispatch built from TOOLS — add subparsers + _run_* (this feature)
├── verbs.py             # thin wrapper functions the CLI calls — add downtime/rally wrappers (this feature)
├── downtime.py           # existing pure functions, reused unchanged
├── rally.py               # existing pure functions, reused unchanged
└── advancement.py          # existing: award_advance, reused by the rally wrapper

tests/engine/
├── test_verbs.py       # extend: one test class per new verb
└── test_client.py        # extend if this file exists; else covered via test_verbs.py + a CLI smoke test

# Part 2 — a different repo (wyrd-chronicle-template), delivered as a separate PR there
.claude/skills/
├── wyrd-character/SKILL.md
├── wyrd-downtime/SKILL.md
└── wyrd-end-session/SKILL.md
```

**Structure Decision**: Part 1 is a single project, extending the existing `engine/wyrd/`
package and its `tests/engine/` suite in place — no new top-level directory, matching how
#402/PR #407 added the chronicle-level verbs. Part 2 introduces `.claude/skills/` to
`wyrd-chronicle-template`, a directory that repo does not have yet; its own plan/tasks entries
here document the shape without committing code to this repo.

## Complexity Tracking

*No Constitution Check violations — table intentionally empty.*
