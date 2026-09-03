# Tasks: Adversary turn parity and the Aftermath exemption

- [x] **T001** Add `rolls_aftermath(entity_state)` to `engine/wyrd/resolution.py` -- true only
      for `type == "character"`; `None`/absent/other type false. (FR-001, FR-003, FR-005)
- [x] **T002** Give `_stage_aftermath` a required keyword-only `entity_state` and raise
      `ValueError` when `rolls_aftermath` is false, before any roll is made. (FR-002)
- [x] **T003** Update the 4 existing `_stage_aftermath` call sites in
      `tests/engine/test_resolution.py` to pass a character entity state.
- [x] **T004** Test: a bare adversary entity state (no `type`) is refused, and no step is
      appended -- the steps list is untouched. (US1)
- [x] **T005** Test: `type: character` with each of `role` player/companion/antagonist stages
      Aftermath identically for the same seed. (US2, FR-004)
- [x] **T006** Test: an adversary's critical resolves identically to a character's for the same
      damage and seed -- no adversary-specific branch. (US3, FR-007)
- [x] **T007** Test: the action list `combat.py` exposes carries no adversary-specific action.
      (US3, FR-006)
- [x] **T008** `ruff check . && ruff format --check . && PYTHONPATH=engine python3 -m pytest -q` green.
