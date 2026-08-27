# Implementation Plan: Decide the engine-code vs. GM-contract-prose boundary

**Branch**: `188-code-vs-prose-boundary` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Restate `02-architecture.md`'s "Code versus prose" section around a checkable test —
deterministic-and-mechanically-checkable is code, requires-creative-judgment is prose — and
check it against `01-principles.md`'s seven engine principles (§1/§2 already code-enforced by
`propose`/`commit`; §6 structural, not prose, per `21-parallel-chronicles.md`'s actual isolation
mechanism; §3/§4/§5/§7 stay prose in full). Apply the same test to concrete `16-session.md`
elements in a table (the Rally, Downtime, Rest, session shapes, the session loop).

## Technical Context

**Language/Version**: N/A — design specification; no code implemented here.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`.

**Constraints**: Every classification checked against the cited principle/document's actual
text (FR-002), not asserted.

**Scale/Scope**: `docs/design/02-architecture.md`'s "Code versus prose" section.

## Constitution Check

- **No ADR** — applies already-established principles, decides nothing new. PASS.
- **Design documents rewritten in place** — the existing section is restated, not appended with
  a changelog note. PASS.
- **Deterministic over inference** — every classification checked against source text; one
  drafted claim (`wyrd doctor` auditing cross-chronicle bleed) was caught unverified and
  corrected before it shipped. PASS.
- **Setting-agnostic** — no setting or system name introduced. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/072-code-vs-prose-boundary/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/02-architecture.md   # "Code versus prose" section restated
```

## Complexity Tracking

*(empty — no constitution violations)*
