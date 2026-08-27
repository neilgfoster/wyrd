# Implementation Plan: 03-rules.md introduces engine-wide values before first use

**Branch**: `044-rules-intro-terminology` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add a short intro block to `docs/design/03-rules.md`, between the existing "Naming rule" note and
`## 1. Resolution`, defining Skill and Stamina at the minimum depth needed to make `skill%`
comprehensible on first read, pointing to `10-the-character.md` for full detail, and stating the
engine-fixed/setting-data split for both — plus a one-line note that the same split applies to
every label in the existing rename table above it.

## Technical Context

**Language/Version**: N/A — Markdown design document only

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`; new text
checked directly against `10-the-character.md`'s "What a character carries" table and
`11-character-creation.md`'s retune note for consistency (not assumed).

**Constraints**: No duplication of `10-the-character.md`'s full definitions (FR-004). No ADR
(documentation-ordering fix, no alternative rejected).

**Scale/Scope**: One ~15-line addition to `docs/design/03-rules.md`.

## Constitution Check

- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — inserted at the natural point in the existing
  structure, no changelog note. PASS.
- **No ADR needed** — no alternative rejected (per spec.md Assumptions). PASS.
- **Deterministic over inference** — consistency checked directly against
  `10-the-character.md`/`11-character-creation.md`, not assumed. PASS.

No violations.

## Project Structure

```text
specs/044-rules-intro-terminology/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md

docs/design/03-rules.md   # new intro block, before ## 1. Resolution
```

## Complexity Tracking

*(empty — no constitution violations)*
