# Tasks: Chronicle state invariants: passive validation and active cascades

**Input**: plan.md, spec.md, data-model.md, quickstart.md (all in this directory)
**Tests**: requested — spec.md's own acceptance scenarios and SC-001..003 name concrete test
cases, and `CLAUDE.md`'s "deterministic over inference" rule means these invariants must be
checked, not asserted.

## Phase 1: Setup

- [x] T001 Read `engine/wyrd/resolution.py`'s `commit()`, `_cascade_from_mutation`, and
  `entity.py`'s `check_containment`/`unresolved_references`/`load_set`/`resolve_entity` in full,
  to confirm the exact call shapes this feature builds on (no code change; a confirmation pass
  before writing new functions, per data-model.md).

## Phase 2: Foundational (blocking prerequisites)

- [x] T002 Implement `_load_chronicle_entities(any_touched_path: pathlib.Path) -> dict[str, dict]`
  in `engine/wyrd/resolution.py` (data-model.md § `_load_chronicle_entities`): locate the
  chronicle root by walking up from `any_touched_path` to the first directory containing
  `entities/`, `overlay/`, `setting/` or `chronicle.yaml`; glob `setting/*.md` and
  `overlay/*.md`, resolve each setting id via `entity.resolve_entity`, and merge in every
  `entities/*.md` file directly; raise `ProposalError` if no chronicle root is found.
- [x] T003 Implement the four passive-check helpers this feature needs, in
  `engine/wyrd/resolution.py`, as private functions callable from a single validation pass:
  duplicate-id membership check, and the two new numeric checks (`fortune.current ≤ fate.max`,
  tracker `0..max`), each reading via `_get_nested` and skipping cleanly when the relevant fields
  are absent (data-model.md's rule table).
- [x] T004 Implement `_validate_proposal(mutations: list[dict], entities: dict[str, dict]) -> None`
  in `engine/wyrd/resolution.py` (data-model.md § `_validate_proposal`): apply each mutation to a
  scratch copy of its target entity's state (reusing `_apply_mutation`), merge the scratch copies
  into the entity set from T002, then run T003's checks plus `entity.check_containment` and
  `entity.unresolved_references` against the merged set, raising `ProposalError` naming the rule
  and offending entity/field on the first violation, in the order: duplicate id → unresolved
  reference → parent cycle → fortune/fate → tracker bounds.
- [x] T005 Wire `_validate_proposal` into `commit()` in `engine/wyrd/resolution.py`: call
  `_load_chronicle_entities` and `_validate_proposal` immediately after popping the open
  proposal (`_pop_open_proposal`) and before any entity file is loaded/mutated/saved — so a
  raised `ProposalError` guarantees FR-007 (nothing written) by ordering, not rollback.

**Checkpoint**: `commit()` now rejects the four passive-rule violations outright; existing
`test_resolution.py` tests (propose/commit/reroll/discard) must still pass unchanged.

## Phase 3: User Story 1 - A malformed commit is rejected before it touches disk (P1)

**Goal**: prove each of the four passive rules independently rejects a violating commit and
leaves every touched entity file byte-identical to before the call.

**Independent Test**: run this phase's tests alone; each builds a temporary chronicle, stages one
specific violation, and asserts both the raised error and the unchanged file bytes.

- [x] T006 [P] [US1] Add a pytest fixture (or reuse an existing one) in
  `tests/engine/test_resolution.py` that builds a minimal temporary chronicle directory
  (`entities/`, `overlay/`, `setting/`) with one character entity, for this phase's tests to share.
- [x] T007 [P] [US1] Test: a proposal that would create a duplicate entity id is rejected by
  `commit`, and no entity file changes, in `tests/engine/test_resolution.py`.
- [x] T008 [P] [US1] Test: a proposal that would set an unresolvable `parent`/`links`/`overlay_of`
  reference is rejected by `commit`, and no entity file changes, in
  `tests/engine/test_resolution.py`.
- [x] T009 [P] [US1] Test: a proposal that would introduce a `parent` cycle (single-entity
  self-cycle, and a two-entity cycle across the same proposal per spec.md's Edge Cases) is
  rejected by `commit`, and no entity file changes, in `tests/engine/test_resolution.py`.
- [x] T010 [P] [US1] Test: a proposal that would raise `fortune.current` above `fate.max` is
  rejected by `commit`, and no entity file changes; and a proposal touching an entity with no
  `fortune`/`fate` fields is unaffected by this rule, in `tests/engine/test_resolution.py`.
- [x] T011 [P] [US1] Test: a proposal that would push a tracker's `value` outside `0..max` is
  rejected by `commit`, and no entity file changes, in `tests/engine/test_resolution.py`.
- [x] T012 [US1] Test: a proposal violating none of the four rules commits exactly as it does
  today (regression guard against T002-T005 over-rejecting), in
  `tests/engine/test_resolution.py`.
- [x] T013 [US1] Test: a multi-entity proposal where only one entity's mutations violate a
  passive check is rejected as a whole, and *every* touched entity's file is unchanged (spec.md
  Edge Cases, FR-007), in `tests/engine/test_resolution.py`.

**Checkpoint**: User Story 1 independently complete and testable — `commit()` now enforces all
four passive rules with full-rejection semantics.

## Phase 4: User Story 2 - Active cascades stay staged inside the same proposal (P2)

**Goal**: prove the three existing cascades (taint→Transformation, trauma→test→Affliction,
transformation-count→lost) still stage correctly, and that a cascade-produced mutation is
checked by the exact same passive-validation pass as a directly requested one.

**Independent Test**: run this phase's tests alone; each proposes a crossing mutation, asserts
the cascade's steps are already present pre-commit, then commits and asserts everything landed
together.

- [x] T014 [P] [US2] Test: a taint mutation crossing a multiple of 3 has the Transformation
  roll's steps already staged by `propose`, and `commit` applies both together, in
  `tests/engine/test_resolution.py` (extends existing transformation-chain coverage with the
  passive-validation pass now in front of `commit`).
- [x] T015 [P] [US2] Test: a trauma mutation crossing past the floor has the gating test (and, on
  a failed test, the Affliction roll) already staged by `propose`, and `commit` applies all of it
  together, in `tests/engine/test_resolution.py`.
- [x] T016 [P] [US2] Test: a transformation mutation reaching `hidden_threshold` has `status: lost`
  already staged by `propose`, and `commit` applies it alongside the crossing mutation, in
  `tests/engine/test_resolution.py`.
- [x] T017 [US2] Test: a cascade-produced mutation that would itself violate a passive check
  (e.g. an out-of-range tracker written by a cascade) is rejected by `commit` exactly like a
  directly requested one (FR-006, spec.md Edge Cases), in `tests/engine/test_resolution.py`.

**Checkpoint**: User Story 2 independently complete and testable — cascades proven not to regress
under the new validation pass.

## Phase 5: User Story 3 - Spent is read, never written (P3)

**Goal**: `is_spent()` correctly computes Spent from current state, and no write path ever
persists a `spent` field.

**Independent Test**: run this phase's tests alone, independent of `propose`/`commit`.

- [x] T018 [P] [US3] Implement `is_spent(character_state: dict) -> bool` in
  `engine/wyrd/resolution.py` (data-model.md § `is_spent`): `resolve.current ≤ max(taint, trauma)`
  with each axis exempted at `0` per ADR 0049; `False` when both axes are `0`.
- [x] T019 [P] [US3] Test: `is_spent()` at each of the four boundary conditions from spec.md User
  Story 3 (Spent with both axes nonzero, Spent with one axis exempted at 0, not Spent, both axes
  at 0), in `tests/engine/test_resolution.py`.
- [x] T020 [US3] Test: after a full `propose`/`commit` cycle (including a cascade from Phase 4),
  the committed entity file carries no `spent` field, in `tests/engine/test_resolution.py`.

**Checkpoint**: User Story 3 independently complete and testable.

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T021 Run `ruff check .` and `ruff format --check .` repo-wide; fix any finding this
  feature's changes introduced (SC-004). Per `CLAUDE.md`, do not scope-limit this to just the
  changed files if it reports pre-existing findings elsewhere — confirm the repo was clean before
  this feature started, and fix anything this feature caused.
- [x] T022 Run `PYTHONPATH=engine python3 -m pytest -q` for the full suite (not just
  `test_resolution.py`) to confirm no regression elsewhere (e.g. `test_creation.py`,
  `test_combat.py`, or any other caller of `commit`).
- [x] T023 Walk `quickstart.md`'s three manual validation scenarios once by hand (or as an
  additional integration test) to confirm the written guide still matches actual behavior.
