# Tasks: Dread as a reaction/social test penalty

**Input**: Design documents from `specs/101-dread-reaction-penalty/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

Tests run under `PYTHONPATH=engine python3 -m pytest -q`. `ruff check .` and
`ruff format --check .` must stay green.

## Phase 1: Setup

- [X] T001 Locate the existing `ordinary-test`/reaction-test test file(s) under `engine/tests/`
  to extend (no new test module needed if one already covers `ordinary-test` resolution)

## Phase 2: Foundational

- [X] T002 Thread `dread_witnessed: bool = False` through `resolution.propose` and
  `resolution.propose_batch`'s request dict in `engine/wyrd/resolution.py`
- [X] T003 Add `dread_witnessed` to `_normalize_request` in `engine/wyrd/resolution.py`,
  defaulting to `False`
- [X] T004 [P] Thread `dread_witnessed` through `verbs.propose` in `engine/wyrd/verbs.py`
- [X] T005 [P] Add `--dread-witnessed` (`store_true`) to the `propose` CLI parser and pass it
  through in `engine/wyrd/client.py`
- [X] T006 [P] Add `dread_witnessed` to the `propose` tool schema in `engine/wyrd/catalog.py`

**Checkpoint**: request plumbing carries the new field end-to-end (CLI → verbs → resolution),
inert until Phase 3 reads it.

## Phase 3: User Story 1 - Dread penalises a test toward an unfamiliar witness (Priority: P1) 🎯 MVP

**Goal**: A reaction/social test toward a transformed character with nonzero Dread, witnessed by
someone without established peace, resolves at skill plus modifiers minus Dread.

**Independent Test**: Resolve `ordinary-test` with `target` set to a character with nonzero
`dread` and `dread_witnessed=True`; confirm `roll.effective_pct` drops by exactly that Dread,
clipped by the existing floor.

- [X] T007 [US1] In `_resolve_ordinary_test` (`engine/wyrd/resolution.py`), read
  `target_state.get("dread", 0)` when `dread_witnessed` is `True` and a `target_state` is given,
  and fold `-dread` into the `declaration_bonus` passed to `_resolve_test`
- [X] T008 [US1] Add a test in `engine/tests/` asserting an `ordinary-test` with
  `dread_witnessed=True` against a target with nonzero `dread` resolves at
  `skill + difficulty_bonus + declaration_bonus - dread`, run through the existing clamp
- [X] T009 [US1] Add a test asserting the Dread penalty stacks correctly alongside a nonzero
  `declaration_bonus` on the same request (Acceptance Scenario 2)
- [X] T010 [US1] Add a test asserting a large Dread value (e.g. driving the raw sum negative)
  still returns a valid clamped percentage, never a negative one (Edge Case)

**Checkpoint**: User Story 1 fully functional and independently testable.

## Phase 4: User Story 2 - No penalty when peace is established or Dread is zero (Priority: P2)

**Goal**: The same test resolves exactly as today when peace is flagged established, or Dread is
0.

**Independent Test**: Resolve the same request with `dread_witnessed=False` (the default), or
against a target with `dread == 0`, and confirm `roll.effective_pct` is unchanged from
pre-feature behaviour.

- [X] T011 [US2] Add a test asserting `dread_witnessed=False` (or omitted) against a
  nonzero-Dread target leaves `roll.effective_pct` unaffected
- [X] T012 [US2] Add a test asserting `dread_witnessed=True` against a target with `dread == 0`
  leaves `roll.effective_pct` unaffected
- [X] T013 [US2] Add a test asserting `dread_witnessed=True` with no `target` at all does not
  raise and leaves `roll.effective_pct` unaffected (no target to read Dread from)

**Checkpoint**: Both user stories independently verified; no regression to existing
`ordinary-test`/Exposure/Terror/combat-attack behaviour.

## Phase 5: Polish & Cross-Cutting

- [X] T014 [P] Add a test asserting `dread_witnessed=True` on an `exposure` or `combat-attack`
  request has no effect (FR-006 — confirms the penalty never leaks outside `ordinary-test`)
- [X] T015 Update `docs/design/07-transformations.md`'s "Dread" section only if its wording no
  longer matches the shipped behaviour (expected: no change needed — the section already
  describes this exactly)
- [X] T016 Run `PYTHONPATH=engine python3 -m pytest -q`, `ruff check .`,
  `ruff format --check .`; fix anything red

## Dependencies

- Phase 1 → Phase 2 → Phase 3 (US1, the MVP) → Phase 4 (US2) → Phase 5
- T002 blocks T003; T003 blocks T004-T006; all of Phase 2 blocks T007
- T007 blocks every test task in Phases 3-4
- Phase 5 depends on Phases 3-4 complete

## Parallel Example

```text
# After T003 lands, these can run together:
T004 [P] verbs.py plumbing
T005 [P] client.py CLI flag
T006 [P] catalog.py schema entry
```

## Implementation Strategy

**MVP = Phase 1-3** (User Story 1 only): the penalty applies and is independently verifiable.
Phase 4 (no-op cases) and Phase 5 (cross-mechanic isolation, docs check) round out full
correctness before the PR is raised, but US1 alone is a demonstrable, shippable increment.
