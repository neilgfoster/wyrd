# Implementation Plan: Career graph and advance allocation

**Branch**: `231-career-graph-advance-allocation` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/080-career-advance-allocation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add a new `engine/wyrd/career.py` module: plain dict shapes for a career and an optional
ancestry, and `validate_allocation(actions, career, ancestry=None) -> dict` — a pure function
that replays a sequence of `open`/`raise` actions against the career's (and ancestry's) declared
skills and caps, enforcing the 8-total / 2-minimum-opened / cap / eligibility rules from
`docs/design/11-character-creation.md` section 3, and returning either the resulting skill
percentages or a specific rejection reason.

## Technical Context

**Language/Version**: Python 3.11+ (unchanged)

**Primary Dependencies**: None — reuses #221's `rules.SKILL_OPEN_VALUE`/`SKILL_ADVANCE_STEP`
rather than redefining 25/5

**Storage**: None — pure function, no chronicle state (matching #222's `opposed_test` and
#229's validation functions)

**Testing**: stdlib `unittest`, no pytest (unchanged)

**Target Platform**: Any platform with Python 3.11+

**Project Type**: CLI / library, adding one new module (`career.py`) plus catalog/verb/CLI
wiring

**Performance Goals**: Not performance-sensitive

**Constraints**: Stdlib-only; setting-agnostic; MUST reuse #221's `SKILL_OPEN_VALUE`/
`SKILL_ADVANCE_STEP` constants rather than hardcoding 25/5 again, so the two places a skill's
scale is defined can never drift

**Scale/Scope**: One new module with one validation function and its data shapes, plus the
usual catalog/verb/CLI additions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository** — N/A, original code/tests only. PASS.
- **No setting or system names** — N/A; career/skill names in tests are generic placeholders
  (`stealth`, `swordplay`), not references to any real system. PASS.
- **Tone is a setting property** — N/A. PASS.
- **Deterministic over inference** (ADR 0005) — every rule here (total count, cap, eligibility,
  open-before-raise) has one correct answer given the allocation and career; nothing is
  inferred. Which career/allocation to *choose* stays explicitly out of scope (ADR 0014, spec's
  Assumptions). PASS.
- **Reuse over reimplementation** — `SKILL_OPEN_VALUE`/`SKILL_ADVANCE_STEP` from #229 are
  imported, not redefined. PASS.
- **Capability changes go through the Spec Kit cycle** — satisfied by this plan.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/080-career-advance-allocation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
engine/
└── wyrd/
    ├── career.py       # NEW: validate_allocation(actions, career, ancestry=None) -> dict
    ├── catalog.py       # + "validate-allocation" TOOLS entry
    ├── verbs.py           # + thin wrapper
    └── client.py            # + subcommand

tests/
└── engine/
    ├── test_career.py   # NEW
    ├── test_verbs.py      # + new verb case
    └── test_client.py       # + new CLI case
```

**Structure Decision**: `career.py` is a new module, separate from `character.py` (#229), since
it validates a *career/allocation* shape rather than the character entity itself —
`character.py`'s job is the entity's own structural rules (wounds), not what a valid path to a
set of skill values looks like. Both are small, focused modules under the same
`docs/design/27-tooling.md` section 3 convention that already separates `rules.py`/`state.py`.
