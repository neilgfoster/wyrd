# Implementation Plan: Turn order and round structure

**Branch**: `243-turn-order-round-structure` | **Date**: 2026-09-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/086-turn-order-round-structure/spec.md`

## Summary

New module `engine/wyrd/combat.py`: a pure function `determine_first_actor` implementing
`docs/design/03-rules.md` §2's exchange-starter/armed-side/player-side rule, plus a small
persisted-state API (`start_combat`, `advance_round`, `can_act`, `attack_modifier`) reading/
writing a `combat` key in chronicle state via `state.py`'s existing atomic save/load. No change
to `resolution.py` — this feature reports the numbers a caller (the GM layer, or a future scene-
orchestration feature) consults before deciding whose turn it is and what modifier to pass into
`propose`'s own `declaration_bonus`.

## Technical Context

**Language/Version**: Python 3.11+, stdlib only.

**Primary Dependencies**: none beyond stdlib — extends `engine/wyrd/state.py`'s chronicle-state
read/write.

**Storage**: chronicle-level state (`state.py`'s `chronicle_state.yaml`), not per-entity — a
combat scene is chronicle-scoped (spec.md Assumptions).

**Testing**: `pytest`, `ruff check .`, `ruff format --check .`.

**Target Platform**: CLI/library, same as `engine/wyrd/`.

**Project Type**: single project, extending the existing `engine/wyrd/` layout.

**Performance Goals**: N/A.

**Constraints**: Starting a combat, advancing a round, and querying `can_act`/`attack_modifier`
must all go through the existing atomic chronicle-state write path — no new persistence
mechanism.

**Scale/Scope**: exactly spec.md's four user stories — first-actor determination, round
advancement, surprise, ambush. No engagement/action-economy state (#244), no escape (#245), no
crowd rule (#246) — those are separate sibling features.

## Constitution Check

- No setting/system names — `combat`, `side`, `surprised`, `ambush` are the engine's own
  vocabulary, matching `docs/design/03-rules.md` §2 and ADR 0018 directly.
- Deterministic over inference — first-actor determination is a pure function over stated inputs,
  never inferred from prose.
- Capability change — goes through the Spec Kit cycle, `specs/` committed.
- No new ADR: implements what ADR 0018 (already accepted) and `03-rules.md` §2 already specify.

**PASS** — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/086-turn-order-round-structure/
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
└── combat.py          # NEW: determine_first_actor, start_combat, advance_round, can_act,
                        # attack_modifier

tests/engine/
└── test_combat.py      # NEW
```

**Structure Decision**: A new `combat.py` module, parallel to `rules.py` (pure resolution
primitives) and `resolution.py` (propose/commit/discard) — this is a third, distinct layer:
scene-level state, not roll resolution. Following the existing `rules.py`→verbs.py→`client.py`
pattern for its own CLI surface is left to a later pass once #244/#245/#246 exist and the
combined CLI shape is clearer (this feature's own acceptance criteria don't require a CLI
subcommand — spec.md's Assumptions frame turn-order enforcement as the caller's responsibility,
consulted via the library API directly).

## Complexity Tracking

*No violations — table omitted.*
