---

description: "Task list for adversary baseline skill resolution"
---

# Tasks: Adversary baseline skill resolution

**Input**: Design documents from `/specs/095-adversary-baseline-resolution/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: included.

## Phase 1: Setup

None -- extends the existing `engine/wyrd/adversary.py` module from #259.

## Phase 2: Foundational

- [ ] T001 Implement `resolve_skill(block: dict, skill: str) -> int` in
  `engine/wyrd/adversary.py`: return `block["skills"][skill]` if `skill` is a key of
  `block["skills"]`, else `block["baseline"]`.

## Phase 3: User Story 1 - unlisted skill resolves at baseline (P1) 🎯 MVP

- [ ] T002 [P] [US1] `test_resolve_skill_unlisted_returns_baseline` in
  `tests/engine/test_adversary.py`.

## Phase 4: User Story 2 - listed skill resolves at its own value, never raised to baseline (P2)

- [ ] T003 [P] [US2] `test_resolve_skill_listed_returns_listed_value` in
  `tests/engine/test_adversary.py`.
- [ ] T004 [P] [US2] `test_resolve_skill_listed_below_baseline_not_raised` in
  `tests/engine/test_adversary.py`: a listed skill below `baseline` returns its own (lower)
  value.

## Phase 5: User Story 3 - independence from the untrained-10% path (P3)

- [ ] T005 [P] [US3] `test_resolve_skill_baseline_equal_to_untrained_still_reads_block` in
  `tests/engine/test_adversary.py`: `baseline` set to `rules.UNTRAINED_SKILL`'s value; confirm
  the result traces to the block's own field (changing the block's `baseline` changes the
  result; the constant is incidental).
- [ ] T006 [P] [US3] `test_select_group_skill_unaffected_by_adversary_resolution` in
  `tests/engine/test_adversary.py` (or alongside existing `rules.py` tests): confirm
  `rules.select_group_skill`'s behavior with a `None` member is untouched by this feature's
  addition.

## Phase 6: Polish

- [ ] T007 Run `PYTHONPATH=engine python3 -m pytest tests/engine/test_adversary.py -q` and the
  full suite (`ruff check . && ruff format --check . && PYTHONPATH=engine python3 -m pytest -q`).
- [ ] T008 Walk through quickstart.md to confirm it matches real behavior.

## Dependencies & Execution Order

- T001 blocks T002-T006.
- T002-T006 are all `[P]`.
