# Implementation Plan: Systems-of-power balance playtest

**Branch**: `051-systems-of-power-playtest` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Extend `docs/design/30-playtest-transcript.md` with a new "Systems of power: a balance pass"
section: a new character (Kester, reusing `09-systems-of-power.md`'s own `ember-craft` worked
example) plays three ordinary `minor`-tier invocations, then a real-seeded (`20260831`)
26-invocation `major`-tier spam sequence with no Rally in between, disclosing every roll. Finds a
genuine cost-structure gap (nothing discourages spamming failed high-tier invocations) and raises
it as follow-up issue #163. Separately confirms the Resolve gap (#157) recurs when
`resolve_cost` is exercised.

## Technical Context

**Language/Version**: Python 3.11+ stdlib (`random`) for roll generation; the record itself is
Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Real seeded rolls throughout (FR-001). The minmax sequence is not cut short to
avoid an inconvenient result — every roll disclosed (FR-002, SC-002). A genuine balance gap is
reported and raised, not fixed inline (FR-003).

**Scale/Scope**: One new ~95-line section in `docs/design/30-playtest-transcript.md`, one
follow-up issue (#163) raised.

## Constitution Check

- **Nothing unpublishable** — the new character (Kester) and its `ember-craft` declaration reuse
  `09-systems-of-power.md`'s own already-published worked example rather than inventing new
  flavor. PASS.
- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — the new section is appended to the existing document
  structure. PASS.
- **No ADR in this feature** — the cost-structure gap's resolution belongs to #163's own
  follow-up. PASS (per spec.md Assumptions).
- **Deterministic over inference** — every claimed roll traces to an actual seeded draw; the
  finding is drawn from what actually happened in the sequence, not asserted in advance. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/051-systems-of-power-playtest/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 10
```

## Complexity Tracking

*(empty — no constitution violations)*
