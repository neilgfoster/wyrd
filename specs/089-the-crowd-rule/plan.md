# Implementation Plan: The crowd rule

**Branch**: `089-the-crowd-rule` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/089-the-crowd-rule/spec.md`

## Summary

Adds crowd support to `engine/wyrd/combat.py` (#243/#244): `is_crowd_member` (the three-part
qualification lookup), `crowd_ease` (the body-count ease table), `register_crowd`/
`crowd_body_count`/`clear_crowd_member` (body-count tracking nested in the same chronicle-scoped
`combat` scene, under a new `crowds` key), and `crowd_attack`/`crowd_parting_blow` (both stage
exactly one `combat-attack` request via `resolution.propose_batch`, eased by `crowd_ease` of the
crowd's current body count against that target). No new resolution mechanic — the crowd's own
attack and parting blow both go through the same `combat-attack` mechanic every other attack in
this engine already uses, via the `declaration_bonus` channel #244's PR already fixed to apply to
`combat-attack`.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only.

**Primary Dependencies**: none beyond stdlib — extends `engine/wyrd/combat.py` (#243/#244/#245)
and calls `resolution.propose_batch` unchanged (the same `combat-attack` request shape
`break_off` already uses, plus its existing `declaration_bonus` field).

**Storage**: chronicle-level state, the same `combat` key #243 established, extended with a
`crowds` dict (`{"<crowd path>": <remaining body count>}`).

**Testing**: `pytest`, `ruff check .`, `ruff format --check .`.

**Target Platform**: CLI/library, same as `engine/wyrd/`.

**Project Type**: single project, extending the existing `engine/wyrd/` layout.

**Performance Goals**: N/A.

**Constraints**: the crowd's own attack and parting blow are always exactly one
`resolution.propose_batch` request, never one per body. `clear_crowd_member` never rolls and
never touches `acted` (docs/design/03-rules.md: "without a roll and without spending their
action").

**Scale/Scope**: exactly spec.md's one user story (crowd fight resolution: lookup, free clear,
crowd attack, crowd parting blow). No Aftermath implementation (#213, not yet built) — FR-007 is
satisfied by this feature simply never providing or calling any such entry point for a crowd.

## Constitution Check

- No setting/system names — `crowd`, `is_crowd_member`, `crowd_ease` are the engine's own
  vocabulary, matching `docs/design/03-rules.md` §2's own "Crowds" language directly.
- Deterministic over inference — the qualification thresholds and the ease table are fixed
  constants read directly from the design document's own stated numbers, not derived or
  guessed.
- Capability change — goes through the Spec Kit cycle, `specs/` committed.
- No new ADR: implements what `docs/design/03-rules.md` §2 and ADR 0019 already specify — not a
  new decision, and ADR 0019 is not superseded (its one-blow/skill-gap reasoning is exactly
  what FR-001 encodes).

**PASS** — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/089-the-crowd-rule/
├── plan.md              # This file
├── tasks.md             # Phase 2 output
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
engine/wyrd/
└── combat.py             # + is_crowd_member, crowd_ease, register_crowd, crowd_body_count,
                           #   clear_crowd_member, crowd_attack, crowd_parting_blow

tests/engine/
└── test_combat.py         # + crowd rule tests
```

**Structure Decision**: extends the existing single-project `engine/wyrd/` layout; no new
modules. Crowd functions live in `combat.py` alongside `close`/`break_off`/`escape_scene`, since
docs/design/03-rules.md §2 treats "Crowds" as part of the same section.

## Complexity Tracking

No constitution violations — table not needed.
