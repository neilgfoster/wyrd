# Implementation Plan: Declaration and assistance bonuses

**Branch**: `223-declaration-assistance` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/077-declaration-assistance/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add two closed-set lookups (`declaration_bonus`, `assistance_bonus`) to `engine/wyrd/rules.py`,
and extend #222's `opposed_test` with optional `declaration`/`helper_skill`/`helper_can_attempt`
parameters that add their resulting bonuses to the acting skill before the existing
`effective_pct` clip runs — a backward-compatible extension, not a new resolution path.
`declaration="removes_risk"` short-circuits to a no-roll automatic success.

## Technical Context

**Language/Version**: Python 3.11+ (unchanged)

**Primary Dependencies**: None beyond #221/#222's own `engine/wyrd/rules.py`

**Storage**: None — pure functions, no chronicle state (unchanged from #222)

**Testing**: stdlib `unittest`, no pytest (unchanged)

**Target Platform**: Any platform with Python 3.11+

**Project Type**: CLI / library, extending the existing `engine/wyrd/` package

**Performance Goals**: Not performance-sensitive

**Constraints**: Stdlib-only; setting-agnostic; must not change `opposed_test`'s existing
behavior for callers that supply neither new parameter (FR-005, SC-003) — this is the one
constraint specific to this feature, since it's extending rather than adding a fresh function

**Scale/Scope**: Two new pure functions plus optional-parameter extension of one existing
function, their catalog entries, and CLI wiring

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository** — N/A, original code/tests only. PASS.
- **No setting or system names in `design/` or `README.md`** — N/A; code avoids setting
  vocabulary (spec FR-008). PASS.
- **Tone is a setting property** — N/A. PASS.
- **Deterministic over inference** (ADR 0005) — this feature is exactly the deterministic half
  of a split the spec's Assumptions section states explicitly: category classification and
  can-attempt judgment stay with the caller; only the point-value lookup given a category is
  computed here. PASS.
- **The dice roller is non-negotiable** — the "removes_risk" no-roll path is a real absence of a
  roll, not a hidden second dice path; every other path still calls #222's `roll_d100`
  indirectly through the unmodified `opposed_test` roll step. PASS.
- **Rule changes apply forward only** — N/A, additive capability. PASS.
- **Capability changes go through the Spec Kit cycle** — satisfied by this plan.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/077-declaration-assistance/
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
    ├── rules.py       # + declaration_bonus(category), assistance_bonus(skill, can_attempt)
    │                   #   + opposed_test gains declaration/helper_skill/helper_can_attempt kwargs
    ├── catalog.py     # + "declaration-bonus", "assistance-bonus" TOOLS entries;
    │                   #   "opposed-test" entry's inputSchema extended
    ├── verbs.py       # + declaration_bonus, assistance_bonus thin wrappers; opposed_test
    │                   #   wrapper passes the new kwargs through
    └── client.py      # + declaration-bonus, assistance-bonus subcommands; opposed-test
                        #   subcommand gains new optional flags

tests/
└── engine/
    ├── test_rules.py   # + declaration/assistance/modified-opposed-test cases (extended)
    ├── test_verbs.py   # + new verb cases (extended)
    └── test_client.py  # + new CLI cases (extended)
```

**Structure Decision**: Same pattern as #221/#222 — new functions in existing modules, no new
files. `declaration_bonus` and `assistance_bonus` live in `rules.py` alongside `opposed_test`
since all three are pure. Backward compatibility for `opposed_test`'s existing three-argument
call shape is verified directly (SC-003), not just assumed from "the new parameters default to
off."
