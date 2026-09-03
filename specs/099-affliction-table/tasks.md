---

description: "Task list for the affliction table and Trauma-test cascade"
---

# Tasks: Affliction table and Trauma-test cascade

**Input**: Design documents from `/specs/099-affliction-table/`

**Prerequisites**: plan.md, spec.md

**Tests**: included.

## Phase 1: Setup

None -- extends `engine/wyrd/resolution.py` (the existing cascading-resolution mechanism,
specs/083-cascading-resolution).

## Phase 2: Foundational

- [ ] T001 Add `AFFLICTION_TABLE` to `engine/wyrd/resolution.py`: the twelve rows of
  docs/design/08-afflictions.md ("The table"), row (1-12, the `1d12` result) -> effect data
  sufficient to stage a mutation or a durable standing-condition entry, no severity field.
- [ ] T002 Add `TRAUMA_FLOOR = 6` and `AFFLICTION_TRAUMA_COST = 6` to
  `engine/wyrd/resolution.py` (docs/design/08-afflictions.md "6 is the floor, not itself a
  further point"; docs/design/03-rules.md section 5 "take an Affliction and lose 6 Trauma").

**Checkpoint**: the table data and constants exist; every user story below builds on them.

## Phase 3: User Story 1 - crossing the floor stages a test, not an Affliction outright (P1) 🎯 MVP

- [ ] T003 [US1] Add a `terror` entry to `_MECHANICS`/`_PUBLIC_MECHANICS` in
  `engine/wyrd/resolution.py` (resolve/mutate pair): an ordinary pass/fail test against a
  caller-supplied skill, mirroring `_resolve_exposure`/`_mutate_exposure`; failure stages
  `trauma +1` (docs/design/03-rules.md section 5: "1 per failed Terror test"), tagged with the
  Trauma-test skill the caller supplied for the *next* cascade step; success stages nothing.
  This is the cascade's public entry point.
- [ ] T004 [US1] Add a `trauma-test` entry to `_MECHANICS` in `engine/wyrd/resolution.py`
  (resolve/mutate pair, internal-only -- not in `_PUBLIC_MECHANICS`): an ordinary pass/fail
  `d100` test against a caller-supplied skill (docs/design/08-afflictions.md "the engine names
  no skill"), reading no Wyrd-die degree.
- [ ] T005 [US1] Add a `trauma`-crossing branch to `_cascade_from_mutation` in
  `engine/wyrd/resolution.py`: for a `trauma` mutation, stage one `trauma-test` step per integer
  point strictly greater than `TRAUMA_FLOOR` that the mutation causes `trauma` to pass through or
  land on, in gained order -- landing on exactly `TRAUMA_FLOOR` from below stages nothing. The
  test's skill is read from the triggering mutation's own `trauma_test_skill` key (threaded
  through from the `terror` request's own `skill`, T003).
- [ ] T006 [P] [US1] `test_trauma_reaching_floor_exactly_stages_no_test` in
  `tests/engine/test_resolution.py` (5 -> 6 via `terror` stages zero `trauma-test` steps).
- [ ] T007 [P] [US1] `test_trauma_crossing_past_floor_stages_one_test` in
  `tests/engine/test_resolution.py` (6 -> 7 via `terror` stages exactly one `trauma-test` step).

## Phase 4: User Story 2 - one event crossing multiple points stages one test per point (P1)

- [ ] T008 [P] [US2] `test_trauma_multi_point_gain_stages_one_test_per_point` in
  `tests/engine/test_resolution.py`: a character already at Trauma 5 who takes a further staged
  `trauma +3` mutation (e.g. via `propose_batch` composing two `terror` failures, or a directly
  constructed multi-point mutation) has exactly two `trauma-test` steps staged, for 7 then 8,
  each `depends_on` the previous in gained order.

## Phase 5: User Story 3 - a failed Trauma test rolls the affliction table (P1)

- [ ] T009 [US3] Add `_stage_affliction_roll` to `engine/wyrd/resolution.py`: rolls `1d12`
  against `AFFLICTION_TABLE`, stages the resulting row's effect via the existing
  points-modifier/difficulty-ladder mutation vocabulary (or a durable `afflictions` entry for a
  standing-condition row) plus a flat `trauma -AFFLICTION_TRAUMA_COST` mutation, `depends_on` the
  failed `trauma-test` step.
- [ ] T010 [US3] Wire a failed `trauma-test` outcome to call `_stage_affliction_roll`; a passed
  outcome stages nothing further (mirrors `_mutate_exposure`'s success/fail branch).
- [ ] T011 [P] [US3] `test_failed_trauma_test_stages_affliction_roll_and_loses_six_trauma` in
  `tests/engine/test_resolution.py`.
- [ ] T012 [P] [US3] `test_passed_trauma_test_stages_nothing_further` in
  `tests/engine/test_resolution.py`.

## Phase 6: User Story 4 - the affliction table is repeatable (P2)

- [ ] T013 [P] [US4] `test_duplicate_affliction_row_is_applied_not_rerolled` in
  `tests/engine/test_resolution.py`: a character who has already taken row 3, forced to roll row
  3 again, has it applied as-is (contrast with `_stage_transformation_chain`'s re-roll-on-
  duplicate).

## Phase 7: Edge cases

- [ ] T014 [P] `test_trauma_never_reaching_floor_stages_no_test` in
  `tests/engine/test_resolution.py`.
- [ ] T015 [P] `test_affliction_table_has_twelve_rows_no_severity_field` in
  `tests/engine/test_resolution.py`.
- [ ] T016 [P] `test_check_affliction_cadence_unaffected` in `tests/engine/test_resolution.py` (or
  a direct run of `tools/check_affliction.py`): confirms this feature does not change the
  published sawtooth-cadence figures (SC-005).

## Phase 8: Polish

- [ ] T017 `python3 -m ruff check . && python3 -m ruff format --check .`
- [ ] T018 `PYTHONPATH=engine python3 -m unittest discover -s tests -p "test_*.py" -q`

## Dependencies & Execution Order

- Phase 2 (T001-T002) blocks every later phase.
- Phase 3 (T003-T005) blocks Phase 5 (T009-T010): the affliction roll is staged from a failed
  `trauma-test` step, which does not exist until Phase 3 lands.
- Phase 4's test builds on Phase 3's cascade branch but adds no new production code.
- Phase 6's test builds on Phase 5.
- Phase 7-8 last.
