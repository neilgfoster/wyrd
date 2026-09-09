# Implementation Plan: Chronicle overlay resolution

**Branch**: `113-chronicle-overlay-resolution` | **Date**: 2026-09-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/113-chronicle-overlay-resolution/spec.md`

## Summary

Add overlay resolution to `wyrd.entity`: given a setting entity and an optional overlay file
naming it via `overlay_of`, produce the effective entity `docs/design/25-entities.md`'s chronicle
overlay section describes — overlay fields override, absent fields fall through, and an overlay
may introduce fields the setting entity never had at all (promotion). Builds directly on #305's
`entity.py` (`validate`, `load`, `load_set`) and `state.py`'s file-level I/O; adds a
`load_setting_and_overlays`-style entry point that reads the two directories and returns resolved
effective entities keyed by id.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (matches every existing `engine/wyrd/*`
module).

**Primary Dependencies**: None beyond the standard library. Reuses `wyrd.state.load_entity` for
file-level parsing of both setting and overlay files (an overlay is a partial entity file, not a
different format), and `wyrd.entity.validate`/`load_set` for schema checking the merged result.

**Storage**: Entity files on disk, split across two directories: `chronicle/setting/` (read-only)
and `chronicle/overlay/` (this chronicle's deltas). This feature never writes to either directory.

**Testing**: `pytest`, run with `PYTHONPATH=engine`, in `tests/engine/test_entity.py` (extending
#305's test module rather than adding a new one, since this is the same module).

**Target Platform**: Linux/CLI — no server or UI component.

**Project Type**: Single library project (the existing `engine/` package).

**Performance Goals**: N/A — same scale as #305 (hundreds to low thousands of entity files); a
merge is a single dict-level operation per entity.

**Constraints**: `docs/design/27-tooling.md`'s deterministic-over-inference rule — merge and
validation are pure computation. Ruff (line length 100, rule sets E/F/I/UP) stays clean
repo-wide. `engine/` and `tools/` stay independent (`docs/design/02-architecture.md`).

**Scale/Scope**: One overlay layer per entity (not stacked/versioned overlays), per design/25 and
this feature's own Assumptions.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Per `.specify/memory/constitution.md`, gates are drawn from `CLAUDE.md` and the accepted ADRs:

- **Nothing unpublishable enters this repo** — original engine code implementing an already-
  published design document; no source-book extraction. **Pass.**
- **No setting or system names in design/README** — this feature adds no new vocabulary; it
  implements `overlay_of`, "effective entity" and "promotion" exactly as `25-entities.md` already
  names them. **Pass.**
- **Tone is a setting property** — no tone or genre language introduced. **Pass.**
- **Deterministic over inference** (ADR 0005) — merge is a closed-form dict-level operation
  (overlay field present → override; absent → fall through); nothing inferred. **Pass.**
- **Rule changes apply forward only** — this is new capability, not a retroactive rule change.
  **Pass.**
- **Design documents describe the present** — this plan implements `25-entities.md`'s chronicle
  overlay section as written; no design update anticipated unless implementation surfaces a gap.
  **Pass, pending Phase 1.**
- **Capability changes go through the Spec Kit cycle, `specs/<feature>/` committed** — this plan
  is that artifact. **Pass.**

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/113-chronicle-overlay-resolution/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (kord-feature-tasks — not created here)
```

No `contracts/` directory: this feature adds no external interface (no CLI command, no network
endpoint) — it is an internal library function other `engine/wyrd/*` modules call directly, same
as #305.

### Source Code (repository root)

```text
engine/wyrd/
├── state.py             # existing — file-level I/O this reuses unchanged
└── entity.py             # existing (#305) — validate/load/load_set; this feature ADDS
                            #   overlay_of recognition and a merge/resolve entry point

tests/engine/
└── test_entity.py         # existing (#305) — this feature EXTENDS with overlay test cases
```

**Structure Decision**: Extend `entity.py` in place rather than adding a new module. Overlay
resolution is a thin layer over the same entity-file format #305 already reads and validates —
splitting it into a separate `overlay.py` would duplicate the load/validate plumbing for no
architectural benefit, and design/25 treats the overlay as a property of entity resolution, not a
distinct subsystem.

## Complexity Tracking

*No violations — table not needed.*
