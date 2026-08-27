# Implementation Plan: Name the shared scarce-resource-plus-counterweight pattern

**Branch**: `182-shared-counterweight-pattern` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add a short passage to `03-rules.md`, right after the track table, stating that Taint/Resolve
and Fate/Fortune are the same mechanism — a scarce/permanent resource paired with a renewable
counterweight — applied to two different domains, rather than two coincidentally similar pairs.
No mechanical change.

## Technical Context

**Language/Version**: N/A — documentation-only.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Must not alter either pair's existing mechanics (FR-003).

**Scale/Scope**: One new passage in `03-rules.md`.

## Constitution Check

- **No ADR** — states an existing pattern, makes no design decision. PASS.
- **Design documents rewritten in place** — added at the natural point in `03-rules.md`'s
  existing structure. PASS.
- **No setting or system names** — none introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/063-shared-counterweight-pattern/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/03-rules.md   # new passage after the track table
```

## Complexity Tracking

*(empty — no constitution violations)*
