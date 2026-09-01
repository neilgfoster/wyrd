# Implementation Plan: Character creation procedure

**Branch**: `232-character-creation-procedure` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/081-character-creation-procedure/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Add `create_character(...) -> dict` to a new `engine/wyrd/creation.py` module: calls #231's
`career.validate_allocation`, and on success composes the fixed starting values from
`docs/design/11-character-creation.md` section 2 with the caller's fiction fields into a
complete player-character frontmatter, then saves it via #229's `character.save`. On a failed
allocation, no entity is written.

## Technical Context

**Language/Version**: Python 3.11+ (unchanged)

**Primary Dependencies**: None beyond the existing `engine/wyrd/career.py` (#231) and
`character.py` (#229) — this feature composes them, adding no new primitives of its own besides
the fixed-value table

**Storage**: Writes one character entity file via #229's atomic `character.save` — this is the
first feature in this session's line of work that actually persists a character to disk as its
main effect, rather than a stateless computation

**Testing**: stdlib `unittest`, no pytest (unchanged)

**Target Platform**: Any platform with Python 3.11+

**Project Type**: CLI / library, adding one new module (`creation.py`)

**Performance Goals**: Not performance-sensitive

**Constraints**: Stdlib-only; setting-agnostic; MUST NOT write a character entity if
`validate_allocation` rejects the allocation (FR-004) — the one ordering constraint specific to
this feature, since it's the first to combine "validate, then persist" across two other
features' primitives

**Scale/Scope**: One new function composing two existing modules, plus catalog/verb/CLI wiring

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository** — N/A, original code/tests only. PASS.
- **No setting or system names** — N/A; test fixtures use generic placeholder names. PASS.
- **Tone is a setting property** — N/A. PASS.
- **Deterministic over inference** (ADR 0005) — every value this feature sets (Stamina 6,
  Fate/Fortune by `mortality`, zeroed tracks) has one correct answer given the inputs; which
  career/allocation/name to choose stays explicitly the caller's judgment (ADR 0014). PASS.
- **Reuse over reimplementation** — calls #231's `validate_allocation` and #229's
  `character.save` rather than re-deriving either. PASS.
- **Persist before narrate** (principle 2) — the character is saved as this function's own
  effect; there is no narration step in this engine-layer feature to precede, but the save
  itself is atomic via #221's `state.save_entity`, unchanged. PASS.
- **Capability changes go through the Spec Kit cycle** — satisfied by this plan.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/081-character-creation-procedure/
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
    ├── creation.py     # NEW: create_character(...) -> dict
    ├── catalog.py       # + "create-character" TOOLS entry
    ├── verbs.py           # + thin wrapper
    └── client.py            # + subcommand

tests/
└── engine/
    ├── test_creation.py  # NEW
    ├── test_verbs.py       # + new verb case
    └── test_client.py        # + new CLI case
```

**Structure Decision**: `creation.py` is a new module rather than added to `career.py` or
`character.py` — it's the orchestrating procedure that calls both, and neither of those modules
should depend on the other or on a third "creation" concept, per `docs/design/27-tooling.md`
section 3's separation of concerns (a verb's operation composes existing modules' functions
rather than being folded into one of them).
