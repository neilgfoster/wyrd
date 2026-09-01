# Implementation Plan: Core opposed-test resolution

**Branch**: `222-opposed-test-resolution` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/076-opposed-test-resolution/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Implement the opposed-test formula and the Wyrd die from `docs/design/03-rules.md` section 1 as
a pure function in `engine/wyrd/rules.py`, and expose it through a new `opposed-test` verb in
the catalog #221 established. `effective% = clip(50 + (skill - opponent), 5, 95)`; success at or
under `effective%`; degrees on success only; the Wyrd die read from the natural roll's units
digit, independent of success.

## Technical Context

**Language/Version**: Python 3.11+ (unchanged from #221)

**Primary Dependencies**: None — standard library only, plus #221's own `engine/wyrd/rules.py`
(`roll_d100`), `catalog.py`, `client.py`, `render.py`

**Storage**: None for this feature — the Key Entities section of spec.md notes the result is
stateless and not persisted (unlike #221's `roll` verb)

**Testing**: stdlib `unittest`, no pytest (unchanged from #221)

**Target Platform**: Any platform with Python 3.11+

**Project Type**: CLI / library, extending #221's existing `engine/wyrd/` package

**Performance Goals**: Not performance-sensitive, same as #221

**Constraints**: Stdlib-only; setting-agnostic; must reuse #221's `roll_d100` rather than
reimplementing dice logic (single source of truth for the dice tool, per
`docs/design/27-tooling.md`'s "the dice roller in particular is non-negotiable")

**Scale/Scope**: Single opposed-test resolution function plus its CLI verb; no chronicle state
read or written

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, checked against `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repository** — N/A, original code and tests only. PASS.
- **No setting or system names in `design/` or `README.md`** — N/A, this feature touches
  `engine/` and `specs/` only; the code itself avoids setting vocabulary (spec FR-011). PASS.
- **Tone is a setting property** — N/A, no tone-bearing content. PASS.
- **Deterministic over inference** (ADR 0005) — this feature is itself the deterministic
  resolution primitive; nothing here is inferred by a model. PASS.
- **The dice roller is non-negotiable, single source of truth** (`27-tooling.md`) — this feature
  reuses #221's `rules.roll_d100` rather than rolling independently, so there remains exactly one
  place a d100 is actually generated. PASS.
- **Rule changes apply forward only** — N/A, new capability, no existing rule changed. PASS.
- **Capability changes go through the Spec Kit cycle** — satisfied by this plan and
  `specs/076-opposed-test-resolution/` being committed.

No violations. Nothing to record in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/076-opposed-test-resolution/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

Extends #221's existing `engine/wyrd/` package — no new top-level modules, only new functions
in the modules #221 already established:

```text
engine/
└── wyrd/
    ├── rules.py       # + opposed_test(skill, opponent, seed=None) -> dict
    ├── catalog.py     # + "opposed-test" TOOLS entry
    ├── verbs.py       # + opposed_test verb (thin wrapper: rules.opposed_test, no state I/O)
    └── client.py      # + "opposed-test" CLI subcommand

tests/
└── engine/
    └── test_rules.py  # + opposed_test test cases (existing file, extended)
    test_verbs.py      # + opposed_test verb test case (existing file, extended)
    test_client.py     # + opposed-test CLI test case (existing file, extended)
```

**Structure Decision**: No new files beyond what #221 already created — this feature adds
functions to existing modules, following the pattern `27-tooling.md` section 3 already
describes ("adding a verb means adding a catalog entry and a function; nothing else changes").
`opposed_test` lives in `rules.py` alongside `roll_d100` since both are pure, stateless
resolution logic; the verb wrapper in `verbs.py` differs from `roll`'s in that it performs no
`state.save` call at all (per spec.md's Key Entities: this result is not persisted).
