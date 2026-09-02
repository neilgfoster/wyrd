# Tasks: Action economy and engagement

**Input**: Design documents from `specs/087-action-economy-engagement/`
**Prerequisites**: plan.md, data-model.md, contracts/cli.md, quickstart.md, research.md

## Phase 1: `resolution.py` fix

- [ ] **T001** Fix `_stage_request`'s `combat-attack` branch to add `request["declaration_bonus"]`
      into the attacker's skill boost, not only `declaration_bonus_delta` (spec.md Assumptions;
      required for T004/T005 below to work through the existing channel).
- [ ] **T002** [P] `tests/engine/test_resolution.py`: a regression test that `propose(...,
      mechanic="combat-attack", declaration_bonus=-20)` changes `effective_pct` accordingly.

## Phase 2: Engagement and action economy

- [ ] **T003** Extend `combat.py`'s scene shape with `engaged` (list of `{"a", "b"}` dicts —
      research.md's own finding on why not a two-element list) and `acted` (list); initialize
      both in `start_combat`, clear `acted` in `advance_round` (FR-001, FR-003).
- [ ] **T004** Implement `has_acted`, `engaged_with`, `is_engaged` (FR-003).
- [ ] **T005** Implement `close` (FR-002).
- [ ] **T006** Implement `break_off`, via `resolution.propose_batch` (FR-004, FR-005).

## Phase 3: Ranged attacks

- [ ] **T007** Implement `ranged_attack_difficulty` (FR-006, FR-007).
- [ ] **T008** Implement `resolve_ranged_attack`, including the ally-redirect on Ill Omen
      (FR-007, FR-008).

## Phase 4: Tests

- [ ] **T009** [P] `tests/engine/test_combat.py`: closing creates the pair and marks acted;
      closing again the same round raises (SC-001, User Story 1).
- [ ] **T010** [P] Test: breaking off against one and against two opponents stages the correct
      number of `combat-attack` proposals, each targeting the departing combatant, and removes
      the engagement pairs (SC-002, User Story 2).
- [ ] **T011** [P] Test: breaking off with no engagements stages nothing (FR-005).
- [ ] **T012** [P] Test: `break_off` raises when `opponent_attacks` doesn't exactly match
      `engaged_with(actor)`.
- [ ] **T013** [P] Test: an engaged shooter's ranged attack `effective_pct` differs from an
      unengaged one's by exactly the Difficult modifier, reproducing research.md's seed 2
      scenario exactly (SC-003).
- [ ] **T014** [P] Test: both branches of the ally-redirect (seed 5 redirects, seed 1 doesn't),
      reproducing research.md exactly (SC-004).

## Phase 5: Polish

- [ ] **T015** `ruff check . && ruff format --check . && python3 -m pytest -q` clean (SC-005).
- [ ] **T016** `python3 tools/check_docs.py` still passes (no design document is touched).

## Dependencies

- T001 blocks T002 and Phase 3.
- T003 blocks T004–T006.
- T004–T006 block Phase 4's engagement tests (T009–T012).
- T007–T008 block Phase 4's ranged tests (T013–T014).
- T015–T016 run last.
