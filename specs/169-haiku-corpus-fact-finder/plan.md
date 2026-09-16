# Implementation Plan: Haiku corpus fact-finder subagent for create-setting

**Branch**: `169-haiku-corpus-fact-finder` | **Date**: 2026-09-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/169-haiku-corpus-fact-finder/spec.md`

## Summary

Add the first real `.claude/agents/` subagent definition to `wyrd-setting-template` — a
`model: haiku` subagent scoped to one closed retrieval task: given a claim and a corpus
file/directory, return the exact supporting or contradicting quote and its source location, or
report that none exists. Update `create-setting`'s own `SKILL.md` to declare `model: sonnet` and
rewrite Phase 3's grounding steps and Phase 4's grep-verification step to invoke that subagent
instead of reading/searching `corpus/` inline, while leaving every prose-writing and
register/content-judgement step on the invoking Sonnet-tier skill. This is the design/spec side
of the change: the artefacts land in this repo (`wyrd`), the actual files change in
`wyrd-setting-template`, matching the established split for prior features in this family
(#403/#404/#405/#418/#430/#431).

## Technical Context

**Language/Version**: Markdown (SKILL.md/agent-definition frontmatter + prose); no code

**Primary Dependencies**: Claude Code's own subagent-definition mechanism (`.claude/agents/*.md`
frontmatter: `name`, `description`, `tools`, `model`), confirmed against real examples at
`/root/.claude/plugins/marketplaces/claude-plugins-official/plugins/*/agents/*.md`

**Storage**: N/A — no state, no database; the subagent reads `corpus/*.txt` files already on disk
in a setting repo

**Testing**: Manual re-read of the full updated `create-setting` Phase 3/4 flow against the new
structure (`wyrd-setting-template` has no CI/test suite), plus a manual dry run of one
corpus-fact-finding lookup against a real setting's `corpus/` text where feasible

**Target Platform**: Claude Code sessions operating on a `wyrd-setting-*` repository

**Project Type**: Documentation/skill-definition change (no source code, no build)

**Performance Goals**: N/A — not a performance-sensitive feature

**Constraints**: Nothing unpublishable enters `wyrd` (this repo) — the subagent definition and
skill rewrite themselves contain no setting-specific or copyrighted material, only mechanism. The
actual capability change lands in `wyrd-setting-template`, a template repo with no CI.

**Scale/Scope**: One new agent-definition file, one rewritten `SKILL.md` (frontmatter + two
phases), in one repository outside this one.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository** — this spec, plan, and its artefacts describe
  a mechanism (subagent delegation) and reference no setting-specific or copyrighted content.
  PASS.
- **No setting or system names in `design/`/`README.md`** — not touched by this change; the
  subagent definition and skill live in `wyrd-setting-template`, not under `docs/design/`. PASS.
- **Anything with a correct answer is computed, not inferred** — the subagent's whole point is to
  turn an inline, unverifiable Sonnet-tier corpus search into a checkable retrieval call with a
  right answer (the quote exists verbatim or it doesn't), consistent with
  [`docs/design/27-tooling.md`](../../docs/design/27-tooling.md) section 5's own tiering table,
  which already named this exact delegation shape without ever building it. PASS.
- **Capability changes go through the Spec Kit cycle** — this spec/plan/tasks trail is exactly
  that, even though the capability itself lands in a different repository. PASS.

No violations; Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/169-haiku-corpus-fact-finder/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks — not created here)
```

No `contracts/` directory: this feature has no API surface in this repository. The subagent
definition's own frontmatter *is* the interface it exposes, and that lives in
`wyrd-setting-template`, documented in `data-model.md` below instead of a separate contracts
directory, since it is a single Markdown file's shape rather than a machine-checked schema.

### Source Code (repository root)

This repository (`wyrd`) receives no source-code change — only this `specs/` documentation
trail. The actual change lands in a sibling checkout:

```text
wyrd-setting-template/
├── .claude/
│   ├── agents/
│   │   └── corpus-fact-finder.md      # new — model: haiku subagent definition
│   └── skills/
│       └── create-setting/
│           └── SKILL.md               # rewritten — model: sonnet frontmatter,
│                                       # Phase 3/4 delegate to corpus-fact-finder
```

**Structure Decision**: Documentation-only in `wyrd`; the capability itself is a single new file
(`wyrd-setting-template/.claude/agents/corpus-fact-finder.md`) plus a targeted rewrite of one
existing file (`wyrd-setting-template/.claude/skills/create-setting/SKILL.md`). No new
directories beyond `.claude/agents/`, which is the first of its kind in any wyrd repository (per
the issue's own framing).

## Complexity Tracking

Not applicable — no Constitution Check violations.
