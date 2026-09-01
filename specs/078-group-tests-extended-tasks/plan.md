# Implementation Plan: Group tests and extended tasks

**Branch**: `224-group-tests-extended-tasks` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/078-group-tests-extended-tasks/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `select_group_skill(member_skills, mode)` (pure selection: max/min, untrained-10% for a
missing member) and `resolve_extended_interval(skill, opponent, progress, target, ...)` (wraps
`opposed_test`, adds `max(1, degrees)` on success) to `engine/wyrd/rules.py`, plus
`group_test(member_skills, mode, opponent, ...)` that composes selection with `opposed_test`
directly. Both new top-level functions reuse #222/#223's `opposed_test` for the actual roll —
this feature adds no new roll logic and no new Wyrd-die logic.

## Technical Context

**Language/Version**: Python 3.11+ (unchanged)

**Primary Dependencies**: None beyond the existing `engine/wyrd/rules.py` (`opposed_test`)

**Storage**: None — pure functions; extended-task progress is passed in and returned, not
persisted by this feature (spec.md's Key Entities and Assumptions)

**Testing**: stdlib `unittest`, no pytest (unchanged)

**Target Platform**: Any platform with Python 3.11+

**Project Type**: CLI / library, extending the existing `engine/wyrd/` package

**Performance Goals**: Not performance-sensitive

**Constraints**: Stdlib-only; setting-agnostic; a group test MUST perform exactly one roll
regardless of member-list size (SC-002) — the one constraint specific to this feature's own
correctness, since "one roll" is the entire point of the subsection it implements

**Scale/Scope**: Two new pure functions (`select_group_skill`, `resolve_extended_interval`) plus
one composing function (`group_test`), their catalog entries, and CLI wiring

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository** — N/A, original code/tests only. PASS.
- **No setting or system names** — N/A; code avoids setting vocabulary (spec FR-012). PASS.
- **Tone is a setting property** — N/A. PASS.
- **Deterministic over inference** (ADR 0005) — group-skill selection (max/min of given numbers)
  and progress arithmetic (`max(1, degrees)`) are both single-correct-answer computations; which
  fictional question applies is left to the caller per spec's Assumptions. PASS.
- **The dice roller is non-negotiable, single source of truth** — both new functions call
  `opposed_test` (which itself calls `roll_d100`) rather than rolling independently; SC-002
  verifies a group test makes exactly one such call regardless of party size. PASS.
- **Rule changes apply forward only** — N/A, additive capability. PASS.
- **Capability changes go through the Spec Kit cycle** — satisfied by this plan.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/078-group-tests-extended-tasks/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

Extends the existing `engine/wyrd/` package — no new top-level modules:

```text
engine/
└── wyrd/
    ├── rules.py       # + select_group_skill, group_test, resolve_extended_interval
    ├── catalog.py     # + "group-test", "extended-task-interval" TOOLS entries
    ├── verbs.py       # + thin wrappers for both
    └── client.py      # + group-test, extended-task-interval subcommands

tests/
└── engine/
    ├── test_rules.py   # + group-test and extended-task cases (extended)
    ├── test_verbs.py   # + new verb cases (extended)
    └── test_client.py  # + new CLI cases (extended)
```

**Structure Decision**: Same pattern as #221/#222/#223 — new functions in existing modules, no
new files. `select_group_skill`/`group_test`/`resolve_extended_interval` live in `rules.py`
alongside `opposed_test` since all are pure and all ultimately call it for their one roll.
