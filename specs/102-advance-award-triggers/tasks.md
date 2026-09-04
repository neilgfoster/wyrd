# Tasks: Award advances against the four session triggers

**Input**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md)

**Tests**: included — this is engine behaviour with three distinct refusal paths.

All commands run from the repository root with `PYTHONPATH=engine`.

## Phase 1: The module

- [x] **T001** Create `engine/wyrd/advancement.py` with `TRIGGERS` and `SESSION_ADVANCE_CEILING`,
  each carrying its docs/design/03-rules.md §6 citation. (FR-001, FR-003)
- [x] **T002** Implement `award_advance(trigger, record)` in `engine/wyrd/advancement.py`, checking
  unknown-trigger, then already-awarded, then ceiling, and returning the shapes in data-model.md.
  Never mutates its argument. (FR-001, FR-002, FR-003, FR-004, FR-005)
- [x] **T003** Implement `begin_session(record)` in `engine/wyrd/advancement.py`: fresh `triggers`,
  `advances_unspent` carried through. (FR-006)

## Phase 2: The surface

- [x] **T004** Add `award_advance` and `begin_session` passthroughs to `engine/wyrd/verbs.py`.
- [x] **T005** Add `award-advance` and `begin-session` entries to `TOOLS` in
  `engine/wyrd/catalog.py`, matching the argument shapes in data-model.md.
- [x] **T006** Add both subparsers and their dispatch to `engine/wyrd/client.py`.

## Phase 3: Tests

- [x] **T007 [P]** `tests/engine/test_advancement.py`: each of the four triggers awards once and
  raises `advances_unspent` by exactly 1. (US1, SC-001, FR-005)
- [x] **T008 [P]** Unknown trigger is refused with `refusal: "unknown_trigger"` and leaves the
  record unchanged. (US1 scenario 3, FR-001)
- [x] **T009 [P]** A repeated trigger is refused with `refusal: "already_awarded"`; a new session
  makes it available again. (US2, SC-001)
- [x] **T010 [P]** A fourth *distinct* trigger is refused with `refusal: "session_ceiling"`, and
  that refusal is not equal to the repeated-trigger refusal. (US3, SC-002, SC-003)
- [x] **T011 [P]** `begin_session` clears the triggers and leaves `advances_unspent` untouched;
  `award_advance` never mutates the record it was passed. (FR-006)
- [x] **T012 [P]** No sequence of legal awards drives one session above 3 — exhaustive over all
  orderings of the four triggers. (SC-002)
- [x] **T013 [P]** The module stores and derives no experience-point total: the returned record has
  exactly the two documented keys. (FR-007)
- [x] **T014** `tests/engine/test_client.py`: both new CLI verbs emit the documented JSON, and
  `describe` lists them.

## Phase 4: Verification

- [x] **T015** `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] **T016** `PYTHONPATH=engine python3 -m pytest -q` green.
- [x] **T017** `python3 tools/check_docs.py` and `python3 tools/backlog.py check` clean.

## Dependencies

T001 → T002/T003 → T004 → T005/T006 → tests. Phase 3's `[P]` tasks are independent of each other.
