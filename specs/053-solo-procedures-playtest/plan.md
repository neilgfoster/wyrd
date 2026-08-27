# Implementation Plan: Solo procedures and session/campaign structure playtest

**Branch**: `053-solo-procedures-playtest` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Extend `docs/design/30-playtest-transcript.md` with a new section covering the session loop
(load/orient/recap/beat/rally), an oracle-answer consultation, an oracle-prompt consultation, a
companion beat exercising Bond's Tension offset, and a journey leg with a hazard roll — all with
real seeded dice (seed `20260832`). Corrects a stale scope expectation (Fortune resetting at a
top-level arc boundary, superseded by #137's Luck/Fortune merge) rather than playing against a
rule that no longer exists. Records succession as deliberately untested — forcing it to fit the
playtest schedule would mean manufacturing a death or loss.

## Technical Context

**Language/Version**: Python 3.11+ stdlib (`random`) for roll generation; the record itself is
Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Real seeded rolls throughout (FR-001). The stale Fortune-refresh expectation is
named and corrected, not silently substituted (FR-003). Succession is not forced (FR-004).

**Scale/Scope**: One new ~85-line section in `docs/design/30-playtest-transcript.md`.

## Constitution Check

- **Nothing unpublishable** — continues using Senna Vask; reuses `15-oracle-prompts.md`'s own
  published table rows rather than inventing new content. PASS.
- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — the new section is appended to the existing document
  structure. PASS.
- **No ADR in this feature** — nothing found required a design decision. PASS (per spec.md
  Assumptions).
- **Deterministic over inference** — every claimed roll traces to an actual seeded draw; the
  Fortune-refresh discrepancy is checked against the current text of `03-rules.md` §3, not
  assumed from the epic's original (stale) description. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/053-solo-procedures-playtest/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 11
```

## Complexity Tracking

*(empty — no constitution violations)*
