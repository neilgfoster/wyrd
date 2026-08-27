# Implementation Plan: Combination and minmaxing playtest pass

**Branch**: `054-combination-minmaxing-playtest` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Extend `docs/design/30-playtest-transcript.md` with a new "Combination and minmaxing" section:
seven real, seeded (`20260835`) independent trials of stacking every reroll-granting resource
(the Bargain, Resolve, Fortune) on one fixed-setup failed test, reporting every trial in full.
Finds a genuine combination-level gap (no stated pacing limit on stacking) and raises it as
follow-up issue #167. Separately confirms the scope boundary between systems-of-power's
Ill-Omen-Taint consequence and the combat/opposed-test Omen modifier (ADR 0042) holds as stated.

## Technical Context

**Language/Version**: Python 3.11+ stdlib (`random`) for roll generation; the record itself is
Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Real seeded rolls throughout (FR-001). All seven trials reported, none discarded
(FR-002, SC-002). The genuine gap found is reported and raised, not fixed inline (FR-003). Not
claimed as exhaustive combination coverage (FR-005).

**Scale/Scope**: One new ~65-line section in `docs/design/30-playtest-transcript.md`, one
follow-up issue (#167) raised.

## Constitution Check

- **Nothing unpublishable** — continues using Senna Vask, no new setting content. PASS.
- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — the new section is appended to the existing document
  structure. PASS.
- **No ADR in this feature** — the stacking gap's resolution belongs to #167's own follow-up.
  PASS (per spec.md Assumptions).
- **Deterministic over inference** — every claimed roll traces to an actual seeded draw; the
  finding is drawn from what the trials actually produced, not asserted in advance. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/054-combination-minmaxing-playtest/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 12
```

## Complexity Tracking

*(empty — no constitution violations)*
