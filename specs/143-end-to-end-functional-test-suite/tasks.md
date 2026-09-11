# Tasks: End-to-end functional test suite across the whole engine

**Input**: Design documents from `specs/143-end-to-end-functional-test-suite/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: this feature *is* the test — there are no separate "write a test for the test" tasks.

**Organization**: one new file, `tests/engine/test_integration.py`. Tasks are ordered by the same
subsystem sequence spec.md's FR-002 and User Story 1 describe, since each step's fixture is the
input to the next.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Create `tests/engine/test_integration.py` with the module docstring, the repo's
      standard `sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "engine"))`
      import shim, and imports of every `wyrd` module the sequence touches (`character`,
      `creation`, `resolution`, `combat`, `downtime`, `adversary`, `economy`, `overrides`,
      `journey`, `scenario_selection`, `session`, `rally`, `advancement`, `chronicle`, `state`).

## Phase 2: Foundational

- [x] T002 In `tests/engine/test_integration.py`, add a `EndToEndSequenceTest(unittest.TestCase)`
      with `setUp`/`tearDown` backed by one `tempfile.TemporaryDirectory()`, following the same
      shape `tests/engine/test_client.py`'s `RollCliTest` already uses.

## Phase 3: User Story 1 — one run drives every subsystem (P1)

- [x] T003 [US1] Area 1 (creation): call `creation.create_character` with a valid career/actions
      allocation to build the one player character the whole test carries forward; assert
      `result["valid"] is True` and the returned frontmatter's `skills`/`stamina`/`wounds` shape.
- [x] T004 [US1] Area 2 (action resolution): `resolution.propose(..., mechanic="ordinary-test")`
      against the area-1 character, then `resolution.commit`; assert the proposal's `mutations`
      shape and that `character.load` after commit is unchanged.
- [x] T005 [US1] Area 3 (combat): create a second character file as the target, call
      `combat.start_combat` for scene bookkeeping, then `resolution.propose(...,
      mechanic="combat-attack")` with the seed already verified in
      `tests/engine/test_resolution.py`'s `CombatChainTest`, commit it, and assert the target's
      recorded wound (id, effect, `closed is None`).
- [x] T006 [US1] Area 4 (harm/recovery): take the exact wound id area 3 produced and close it via
      `downtime.apply_mend`, driving the 5-step downtime loop
      (`new_downtime_state`/`advance_downtime` through `destination`/`upkeep`/`advances`/
      `undertaking`/`rest`) and `apply_rest`; assert the wound's `closed` is no longer `None` and
      stamina is restored.
- [x] T007 [US1] Area 5 (adversaries): write an inline bestiary fixture, `adversary.load` it, use
      `adversary.adjusted_skill` to compute a scaled skill value, and save that value into a
      minimal `type: creature` entity file; assert the entity file's skill equals the value
      `adjusted_skill` returned.
- [x] T008 [US1] Area 6 (condition tracks): `resolution.propose(..., mechanic="exposure")` against
      the area-1 character using the exact seed/skill from `test_resolution.py`'s
      `WorkedExampleTest`, commit it, and assert the `taint` mutation's value and (with a starting
      taint chosen to cross a threshold) that a transformation/hidden-threshold field is set.
- [x] T009 [US1] Area 7 (economies): call `economy.spend_coin`, `economy.adjust_standing`, and
      `economy.gain_allegiance` against the area-1 character's frontmatter, write the results back
      via `character.save`, and assert `coin`/`reputation.score`/`allegiances` on the saved file.
- [x] T010 [US1] Area 8 (systems of power): construct a `power` dict and call
      `resolution.propose(..., mechanic="system-of-power")` against the area-1 character (whose
      `taint`/`strain`/`resolve` fields already carry area-6's values), commit it, and assert
      whichever of the `strain`/`trauma`/`taint` mutations fired matches the character's post-load
      state.
- [x] T011 [US1] Area 9 (solo procedures): build an inline `journey` dict, call
      `journey.legs_for`/`journey.roll_hazard`, feed the returned `hazard["request"]` straight
      into `resolution.propose` (closing back through area 2's machinery) against the area-1
      character, and assert the hazard's matched entry and the resulting roll outcome.
- [x] T012 [US1] Area 10 (session/campaign structure): drive `session.new_loop_state`/
      `advance_loop` through `orient`/`recap`/`beat`/`close`, and `rally.apply_rally` using the
      area-1 character's post-sequence `strain`/`stamina`, writing the result back via
      `character.save`; assert the loop's step sequence and the rally's awarded
      `advances_unspent`.
- [x] T013 [US1] Area 11 (chronicle bootstrap): call `state.default_chronicle_state` +
      `state.save_chronicle`/`load_chronicle` for the top-level bootstrap, then use
      `chronicle.record_rolled` on an intentionally-uncommitted proposal id from an earlier area,
      `chronicle.discard_at_rally`, and `resolution.discard` to close it out; assert the round-
      tripped chronicle state and that the discarded proposal id can no longer be committed.

## Phase 4: User Story 2 — handoffs are asserted, not just exercised (P2)

- [x] T014 [US2] Review T003-T013: for each of the ten adjacent-area boundaries, confirm the
      assertion's expected value is read from the *previous* area's actual return/state (never a
      value hard-coded independently of it) — tighten any assertion in
      `tests/engine/test_integration.py` that only checks "no exception raised."

## Phase 5: User Story 3 — green under the repo's lint/test convention (P3)

- [x] T015 [US3] Run `python3 -m ruff check tests/engine/test_integration.py` and
      `python3 -m ruff format --check tests/engine/test_integration.py`; fix any finding in the
      new file.
- [x] T016 [US3] Run `PYTHONPATH=engine python3 -m pytest tests/engine/test_integration.py -q`
      twice in a row and confirm identical pass/fail output both times (SC-004), then run
      `PYTHONPATH=engine python3 -m pytest -q` for the full existing suite alongside it.

## Phase 6: Polish

- [x] T017 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` repo-wide to
      confirm no other file regressed.

## Dependencies

T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014
→ T015 → T016 → T017. The sequence is strictly linear: each area's fixture is the next area's
input, per spec.md's Assumptions and this feature's own FR-001 (single carried-forward
character).

## Implementation strategy

MVP = Phase 3 (T003-T013) alone already satisfies User Story 1 end to end; Phases 4-6 harden the
assertions and confirm lint/determinism rather than adding new sequence steps.
