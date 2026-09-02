# Tasks: Omen carryover

**Input**: Design documents from `specs/085-omen-carryover/`
**Prerequisites**: plan.md, data-model.md, contracts/cli.md, quickstart.md, research.md

## Phase 1: Shared staging core

- [ ] **T001** Add `_read_wyrd_omen(wyrd_die)`: `fair_omen` -> `+10`, `ill_omen` -> `-10`,
      otherwise `None` (FR-003).
- [ ] **T002** Extend `_stage_request` with `extra_depends_on: list[int] | None = None`, merged
      into the built top-level step's own `depends_on`.
- [ ] **T003** Add `_stage_requests(steps, ordered_requests, state_cache, seed_cursor,
      resource_deltas={})`: per-actor token tracking exactly per data-model.md's Relationships
      (FR-001–FR-006).

## Phase 2: Wire into `propose_batch` and `reroll`

- [ ] **T004** `propose_batch` calls `_stage_requests` once over its own normalized requests, in
      place of its previous per-request `_stage_request` loop.
- [ ] **T005** `reroll` collects every top-level request within the downstream set (not only the
      named step's own), in `step_id` order, and calls `_stage_requests` over all of them, with
      `resource_deltas={0: RESOURCE_MODIFIERS[resource]}` (FR-007).
- [ ] **T006** Update the two pre-existing #236/#237 tests whose already-seeded scenarios happen
      to read a Wyrd Omen, to expect the now-correctly-staged `pending_omen` mutation.

## Phase 3: Tests

- [ ] **T007** [P] `tests/engine/test_resolution.py`: reproduce research.md's main worked example
      (seed 40) — step 1's `effective_pct` modified, `depends_on` edge, staged `pending_omen`
      mutation (SC-001, User Story 1).
- [ ] **T008** [P] Test: reroll of step 0 in the same scenario (seed 1) discards step 1's
      original result and freshly re-resolves it with no stale dependency (SC-001, User Story 4).
- [ ] **T009** [P] Test: a persisted incoming `pending_omen` applies to a fresh proposal's first
      request with no `depends_on` edge, and survives `discard` untouched (SC-002, User Story 2).
- [ ] **T010** [P] Test: three same-actor requests (seed 59) demonstrate replace-not-stack and no
      spurious mutation when the final token equals the original (SC-003, SC-004, User Story 3).
- [ ] **T011** [P] Test: two unrelated actors in the same batch never see each other's Omens
      (Edge Cases).

## Phase 4: Polish

- [ ] **T012** `ruff check . && ruff format --check . && python3 -m pytest -q` clean (SC-005).
- [ ] **T013** `python3 tools/check_docs.py` still passes (no design document is touched).

## Dependencies

- T001–T003 block T004–T006.
- T004–T006 block Phase 3.
- Phase 3 tasks are independent of each other.
- T012–T013 run last.
