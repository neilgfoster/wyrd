# Tasks: The Aftermath table and wound records

**Input**: plan.md, data-model.md, spec.md from this directory.

## T001 — `AFTERMATH_TABLE` and `_aftermath_band` in `engine/wyrd/resolution.py`

Add the 8-row table (data-model.md's table) and a `_aftermath_band(total)` lookup mirroring
`_critical_band`'s fallthrough-to-last-row shape. [P1 — US1]

## T002 — `_stage_aftermath` staging function

Mirror `_stage_critical`'s shape: roll `d100`, modifier `5 × points_below_zero`, resolve the row,
build zero-or-one wound mutation (`{}`/`{"dread": 1}`/`{"skill": -10, recurring: True, bears_on}`
per data-model.md), append the `steps` entry. [P1 — US1, US2]

## T003 — Reject non-positive `points_below_zero`

Caller-contract guard per spec.md's Edge Cases: raise `ValueError` for `points_below_zero <= 0`.
[P1 — US1]

## T004 — Wound-record shape tests

`tests/test_resolution.py`: for each wound-producing row, assert the produced record passes
`character.validate_wound` unmodified and carries the fields data-model.md specifies. [P1 — US2]

## T005 — Row-boundary tests

`tests/test_resolution.py`: assert each of the 7 published boundaries (6/30/31, 52/53, 66/67,
78/79, 88/89, 98/99, 110/111) resolves to the correct row key, and a total well above 111 still
resolves to `death`. [P1 — US1]

## T006 — Non-wound rows produce no mutation, no entity, no status change

`tests/test_resolution.py`: assert `out-of-action`, `taken`, `death` produce no wound mutation;
assert nothing in this feature creates a `character`/`thread` entity or touches a `status` field
(grep-level or direct assertion that `_stage_aftermath` has no such side effect). [P1 — US3]

## T007 — `specs/091-aftermath-wound-records/check_aftermath_engine.py`

`specs/002-aftermath-table/check_aftermath.py` already computes and asserts the 71%/23% figures
against a standalone validated model. Following #251's `check_criticals_engine.py` precedent,
this feature's check script cross-checks the *engine's own* `AFTERMATH_TABLE` constant against
that already-validated model (ranges/keys agree) rather than recomputing the odds a second time
-- guarding against the engine's copy drifting from the validated one. [P1 — US1, SC-003]

## T008 — Wire into caller (if an existing combat-resolution entry point exists)

Confirm whether `resolution.py` has (or #251 left a stub for) a post-fight entry point that would
call `_stage_aftermath`; if none exists yet, leave `_stage_aftermath` as a standalone staging
function callable by a future feature (companion status transitions, mortal-critical death-row
re-read) — do not invent a new public API surface beyond what spec.md's scope calls for. [P2]

## Dependencies

T001 → T002 → (T003, T004, T005, T006, T007) — table and staging function must exist before
anything tests or checks against them. T008 is independent, informational.
