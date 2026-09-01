# Implementation Plan: Character entity schema and validator

**Branch**: `229-character-entity-schema` | **Date**: 2026-09-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/079-character-entity-schema/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Extend `engine/wyrd/state.py`'s reader/writer to (a) parse/serialize an **entity file**
(`---`-delimited YAML frontmatter + markdown body, per `docs/design/25-entities.md`) rather than
only a bare YAML value, and (b) parse/serialize **list-of-mapping** values (needed for `wounds`,
`career_history`, etc.) — a real gap found while implementing this feature, not present in
#221-#224's minimal state shape. Add a new `engine/wyrd/character.py` module holding the
player-character shape's field list, wound validation (the closed effect set, `bears_on`
requirement, `recurring`/`closed` exclusivity), and active-effects computation. Add skill-scale
constants to `rules.py`.

## Technical Context

**Language/Version**: Python 3.11+ (unchanged)

**Primary Dependencies**: None beyond the existing `engine/wyrd/state.py` (extended) and
`rules.py` (`UNTRAINED_SKILL`, reused not duplicated)

**Storage**: Character entities are files on disk, read/written via the extended `state.py`
atomic save/load — same atomicity guarantee as #221, applied to a richer value shape

**Testing**: stdlib `unittest`, no pytest (unchanged)

**Target Platform**: Any platform with Python 3.11+

**Project Type**: CLI / library, extending the existing `engine/wyrd/` package plus one new
module (`character.py`)

**Performance Goals**: Not performance-sensitive

**Constraints**: Stdlib-only; setting-agnostic; no third-party YAML dependency — the reader/
writer extension must stay within the same restricted-subset philosophy #221 established, not
grow into a general YAML library

**Scale/Scope**: A frontmatter/body split function pair in `state.py`, a list-of-mapping
extension to `state.py`'s existing reader/writer, one new module (`character.py`) with the field
list, wound validation, and active-effects computation, plus two skill-scale constants in
`rules.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository** — N/A, original code/tests only. PASS.
- **No setting or system names** — N/A; the character shape's field names are all engine names
  per `docs/design/10-the-character.md`'s own framing ("every name here is an engine name").
  PASS.
- **Tone is a setting property** — N/A. PASS.
- **Deterministic over inference** (ADR 0005) — every wound rule (closed effect set, `bears_on`
  requirement, `recurring`/`closed` exclusivity) has a single correct answer given the data;
  nothing here is inferred. PASS.
- **No third-party YAML dependency** (`docs/design/27-tooling.md` section 2) — the extension
  stays inside the existing restricted-subset reader/writer, following
  `tools/check_bestiary.py`'s already-proven list-of-mapping pattern rather than reaching for
  PyYAML now that the shape has gotten more complex. PASS.
- **The engine names no skill** (ADR 0013) — `bears_on` and `career`/`loyalty` values are stored
  as opaque strings; nothing in this feature's code branches on a specific skill or career
  identifier. PASS.
- **Capability changes go through the Spec Kit cycle** — satisfied by this plan.

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/079-character-entity-schema/
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
    ├── state.py         # + parse_entity/dump_entity (frontmatter+body split);
    │                     #   + list-of-mapping support in the existing reader/writer
    ├── character.py      # NEW: PLAYER_CHARACTER_FIELDS, validate_wound, validate_character,
    │                       #      active_wound_effects, default_player_character
    ├── rules.py            # + SKILL_OPEN_VALUE = 25, SKILL_ADVANCE_STEP = 5
    ├── catalog.py           # + "character-load", "character-save", "skill-scale" TOOLS entries
    ├── verbs.py               # + thin wrappers
    └── client.py               # + subcommands

tests/
└── engine/
    ├── test_state.py     # + entity frontmatter/body split, list-of-mapping round-trip cases
    ├── test_character.py  # NEW: wound validation, active-effects, full round-trip
    ├── test_rules.py        # + skill-scale constant cases
    ├── test_verbs.py          # + new verb cases
    └── test_client.py          # + new CLI cases
```

**Structure Decision**: `character.py` is a new module (not folded into `rules.py` or `state.py`)
because it holds character-domain validation logic distinct from both `rules.py`'s pure
resolution functions and `state.py`'s generic, entity-agnostic persistence primitives — matching
`docs/design/27-tooling.md` section 3's module list, which already names separate concerns for
rules/tables/state rather than one undifferentiated file.
