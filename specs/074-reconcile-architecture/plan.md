# Implementation Plan: Reconcile 02-architecture.md against the engine-design decisions

**Branch**: `190-reconcile-architecture` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Fix the `wyrd-chronicle-<name>/` tree's `codex/` → `entities/` naming drift against
`22-state.md`/`23-chronicle-bootstrap.md`, correct the `engine/` tree line's stale "not yet
built" comment now that #187/#188/#189 have specified the CLI/memory-tiers/code-prose boundary
in full, and confirm the rest of the document (Memory tiers, Code versus prose, Deployment)
already reflects those three landed features with no further drift.

## Technical Context

**Language/Version**: N/A — design specification; no code implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Rewrites `docs/design/02-architecture.md` in place, describing the present —
no changelog notes. Makes no new decision; only reconciles the document against decisions
already recorded by #187/#188/#189.

**Scale/Scope**: `docs/design/02-architecture.md`.

## Constitution Check

- **No ADR** — decides nothing new; corrects a document against already-recorded decisions.
  PASS.
- **Design documents rewritten in place** — edits apply directly, no changelog notes. PASS.
- **Deterministic over inference** — the `codex/`→`entities/` drift was found and confirmed by
  grep against the two other documents using the same concept, not by assumption. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/074-reconcile-architecture/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/02-architecture.md   # entities/ naming fix, engine/ tree-line fix
```

## Complexity Tracking

*(empty — no constitution violations)*
