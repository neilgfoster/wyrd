---

description: "Task list for adversary block loading and validation"
---

# Tasks: Adversary block loading and validation

**Input**: Design documents from `/specs/094-adversary-block-loading/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: included -- this is an engine correctness feature.

## Phase 1: Setup

None -- extends the existing `engine/wyrd/` project; no new dependencies.

## Phase 2: Foundational (Blocking Prerequisites)

- [ ] T001 Create `engine/wyrd/adversary.py` with the module docstring, and the constants
  mirroring `tools/check_bestiary.py`: `REQUIRED_FIELDS`, `OPTIONAL_FIELDS`, `ALL_FIELDS`,
  `ARMOUR_RANKS`, `DAMAGE_TYPES`, `SKILL_MIN`/`SKILL_MAX`, `STAMINA_MIN`, `TRAIT_EFFECTS`,
  `ID_RE`, `DAMAGE_RE` (data-model.md's validation-rules table).
- [ ] T002 Implement `validate_adversary(entry: dict) -> None` in `engine/wyrd/adversary.py`,
  raising `state.StateError` naming the id and field for the first (or, matching
  `check_entry`'s spirit, every) violation: missing required field, unrecognised field, `id`
  shape, `baseline`/`stamina_max`/`armour`/`skills` value checks, `damage`/`damage_type` shape
  and pairing, `ranged` type, `traits[n]` shape and closed-vocabulary effect keys.
- [ ] T003 Implement `load(id: str, path: pathlib.Path) -> dict` in `engine/wyrd/adversary.py`:
  read `path` via `state.parse_yaml`, find the `creatures` entry matching `id` (raising
  `state.StateError` naming the id and path if none matches), validate it via T002, default
  `ranged` to `False` when absent, and return the resulting mapping.

**Checkpoint**: the load/validate module exists; every user story below is a test pass over it.

## Phase 3: User Story 1 - Load one adversary block by id (Priority: P1) 🎯 MVP

- [ ] T004 [P] [US1] `test_load_valid_entry_by_id` in `tests/engine/test_adversary.py`: a
  well-formed bestiary file, load by id, assert every declared field is present and unchanged.
- [ ] T005 [P] [US1] `test_load_unknown_id_raises` in `tests/engine/test_adversary.py`: a
  bestiary file with entries, request an id not present, assert `StateError` naming the id.

## Phase 4: User Story 2 - Reject a malformed block (Priority: P2)

- [ ] T006 [P] [US2] `test_load_missing_required_field_raises` in
  `tests/engine/test_adversary.py`: an entry missing e.g. `baseline`, assert `StateError` naming
  `baseline`.
- [ ] T007 [P] [US2] `test_load_unrecognised_field_raises` in `tests/engine/test_adversary.py`:
  an entry with an extra field the block doesn't define, assert `StateError` naming it.
- [ ] T008 [P] [US2] `test_load_damage_without_damage_type_raises` and
  `test_load_damage_type_without_damage_raises` in `tests/engine/test_adversary.py`: each half
  of the pairing alone is rejected.
- [ ] T009 [P] [US2] `test_load_no_attack_at_all_is_legal` in `tests/engine/test_adversary.py`:
  an entry with neither `damage` nor `damage_type` loads successfully.
- [ ] T010 [P] [US2] `test_load_out_of_range_value_raises` in `tests/engine/test_adversary.py`:
  at least one out-of-range case each for `baseline`/`stamina_max`/`armour`/a `skills` value.
- [ ] T011 [P] [US2] `test_load_trait_outside_closed_vocabulary_raises` in
  `tests/engine/test_adversary.py`: a `traits[n].effect` key not in the closed six is rejected.

## Phase 5: User Story 3 - Optional fields default sensibly (Priority: P3)

- [ ] T012 [P] [US3] `test_load_ranged_defaults_false` in `tests/engine/test_adversary.py`: an
  entry omitting `ranged` loads with `ranged: False`.
- [ ] T013 [P] [US3] `test_load_ranged_true_passes_through` in `tests/engine/test_adversary.py`:
  an entry declaring `ranged: true` loads with `ranged: True`, unchanged.

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T014 Run `python3 -m pytest tests/engine/test_adversary.py -q` and the full suite
  (`ruff check . && ruff format --check . && python3 -m pytest -q`).
- [ ] T015 Walk through quickstart.md's three scenarios to confirm they match real behavior; fix
  quickstart.md if the API shape drifted during implementation.

## Dependencies & Execution Order

- Phase 2 (T001-T003) blocks every test task.
- T004-T013 are all `[P]` -- independent test functions in one new file, once Phase 2 lands.
- Phase 6 depends on Phases 2-5.
