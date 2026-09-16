---
description: "Task list for Anti-inflation checks for generated content (issue #421)"
---

# Tasks: Anti-inflation checks for generated content

**Input**: Design documents from `specs/163-anti-inflation-checks/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/generation-checks.md

**Tests**: included — this feature is pure logic with no UI, so its acceptance criteria are
verified entirely by unit tests (spec.md's own User Stories are written as test scenarios).

**Organization**: tasks are grouped by user story per spec.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: which user story this task belongs to

## Phase 1: Setup

- [x] T001 Create `engine/wyrd/generation_checks.py` with a module docstring naming FR-007-011 as
      its scope, restating this feature's own out-of-scope note (FR-001-006 in `generation.py`,
      FR-012-020 in the two sibling features), per contracts/generation-checks.md.
- [x] T002 Create `tests/engine/test_generation_checks.py` with the standard `PYTHONPATH=engine`
      import of `wyrd.generation_checks`, matching `tests/engine/test_generation.py`'s import
      style.

**Checkpoint**: empty module + test file exist, importable.

## Phase 2: Foundational — shared helper both checks and tests build on

**⚠️ CRITICAL**: no user story task can be implemented until this phase is complete.

- [x] T003 In `engine/wyrd/generation_checks.py`, define a small `_entry(rule, outcome, detail="")`
      helper building the `{rule, outcome, detail}` dict every check function returns, per
      data-model.md's check-entry shape — the one piece of shared plumbing all five checks and
      `run_checks` use, so the shape is defined exactly once.

**Checkpoint**: helper exists and is importable; no check logic yet.

## Phase 3: User Story 1 — A generated result is gated before it can be offered (Priority: P1) 🎯 MVP

**Goal**: FR-007 (entity-membership) rejects a candidate naming any entity outside the three
closed sources, and passes one naming only entities the sources cover.

**Independent Test**: per spec.md User Story 1's Acceptance Scenarios.

### Tests for User Story 1

- [x] T004 [P] [US1] In `tests/engine/test_generation_checks.py`, test
      `check_entity_membership` rejects a candidate naming an entity absent from
      `known_entities`, the request's `threads`/`threat_state` ids, and any invention label —
      the entry's `detail` names the offending entity (contracts/generation-checks.md).
- [x] T005 [P] [US1] In `tests/engine/test_generation_checks.py`, test the same function passes
      a candidate naming only entities present in `known_entities`.
- [x] T006 [P] [US1] In `tests/engine/test_generation_checks.py`, test the same function passes
      a candidate naming only entities present in the request's `threads`/`threat_state` ids
      (`live-play` mode), independent of `known_entities`.
- [x] T007 [P] [US1] In `tests/engine/test_generation_checks.py`, test the same function passes a
      `setting-authoring`-mode candidate naming an entity absent from all closed sources when
      `request['invention_permitted']` is `True` and the candidate's `named_entities` entry is
      labelled `invented, per Phase 1 Q3` — and rejects the identical candidate when that label
      is missing (spec.md Edge Cases).

### Implementation for User Story 1

- [x] T008 [US1] In `engine/wyrd/generation_checks.py`, implement `check_entity_membership`
      per contracts/generation-checks.md's signature and FR-007 (depends on T003).

**Checkpoint**: User Story 1 fully testable independently — FR-007 covered end to end.

---

## Phase 4: User Story 2 — A rejection is explainable, not silent (Priority: P1)

**Goal**: FR-009 (danger-band) reuses the existing danger-scaling arithmetic and reports a
specific `detail` naming the candidate's danger and the band it exceeded; the remaining checks
(FR-008, FR-011) also each carry a specific, non-empty `detail` on rejection.

**Independent Test**: per spec.md User Story 2's Acceptance Scenarios.

### Tests for User Story 2

- [x] T009 [P] [US2] In `tests/engine/test_generation_checks.py`, test `check_danger_band` rejects
      a candidate whose `danger` exceeds `request['danger_rating']`, and that the entry's `detail`
      states both the candidate's danger and the rating it exceeded.
- [x] T010 [P] [US2] In `tests/engine/test_generation_checks.py`, test `check_danger_band` passes
      a candidate whose `danger` is at or below `request['danger_rating']`.
- [x] T011 [P] [US2] In `tests/engine/test_generation_checks.py`, test `check_danger_band`'s
      result for a representative input equals `corpus_scenario.scale_danger`'s own return value
      called directly with the same `{danger, written_for}`/`party` inputs — SC-002's "identical
      banding numbers" assertion, not a separately hand-computed number.
- [x] T012 [P] [US2] In `tests/engine/test_generation_checks.py`, test `check_prophecy` rejects a
      `prophecy_claim` of `destiny`/`hidden_bloodline`/`prewritten_fate` under
      `tone_contract.prophecy: forbidden`, and passes the same claims under `rare`/`central`.
- [x] T013 [P] [US2] In `tests/engine/test_generation_checks.py`, test `check_prophecy` rejects a
      `threat_updates` entry at `known_to_player: understood` under `prophecy: forbidden`
      (spec.md Assumptions), and passes a candidate with `prophecy_claim: none` and no
      `understood` entries.
- [x] T014 [P] [US2] In `tests/engine/test_generation_checks.py`, test `check_favourable_
      coincidence` rejects a `coincidences` entry whose `supported_by` is `None` or not among the
      request's own `threads`/`threat_state`/`existing_entities` ids, and passes one whose
      `supported_by` matches a live thread id.

### Implementation for User Story 2

- [x] T015 [US2] In `engine/wyrd/generation_checks.py`, implement `check_danger_band` calling
      `corpus_scenario.scale_danger` per contracts/generation-checks.md and research.md's decision
      (depends on T003).
- [x] T016 [US2] In `engine/wyrd/generation_checks.py`, implement `check_prophecy` per
      contracts/generation-checks.md and spec.md's Assumptions (depends on T003).
- [x] T017 [US2] In `engine/wyrd/generation_checks.py`, implement `check_favourable_coincidence`
      per contracts/generation-checks.md (depends on T003).

**Checkpoint**: User Stories 1 and 2 both independently testable; FR-010 (scale-drift) not yet
implemented.

---

## Phase 5: User Story 3 — Scale-drift is narrowed or rejected, per the request's own tone (Priority: P2)

**Goal**: FR-010 gates only under `scale_drift: suppressed`, and distinguishes `narrowed` (an
existing threat's imminence/ambient change, reducible to what the contract permits) from `reject`
(a new, connectionless threat, which cannot be narrowed into a connected one).

**Independent Test**: per spec.md User Story 3's Acceptance Scenarios.

### Tests for User Story 3

- [x] T018 [P] [US3] In `tests/engine/test_generation_checks.py`, test `check_scale_drift` returns
      `narrowed` for a `threat_updates` entry on an existing threat (`entity_id` set) whose
      `imminence_delta` exceeds what `scale_drift: suppressed` permits, and that the entry's
      `detail` states the narrowed value.
- [x] T019 [P] [US3] In `tests/engine/test_generation_checks.py`, test `check_scale_drift` returns
      `reject` for a `threat_updates` entry with `entity_id: None` (a new threat) and an empty/
      absent `connection`, under the same `scale_drift: suppressed` contract — reusing
      `threat.validate_connections` for the connection check.
- [x] T020 [P] [US3] In `tests/engine/test_generation_checks.py`, test `check_scale_drift` returns
      `pass` for both of the above candidates' `threat_updates` when
      `tone_contract.scale_drift == "allowed"` — FR-010 never gates under `allowed`.

### Implementation for User Story 3

- [x] T021 [US3] In `engine/wyrd/generation_checks.py`, implement `check_scale_drift` per
      contracts/generation-checks.md, reusing `threat.validate_connections` for the
      connectionless-new-threat leg (depends on T003).

**Checkpoint**: all three user stories independently testable; FR-007-011 fully covered.

---

## Phase 6: Cross-cutting — the aggregator (FR-008 spec requirement)

**Purpose**: `run_checks` is the one entry point the (future) generation pipeline calls; it must
run all five checks in FR-007..FR-011 order and perform none of their logic itself.

- [x] T022 [P] In `tests/engine/test_generation_checks.py`, test `run_checks` returns exactly five
      entries, in `FR-007, FR-008, FR-009, FR-010, FR-011` order, for a fully-passing candidate.
- [x] T023 [P] In `tests/engine/test_generation_checks.py`, test `run_checks`'s output list is
      exactly the same shape `generation.new_result`'s `checks` argument expects — pass it
      straight through and assert `new_result(...)['checks']` equals `run_checks`'s own return
      value unchanged (contracts/generation-checks.md's Consumer contract).
- [x] T024 In `engine/wyrd/generation_checks.py`, implement `run_checks` as a thin aggregator
      calling the five check functions in order (depends on T008, T015, T016, T017, T021).

**Checkpoint**: all acceptance criteria in the issue and spec.md are covered by a passing test.

## Phase 7: Polish

- [x] T025 [P] Run `python3 -m ruff check engine/wyrd/generation_checks.py
      tests/engine/test_generation_checks.py` and `python3 -m ruff format --check` on the same
      files; fix any findings.
- [x] T026 [P] Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_generation_checks -v`
      and confirm every task above's test passes.
- [x] T027 Re-read spec.md's acceptance criteria and data-model.md's validation rules once more
      against the finished `generation_checks.py`, confirming nothing was missed (no code review
      substitute — a final self-check before opening the PR).

## Dependencies & Execution Order

- Phase 1 (Setup) has no dependencies.
- Phase 2 (Foundational) depends on Phase 1 and blocks every user-story phase.
- Phase 3 (US1), Phase 4 (US2), and Phase 5 (US3) each depend on Phase 2 only, and touch disjoint
  functions (`check_entity_membership`; `check_danger_band`/`check_prophecy`/`check_favourable_
  coincidence`; `check_scale_drift`) — all three can proceed in parallel once T003 lands.
- Phase 6 (aggregator) depends on Phases 3, 4, and 5 all being implemented (it calls all five
  functions).
- Phase 7 depends on everything above.

## Parallel Example

```text
# After T003 lands, all three user stories' work can run together:
T004-T008 (US1)  ‖  T009-T017 (US2)  ‖  T018-T021 (US3)
```
