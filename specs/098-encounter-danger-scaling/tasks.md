---

description: "Task list for encounter danger scaling"
---

# Tasks: Encounter danger scaling

**Input**: Design documents from `/specs/098-encounter-danger-scaling/`

**Prerequisites**: plan.md, spec.md

**Tests**: included.

## Phase 1: Setup

None -- extends `engine/wyrd/adversary.py` (#259/#260).

## Phase 2: Foundational

- [ ] T001 Add `effective_party_size(bodies: int) -> Fraction` to `engine/wyrd/adversary.py`:
  the exact sum `1 + 1/2 + ... + 1/bodies` (ADR 0024). `bodies <= 0` returns `Fraction(0)`.
- [ ] T002 Add `danger_ratio(party: int, written_for: int) -> Fraction` to
  `engine/wyrd/adversary.py`: `effective_party_size(party) / effective_party_size(written_for)`,
  or exactly `Fraction(1)` when `written_for` is missing/zero (docs/design/03-rules.md section
  7).

**Checkpoint**: the shared effective-size and ratio helpers exist; every user story below builds
on them.

## Phase 3: User Story 1 - the identity case (Priority: P1) 🎯 MVP

- [ ] T003 [US1] Add `danger_effective(danger, party, written_for) -> Fraction` to
  `engine/wyrd/adversary.py`: `danger * danger_ratio(party, written_for)`, never rounded.
- [ ] T004 [US1] Add `scaled_count(written_count, danger, party, written_for) -> int` to
  `engine/wyrd/adversary.py`: `written_count * danger_effective(...) / danger`, rounded half up,
  floored at 1 when `written_count >= 1`, left as-is (0) otherwise.
- [ ] T005 [P] [US1] `test_scaled_count_identity_case` in `tests/engine/test_adversary.py`
  (`party == written_for` reproduces the written count exactly).
- [ ] T006 [P] [US1] `test_danger_effective_identity_case` in `tests/engine/test_adversary.py`.

## Phase 4: User Story 2 - a smaller party thins and eases (Priority: P1)

- [ ] T007 [US2] Add `skill_adjustment(party, written_for) -> int` to
  `engine/wyrd/adversary.py`: `15.5 * log2(ratio)`, rounded half up to the nearest 5, clipped to
  `[-20, +20]`.
- [ ] T008 [US2] Add `adjusted_skill(block, skill, party, written_for) -> int` to
  `engine/wyrd/adversary.py`: `resolve_skill(block, skill) + skill_adjustment(party,
  written_for)`, floored at 0.
- [ ] T009 [P] [US2] `test_danger_effective_worked_example_three_of_four` in
  `tests/engine/test_adversary.py` (`danger_effective == Fraction(66, 25)` i.e. `2.64` exactly).
- [ ] T010 [P] [US2] `test_scaled_count_worked_example_six_cultists_to_five` in
  `tests/engine/test_adversary.py`.
- [ ] T011 [P] [US2] `test_scaled_count_worked_example_three_watchmen_stays_three` in
  `tests/engine/test_adversary.py`.
- [ ] T012 [P] [US2] `test_skill_adjustment_smaller_party_is_non_positive` in
  `tests/engine/test_adversary.py`.
- [ ] T013 [P] [US2] `test_skill_adjustment_matches_published_table` in
  `tests/engine/test_adversary.py` -- every `party`/`written_for` pair 1..6 against
  docs/design/03-rules.md section 7's printed table.

## Phase 5: User Story 3 - a larger party thickens and toughens (Priority: P2)

- [ ] T014 [P] [US3] `test_scaled_count_larger_party_at_least_written_count` in
  `tests/engine/test_adversary.py`.
- [ ] T015 [P] [US3] `test_skill_adjustment_larger_party_is_non_negative` in
  `tests/engine/test_adversary.py`.

## Phase 6: User Story 4 - never mutates the source block (Priority: P1)

- [ ] T016 [P] [US4] `test_adjusted_skill_does_not_mutate_block` in
  `tests/engine/test_adversary.py`: snapshot a block, call `adjusted_skill` twice at two
  different `party`/`written_for` pairs, assert the block dict is unchanged and the two results
  can differ.

## Phase 7: Edge cases and identity-diagonal coverage

- [ ] T017 [P] `test_danger_ratio_missing_written_for_runs_as_written` in
  `tests/engine/test_adversary.py` (`written_for` `None`/0 both yield ratio 1).
- [ ] T018 [P] `test_adjusted_skill_floors_at_zero` in `tests/engine/test_adversary.py`.
- [ ] T019 [P] `test_scaled_count_zero_written_count_stays_zero` in
  `tests/engine/test_adversary.py`.
- [ ] T020 [P] `test_identity_diagonal_every_size_one_to_six` in
  `tests/engine/test_adversary.py`: for every `n` 1..6, `party == written_for == n` reproduces
  the written count and a zero skill adjustment.

## Phase 8: Polish

- [ ] T021 `python3 -m ruff check . && python3 -m ruff format --check .`
- [ ] T022 `PYTHONPATH=engine python3 -m pytest -q`

## Dependencies & Execution Order

- Phase 2 (T001-T002) blocks every later phase.
- Phase 3 (T003-T004) blocks Phase 4's `skill_adjustment`/`adjusted_skill` only insofar as both
  live in the same module; no functional dependency between them.
- Phases 3-6 tests are independent of each other ([P]) once Phase 2 lands.
- Phase 7-8 last.
