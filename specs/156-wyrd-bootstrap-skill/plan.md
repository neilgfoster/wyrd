# Implementation Plan: Wyrd bootstrap skill

**Branch**: `156-wyrd-bootstrap-skill` | **Date**: 2026-09-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/156-wyrd-bootstrap-skill/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a `/wyrd-bootstrap` Claude Code skill — `.claude/skills/wyrd-bootstrap/SKILL.md` in the
**wyrd-chronicle-template** repository, not this one — that a player runs once, immediately
after the chronicle's deterministic `./bootstrap` script. It completes the interpretation half
that script's own docstring defers: character creation (via the engine's `create-character` CLI
verb), choosing an opening situation from the recorded intent, seeding at least one Threat with
a stated personal connection into `overlay/`, writing the assembled state via the `save` CLI
verb, and making the first commit. No engine code changes: this feature is prose/skill-authoring
that calls existing, already-merged CLI verbs (`create-character` in this repo's
`engine/wyrd/`, and `save`/`load`/`validate` from #402). The only artefact this repository
(`wyrd`) commits is the Spec Kit trail itself (`specs/156-wyrd-bootstrap-skill/`); the skill file
lands as a separate PR against `wyrd-chronicle-template`.

## Technical Context

**Language/Version**: Markdown (Claude Code `SKILL.md` prose + embedded bash/Python
invocations), Python 3.11 for the engine CLI it calls

**Primary Dependencies**: `engine/wyrd/client.py`'s existing verbs (`create-character`, `save`,
`load`, `validate`) — no new engine code

**Storage**: chronicle-repo files (`chronicle.yaml`, `chronicle.yaml.json`, `pc.yaml`,
`overlay/*.md`, `entities/*.md`) — no database

**Testing**: manual quickstart walkthrough against a real bootstrapped chronicle (darkfuture or
titan setting), since `wyrd-chronicle-template` has no `.kord/`/automated-check substrate of its
own; this repo's `pyproject.toml` ruff gate applies only if any engine-repo file changes, which
this feature is not expected to require

**Target Platform**: Claude Code, invoked inside a `wyrd-chronicle-*` repository

**Project Type**: single skill-authoring change in a sibling repository (`wyrd-chronicle-template`)

**Performance Goals**: N/A — a one-time, human-paced interview and a handful of CLI calls

**Constraints**: must call existing CLI verbs rather than reimplementing any mechanic (issue
#403's own DoD); must not bake a setting/system name into the skill's own prose (CLAUDE.md); must
follow the file-location and CLI-discovery conventions the three precedent skills
(`/wyrd-character`, `/wyrd-downtime`, `/wyrd-end-session`) already established

**Scale/Scope**: one new file (`SKILL.md`) in `wyrd-chronicle-template`, exercised once per
chronicle

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, the check is against `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repository** — satisfied: this repository's own change is
  the Spec Kit trail only (no source text, no setting content). The skill file itself, landing in
  `wyrd-chronicle-template`, is prose the feature's own author writes and contains no extracted
  copyrighted material.
- **No setting or system names in `docs/design/` or `README.md`** — satisfied: this plan touches
  neither. The skill's own prose (in the other repo) is required by the spec (FR-012) to name no
  setting beyond what it reads from the chosen setting at bootstrap time.
- **Tone is a setting property** (ADR 0004) — satisfied: the skill reads `intent.lethality` and
  the setting's own tables; it invents no register of its own.
- **Anything with a correct answer is computed, not inferred** (ADR 0005) — satisfied: every
  mechanical number (skill percentages, Fate, Stamina) is required (FR-004) to come verbatim from
  `create-character`'s return value, matching the precedent skills' own "Never" sections.
- **Capability changes go through the Spec Kit cycle, with `specs/<feature>/` committed** —
  satisfied by this very plan; `specs/156-wyrd-bootstrap-skill/` is committed to this repo even
  though the shipped capability lands in `wyrd-chronicle-template`, per the task's own instruction
  to run the gate from here.
- **ADR 0013 (the engine names no game-mechanic skill)** — satisfied: FR-012 requires the skill's
  own prose not to blur "Claude Code skill" with the engine's mechanic vocabulary.

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/156-wyrd-bootstrap-skill/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

This feature's actual shipped artefact is **not** in this repository. It lands as a single new
file in a sibling repository:

```text
# wyrd-chronicle-template (separate repo, separate PR)
.claude/skills/wyrd-bootstrap/
└── SKILL.md              # the feature's entire deliverable
```

This repository (`wyrd`) commits only the Spec Kit trail above — no `src/`, no `tests/` tree
changes are expected, since `create-character`/`save`/`load`/`validate` already exist and are
called, not modified.

**Structure Decision**: single skill file in `wyrd-chronicle-template/.claude/skills/
wyrd-bootstrap/SKILL.md`, following the same location and one-file-per-skill shape as
`/wyrd-character`, `/wyrd-downtime`, and `/wyrd-end-session` in that same repository.

## Complexity Tracking

*No violations — table not needed.*
