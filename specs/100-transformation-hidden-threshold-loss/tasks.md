# Tasks: Transformation count reaching the hidden threshold

**Input**: [plan.md](plan.md), [data-model.md](data-model.md), [spec.md](spec.md)

## T001 — Record every Transformation on `transformations` (FR-001)

In `engine/wyrd/resolution.py` `_stage_transformation_chain`, add an `append` mutation for
`transformations` (value: the row number) alongside the existing `taint`/`dread`
mutations, applied the same way (`_apply_mutation`).

## T002 — Stage the loss transition when the count reaches the hidden threshold (FR-002, FR-003, FR-007)

After appending to `transformations` and applying that mutation, compare
`len(state["transformations"])` against `state["hidden_threshold"]` (guard: only when
`hidden_threshold` is not `None`). When the count reaches (`>=`) the threshold, append a further
`set` mutation on `status` to `"lost"`, applied to `state` the same way, on the same step.

## T003 — Stop the re-roll loop for a lost character (FR-008)

Once the loss transition (T002) has fired for this cascade invocation, `return` from
`_stage_transformation_chain` instead of continuing the `while Taint >= threshold` re-roll loop,
even if Taint would otherwise call for another roll.

## T004 — Confirm no threshold-value leak (FR-006)

Read the new step's `roll` and `mutations` dict shapes staged by T001-T003 and confirm neither
carries the numeric `hidden_threshold` value itself (only the `status`/`transformations`
mutations, which don't reveal it). No code change expected — verification only, done alongside
implementation.

## T005 — Test: player character's Transformation count reaches hidden threshold (US1, SC-001, SC-002)

In `tests/engine/test_resolution.py` `TransformationCascadeTest` (or a new test class in the same
file, matching existing conventions), add a test: a player-character state with
`hidden_threshold` set and `transformations` one entry short of it; drive a further Taint
crossing; assert the resulting steps stage `transformations` append + `status: lost`, and that
`fate` is unchanged before/after.

## T006 — Test: below-threshold Transformation stages no loss (US1 edge case)

Add a test: same setup as T005 but with `transformations` more than one below `hidden_threshold`;
assert no `status` mutation is staged after the cascade.

## T007 — Test: companion's Transformation count reaches hidden threshold (US2, SC-004)

Add a test: a companion state (`role: companion`) whose count reaches `hidden_threshold`; assert
`status: lost` is staged and no player-character-only machinery (e.g. no extra mutation beyond
`status`) is staged for the companion.

## T008 — Test: re-roll loop does not continue past the loss transition (Edge case, T003)

Add a test: a state where staging a Transformation both reaches `hidden_threshold` and leaves
Taint still at/over the crossed threshold; assert the cascade stages exactly one Transformation
step (plus the loss transition) rather than continuing to re-roll.

## T009 — Run the full suite and lints

`PYTHONPATH=engine python3 -m pytest -q`, `python3 -m ruff check .`,
`python3 -m ruff format --check .` — all green.

## T010 — Reconcile `docs/design/22-state.md` wording with `07-transformations.md` if still divergent

`22-state.md`'s invariants line says "count **exceeding** `hidden_threshold`"; `07-transformations.md`
says "count ... **reaches** the hidden threshold." Confirm the implementation matches "reaches"
(`>=`), which is the more specific, titled section, and adjust `22-state.md`'s wording to match
("reaching") so the two documents no longer describe the trigger differently (CLAUDE.md recurring
fault class 3).
