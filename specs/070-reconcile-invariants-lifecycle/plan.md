# Implementation Plan: Reconcile write invariants and state the transaction lifecycle

**Branch**: `197-reconcile-invariants-lifecycle` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Rewrite `22-state.md`'s "Invariants" section: split into passive validation and active triggers
(the latter now correctly stated as spawning cascading resolution's further rolls, per
`31-action-resolution.md`), restate "persist precedes narrate" against the propose/commit model,
correct the Spent formula to ADR 0049's dual threshold, and state the transaction lifecycle by
reusing `chronicle.yaml`'s existing `pending.rolled` field rather than inventing a new mechanism.
Add `wyrd reroll` to `02-architecture.md`'s CLI sketch, which #195 specified but never added.

## Technical Context

**Language/Version**: N/A — design specification; no code implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Reuses `pending.rolled` for the transaction lifecycle rather than a new field
(FR-004). Does not change Resolve's own formula (already correct per ADR 0049) — only corrects
where it was stated stale.

**Scale/Scope**: `docs/design/22-state.md`'s Invariants and Interrupted-sessions sections;
`docs/design/02-architecture.md`'s CLI sketch.

## Constitution Check

- **No ADR** — reconciles documents against decisions already made, makes no new one. PASS.
- **Design documents rewritten in place** — the Invariants section is rewritten, not appended
  with a changelog note; the stale Spent formula is corrected in place. PASS.
- **Deterministic over inference** — the transaction-lifecycle answer is derived from an
  already-existing field's own stated behaviour (`pending.rolled`, cleared at the next Rally),
  not invented. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/070-reconcile-invariants-lifecycle/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/22-state.md          # Invariants rewritten, transaction lifecycle stated
docs/design/02-architecture.md   # wyrd reroll added to the CLI sketch
```

## Complexity Tracking

*(empty — no constitution violations)*
