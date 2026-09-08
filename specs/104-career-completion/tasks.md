# Tasks: Career completion grants Stamina and a Mark

**Input**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md),
[research.md](research.md)

**Tests**: included — one payout path, three ways it must *not* fire, and one ceiling.

All commands run from the repository root with `PYTHONPATH=engine`.

## Phase 1: The predicate

- [x] **T001** `engine/wyrd/career.py`: make `career_complete` return `False` for a career
  granting no skills, so an empty grant list is not vacuously complete. (FR-001, research.md R4)

## Phase 2: The payout

- [x] **T002** `engine/wyrd/advancement.py`: add `STAMINA_MAX_CEILING = 10`, citing
  docs/design/03-rules.md §6 and `tools/check_advancement.py` as the figure's origin. (FR-004)
- [x] **T003** Widen `_view` and `new_view` with `stamina_max`, `marks` and `career_completed`,
  each optional on input with data-model.md's default, so a #277-era caller still works.
- [x] **T004** Add the completion transition and apply it to the `raise` and `open` paths: on a
  not-complete → complete edge, append one Mark naming the career and raise `stamina_max` by one
  bounded by the ceiling, setting `career_completed`. (FR-002, FR-003, FR-004, FR-008)
- [x] **T005** `_spend_change_career`: write the departing instance's `career_completed` flag into
  the history entry instead of recomputing `career_complete` from live skills, and enter the new
  career with `career_completed` reset to `False`. (FR-005, FR-006, FR-007, research.md R3)
- [x] **T006** Confirm every refusal path returns the three new fields unchanged — `_refuse`
  rebuilds the view, so it must carry them. (FR-009, FR-011)

## Phase 3: The surface

- [x] **T007** `engine/wyrd/catalog.py`: widen the `spend-advance` description to say that a spend
  which completes the career grants maximum Stamina and a Mark. No schema change — the view is
  passed opaquely as JSON.

## Phase 4: Tests

- [x] **T008 [P]** `tests/engine/test_career.py`: a career granting no skills is not complete; a
  skill held above the cap still counts toward completion. (FR-001, Edge Cases)
- [x] **T009 [P]** `tests/engine/test_advancement.py`: the payout fires on the spend that finishes
  the last granted skill, and not on the spend before it; opening the last granted skill at 25%
  does not complete the career. (US1, FR-002, FR-003)
- [x] **T010 [P]** Per-instance: a further spend inside an already-paid career pays nothing; a
  career left unfinished and re-entered pays on the fresh instance; a career completed twice
  yields two Marks. (US2, FR-005, FR-006)
- [x] **T011 [P]** The ceiling: 9 → 10 pays Stamina and a Mark, 10 → 10 pays the Mark only, and
  the whole twelve-instance chronicle is asserted against `tools/check_advancement.py`'s
  `stamina_ceiling()` and `run_chronicle()` rather than restated figures. (US3, SC-001, SC-002,
  SC-003)
- [x] **T012 [P]** Departure and purity: the history entry's `completed` follows the paid flag
  even after a wound lowers a skill below the cap; every refusal leaves `stamina_max`, `marks` and
  `career_completed` byte-identical; nothing passed in is mutated. (FR-007, FR-009, FR-011,
  SC-004)
- [x] **T013 [P]** `tests/engine/test_client.py`: the CLI round-trips the widened view and its
  payout in the `spend-advance` response.

## Phase 5: Documentation

- [x] **T014** `docs/design/03-rules.md` §6: state *when* a completion pays — on the advance that
  finishes the last granted skill — and that an instance pays once. The rule's substance is
  already there; this is the sentence the engine had to answer and the document did not.

## Phase 6: Verification

- [x] **T015** `python3 tools/check_advancement.py` runs clean and its published figures are the
  ones the tests assert against.
- [x] **T016** `PYTHONPATH=engine python3 -m pytest -q` green repo-wide.
- [x] **T017** `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] **T018** `python3 tools/check_docs.py` clean — 03-rules.md changed, so the graph is
  re-checked rather than assumed.
