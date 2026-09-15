# Implementation Plan: The /wyrd-play skill

**Branch**: `157-wyrd-play-skill` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/157-wyrd-play-skill/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Author `/wyrd-play` as a Claude Code skill (`SKILL.md`) in `wyrd-chronicle-template`, following
the same conventions the four existing chronicle skills already establish
(`wyrd-character`, `wyrd-downtime`, `wyrd-end-session`, `wyrd-bootstrap`). It is prompt-level
instructions only -- no engine code changes -- that: (1) loads the Always-loaded memory tier via
`session-context`, resuming a `pending` marker if one exists; (2) orients the player in prose;
(3) runs one beat, calling `propose`/`commit`/`discard`, `opposed-test`, `track`,
`declaration-bonus`, `advance-time`, and `threat-check` for every mechanical step, narrating
only from their returned results; (4) closes the beat with a `rally` call and a `save`,
persisting before narrating, or writes a `pending` marker if the player must stop mid-beat.

## Technical Context

**Language/Version**: Markdown (Claude Code `SKILL.md` prompt instructions) + the shell/Python
invocations it documents (Python 3.11+, matching the engine's own target)

**Primary Dependencies**: The `wyrd` engine CLI (`python3 -m wyrd.client <verb>`), already
vendored into a bootstrapped chronicle at `engine/wyrd/` -- no new dependency

**Storage**: Chronicle YAML/Markdown files under a bootstrapped chronicle repo
(`chronicle.yaml`, `pc.yaml`, `overlay/`, `entities/`, `recap.md`) -- no new storage

**Testing**: A `quickstart.md`-style manual walkthrough against a real bootstrapped chronicle
(the setting-agnostic engine has no automated end-to-end test harness for a Claude Code skill's
own prose instructions; the four sibling skills use the same verification approach)

**Target Platform**: Claude Code, invoked from within a `wyrd-chronicle-*` repository

**Project Type**: Documentation/prompt artifact (a Claude Code skill) in a separate repository
(`wyrd-chronicle-template`) from the engine repository that hosts this Spec Kit cycle

**Performance Goals**: N/A (no runtime performance target; a single invocation runs one beat)

**Constraints**: Every mechanical number reported must trace verbatim to an existing engine CLI
verb's return value (FR-007); no engine or setting vocabulary invented in the skill's own prose
(FR-013); no option menus or exposed engine scaffolding (FR-005, FR-006)

**Scale/Scope**: One new file (`wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md`); no
engine code changes, since #402's chronicle-level verbs and #403's `/wyrd-bootstrap` are already
merged prerequisites

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, the Constitution Check is evaluated against `CLAUDE.md`
and the accepted ADRs, not a separate principle list:

- **Nothing unpublishable enters this repository** -- N/A: this feature adds no content to the
  `wyrd` engine repo beyond `specs/157-wyrd-play-skill/`; the skill file itself lands in
  `wyrd-chronicle-template`, a template repo, and contains no setting-specific or copyrighted
  material.
- **No setting or system names in `design/` or `README.md`** -- satisfied: this plan and the
  skill it describes name no setting; `SKILL.md`'s own prose reads voice/tone from whatever
  setting a chronicle was bootstrapped against, never bakes one in (FR-013).
- **Tone is a setting property, never baked into a mechanic** -- satisfied: the skill's
  orientation/narration prose is deliberately setting-agnostic; register comes from the
  chronicle's own `voice.md`/tone contract at invocation time.
- **Anything with a correct answer is computed, not inferred** -- satisfied: FR-007/FR-009
  require every roll, degree of success, threshold, and mutation to trace to an existing CLI
  verb's own return value; the skill never recomputes one in prose (mirrors the four sibling
  skills' own "Never" sections).
- **Rule changes apply forward only; history is never recomputed** -- N/A: no rule changes.
- **Design documents describe the present** -- N/A: no `docs/design/` document is being
  edited by this feature (the skill's behaviour is already specified by `16-session.md` and
  `02-architecture.md`, unchanged by this plan).
- **Capability changes go through the Spec Kit cycle, with `specs/<feature>/` committed** --
  satisfied: this is exactly that cycle, and `specs/157-wyrd-play-skill/` is committed
  alongside the skill file.

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/157-wyrd-play-skill/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

This feature's actual deliverable lives in a **different** repository from the one hosting this
Spec Kit cycle -- `wyrd-chronicle-template`, not `wyrd` -- per CLAUDE.md's repository table
(chronicle-level skills belong in the chronicle template, not the engine repo) and this issue's
own instruction to keep the tracking/spec side in `wyrd` while the file changes land in
`wyrd-chronicle-template`.

```text
# wyrd-chronicle-template (separate repository; not this one)
.claude/
└── skills/
    ├── wyrd-bootstrap/SKILL.md      # existing sibling skill (reference for conventions)
    ├── wyrd-character/SKILL.md      # existing sibling skill (reference for conventions)
    ├── wyrd-downtime/SKILL.md       # existing sibling skill (reference for conventions)
    ├── wyrd-end-session/SKILL.md    # existing sibling skill (reference for conventions)
    └── wyrd-play/SKILL.md           # NEW -- this feature's deliverable
```

**Structure Decision**: A single new `SKILL.md` file under
`wyrd-chronicle-template/.claude/skills/wyrd-play/`, following the exact directory shape and
internal conventions (CLI-location snippet, JSON-parsing discipline, a final "Never" section)
the four existing sibling skills already use. No engine code changes in the `wyrd` repository;
this repository's changes are limited to the Spec Kit artifacts under `specs/157-wyrd-play-skill/`.

## Complexity Tracking

*No Constitution Check violations -- this section is not needed.*
