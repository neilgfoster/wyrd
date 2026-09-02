---

description: "Task list for adversary trait effects"
---

# Tasks: Adversary trait effects

**Input**: Design documents from `/specs/096-adversary-trait-effects/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: included.

## Phase 1: Setup

None -- extends `engine/wyrd/adversary.py` (#259) and `engine/wyrd/rules.py`.

## Phase 2: Foundational

- [ ] T001 Add a `_trait_effect_values(traits, key)` helper in `engine/wyrd/adversary.py`:
  returns the list of `effect[key]` values across `traits` (or `[]` for `None`/empty traits) --
  shared by every trait computation below.
- [ ] T002 Add `omen_width: int = 0` to `rules._wyrd_die` in `engine/wyrd/rules.py`: units digit
  in `0..omen_width` reads `ill_omen`, in `(9-omen_width)..9` reads `fair_omen`, matching today's
  exact behavior at `omen_width=0`.
- [ ] T003 Thread `omen_width: int = 0` through `rules.opposed_test` in `engine/wyrd/rules.py`,
  passed straight to `_wyrd_die`.

**Checkpoint**: the shared helper and the wyrd-band plumbing exist; every user story below adds
its own computation on top.

## Phase 3: User Story 1 - stamina_max / armour_rank (Priority: P1) 🎯 MVP

- [ ] T004 [US1] Implement `effective_block(block)`'s `stamina_max` and `armour` computation in
  `engine/wyrd/adversary.py` (data-model.md): sum `stamina_max` trait effects, floor at
  `STAMINA_MIN`; shift `armour` along `ARMOUR_RANKS` by the summed `armour_rank` effects,
  clamped.
- [ ] T005 [P] [US1] `test_effective_block_stamina_max_trait` in
  `tests/engine/test_adversary.py`.
- [ ] T006 [P] [US1] `test_effective_block_armour_rank_trait_and_floor_clamp` in
  `tests/engine/test_adversary.py` (covers both the shift and the at-floor no-op case).

## Phase 4: User Story 2 - damage / damage_type (Priority: P1)

- [ ] T007 [US2] Implement `effective_block(block)`'s `damage`/`damage_type` computation in
  `engine/wyrd/adversary.py`: parse `block["damage"]` via `DAMAGE_RE`, adjust its dice count by
  the summed `damage` trait effects (floored at 1), reassemble; override `damage_type` with the
  last active `damage_type` trait effect, if any.
- [ ] T008 [P] [US2] `test_effective_block_damage_dice_trait_add_and_remove` in
  `tests/engine/test_adversary.py`.
- [ ] T009 [P] [US2] `test_effective_block_damage_dice_floor_at_one` in
  `tests/engine/test_adversary.py`.
- [ ] T010 [P] [US2] `test_effective_block_damage_type_trait_overrides` in
  `tests/engine/test_adversary.py`.
- [ ] T011 [P] [US2] `test_effective_block_no_traits_returns_unmodified_fields` in
  `tests/engine/test_adversary.py`.

## Phase 5: User Story 3 - difficulty ladder shift (Priority: P2)

- [ ] T012 [US3] Implement `shift_difficulty(base, rungs)` in `engine/wyrd/adversary.py`, using
  `tuple(resolution.DIFFICULTY_BONUSES)` for the ladder order.
- [ ] T013 [P] [US3] `test_shift_difficulty_moves_along_ladder` in
  `tests/engine/test_adversary.py`.
- [ ] T014 [P] [US3] `test_shift_difficulty_clamps_at_both_ends` in
  `tests/engine/test_adversary.py`.

## Phase 6: User Story 4 - wyrd band widening (Priority: P3)

- [ ] T015 [P] [US4] `test_wyrd_die_omen_width_zero_matches_existing_behavior` in
  `tests/engine/test_rules.py`.
- [ ] T016 [P] [US4] `test_wyrd_die_omen_width_widens_both_bands` in `tests/engine/test_rules.py`.
- [ ] T017 [US4] Implement `wyrd_band_width(block)` in `engine/wyrd/adversary.py`.
- [ ] T018 [P] [US4] `test_wyrd_band_width_sums_traits` in `tests/engine/test_adversary.py`.

## Phase 7: User Story 5 - stacking (Priority: P2)

- [ ] T019 [P] [US5] `test_effective_block_stacks_two_stamina_max_traits` in
  `tests/engine/test_adversary.py` (covered incidentally by T005 if written with two traits;
  keep as its own explicit test per the issue's own named acceptance criterion).

## Phase 8: Polish

- [ ] T020 Run `PYTHONPATH=engine python3 -m pytest tests/engine/test_adversary.py
  tests/engine/test_rules.py -q` and the full suite (`ruff check . && ruff format --check . &&
  PYTHONPATH=engine python3 -m pytest -q`).
- [ ] T021 Walk through quickstart.md to confirm it matches real behavior.

## Dependencies & Execution Order

- Phase 2 (T001-T003) blocks Phases 3-6.
- Phases 3-7 are independent of each other once Phase 2 lands.
- Phase 8 depends on all prior phases.
