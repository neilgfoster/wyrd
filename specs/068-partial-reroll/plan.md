# Implementation Plan: The dependency-graph partial-reroll mechanism

**Branch**: `195-partial-reroll` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Add a "Partial reroll" section to `docs/design/31-action-resolution.md`: `reroll` takes a
proposal id, a target step, and a reroll resource; computes the downstream set from the
`depends_on` graph #194 already stages; discards and freshly re-resolves exactly that set
(checked against cascading resolution again); leaves everything outside it untouched; stages the
resource's own cost alongside the re-resolution; and does not invalidate the proposal id. A
worked example (two independent Exposure tests in one proposal, one rerolled via the Bargain,
real seeded rolls including an honest still-fails outcome) shows the untouched branch surviving
byte-identical.

## Technical Context

**Language/Version**: N/A — design specification; no code implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Reuses #194's `depends_on` graph rather than inventing a new dependency
mechanism (FR-002). Does not address combat's own attack→damage outcome-conditional chain —
raised separately.

**Scale/Scope**: One new section in `docs/design/31-action-resolution.md`.

## Constitution Check

- **No ADR** — a direct extension of ADR 0050 and #194's already-established `depends_on` graph,
  not a new fork. PASS.
- **Design documents rewritten in place** — the new section extends the same growing document,
  per the structural decision #193/#194 already established. PASS.
- **Deterministic over inference** — the worked example uses real seeded rolls, including an
  honest non-cherry-picked outcome. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/068-partial-reroll/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/31-action-resolution.md   # new "Partial reroll" section
```

## Complexity Tracking

*(empty — no constitution violations)*
