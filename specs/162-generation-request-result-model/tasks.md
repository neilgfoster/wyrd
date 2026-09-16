---
description: "Task list for Generation request/result data model and mode validation (issue #420)"
---

# Tasks: Generation request/result data model and mode validation

**Input**: Design documents from `specs/162-generation-request-result-model/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md (specs/161's, referenced not
duplicated), contracts/generation-request.md (specs/161's, referenced not duplicated)

**Tests**: included — this feature is pure logic with no UI, so its acceptance criteria are
verified entirely by unit tests (spec.md's own User Stories are written as test scenarios).

**Organization**: tasks are grouped by user story per spec.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependencies)
- **[Story]**: which user story this task belongs to

## Phase 1: Setup

- [x] T001 Create `engine/wyrd/generation.py` with module docstring naming FR-001-006 as its
      scope and explicitly noting FR-007-020 are out of scope (sibling features).
- [x] T002 Create `tests/engine/test_generation.py` with the standard `PYTHONPATH=engine` import
      of `wyrd.generation`, matching an existing test module's (e.g. `tests/engine/test_era.py`)
      import style.

**Checkpoint**: empty module + test file exist, importable.

## Phase 2: Foundational — shapes both user stories build on

**⚠️ CRITICAL**: no user story task can be implemented until this phase is complete.

- [x] T003 In `engine/wyrd/generation.py`, define `GenerationRequest` as a dataclass with fields
      `scale`, `mode`, `setting_ref`, `tone_contract`, `written_for` (default `None`), and the
      mode-specific fields as optional/defaulted: `threads`, `threat_state`, `danger_rating`,
      `era` (live-play); `voice`, `existing_entities`, `invention_permitted` (setting-authoring) —
      per data-model.md's field table.
- [x] T004 In `engine/wyrd/generation.py`, define `GenerationResult` as a dataclass with fields
      `candidate`, `checks` (list of `{rule, outcome, detail}`), and `consumed` — per
      data-model.md's `GenerationResult` table. No population logic — this feature only defines
      the shape (FR-007).
- [x] T005 In `engine/wyrd/generation.py`, define a structured rejection type (e.g.
      `GenerationRequestError` with `code`/`detail` fields) per research.md's decision and FR-008
      — every validation failure below returns/raises this, never a bare exception or bool.

**Checkpoint**: both shapes exist and are importable; no validation logic yet.

## Phase 3: User Story 1 — Construct and validate a request for any scale (Priority: P1) 🎯 MVP

**Goal**: one `GenerationRequest` shape validates correctly across all three scales, and a
campaign-spine request is confirmed as an arc-with-no-parent alias, never a fourth type.

**Independent Test**: per spec.md User Story 1's Acceptance Scenarios.

### Tests for User Story 1

- [x] T006 [P] [US1] In `tests/engine/test_generation.py`, table-driven test: for each of
      `beat`/`arc`/`campaign-spine` × both modes, a request missing `written_for` is rejected
      except `campaign-spine` in `setting-authoring` mode, which is accepted — per FR-003 and
      spec.md's Edge Cases (campaign-spine in live-play still requires `written_for`).
- [x] T007 [P] [US1] In `tests/engine/test_generation.py`, test that a `campaign-spine`-scale
      request is confirmed by the dedicated alias-check function to be structurally an `arc`
      request with no `parent` and `scale: campaign` (FR-002, SC-002).
- [x] T008 [P] [US1] In `tests/engine/test_generation.py`, test that `scale`, `mode`,
      `setting_ref`, and `tone_contract` are each individually rejected as missing when absent
      (FR-003).

### Implementation for User Story 1

- [x] T009 [US1] In `engine/wyrd/generation.py`, implement `is_campaign_spine_shape(request)`
      (or equivalently named function) per research.md's decision to keep this check separately
      callable/testable (FR-002).
- [x] T010 [US1] In `engine/wyrd/generation.py`, implement the base-field presence checks of
      `validate_request()`: `scale`, `mode`, `setting_ref`, `tone_contract` always required;
      `written_for` required per the FR-003 table (depends on T003, T005, T009).

**Checkpoint**: User Story 1 fully testable independently — base shape + campaign-spine alias
validated, mode-specific state not yet checked.

---

## Phase 4: User Story 2 — Reject a live-play request with insufficient grounding (Priority: P2)

**Goal**: a `live-play` request with no `threads` and no `threat_state` is rejected before any
generation step would run.

**Independent Test**: per spec.md User Story 2's Acceptance Scenarios.

### Tests for User Story 2

- [x] T011 [P] [US2] In `tests/engine/test_generation.py`, test a `live-play` request with
      `threads: []` and no `threat_state` is rejected with a structured reason.
- [x] T012 [P] [US2] In `tests/engine/test_generation.py`, test the same request with one live
      thread added passes this specific check.
- [x] T013 [P] [US2] In `tests/engine/test_generation.py`, test a `live-play` request missing
      `danger_rating` or `era` is rejected (FR-004).

### Implementation for User Story 2

- [x] T014 [US2] In `engine/wyrd/generation.py`, extend `validate_request()` with the FR-004
      `live-play` checks: `danger_rating`/`era` presence, and the "`threads` or `threat_state`
      non-empty" grounding rule from spec.md's Edge Cases (depends on T010).

**Checkpoint**: User Stories 1 and 2 both independently testable; setting-authoring mode not yet
checked.

---

## Phase 5: User Story 3 — Reject a setting-authoring request missing the Q3 grant (Priority: P2)

**Goal**: a `setting-authoring` request without `invention_permitted: true` is rejected before any
generation step would run, naming the missing permission.

**Independent Test**: per spec.md User Story 3's Acceptance Scenarios.

### Tests for User Story 3

- [x] T015 [P] [US3] In `tests/engine/test_generation.py`, test a `setting-authoring` request with
      no `invention_permitted` field is rejected naming the missing permission.
- [x] T016 [P] [US3] In `tests/engine/test_generation.py`, test the same request with
      `invention_permitted: false` is rejected the same way.
- [x] T017 [P] [US3] In `tests/engine/test_generation.py`, test the same request with
      `invention_permitted: true` and `voice`/`existing_entities` present passes this check.

### Implementation for User Story 3

- [x] T018 [US3] In `engine/wyrd/generation.py`, extend `validate_request()` with the FR-005
      `setting-authoring` checks: `voice`/`existing_entities` presence, and
      `invention_permitted is True` (not merely truthy) required or reject (depends on T010).

**Checkpoint**: all three user stories independently testable.

---

## Phase 6: Cross-cutting — FR-006 mode-boundary invariant and mutual exclusion

**Purpose**: the invariant spec.md calls out explicitly as its own test target, plus the
mode-exclusivity edge case, cutting across all three user stories' work.

- [x] T019 [P] In `tests/engine/test_generation.py`, test that a `live-play` request additionally
      carrying `voice`, `existing_entities`, or `invention_permitted` is rejected (FR-006's mutual
      exclusion), and symmetrically for a `setting-authoring` request carrying `threads`,
      `threat_state`, or `danger_rating`.
- [x] T020 [P] In `tests/engine/test_generation.py`, write SC-004's own invariant test directly:
      construct a minimal valid `live-play` request and a minimal valid `setting-authoring`
      request and assert programmatically that the only fields differing between which are
      *set* are the mode-specific state fields — never anything that would later gate which
      anti-inflation rule applies (FR-006). This test documents the boundary this feature commits
      to for the sibling features that implement FR-007-011.
- [x] T021 In `engine/wyrd/generation.py`, implement the mutual-exclusion check in
      `validate_request()` exercised by T019 (depends on T014, T018).

**Checkpoint**: all acceptance criteria in the issue and spec.md are covered by a passing test.

## Phase 7: Polish

- [x] T022 [P] Run `python3 -m ruff check engine/wyrd/generation.py tests/engine/test_generation.py`
      and `python3 -m ruff format --check` on the same files; fix any findings.
- [x] T023 [P] Run `PYTHONPATH=engine python3 -m pytest tests/engine/test_generation.py -v` and
      confirm every task above's test passes.
- [x] T024 Re-read spec.md's acceptance criteria and data-model.md's validation rules once more
      against the finished `generation.py`, confirming nothing was missed (no code review
      substitute — a final self-check before opening the PR).

## Dependencies & Execution Order

- Phase 1 (Setup) has no dependencies.
- Phase 2 (Foundational) depends on Phase 1 and blocks every user-story phase.
- Phase 3 (US1) depends on Phase 2 only.
- Phase 4 (US2) and Phase 5 (US3) each depend on Phase 2 and on T010 (the base validator existing)
  from Phase 3, but are otherwise independent of each other — T011-T013/T014 and T015-T017/T018
  touch disjoint code paths (`live-play` vs `setting-authoring` branches) and can proceed in
  parallel once T010 lands.
- Phase 6 depends on both Phase 4 and Phase 5 (needs both branches implemented to check mutual
  exclusion between them).
- Phase 7 depends on everything above.

## Parallel Example

```text
# After T010 lands, US2's and US3's test-writing tasks can run together:
T011, T012, T013 (US2 tests)  ‖  T015, T016, T017 (US3 tests)
```
