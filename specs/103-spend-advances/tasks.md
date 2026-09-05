# Tasks: Spend advances — raise, open, change career

**Input**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md)

**Tests**: included — three spends with eight distinct refusal paths between them.

All commands run from the repository root with `PYTHONPATH=engine`.

## Phase 1: The career graph

- [x] **T001** Add `is_entry(career)` and `find_career(career_id, careers)` to
  `engine/wyrd/career.py`. (FR-005, FR-007)
- [x] **T002** Add `career_complete(skills, career)`: every granted skill held at or above that
  career's cap. (FR-009)
- [x] **T003** Add `completed_career_ids(career_history)`, reading completion off the recorded
  history rather than re-deriving it from live skills. (FR-006, research.md)
- [x] **T004** Add `change_career_legality(target, careers, career_history)` returning
  `unknown_career` / `prerequisites_unmet` per data-model.md, with entry careers always legal.
  (FR-005, FR-006, FR-007)

## Phase 2: The spend

- [x] **T005** Add `SPENDS` and `ADVANCE_COST` to `engine/wyrd/advancement.py`, with their
  docs/design/03-rules.md §6 citations, plus `new_view` for the four-field character view.
  (FR-001)
- [x] **T006** Implement `spend_advance`: unknown spend first, empty purse second, then the named
  action's own rules, returning the data-model.md shapes and mutating nothing. (FR-002, FR-010,
  FR-012)
- [x] **T007** Raise: +5%, requires open and granted, refused at the cap rather than clamped.
  (FR-003)
- [x] **T008** Open: 25%, requires granted and not already held. (FR-004)
- [x] **T009** Change career: legality via `career.py`, appending the departed career with its
  completion flag and leaving every skill untouched. (FR-008, FR-011)

## Phase 3: The surface

- [x] **T010** Add a `spend_advance` passthrough to `engine/wyrd/verbs.py`.
- [x] **T011** Add the `spend-advance` entry to `TOOLS` in `engine/wyrd/catalog.py`, matching
  data-model.md's argument shape.
- [x] **T012** Add the subparser and its dispatch to `engine/wyrd/client.py`.

## Phase 4: Tests

- [x] **T013 [P]** `tests/engine/test_career.py`: entry vs non-entry, completion at and above the
  cap, completion read from history, OR-semantics on prerequisites, a career merely entered not
  qualifying, and an unknown career refused by name. (FR-005, FR-006, FR-007, FR-009)
- [x] **T014 [P]** `tests/engine/test_advancement.py`: the raise path, including the ancestry
  widening and the nine-advance climb asserted against `tools/check_advancement.py`'s own
  `advances_to_cap()` rather than a restated 9. (US1, SC-001)
- [x] **T015 [P]** The open path and its two refusals. (US2, FR-004)
- [x] **T016 [P]** The change-career path: entry always legal, the departure record's completion
  flag, skills untouched, prerequisites, re-entry appending a fresh instance. (US3, FR-008)
- [x] **T017 [P]** The refusal suite: three spends only, every spend costs 1, an empty purse
  refuses before the action's own legality, and no path mutates its inputs. (FR-001, FR-002,
  FR-012, SC-002, SC-004)
- [x] **T018 [P]** `tests/engine/test_client.py`: the CLI's success shape, a refusal shape, and
  `describe` listing the new verb.

## Phase 5: Verification

- [x] **T019** `python3 -m ruff check . && python3 -m ruff format --check .` clean repo-wide.
- [x] **T020** `PYTHONPATH=engine python3 -m pytest -q` green.
- [x] **T021** `python3 tools/check_docs.py` clean — no design document changes, so the graph is
  unchanged, but the check is run rather than assumed.
