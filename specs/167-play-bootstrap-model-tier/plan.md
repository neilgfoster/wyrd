# Implementation Plan: Tier /wyrd-play and /wyrd-bootstrap at Sonnet, with effort decided per skill

**Branch**: `167-play-bootstrap-model-tier` | **Date**: 2026-09-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/167-play-bootstrap-model-tier/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `model: sonnet` plus a deliberately-chosen, written-justified `effort:` value to the
frontmatter of `wyrd-chronicle-template/.claude/skills/wyrd-play/SKILL.md` and
`wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md`. No behavioural or CLI-contract
change: this is a frontmatter-and-prose-only edit to two already-shipped skill files, made in the
repository that owns them (`wyrd-chronicle-template`), following the same repo-split precedent
established by wyrd#403/#404/#405/#418 (Spec Kit cycle runs in `wyrd`, where the substrate is
installed; the capability itself lands in `wyrd-chronicle-template`).

The effort-level decision for each skill is the one piece of actual "design" work this plan does:
weigh each skill's own steps (already read in full against `docs/design/27-tooling.md` section 5)
into mechanical-vs-judgement categories, and pick the tier that keeps the judgement-heavy majority
of the skill running at full reasoning depth, per §5's explicit "that is the one place not to
economise" stance.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: N/A -- this feature edits YAML frontmatter and Markdown prose inside two
existing `SKILL.md` files; no source code is added or changed.

**Primary Dependencies**: N/A.

**Storage**: N/A.

**Testing**: N/A -- `wyrd-chronicle-template` has no CI or automated tests (confirmed in
wyrd#430's own Definition of Done). Verification is manual: re-read both updated skill files in
full and confirm the frontmatter and justification prose meet spec.md's functional requirements.

**Target Platform**: Claude Code (the harness that reads a `SKILL.md`'s `model:`/`effort:`
frontmatter to select which model and reasoning-effort tier runs an invocation).

**Project Type**: Documentation / configuration change to two Claude Code skill definitions.

**Performance Goals**: N/A.

**Constraints**: Sonnet is a hard ceiling for both skills -- `model: opus` must never appear.
`effort:` must be an explicit, justified value -- never left unset, never silently defaulted to
the lowest tier.

**Scale/Scope**: Exactly two files, in one other repository (`wyrd-chronicle-template`); no other
skill's tiering changes as part of this feature (epic wyrd#429's remaining skills are separate,
later work).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` in this repo is the unfilled Spec Kit template (no project-
specific principles have been ratified into it) -- there are no constitution-derived gates to
check here. The controlling ground rules for this feature are `wyrd`'s own `CLAUDE.md` (engine
repo conventions: ADRs, PR shape, ruff cleanliness) and `docs/design/27-tooling.md` section 5
(model tiering), both of which this plan and the spec already reason against directly. No
violation to record.

## Project Structure

### Documentation (this feature)

```text
specs/167-play-bootstrap-model-tier/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

`data-model.md` and `contracts/` are omitted: this feature introduces no data entities and no
interface contract (it is a frontmatter/prose edit to two existing skill files, not a new API,
CLI verb, or schema).

### Source Code (repository root)

This feature makes no change to `wyrd`'s own source tree (`engine/`, `tools/`, `tests/`). The
actual edit lands in a different repository entirely:

```text
wyrd-chronicle-template/
└── .claude/
    └── skills/
        ├── wyrd-play/
        │   └── SKILL.md        # add model:/effort: frontmatter + justification prose
        └── wyrd-bootstrap/
            └── SKILL.md        # add model:/effort: frontmatter + justification prose
```

**Structure Decision**: Single-project structure does not apply -- there is no `src/`/`tests/`
split to choose between, because this feature edits two existing Markdown files in place. The
only "structure" decision is the repo split itself (spec/plan/tasks trail in `wyrd`, capability in
`wyrd-chronicle-template`), which is fixed precedent from wyrd#403/#404/#405/#418, not a fresh
choice made by this plan.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations recorded -- table omitted.
