# Tasks: Downtime phase, including Mend

Input: design artifacts in `specs/116-downtime-mend/` (plan.md, research.md, data-model.md,
quickstart.md). Tests before implementation, per data-model.md's function signatures.

## T001 — Downtime loop state and transitions [P1, User Story 1]

In `engine/wyrd/downtime.py`: `DOWNTIME_STEPS`, `new_downtime_state()`, `advance_downtime(state,
to_step, *, undertaking=None)` per data-model.md. Enforce the linear
destination→upkeep→advances→undertaking→rest sequence and the exactly-one-undertaking gate.

## T002 — Upkeep [P1, User Story 1]

`apply_upkeep(destination, standing, coin, *, trade=None)` per data-model.md: at-home no-op,
away-from-home requires exactly one of "standing"/"coin", coin trade rejected on insufficient
funds.

## T003 — Undertaking vocabulary [P1, User Story 1]

`UNDERTAKINGS = ("recover", "mend", "pursue", "cultivate", "learn", "ask")`, validated by
`advance_downtime`'s "undertaking" transition (T001).

## T004 — Rest [P1, User Story 1]

`apply_rest(stamina_max)` — unconditional, returns `stamina_max`.

## T005 — Calendar-advance fact [P1, User Story 1]

`close_downtime(state)` returning `{"calendar_advanced": True}`.

## T006 — Mend [P1, User Story 2]

`MEND_LADDER` fixed lookup (skill: -10→-5→closed; stamina_max: -1→closed; dread: +1→closed) and
`apply_mend(wound_id, wounds, *, closed_marker)` per data-model.md: unknown-id, recurring, and
already-closed rejections; steps one rung or closes; never mutates the input list.

## T007 — Unit tests

`tests/engine/test_downtime.py` (stdlib unittest, matching `tests/engine/test_rally.py`) covering every acceptance scenario in spec.md (User Stories 1 and 2,
Edge Cases): loop transitions and the exactly-one gate, both Upkeep trade paths and the at-home
no-op and insufficient-funds rejection, Rest unconditionality, calendar-advance exposure, Mend at
every ladder rung for all three effect types, Mend against a recurring/unknown/already-closed
wound, and Mend consuming the Downtime undertaking slot.

## T008 — Regression check

Run `specs/014-stamina-recovery/check_recovery.py` before and after, per quickstart.md and
spec.md's SC-004; confirm no diff (this feature reads the same wound-shape assumptions that
script already relies on but does not change them).

## T009 — Lint and docs cross-check

`ruff check . && ruff format --check .`; `python3 tools/check_docs.py` (no new design doc added,
but confirm the check still passes); update `docs/design/16-session.md` only if implementation
uncovers a discrepancy from the spec (none expected — this feature implements that doc as
written).

## Dependencies

T001-T006 can be implemented in any order (independent pure functions over shared vocabulary
constants) but T007 depends on all of them. T008-T009 run after T007 is green.
