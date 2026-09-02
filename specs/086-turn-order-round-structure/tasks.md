# Tasks: Turn order and round structure

**Input**: Design documents from `specs/086-turn-order-round-structure/`
**Prerequisites**: plan.md, data-model.md, contracts/cli.md, quickstart.md, research.md

## Phase 1: Core module

- [ ] **T001** Create `engine/wyrd/combat.py`; implement `determine_first_actor` (pure function,
      FR-002).
- [ ] **T002** Implement `start_combat`: validates `started_by`/`player_side`, computes
      `first_actor`, writes `{"combat": {...}}` into chronicle state via `state.py` (FR-001,
      FR-003).
- [ ] **T003** Implement `advance_round` (FR-004).
- [ ] **T004** Implement `can_act` (FR-005) and `attack_modifier` (FR-006).

## Phase 2: Tests

- [ ] **T005** [P] `tests/engine/test_combat.py`: `determine_first_actor` for all four
      combinations in research.md (explicit starter; mutual + one armed; mutual + both armed;
      mutual + neither armed) — SC-001.
- [ ] **T006** [P] Test: `start_combat` raises `ValueError` for an unknown `started_by`/
      `player_side` (Edge Cases).
- [ ] **T007** [P] Test: `can_act` for a surprised side is `False` in round 1, `True` after
      `advance_round` — SC-002.
- [ ] **T008** [P] Test: `attack_modifier` for an ambushing side is `20` in round 1, `0` after
      `advance_round` — SC-003.
- [ ] **T009** [P] Test: a `resolution.propose` `combat-attack` against a surprised side's
      member resolves unaffected (User Story 3 Scenario 2) — confirms this feature adds no
      defensive penalty of its own.

## Phase 3: Polish

- [ ] **T010** `ruff check . && ruff format --check . && python3 -m pytest -q` clean (SC-004).
- [ ] **T011** `python3 tools/check_docs.py` still passes (no design document is touched).

## Dependencies

- T001 blocks T002–T004.
- T002–T004 block Phase 2.
- Phase 2 tasks are independent of each other.
- T010–T011 run last.
