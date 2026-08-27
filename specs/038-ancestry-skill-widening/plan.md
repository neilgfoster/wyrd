# Implementation Plan: Ancestry widens creation's skill pool, never its budget

**Branch**: `038-ancestry-skill-widening` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/038-ancestry-skill-widening/spec.md`

## Summary

Close issue #121 by recording ADR 0040 (ancestry is optional setting-declared data that widens
creation's eligible skill pool to the union of the starting career's list and the ancestry's list,
with no additional advances and no stat modifier) and folding its statement into
`docs/design/05-character-creation.md` §3, next to the existing 8-advances rule. Documentation-only:
no code, schema, or entity-model change in this repository, since career/skill data lives in
`wyrd-setting-*` repositories, not here.

## Technical Context

**Language/Version**: N/A — Markdown design documents only

**Primary Dependencies**: N/A

**Storage**: N/A

**Testing**: `python3 tools/check_docs.py` (reachability, ADR indexing, link policy) and
`python3 tools/check_dangling_mechanics.py` (no new unexplained mechanic name).

**Target Platform**: N/A

**Project Type**: Documentation change — one new ADR, one edit to an existing design document

**Performance Goals**: N/A

**Constraints**: Must not change the 8-advance figure `check_creation.py`/`check_advancement.py`
already compute against (spec FR-003, SC-004). Must not introduce a new mechanism beyond a second
skill-list source feeding the existing doors (FR-006).

**Scale/Scope**: One new ADR (~80 lines), one new subsection in `05-character-creation.md` §3.

## Constitution Check

No `.specify/memory/constitution.md` exists; this repo's CLAUDE.md governs instead.

- **The engine is setting-agnostic** — "ancestry" is descriptive English, not a term borrowed from
  a source system; no setting or species name appears. PASS.
- **Decisions are recorded** — a real alternative (no differentiation; a separate ancestry budget)
  is rejected, and the question would plausibly be re-asked, so ADR 0040 is written (per this
  repo's own two-part test for when a decision earns a record). PASS.
- **Design documents are rewritten in place** — the new text sits inside `05-character-creation.md`
  §3's existing prose, not appended as a changelog note. PASS.
- **The documents are a checked graph** — the new ADR is added to the ADR index and
  `check_docs.py`'s decision-record check is run after the edit. PASS (verified in Implementation).
- **Deterministic over inference** — `check_docs.py` and `check_dangling_mechanics.py` are run
  rather than assumed to pass.

No violations. No Complexity Tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/038-ancestry-skill-widening/
├── plan.md              # This file
├── spec.md              # Feature spec
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

No source tree changes. Files touched outside `specs/`:

```text
docs/adr/0040-ancestry-widens-the-skill-pool-never-the-budget.md   # new ADR
docs/design/05-character-creation.md                               # §3 gains the ancestry rule
```

## Complexity Tracking

*(empty — no constitution violations)*
