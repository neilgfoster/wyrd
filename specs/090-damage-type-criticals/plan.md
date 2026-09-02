# Implementation Plan: Damage-type critical tables

**Branch**: `090-damage-type-criticals` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/090-damage-type-criticals/spec.md`

## Summary

Extend critical resolution (`engine/wyrd/resolution.py`) from slashing-only to all four closed
damage types (slashing, piercing, blunt, searing), each reading its own row table from
`docs/design/05-criticals.md`. Introduces `damage_type` as a new caller-supplied parameter on a
`combat-attack` request, threaded the same way `weapon_dice`/`armour_dice` already are, defaulting
to `slashing` so every existing caller/test is unaffected. An unrecognized damage type is a
`ValueError` load error, matching the engine's existing convention for closed-set violations.

## Technical Context

**Language/Version**: Python 3.11+, standard library only (no new dependencies).

**Primary Dependencies**: None beyond what `engine/wyrd/` already uses.

**Storage**: N/A — this feature touches in-memory resolution logic and the character-entity wound
schema already defined in `engine/wyrd/character.py`; no new storage shape.

**Testing**: `pytest` (`tests/engine/`), plus a probability-check script under `specs/` following
the existing `specs/015-damage-type-criticals/check_criticals.py` convention.

**Target Platform**: Wherever the engine already runs — CLI (`client.py`) and MCP server
(`catalog.py`).

**Project Type**: Library/engine module (no frontend).

**Performance Goals**: N/A — table lookup is O(rows), unchanged in kind from today's
`critical-slashing`.

**Constraints**: stdlib-only (CLAUDE.md). No setting/system vocabulary in engine code
(CLAUDE.md). Deterministic-over-inference: probability claims are checked by script, not asserted
(ADR 0005).

**Scale/Scope**: Four fixed row tables (6 rows each), one new request parameter, one new
validation path.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Nothing unpublishable enters this repository.** This feature adds no source text, no
  setting-specific content — only engine mechanics already fully specified in
  `docs/design/05-criticals.md`. PASS.
- **No setting or system names.** Damage-type keys (`slashing`, `piercing`, `blunt`, `searing`)
  and row keys (`slashing-glancing`, etc.) are already the engine's own published vocabulary, not
  borrowed from any source system. PASS.
- **Tone is a setting property.** Row *descriptions* are the engine's defaults; nothing here bakes
  tone into a mechanic — descriptions stay overridable via `overrides.tables:` exactly as slashing
  already is. PASS.
- **Deterministic over inference (ADR 0005).** SC-001–SC-004 are all script-checked: exact row
  data cross-checked against `specs/015-damage-type-criticals/check_criticals.py`'s existing
  (already-validated) `TABLES` dict, boundary totals checked exhaustively, and the load-error path
  checked directly — no probability claim is eyeballed. PASS.
- **Rule changes apply forward only.** N/A — this is new capability, not a change to an existing
  rolled result. PASS.
- **Capability changes go through the Spec Kit cycle.** This plan is that cycle. PASS.

No violations. Complexity Tracking not needed.

## Project Structure

### Documentation (this feature)

```text
specs/090-damage-type-criticals/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/            # Phase 1 output
└── tasks.md              # Phase 2 output (kord-feature-tasks — not created by this command)
```

### Source Code (repository root)

This is a single-package engine repo (`engine/wyrd/`), not a multi-project layout. No new
directories are introduced.

```text
engine/wyrd/
├── resolution.py   # CRITICAL_*_TABLE constants (add 3), _critical_band (generalize from
│                    # _critical_slashing_band), _stage_critical (thread damage_type),
│                    # _normalize_request/_stage_request (thread damage_type parameter)
├── combat.py        # crowd_attack/_crowd_attack_request, resolve_ranged_attack: accept and
│                    # forward an optional damage_type
├── verbs.py          # thin CLI-facing wrapper: accept and forward damage_type
├── client.py         # CLI arg parsing: add --damage-type
└── catalog.py         # MCP tool schema: add damage_type to propose's inputSchema

tests/engine/
├── test_resolution.py   # new cases: each of the 3 new tables' boundaries, mortal handling,
│                          # unrecognized-type load error, default-to-slashing
└── test_combat.py        # new/updated cases: damage_type forwarded through crowd/ranged paths

specs/090-damage-type-criticals/
└── check_criticals_engine.py   # cross-checks the engine's own CRITICAL_*_TABLE constants
                                  # against specs/015's already-validated TABLES dict — reuse,
                                  # not re-derivation (SC-001, SC-002, SC-003)
```

**Structure Decision**: Single-package engine layout, unchanged from every prior feature in this
repo. No new top-level directories.

## Complexity Tracking

*No violations — table intentionally left empty.*
