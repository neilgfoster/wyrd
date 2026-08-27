# Implementation Plan: Define the model-tiering target and its verification

**Branch**: `189-model-tiering-target` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add "The actual target, stated precisely" to `27-tooling.md` §5: correct the epic's own looser
"Haiku-sufficient" framing against §5's already-decided position (GM session stays on the
capable model), restate the real target (the capable model's job shrinks to exactly what needs
narrative judgement), state verification as an audit of the CLI surface against §5's tiering
table (reusing #188's existing code/prose classification, not a new mechanism), and state
plainly that narration running on a smaller model is rejected, not deferred.

## Technical Context

**Language/Version**: N/A — design specification; no code implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Does not reopen or change §5's existing decision — only corrects a looser
restatement of it (FR-001, FR-002).

**Scale/Scope**: `docs/design/27-tooling.md` §5.

## Constitution Check

- **No ADR** — §5's decision already exists; this corrects a restatement of it, decides nothing
  new. PASS.
- **Design documents rewritten in place** — the new subsection extends §5 in place. PASS.
- **Deterministic over inference** — verification is stated as an inspection audit, not an
  aspiration. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/073-model-tiering-target/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/27-tooling.md   # sec5 gains "The actual target, stated precisely"
```

## Complexity Tracking

*(empty — no constitution violations)*
