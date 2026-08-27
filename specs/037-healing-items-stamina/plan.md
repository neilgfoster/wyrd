# Implementation Plan: Healing items have no mechanical effect on Stamina

**Branch**: `037-healing-items-stamina` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/037-healing-items-stamina/spec.md`

## Summary

Close issue #120 by stating explicitly, in `docs/design/03-rules.md`'s Stamina recovery section,
that a consumable healing item has no mechanical effect on Stamina — recovery stays entirely on
the Rally/downtime/Mend clocks ADR 0020 established. Documentation-only: no new mechanism, no
code, no schema.

## Technical Context

**Language/Version**: N/A — Markdown design document only

**Primary Dependencies**: N/A

**Storage**: N/A

**Testing**: `python3 tools/check_docs.py` (reachability/link policy — the document already exists
and is reachable, so this just needs to keep passing) and a manual grep for `check_docs.py`'s
mechanic-name check to confirm no new vocabulary is introduced for the dangling-mechanic check to
trip on.

**Target Platform**: N/A

**Project Type**: Documentation change to an existing design document

**Performance Goals**: N/A

**Constraints**: Must not introduce a new mechanic name, clock, or item-effect vocabulary (spec
FR-004). Must sit in `docs/design/03-rules.md` next to the existing Stamina recovery rule, not in
a new document.

**Scale/Scope**: One paragraph added to one existing document.

## Constitution Check

No `.specify/memory/constitution.md` exists in this repo; the repo's own CLAUDE.md is the
governing document instead. Relevant constraints and how this plan satisfies them:

- **The engine is setting-agnostic** — the new text names no setting, no source-system item, and
  no genre-specific flavour; it states a mechanical position only. PASS.
- **Design documents are rewritten in place, always describing the present** — the addition is
  inserted into the existing Stamina recovery prose, not appended as a changelog note. PASS.
- **Deterministic over inference** — `tools/check_docs.py` is run after the edit to verify
  reachability/link policy rather than assuming it. PASS.
- **No ADR is warranted**: the decision does not reject a workable alternative that would have
  produced a different engine — ADR 0020 already made the substantive call (no new cadence); this
  closes a silent gap in its documentation, it doesn't reopen or re-litigate the decision. This
  matches the issue's own Definition of Done ("documentation-only design decision unless a
  mechanism is chosen").

No violations. No Complexity Tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/037-healing-items-stamina/
├── plan.md              # This file
├── spec.md              # Feature spec
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

No source tree changes. The only file touched outside `specs/` is:

```text
docs/design/03-rules.md   # Stamina recovery section gains one explicit paragraph
```

## Complexity Tracking

*(empty — no constitution violations)*
