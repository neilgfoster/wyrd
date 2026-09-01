# Tasks: Propose/commit/discard core

**Input**: Design documents from `specs/082-propose-commit-core/`
**Prerequisites**: plan.md, data-model.md, contracts/cli.md, quickstart.md

## Phase 1: Core module

- [ ] **T001** Create `engine/wyrd/resolution.py`: `ProposalStore`-backed in-memory dict, the
      `Proposal`/`Mutation` shapes from `data-model.md`, and the mechanic registry with
      `ordinary-test` and `exposure` entries (FR-001–FR-003, FR-009).
- [ ] **T002** Implement `propose(actor, mechanic, skill, target, difficulty, declaration_bonus,
      *, state_path, seed)`: loads actor/target state via `state.py`/`character.py`, resolves
      via `rules.py`, computes mutations via the mechanic's `mutate`, stores an open Proposal,
      returns `{proposal_id, roll, mutations}` (FR-001, FR-002, FR-003, FR-004, FR-005).
- [ ] **T003** Implement `commit(proposal_id, *, state_path)`: looks up the open proposal,
      applies its mutations atomically via `state.py`'s atomic write, invalidates the id
      (FR-006).
- [ ] **T004** Implement `discard(proposal_id)`: writes nothing, invalidates the id (FR-007).
- [ ] **T005** `commit`/`discard` raise a distinct error (`resolution.ProposalError` or similar)
      for an id that is missing or already resolved (FR-008).
- [ ] **T006** `propose` raises `ValueError` for an unknown mechanic name, and for a named
      `target` that does not resolve to an existing entity (Edge Cases).

## Phase 2: Tests

- [ ] **T007** [P] `tests/engine/test_resolution.py`: reproduce the design document's Senna Vask
      worked example exactly (seed `20260852`, `bargaining: 40`, moderate Exposure tier) —
      roll 77, `effective_pct` 40, outcome fail, mutation `taint +2` (SC-001, User Story 1).
- [ ] **T008** [P] Test: state read immediately after `propose` is unchanged, for both a
      mutation-implying and a no-mutation outcome (SC-002, User Story 1 Scenario 3, User Story 2
      Scenario 1).
- [ ] **T009** [P] Test: `commit` applies exactly the staged mutations and nothing else; state
      after matches state before plus the mutation (SC-003, User Story 2 Scenario 2).
- [ ] **T010** [P] Test: `discard` leaves state exactly as before `propose` was called (SC-003,
      User Story 2 Scenario 3).
- [ ] **T011** [P] Test: `commit`/`discard` called twice on the same id raises an error the
      second time, for both commit-then-commit and commit-then-discard combinations (SC-004,
      User Story 3 Scenario 1/2).
- [ ] **T012** [P] Test: `commit`/`discard` against a fabricated/never-issued id raises an error
      (SC-004, User Story 3 Scenario 3).
- [ ] **T013** [P] Test: `propose` for an unknown mechanic, and for a nonexistent target entity,
      raises `ValueError` (Edge Cases).

## Phase 3: CLI/verbs integration

- [ ] **T014** Add `propose`/`commit`/`discard` wrappers to `engine/wyrd/verbs.py`, matching the
      existing verb style (thin pass-through to `resolution.py`, returning plain dicts).
- [ ] **T015** Wire `propose`/`commit`/`discard` CLI subcommands into `engine/wyrd/client.py`,
      matching `docs/design/02-architecture.md`'s existing sketch and `contracts/cli.md`.
- [ ] **T016** [P] `tests/engine/test_client.py`/`tests/engine/test_verbs.py`: cover the new CLI
      subcommands and verb wrappers at the same level of coverage as existing verbs.

## Phase 4: Polish

- [ ] **T017** `ruff check . && ruff format --check . && python3 -m pytest -q` clean (SC-005).
- [ ] **T018** Confirm `python3 tools/check_dangling_mechanics.py` and
      `python3 tools/check_docs.py` still pass (no design document is touched by this feature,
      but the check catches any accidental drift).

## Dependencies

- T001 blocks T002–T006.
- T002–T006 block all of Phase 2 (T007–T013).
- T002–T006 block Phase 3 (T014–T016).
- Phase 2 and Phase 3 tasks marked [P] are independent of each other within their own phase and
  may be done in any order once their phase's blocking tasks land.
- T017–T018 run last, after everything else.
