# Implementation Plan: Mortal blows, Fate, and death

**Branch**: `092-mortal-blows-fate-death` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/092-mortal-blows-fate-death/spec.md`

## Summary

Wire `_stage_aftermath` (landed, currently unwired — spec.md's own T008 in
`specs/091-aftermath-wound-records`) into the three mechanisms that close or force a `death`
result: a mortal critical forces the roll onto `death` at staging time; `mortality: low` closes
`death` onto the worst non-death row, also at staging time (both are deterministic and require no
player input, so both happen inside `_stage_aftermath` itself rather than as a later step). A
Fate spend is different — it is a player choice made *after* seeing a `death` result, so it is a
new standalone function, `close_death_row`, that re-reads an already-staged `aftermath` step and
returns the mutations to apply (Fate decrement, wound/effect mutation, companion `status`
transition where the entity is a companion). None of this goes through the `propose`/`commit`
dice-rolling pipeline (docs/design/31-action-resolution.md) — a Fate spend rolls nothing, so it
does not belong in `_MECHANICS`/`_stage_request`'s dispatch, the same way `creation.py`'s
`create_character` is a plain function rather than a staged mechanic.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (existing project constraint)

**Primary Dependencies**: none new — reuses `wyrd.resolution._aftermath_band`,
`wyrd.character.validate_wound`, `wyrd.state`

**Storage**: N/A — mutations are returned/applied against in-memory character-entity
frontmatter dicts the same way every other `resolution.py` mutation already is; persistence is
`state.py`'s/`character.py`'s existing `save` job, unchanged by this feature

**Testing**: `pytest` (existing suite convention: `tests/engine/test_resolution.py`)

**Target Platform**: N/A — library code, no platform dependency

**Project Type**: single project (existing `engine/wyrd/` package)

**Performance Goals**: N/A — deterministic table lookups and dict mutations, no
performance-sensitive path

**Constraints**: stdlib-only (CLAUDE.md); the re-read mechanism must be deterministic in both
directions with no second roll (spec.md's Definition of Done); Fate may only be spent against a
`death` result, never at a distance, never improving any other row (spec.md FR-002)

**Scale/Scope**: two staging-time behaviours added to an existing function
(`_stage_aftermath`'s `mortal`/`mortality` parameters), one new standalone function
(`close_death_row`) plus its companion-status helper, and the CLI/verb surface needed to expose a
Fate spend as an operator-facing action

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Nothing unpublishable: no source-derived text is added — every row key, effect, and the
  Fate-closes-death-rows mechanism already live in `docs/design/06-aftermath.md` and
  `docs/adr/0009-fate-closes-the-death-rows.md`, both already published. PASS.
- No setting/system names: this feature adds no new vocabulary — it reuses `death`,
  `mortal`, `mortality`, `status` (`dead`/`away`) exactly as the design docs already name them.
  PASS.
- Tone stays a setting property: `mortality` is consumed as an opaque parameter
  (`low`/`standard`/`high`), never interpreted for register or narrative content — the same
  pattern `creation.py` already uses. PASS.
- Deterministic over inference: both re-read directions (mortal-critical-to-death,
  Fate-spend-off-death) are table lookups with no judgement call, per spec.md's Definition of
  Done; a check script asserts idempotence/determinism claims rather than eyeballing them. PASS.
- Rule changes apply forward only: N/A — new functionality, not a change to an existing rule.
  PASS.
- Capability change goes through Spec Kit: this plan. PASS.

No violations. Complexity Tracking is not needed.

## Project Structure

### Documentation (this feature)

```text
specs/092-mortal-blows-fate-death/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A — internal engine function, no external contract)
└── tasks.md             # Phase 2 output (kord-feature-tasks)
```

### Source Code (repository root)

```text
engine/
├── wyrd/
│   ├── resolution.py     # extend _stage_aftermath (mortal, mortality params);
│   │                     # add close_death_row and its companion-status helper
│   └── character.py      # unchanged — reused as-is (validate_wound, save)
tests/
└── engine/
    └── test_resolution.py  # extend AftermathTest: mortal-forcing, mortality:low closure,
                             # Fate spend re-read, companion-status transitions
tools/
└── check_death_row_determinism.py  # new check script asserting the re-read is deterministic
                                     # and idempotent across repeated resolutions (SC-002)
```

**Structure Decision**: Single project, extending the existing `engine/wyrd/resolution.py`
module in place — the same file `_stage_aftermath`/`_stage_critical` already live in, and the
same pattern `AftermathTest` already established in #252's PR. No new module is warranted for
two staging-time parameters and one standalone function.

## Complexity Tracking

*No violations — table omitted.*
