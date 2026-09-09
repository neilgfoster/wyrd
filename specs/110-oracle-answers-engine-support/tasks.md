# Tasks: Oracle answers engine support

**Input**: plan.md, spec.md from `specs/110-oracle-answers-engine-support/`

## Phase 1: Data and lookup

- [ ] T001 Add `ORACLE_ANSWER_THRESHOLDS` (the five bands' `T` values, transcribed exactly from
      `docs/design/14-oracle-answers.md`), a pure row-derivation helper, and
      `oracle_answer(band, roll) -> tuple[str, str]` (outcome, wyrd) to `engine/wyrd/rules.py`,
      raising `ValueError` for an unrecognized band or an out-of-range roll (FR-001, FR-002,
      FR-003). Reuse the module's existing `_wyrd_die` helper for the Wyrd die read (FR-004).

## Phase 2: Verb wiring

- [ ] T002 Add `oracle_answer(band, seed=None)` to `engine/wyrd/verbs.py`: rolls via
      `rules.roll_d100`, looks up via `rules.oracle_answer`, returns the read-only result dict
      (FR-004, FR-005, FR-006). [depends on T001]
- [ ] T003 Add the `"oracle-answer"` entry to `engine/wyrd/catalog.py`'s `TOOLS`, mirroring
      `"oracle-prompt"`'s shape (band enum, optional seed, `readOnlyHint: true`). [depends on
      T001]
- [ ] T004 Add the `oracle-answer` subparser and dispatch to `engine/wyrd/client.py`, following
      the `oracle-prompt` pattern (FR-007). [depends on T002, T003]

## Phase 3: Tests

- [ ] T005 [P] Exhaustive table-coverage test: every roll 1-100 for each of the five bands
      resolves to the documented outcome, including every threshold boundary (`T`, `T+1`) (SC-001).
- [ ] T006 [P] Error-path tests: unrecognized band raises `ValueError`; out-of-range roll raises
      `ValueError`.
- [ ] T007 [P] Verb-level test: `verbs.oracle_answer` returns the expected shape (including
      `wyrd`) and never touches `state.py`.

## Phase 4: Verify

- [ ] T008 Run `python3 tools/check_oracle_answers.py` and confirm it still passes unchanged
      (SC-002).
- [ ] T009 Run `python3 -m pytest -q` (`PYTHONPATH=engine`), `python3 -m ruff check .`,
      `python3 -m ruff format --check .`, `python3 tools/check_docs.py`, `python3
      tools/backlog.py check` — all clean (SC-003).

## Dependencies

T001 → T002/T003 → T004. T005-T007 depend on T001-T004 landing. T008 is independent (reads the
already-published doc, unaffected by this feature) and can run any time. T009 is last.