- [x] T024 Update `docs/design/22-state.md` if implementation surfaced any wording gap between
  the design doc and the actual enforced rule (e.g. how the chronicle root is located) — design
  docs are rewritten in place per `CLAUDE.md`; only touch it if something is actually inaccurate,
  not to restate what's already correct.

## Dependencies & Execution Order

- Phase 1 (T001) → Phase 2 (T002-T005, strictly sequential: each builds on the previous) → Phases
  3/4/5 (independent of each other, can run in any order or in parallel once Phase 2 lands) →
  Phase 6 (after all user stories).
- Within Phase 3, T006 must land before T007-T013 (shared fixture). T007-T011 are parallel
  ([P]); T012-T013 depend on T007-T011 existing as a pattern to extend but touch the same file,
  so treat as sequential after them.
- Within Phase 4, T014-T016 are parallel ([P]); T017 depends on the pattern they establish.
- Within Phase 5, T018 (implementation) must land before T019/T020 (tests); T018-T019 are
  markable [P] against Phase 3/4 files since `is_spent` is additive and doesn't touch
  `_validate_proposal`.

## MVP Scope

User Story 1 (Phase 3) alone is a viable, independently valuable increment: `commit()` stops
writing broken state, even before cascade regression coverage (Phase 4) or the Spent accessor
(Phase 5) land. Recommended order is still 1→2→3 as written, since Phase 2 is a hard prerequisite
for all three stories and the stories are small enough that splitting delivery further has little
benefit here.
