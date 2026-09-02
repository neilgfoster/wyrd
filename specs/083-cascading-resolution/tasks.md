# Tasks: Cascading resolution

**Input**: Design documents from `specs/083-cascading-resolution/`
**Prerequisites**: plan.md, data-model.md, contracts/cli.md, quickstart.md, research.md

## Phase 1: Step/cascade plumbing

- [ ] **T001** Extend `resolution.py`'s internal proposal record with a `steps` list (Step:
      `step_id`, `mechanic`, `roll`, `mutations` tagged `produced_by_step`, `depends_on`);
      `propose`'s response gains `steps` while `roll`/`mutations` keep their #235 shape (FR-001,
      FR-010).
- [ ] **T002** Thread a deterministic seed sequence through a cascade: each internal roll (a
      `roll_d100` call, or each die of an `NdM` spec) uses `seed`, then `seed + 1`, and so on
      (research.md's Decision).
- [ ] **T003** Add a small `NdM` dice-spec roller (e.g. `_roll_dice("1d8", seed)`), local to
      `resolution.py`.
- [ ] **T004** Add a threshold-rule registry and the recursive check `propose` runs against every
      newly staged mutation (FR-002).

## Phase 2: Taint → Transformation cascade

- [ ] **T005** Implement the `transformation` mechanic: `1d6` against the six-row table
      (`docs/design/07-transformations.md`), severities `[1,1,2,2,3,4]`, unique-per-character
      (skip/re-roll a row already taken this cascade) (FR-007).
- [ ] **T006** Wire `taint` into the threshold registry: crossing a multiple of 3 stages a
      `transformation` step; its own Taint reduction is re-checked, repeating until Taint clears
      the threshold (FR-002, FR-008).
- [ ] **T007** Stage `dread += severity` and, on the character's first Transformation only, a
      `hidden_threshold` `set` mutation from a fresh `1d6 + 2` roll (FR-007).
- [ ] **T008** [P] `tests/engine/test_resolution.py`: reproduce research.md's Taint-into-
      Transformation worked example exactly (seed 5) — SC-002.
- [ ] **T009** [P] Test: the multi-reroll scenario (seed 7) resolves within one `propose` call,
      draws two distinct table rows, and clears the threshold — SC-003.
- [ ] **T010** [P] Test: a mutation that does not cross a threshold stages no `transformation`
      step.

## Phase 3: Combat chain

- [ ] **T011** Implement the `combat-attack` mechanic (an opposed test against `target`, reusing
      `rules.opposed_test`), reading telling directly off `degrees >= 6` (FR-003, per spec.md's
      Assumption that ADR 0044's virtual-roll symmetry is out of scope).
- [ ] **T012** On a landed attack, stage `weapon-damage` (doubled if telling) and `armour` steps,
      both depending on the attack step (FR-003, FR-004).
- [ ] **T013** Combine weapon-damage and armour into a Stamina mutation
      (`max(1, damage - armour)`), tagged to the armour step, then run it through the threshold
      registry for `stamina.current` crossing below 0 (FR-004, FR-005).
- [ ] **T014** Implement the `critical` mechanic: `critical-slashing` only, `1d6 + points below
      zero`, the six-row table from `docs/design/05-criticals.md` (FR-006).
- [ ] **T015** [P] `tests/engine/test_resolution.py`: reproduce research.md's combat-chain worked
      example exactly (seed 2) — SC-001.
- [ ] **T016** [P] Test: an attack that does not land stages no further step (User Story 1
      Scenario 5).
- [ ] **T017** [P] Test: a mortal-band critical (`21+`) stages no further step (User Story 3,
      SC-004).

## Phase 4: Integration

- [ ] **T018** `commit`/`discard` correctly apply/discard mutations drawn from multiple steps,
      atomically (extend #235's existing commit/discard tests with a multi-step proposal).
- [ ] **T019** `ruff check . && ruff format --check . && python3 -m pytest -q` clean (SC-005).

## Dependencies

- T001–T004 block Phase 2 and Phase 3.
- T005–T007 block T008–T010.
- T011–T014 block T015–T017.
- Phase 2 and Phase 3 are independent of each other once Phase 1 lands.
- T018–T019 run last.
