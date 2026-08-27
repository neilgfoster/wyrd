# Implementation Plan: Condition-tracks playtest

**Branch**: `048-condition-tracks-playtest` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Extend `docs/design/30-playtest-transcript.md` with a new "Condition tracks: Taint, Trauma,
Strain — and a gap found in Resolve" section, using Senna Vask and a real seeded `python3 random`
sequence (seed `20260830`) to play the Bargain, a Fault-Line-biased Exposure crossing a Taint
threshold, the resulting Transformation and hidden-threshold rolls, an ordinary (unbiased)
Exposure, the Trauma sawtooth to an Affliction, and Strain's Rally recovery. Where a scene needed
a specific outcome (a failure, 6+ Trauma), further real attempts were made and every one reported.
A genuine gap was found in Resolve (no stated gain mechanic anywhere in the corpus) and reported
rather than papered over; raised as follow-up issue #157.

## Technical Context

**Language/Version**: Python 3.11+ stdlib (`random`) for roll generation; the record itself is
Markdown.

**Testing**: `python3 tools/check_docs.py`, `python3 tools/check_dangling_mechanics.py` (clean,
no new false positive this time), `python3 -m pytest -q`.

**Constraints**: Real seeded rolls throughout, every repeated-attempt sequence shown in full, no
discarded rolls (FR-002). Resolve gap reported, not invented around (FR-004).

**Scale/Scope**: One new ~110-line section in `docs/design/30-playtest-transcript.md`, one
follow-up issue (#157) raised.

## Constitution Check

- **Nothing unpublishable** — continues using Senna Vask, the same invented-for-this-exercise
  character #14/R3 established. PASS.
- **No setting or system names** — none introduced. PASS.
- **Design documents rewritten in place** — the new section is appended to the existing document
  structure. PASS.
- **No ADR in this feature** — the Resolve gap's resolution belongs to #157, not this playtest
  record. PASS (per spec.md Assumptions).
- **Deterministic over inference** — every claimed roll traces to an actual seeded draw, checked
  by hand against the relevant table (transformation severity, hidden threshold, affliction row),
  not asserted. PASS.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/048-condition-tracks-playtest/
├── plan.md, spec.md, tasks.md
└── checklists/requirements.md
```

### Repository changes

```text
docs/design/30-playtest-transcript.md   # new section 8
```

## Complexity Tracking

*(empty — no constitution violations)*
