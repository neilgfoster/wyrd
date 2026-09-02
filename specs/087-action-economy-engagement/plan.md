# Implementation Plan: Action economy and engagement

**Branch**: `244-action-economy-engagement` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/087-action-economy-engagement/spec.md`

## Summary

Extends `engine/wyrd/combat.py` (#243) with engagement tracking (a set of pairs) and a per-round
"acted" set, both nested in the same persisted `combat` scene dict. `close`/`break_off` mutate
that state; `break_off` also calls `resolution.propose_batch` (unchanged signature) to stage the
parting-blow attacks. `ranged_attack_difficulty` and `resolve_ranged_attack` compute the two
named difficulty rows and the ally-redirect, composing through `resolution.propose`'s existing
`declaration_bonus` parameter — fixed in this same PR so `combat-attack` actually respects it
(spec.md Assumptions).

## Technical Context

**Language/Version**: Python 3.11+, stdlib only.

**Primary Dependencies**: none beyond stdlib — extends `engine/wyrd/combat.py` (#243) and
`engine/wyrd/resolution.py` (the `declaration_bonus` fix).

**Storage**: chronicle-level state, same `combat` key #243 already established.

**Testing**: `pytest`, `ruff check .`, `ruff format --check .`.

**Target Platform**: CLI/library, same as `engine/wyrd/`.

**Project Type**: single project, extending the existing `engine/wyrd/` layout.

**Performance Goals**: N/A.

**Constraints**: `break_off` never rolls to leave — only the parting blow(s) it stages roll.
`close`/`break_off` never invalidate an in-progress `resolution` proposal; they operate on
separate state (the `combat` scene vs. a `resolution` proposal).

**Scale/Scope**: exactly spec.md's four user stories. No escape/pursuit (#245), no crowd rule
(#246).

## Constitution Check

- No setting/system names — `close`, `break_off`, `engaged`, Difficult/Challenging are the
  engine's own vocabulary, matching `docs/design/03-rules.md` §1's difficulty ladder and §2
  directly.
- Deterministic over inference — the ally-redirect reads the Wyrd die already computed by
  `resolution.propose`, never infers "hit the ally" from anything else.
- Capability change — goes through the Spec Kit cycle, `specs/` committed.
- No new ADR: implements what `docs/design/03-rules.md` §2 already specifies; the
  `declaration_bonus` fix corrects an implementation gap against #211's own already-accepted
  design, not a new decision.

**PASS** — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/087-action-economy-engagement/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md
```

### Source Code (repository root)

```text
engine/wyrd/
├── combat.py           # extended: close, break_off, has_acted, ranged_attack_difficulty,
│                        # resolve_ranged_attack
└── resolution.py        # fixed: combat-attack now respects request["declaration_bonus"]

tests/engine/
├── test_combat.py       # extended
└── test_resolution.py   # extended: one regression test for the declaration_bonus fix
```

**Structure Decision**: Continues extending `combat.py` (#243) rather than a new module —
engagement and action economy are the same scene-level layer turn order already lives in.

## Complexity Tracking

*No violations — table omitted.*
