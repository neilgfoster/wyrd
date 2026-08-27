# Implementation Plan: Resolution and opposed-tests playtest

**Branch**: `046-resolution-opposed-playtest` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Extend `docs/design/30-playtest-transcript.md` with a new "Resolution and opposed tests: a deeper
pass" section, using Senna Vask (the existing playtest character) and a real seeded
`python3 random` sequence (seed `20260827`, distinct from #14/R3's `20260826`) to play through the
difficulty ladder, declaration bonuses, untrained attempts, assistance, the player-facing
opposed-test shape, and the two-player-controlled-entities edge case. No fault found; three
genuine edge cases (a natural 100, degrees-on-failure, the two-entity contest) confirmed against
`03-rules.md` §1 and recorded.

## Technical Context

**Language/Version**: Python 3.11+ stdlib (`random`) for the roll generation; the playtest record
itself is Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py`,
`python3 -m pytest -q`. The roll-generation script itself is a one-time scratch tool (not
committed — the same treatment #14/R3's own generation process received), its output transcribed
into the document verbatim.

**Constraints**: Real seeded rolls, not curated (FR-001). No die drawn for an already-impossible
attempt (FR-003). Degrees reported only on success (FR-004).

**Scale/Scope**: One new ~90-line section in `docs/design/30-playtest-transcript.md`, plus a small
fix to a stale cross-reference in the same document (§5's "creation steps 1–9" → "1–8", stale
since the Luck merge renumbered creation's steps).

## Constitution Check

- **Nothing unpublishable** — the setting data used (Senna Vask, the wayfarer career) is the same
  invented-for-this-exercise data #14/R3 already established, carries no real setting name. PASS.
- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — the new section is appended to the existing document
  structure; the stale step-count fix is corrected in place, not left as a "previously" note.
  PASS.
- **No ADR needed** — no fault requiring a design decision was found; this is a verification
  exercise, not a decision. PASS (per spec.md Assumptions).
- **Deterministic over inference** — every claimed result traces to an actual computed roll,
  checked by hand against `03-rules.md` §1's formulas, not asserted. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/046-resolution-opposed-playtest/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 6; one stale cross-reference fixed
```

## Complexity Tracking

*(empty — no constitution violations)*
