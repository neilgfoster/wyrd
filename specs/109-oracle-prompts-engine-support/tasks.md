# Tasks: Oracle prompts engine support

**Input**: plan.md, spec.md from `specs/109-oracle-prompts-engine-support/`

## Phase 1: Data and lookup

- [ ] T001 Add `ORACLE_PROMPT_TABLES` (the four families' ten-row tables, transcribed exactly from
      `docs/design/15-oracle-prompts.md`) and `oracle_prompt(family, roll)` to `engine/wyrd/rules.py`,
      raising `ValueError` for an unrecognized family or an out-of-range roll (FR-001, FR-002,
      FR-003).

## Phase 2: Verb wiring

- [ ] T002 Add `oracle_prompt(family, seed=None)` to `engine/wyrd/verbs.py`: rolls via
      `rules.roll_d100`, looks up via `rules.oracle_prompt`, returns the read-only result dict
      (FR-004, FR-005, FR-006). [depends on T001]
- [ ] T003 Add the `"oracle-prompt"` entry to `engine/wyrd/catalog.py`'s `TOOLS`. [depends on T001]
- [ ] T004 Add the `oracle-prompt` subparser and dispatch to `engine/wyrd/client.py`, following the
      `skill-scale`/`declaration-bonus` pattern. [depends on T002, T003]

## Phase 3: Tests

- [ ] T005 [P] Exhaustive table-coverage test: every roll 1-100 for each of the four families
      resolves to the documented row (SC-001).
- [ ] T006 [P] Error-path tests: unrecognized family raises `ValueError`; out-of-range roll raises
      `ValueError`.
- [ ] T007 [P] Verb-level test: `verbs.oracle_prompt` returns the expected shape and never touches
      `state.py`.

## Phase 4: Fix check script and verify

- [ ] T008 Fix `tools/check_oracle_prompts.py`'s stale `DOC` path (`13-` → `15-`) (FR-007). Run it
      and confirm it passes (SC-002).
- [ ] T009 Run `python3 -m pytest -q` (`PYTHONPATH=engine`), `python3 -m ruff check .`,
      `python3 -m ruff format --check .`, `python3 tools/check_docs.py`, `python3
      tools/backlog.py check` — all clean (SC-003).

## Dependencies

T001 → T002/T003 → T004. T005-T007 depend on T001-T004 landing. T008 is independent (only touches
the tools script) and can run any time. T009 is last.
