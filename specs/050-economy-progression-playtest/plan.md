# Implementation Plan: Economy and progression playtest

**Branch**: `050-economy-progression-playtest` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Extend `docs/design/30-playtest-transcript.md` with a new "Economy and progression" section:
Senna Vask earns a session's trigger-based advances, completes her wayfarer career (70% cap, +1
Stamina, a Mark), changes career, and exercises the martial-weapon Standing cost plus both Upkeep
payment branches and a gear purchase. Unlike #147-#149, nothing in scope involves a dice roll —
advancement, career completion, Standing and coin are all deterministic per `03-rules.md` §2/§6
and `16-session.md` — so this section states that explicitly rather than force a roll in where
none belongs.

## Technical Context

**Language/Version**: N/A — Markdown design document only; no roll-generation script needed.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`.

**Constraints**: Every mechanical claim traces to `03-rules.md` §2/§6 or `16-session.md`'s Upkeep
row (SC-002). The Stamina-10 ceiling is not re-derived by hand — `check_advancement.py` already
computes it exactly (FR-003).

**Scale/Scope**: One new ~90-line section in `docs/design/30-playtest-transcript.md`.

## Constitution Check

- **Nothing unpublishable** — continues using Senna Vask and invented gear pricing, the same
  invented-for-this-exercise convention #14/R3 established. PASS.
- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — the new section is appended to the existing document
  structure. PASS.
- **No ADR in this feature** — nothing found required a design decision; one genuine
  documentation silence (career-change skill retention) is recorded as a stated inference, not
  escalated. PASS (per spec.md Assumptions).
- **Deterministic over inference** — every claim traces to the ruleset's own stated mechanics,
  not asserted; where the ruleset itself is silent (career-change retention), that silence is
  named as such rather than papered over. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/050-economy-progression-playtest/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 9
```

## Complexity Tracking

*(empty — no constitution violations)*
