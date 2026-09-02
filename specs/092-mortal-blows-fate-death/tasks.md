# Tasks: Mortal blows, Fate, and death

**Input**: plan.md, research.md, data-model.md, quickstart.md, spec.md from this directory.

## T001 — `_stage_aftermath`: mortal-critical forcing

Add a `mortal: bool = False` keyword parameter. When `True`, force `key`/`effect` to the
`death` row regardless of the rolled total (still record the actual roll/total), and set
`roll["forced_mortal"] = True`. When `False`, set `roll["forced_mortal"] = False` and behave as
today. [P1 — US1]

## T002 — `_stage_aftermath`: `mortality: low` closure

Add a `mortality: str = "standard"` keyword parameter. After the mortal-forcing step (T001)
resolves `key`/`effect`, if `key == "death"` and `mortality == "low"`, re-read onto the worst
non-death row (T004's helper) and set `roll["closed_by"] = "mortality"`,
`roll["fate_spent"] = False`. Otherwise `roll["closed_by"] = None`. Reject any `mortality` value
outside `{"low", "standard", "high"}` with `ValueError`, matching `creation.py`'s existing
validation style. [P1 — US4]

## T003 — Reject `mortal=True` with a non-death rolled result silently overridden

No new guard needed beyond T001 itself — document in `_stage_aftermath`'s docstring that a
mortal-forced result and its underlying roll are both recorded (spec.md Story 1's Acceptance
Scenario 2), and add a regression test asserting the roll/total fields are untouched by forcing.
[P1 — US1]

## T004 — `_worst_non_death_row()` helper

A small module-level helper in `resolution.py` that derives the worst non-death row's `(key,
effect)` from the live Aftermath table structure `_aftermath_band` already consults — never a
hardcoded key (research.md, spec.md Edge Cases). Reused by T002 and T005. [P1 — US2, US4]

## T005 — `close_death_row(steps, step_id, entity, *, spender_state, companion_state=None)`

New standalone function per data-model.md's contract:
- Raise `ValueError` if `steps[step_id]` is not an `aftermath` step, or its `roll["key"] !=
  "death"`, or its `roll["closed_by"]` is already set (spec.md FR-002/FR-004 — nothing left to
  buy, and Fate never touches a non-death row).
- Raise `ValueError` if `spender_state.get("fate", {}).get("current", 0) < 1`.
- On success: rewrite the step's `roll["key"]`/`roll["effect"]` to T004's worst non-death row,
  set `roll["closed_by"] = "fate"`, `roll["fate_spent"] = True`, decrement
  `spender_state["fate"]["current"]` by 1, and return the list of mutations applied (Fate
  decrement; wound mutation if the closed-onto row specifies one; companion `status` mutation if
  `companion_state is not None`, per T007). [P1 — US2]

## T006 — Companion Fate-spend gate

`close_death_row` (or its caller — decide during implementation which layer owns this check, and
say so in the docstring) MUST require, when `companion_state is not None`, that
`spender_state` (the player's own character) is present in the scene and able to act, per
whatever the engine already uses to represent that (research.md: no new presence-tracking
mechanism is introduced). Reject with `ValueError` naming which condition failed
(absent/incapacitated) otherwise, leaving the companion's step unchanged. [P1 — US3]

## T007 — Companion `status` transition helper

A small helper, called by `close_death_row` and by whatever finalizes a *standing* (unclosed)
Aftermath result, that sets a companion entity's `status` field: `dead` when the final row is
`death`, `away` when the final row is `taken`, unchanged otherwise. MUST NOT be applied to a
player-character entity (spec.md FR-011) — guard on `role == "companion"`. [P1 — US5]

## T008 — Mortal-critical forcing tests

`tests/engine/test_resolution.py`, extending `AftermathTest`: assert `mortal=True` forces `key
== "death"` and `forced_mortal is True` across a range of seeds/totals that would otherwise land
on a low row; assert `mortal=False` leaves existing behaviour untouched (regression). [P1 — US1]

## T009 — `mortality: low` closure tests

Assert `mortality="low"` closes both a rolled `death` and a mortal-forced `death` onto the
current worst non-death row, with `closed_by == "mortality"` and `fate_spent is False`; assert
`mortality="standard"`/`"high"` leave `death` standing; assert an invalid `mortality` value
raises `ValueError`. [P1 — US4]

## T010 — Fate-spend tests

Assert a successful `close_death_row` call: rewrites the row, decrements `fate.current` by
exactly 1, sets `closed_by == "fate"` and `fate_spent is True`. Assert rejection cases: 0 Fate
available, non-`death` step, already-closed step (both `"fate"`- and `"mortality"`-closed), and
that none of the rejection cases mutate any state. [P1 — US2]

## T011 — Companion Fate-spend gating tests

Assert `close_death_row` on a companion's `death` step succeeds only when the player's own
character is present and able to act, per T006; assert the two rejection paths (absent,
incapacitated) leave the companion's result at `death` and deduct no Fate. Assert the Fate
deducted on a successful companion spend comes from `spender_state` (the player), never from
`companion_state`. [P1 — US3]

## T012 — Companion status-transition tests

Assert a standing companion `death` result sets `status == "dead"`; assert a standing `taken`
result sets `status == "away"`; assert every other row leaves `status` unchanged; assert the
player character's own entity never receives this mutation (FR-011). [P1 — US5]

## T013 — `tools/check_death_row_determinism.py`

Following the repo's `tools/check_*` convention (`CLAUDE.md` "Deterministic over inference"):
resolve the same mortal-critical-forced and Fate-spend scenarios repeatedly and assert the
outcome (row, effect, `closed_by`) is byte-identical every time — no second roll, no variance
(spec.md SC-002). Also assert idempotence: forcing `mortal=True` a second time over an
already-`death` result changes nothing further.

## Dependencies

T004 → (T002, T005) — the worst-non-death-row helper must exist before either closure path uses
it. T001 → T002 (mortality closure reads the mortal-forced result). T005 → (T006, T007) — the
companion gate and status helper are consulted from within `close_death_row`. T001–T007
(implementation) → T008–T012 (their own tests) → T013 (determinism check, needs both closure
paths working). All test tasks within a phase are parallelizable against each other ([P]) once
their implementation task lands, but are listed here without the marker since each targets the
same test file (`tests/engine/test_resolution.py`) and would conflict on concurrent edits.

## Implementation strategy

MVP: T001 + T004 + T008 (mortal-critical forcing alone) delivers Story 1 independently. T005 +
T010 add the Fate-spend mechanism (Story 2). T006 + T011 add the companion gate (Story 3). T002 +
T009 add `mortality: low` (Story 4). T007 + T012 add companion status transitions (Story 5).
T013 closes out the determinism guarantee once all closure paths exist.
