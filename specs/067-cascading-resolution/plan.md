# Implementation Plan: Cascading resolution for threshold-triggered sub-rolls

**Branch**: `194-cascading-resolution` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add a "Cascading resolution" section to `docs/design/31-action-resolution.md`: a staged mutation
crossing a track's threshold spawns the further roll(s) that track's own rule calls for, as
additional steps in the same proposal, recursively, with each step recording what it depends on.
Termination is justified by citing each track's own already-proven bound (Transformation's
hidden-threshold loop, the Affliction sawtooth), not re-derived. A deferred consequence
(Aftermath) is explicitly excluded from immediate cascading. A worked example reuses real rolls
already on record (§8 of the playtest transcript) to show a Taint-threshold crossing into a
Transformation, fully staged.

## Technical Context

**Language/Version**: N/A — design specification; no code implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Must not re-derive termination proofs that already exist elsewhere (FR-004).
Must not stage a deliberately-deferred consequence as an immediate cascade (FR-005).

**Scale/Scope**: One new section in `docs/design/31-action-resolution.md`, replacing that
document's own "what this does not specify" placeholder for cascading resolution.

## Constitution Check

- **No ADR** — a direct extension of ADR 0050's own already-stated reasoning, not a new decision
  with its own distinct rejected alternative. PASS.
- **Design documents rewritten in place** — the new section replaces the document's own
  forward-reference placeholder rather than appending a changelog note. PASS.
- **Deterministic over inference** — the worked example reuses real, already-verified rolls; no
  new arithmetic is asserted without grounding. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/067-cascading-resolution/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/31-action-resolution.md   # new "Cascading resolution" section
```

## Complexity Tracking

*(empty — no constitution violations)*
