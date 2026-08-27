# Implementation Plan: Review all playtest findings and resolve outstanding gaps

**Branch**: `055-playtest-findings-synthesis` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Extend `docs/design/30-playtest-transcript.md` with a new "The playtest epic's findings,
reviewed together" section: a table of every distinct finding from §6–§12's Findings
subsections with its live-verified tracking status, and two named recurrences (the Resolve gap,
identical, found independently in §8 and §10; and a thematic recurrence between #163 and #167,
both instances of "no pacing limit on repeated spend"). Cross-references added to #163 and #167
as GitHub comments. No design decision made — #155, #163 and #167 remain open for their own
resolution.

## Technical Context

**Language/Version**: N/A — Markdown design document only; no roll-generation script (this
feature reviews, it does not play).

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Every finding's tracked-issue status verified against live GitHub state
(FR-002), not assumed. No design decision made for #155/#163/#167 (FR-004). No playtest content
re-run or re-derived (FR-005).

**Scale/Scope**: One new ~50-line section in `docs/design/30-playtest-transcript.md`, two
GitHub-comment cross-references.

## Constitution Check

- **Nothing unpublishable** — a synthesis of already-published playtest content. PASS.
- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — the new section is appended to the existing document
  structure. PASS.
- **No ADR in this feature** — no design decision is made; #155/#163/#167 each retain their own
  path to an ADR if their eventual resolution needs one. PASS (per spec.md Assumptions).
- **Deterministic over inference** — every issue's status is checked live (`gh issue view`), not
  assumed from memory of the playtest prose. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/055-playtest-findings-synthesis/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 13
```

## Complexity Tracking

*(empty — no constitution violations)*
