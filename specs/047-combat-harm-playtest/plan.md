# Implementation Plan: Combat and harm playtest

**Branch**: `047-combat-harm-playtest` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Extend `docs/design/30-playtest-transcript.md` with a new "Combat and harm: a deeper pass"
section: a real seeded three-round combat exchange (seed `20260828`) against a deliberately
tougher single opponent, resulting in a genuine drop, a critical roll, and an Aftermath roll; a
separately-seeded (`20260829`) six-roll sample at the 35%-death Aftermath row to reach a real
death result for the Fate-spend demonstration; a crowd-clearing encounter (no roll needed); and
Stamina recovery across a Rally and a downtime. One genuine rule ambiguity found during play
(telling blow via a failed defence roll has no stated per-roll procedure) is reported and raised
as a separate follow-up issue (#155) rather than resolved here.

## Technical Context

**Language/Version**: Python 3.11+ stdlib (`random`) for roll generation; the record itself is
Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (one
self-introduced false positive found and fixed — "Against Senna" read as a Title Case reference,
reworded), `python3 -m pytest -q`.

**Constraints**: Real seeded rolls throughout, no curated fight outcome (FR-001). A genuine
ambiguity found during play is reported, not silently resolved (FR-004).

**Scale/Scope**: One new ~100-line section in `docs/design/30-playtest-transcript.md`, one
follow-up issue (#155) raised for the ambiguity found.

## Constitution Check

- **Nothing unpublishable** — the setting data used (a second invented opponent, "the
  bounty-hunter") is the same invented-for-this-exercise data #14/R3 and #147 already
  established. PASS.
- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — the new section is appended to the existing document
  structure. PASS.
- **No ADR in this feature** — the ambiguity found may eventually need one, but that decision
  belongs to the follow-up issue (#155), not this playtest record. PASS (per spec.md Assumptions).
- **Deterministic over inference** — every claimed roll traces to an actual seeded draw, checked
  by hand against the relevant table (critical, Aftermath, crowd qualification), not asserted.
  PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/047-combat-harm-playtest/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 7
```

## Complexity Tracking

*(empty — no constitution violations)*
