# Tasks: Partial reroll

**Input**: Design documents from `specs/084-partial-reroll/`
**Prerequisites**: plan.md, data-model.md, contracts/cli.md, quickstart.md, research.md

## Phase 1: Batch proposals

- [ ] **T001** Add `_normalize_request`/`_stage_request`, factoring the existing single-mechanic
      staging logic out of `propose` into a reusable function taking a `request` dict and a
      shared scratch-state cache, tagging the top-level step's `inputs` (FR — data-model.md).
- [ ] **T002** Add `propose_batch(requests, *, seed=None)`: shared `_SeedCursor` and state cache
      across all requests, each staged via `_stage_request`.
- [ ] **T003** `propose` becomes a single-request call to `propose_batch`; existing tests
      (#235/#236) must pass unchanged.
- [ ] **T004** [P] `tests/engine/test_resolution.py`: reproduce research.md's independent-branch
      scenario (seed 20260854) via `propose_batch` alone (no reroll yet) — matches the design
      doc's own two rolls exactly.

## Phase 2: `reroll` core

- [ ] **T005** Add `_downstream_set(steps, step_id)`: transitive closure over `depends_on`
      (FR-001).
- [ ] **T006** Add `_renumber_and_merge(kept_steps, new_steps, original_step_id)`: rerolled step
      keeps its own id; further new steps get fresh, non-colliding ids (FR-010).
- [ ] **T007** Add `reroll(proposal_id, step, resource, *, seed=None)`: resolve the downstream
      set, discard it, rebuild scratch state from kept steps' own mutations, re-stage via
      `_stage_request` with the resource's `declaration_bonus_delta`, append the resource's cost
      mutation, merge, update the open proposal in place (FR-001–FR-003, FR-007, FR-008).
- [ ] **T008** `reroll` raises for an unknown resource, unknown step, or a step with no recorded
      `inputs` (FR-009).

## Phase 3: Tests

- [ ] **T009** [P] `tests/engine/test_resolution.py`: reroll against step 0 of the independent-
      branch proposal (Bargain, seed 5) reproduces research.md's SC-001 numbers exactly — step 1
      untouched, step 0's mutations combine the fresh roll's own implied mutation with the
      Bargain's cost.
- [ ] **T010** [P] Test: rerolling a step that originally staged a Transformation cascade removes
      the stale cascade step(s) and stages a fresh one (Fortune, seed 6, SC-002) — reproduces
      research.md's differing-row scenario exactly.
- [ ] **T011** [P] Test: each of Resolve/Fortune/Bargain applies its own `effective_pct` modifier
      and cost mutation (seed 1, SC-003), matching research.md exactly.
- [ ] **T012** [P] Test: `commit` after a reroll applies the revised mutations, not the original
      ones (SC-004).
- [ ] **T013** [P] Test: `reroll` does not invalidate the proposal id — a second `reroll` against
      a different step, then `commit`, both succeed.
- [ ] **T014** [P] Test: `reroll` against an internal cascade-only step (e.g. a `transformation`
      or `critical` step id) raises `ValueError`.
- [ ] **T015** [P] Test: `reroll` against an unknown step id, an unknown resource, and a
      closed (already committed/discarded) proposal each raise the correct error.

## Phase 4: Polish

- [ ] **T016** `ruff check . && ruff format --check . && python3 -m pytest -q` clean (SC-005).
- [ ] **T017** `python3 tools/check_docs.py` still passes (no design document is touched).

## Dependencies

- T001–T003 block T004 and all of Phase 2.
- T005–T008 block Phase 3.
- Phase 3 tasks are independent of each other.
- T016–T017 run last.
