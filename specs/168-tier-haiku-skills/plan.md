# Implementation Plan: Tier the mechanical chronicle skills at Haiku

**Branch**: `431-tier-haiku-skills` | **Spec**: [spec.md](spec.md)

## Summary

Add `model: haiku` frontmatter, plus a one-line stated justification, to `wyrd-character`,
`wyrd-downtime` and `wyrd-end-session` in `wyrd-chronicle-template/.claude/skills/`. No behaviour
changes to any of the three skills' actual steps -- this is frontmatter and documentation only
(FR-007). The change lands as a separate PR in `wyrd-chronicle-template`, since that is the repo
these skill files actually live in; this `wyrd` repo's own PR is the Spec Kit trail, per the
established precedent from #403/#404/#405/#418/#430.

## Technical Context

**Language/Version**: N/A -- YAML frontmatter in a Markdown file, no code.

**Storage**: N/A.

**Testing**: No CI/test harness exists in `wyrd-chronicle-template`. Verification is direct
re-reading of each file's frontmatter and body against FR-001 through FR-007, per spec.md's own
Assumptions.

**Project Type**: Documentation/configuration change to three existing skill files.

## Constitution Check

`.specify/memory/constitution.md` is the unfilled Spec Kit template in this repo -- no
project-specific principles are ratified into it. CLAUDE.md's own rules apply instead: commits
explain why not what; no backticks in commit message bodies; PR title/body per the
pull-requests section. None are violated by a frontmatter-only change.

## Project Structure

```
wyrd-chronicle-template/.claude/skills/
├── wyrd-character/SKILL.md    (frontmatter + one-line justification added)
├── wyrd-downtime/SKILL.md     (frontmatter + justification, addressing FR-005)
└── wyrd-end-session/SKILL.md  (frontmatter + one-line justification added)
```

## Phase 0: Research

No open questions -- the spec's own Assumptions section already resolved the one ambiguity
(whether to pair `model: haiku` with an `effort:` value): omit `effort:` unless a specific skill
needs it, following kord's own `model: haiku` skills' convention of pairing it with nothing.

## Phase 1: Design

No data model, no contracts -- this is a three-line frontmatter addition per file plus one
justification sentence each. The "design" is FR-001 through FR-005's own text.

## Phase 2: Implementation approach

For each of the three files: insert `model: haiku` as a new frontmatter line (after
`disable-model-invocation:`), and add one sentence to the "What this skill does" section (or
immediately after the frontmatter) stating the Haiku-tier justification in `27-tooling.md`'s own
language. `wyrd-downtime`'s justification additionally names the five uncoded Undertakings
explicitly (FR-005).
