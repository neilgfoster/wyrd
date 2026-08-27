# Implementation Plan: Clarify the difficulty ladder's asymmetry and the untrained-attempt table's stacked bonuses

**Branch**: `045-difficulty-ladder-clarity` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add a short rationale paragraph after `docs/design/03-rules.md`'s difficulty ladder explaining its
one-step-up/four-steps-down asymmetry, grounded in text already present in the same document
("only roll when it is dramatic", the Declaration table's "no roll" row). Rework the
untrained-attempt table to show Base/Difficulty/Declaration contributions as separate columns
instead of one combined figure. No modifier values change.

## Technical Context

**Language/Version**: N/A — Markdown design document only

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (checked
for a false-positive Title Case trigger from the new prose, found and fixed one: "Below Average"
read as a capitalized mechanic name — reworded), arithmetic of the reworked table checked by hand
(Base + Difficulty + Declaration = At, every row).

**Constraints**: No modifier value changes (FR-003). No new mechanism.

**Scale/Scope**: Two short additions to `docs/design/03-rules.md`, one table reworked.

## Constitution Check

- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — inserted at the natural point, table reworked in
  place, no changelog note. PASS.
- **No ADR needed** — no rule value changes, no alternative rejected. PASS.
- **Deterministic over inference** — dangling-mechanic check run and a false positive caught and
  fixed; table arithmetic checked by hand rather than trusted. PASS.

No violations.

## Project Structure

```text
specs/045-difficulty-ladder-clarity/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md

docs/design/03-rules.md   # asymmetry rationale + reworked untrained-attempt table
```

## Complexity Tracking

*(empty — no constitution violations)*
