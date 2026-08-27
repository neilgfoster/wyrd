# Implementation Plan: Define the register tone field in 01-principles.md

**Branch**: `041-register-tone-field` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add a `register` row to `docs/design/01-principles.md`'s "What each means to the engine" table,
consistent with `24-authoring-a-setting.md`'s existing worked-example description of the field (a
one-line pointer to `voice.md`), and explicitly note it is descriptive rather than enforced —
unlike every other tone field, the engine refuses nothing on `register`'s account.

## Technical Context

**Language/Version**: N/A — Markdown design document only

**Testing**: `python3 tools/check_docs.py` and `python3 tools/check_dangling_mechanics.py`

**Constraints**: No new mechanism (FR-003); consistent with `24-authoring-a-setting.md`'s existing
description (FR-002), not a new, potentially divergent one.

**Scale/Scope**: One table row.

## Constitution Check

- **No setting or system names** — the new row names no setting. PASS.
- **Design documents rewritten in place** — inserted into the existing table, no changelog note.
  PASS.
- **No ADR needed** — no alternative rejected; `register`'s meaning already existed in
  `24-authoring-a-setting.md`, this only documents it where the rest of the tone contract lives.
  PASS (per spec.md Assumptions).
- **Deterministic over inference** — `check_docs.py`/`check_dangling_mechanics.py` run rather than
  assumed. PASS.

No violations.

## Project Structure

```text
specs/041-register-tone-field/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md

docs/design/01-principles.md   # one new table row
```

## Complexity Tracking

*(empty — no constitution violations)*
