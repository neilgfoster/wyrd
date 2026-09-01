# Tasks: Group tests and extended tasks

**Input**: Design documents from `/specs/078-group-tests-extended-tasks/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included, same rationale as #221-#223.

**Organization**: US1 (group tests) and US2 (extended tasks) are independent — both compose over
`opposed_test` but neither depends on the other's logic — and build in parallel.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Extends the existing `engine/wyrd/` and `tests/engine/` — no new files.

---

## Phase 1: Setup

None needed — extends #221-#223's existing modules directly.

---

## Phase 2: Tests (write first, confirm they fail)

- [ ] T001 [P] [US1] Add to `tests/engine/test_rules.py`: `select_group_skill([70,45,30],
      "most_capable")` == 70; `select_group_skill([70,45,30], "least_capable")` == 30;
      `select_group_skill([70, None, 30], "least_capable")` == 10 (untrained substitution,
      FR-002); `select_group_skill([], "most_capable")` raises `ValueError` (FR-004);
      `select_group_skill([50], "bogus")` raises `ValueError` (FR-005)
- [ ] T002 [US1] Add to `tests/engine/test_rules.py`: `group_test(member_skills=[70,45,30],
      mode="most_capable", opponent=50, seed=1)` has `selected_skill == 70` and its
      `effective_pct`/`roll`/`success`/`degrees`/`wyrd` match calling `opposed_test(70, 50,
      seed=1)` directly (composition, not reimplementation); mock `rules.roll_d100` and assert
      it is called exactly once regardless of `len(member_skills)` (SC-002, tested with 1, 3, and
      10 members)
- [ ] T003 [P] [US2] Add to `tests/engine/test_rules.py`: `resolve_extended_interval` with a
      seed/skill/opponent producing a known success degrees `d` has `gained == max(1, d)` for
      `d` in 0..9 (SC-003, specifically confirming `d=0` still yields `gained=1`); a failing
      seed yields `gained == 0` and `progress` unchanged (SC-004, at least 20 distinct failing
      seeds); `done` is `false` at `progress == target - 1` and `true` at `progress == target`
      after the interval (SC-005)
- [ ] T004 [US2] Add to `tests/engine/test_rules.py`: a `declaration="removes_risk"` interval
      yields `gained == 1` (the documented Assumption) without calling `roll_d100`
- [ ] T005 [P] [US1] Add to `tests/engine/test_verbs.py`: `verbs.group_test(...)` returns the
      shape from data-model.md
- [ ] T006 [P] [US2] Add to `tests/engine/test_verbs.py`:
      `verbs.resolve_extended_interval(...)` returns the shape from data-model.md
- [ ] T007 [P] [US1] Add to `tests/engine/test_client.py`: `describe --name group-test` matches
      contracts/cli.md; `group-test --member-skills 70,45,30 --mode most_capable --opponent 50
      --seed 1` returns `selected_skill: 70`; an empty `--member-skills` and an unrecognized
      `--mode` both return structured errors
- [ ] T008 [P] [US2] Add to `tests/engine/test_client.py`: `describe --name
      extended-task-interval` matches contracts/cli.md; `extended-task-interval --skill 45
      --opponent 50 --progress 2 --target 4 --seed 1` returns the documented shape

---

## Phase 3: Implementation

- [ ] T009 [US1] Implement `select_group_skill(member_skills: list[int | None], mode: str) ->
      int` in `engine/wyrd/rules.py`: substitute 10 for any `None` entry, raise `ValueError` for
      an empty list or an unrecognized mode, return `max`/`min` of the substituted list per mode
- [ ] T010 [US1] Implement `group_test(member_skills, mode, opponent, seed=None,
      **opposed_test_kwargs) -> dict` in `rules.py`: call `select_group_skill`, then
      `opposed_test(selected_skill, opponent, seed=seed, **opposed_test_kwargs)`, merge in
      `member_skills`, `mode`, `selected_skill` — depends on T009 and the existing `opposed_test`
- [ ] T011 [US2] Implement `resolve_extended_interval(skill, opponent, progress, target,
      seed=None, **opposed_test_kwargs) -> dict` in `rules.py`: call `opposed_test` once; if
      `no_roll` is true, `gained = 1`; elif `success`, `gained = max(1, degrees)`; else
      `gained = 0`; return the opposed-test result merged with `progress: progress + gained,
      target, gained, done: (progress + gained) >= target`
- [ ] T012 [P] [US1] Add `group-test` to `TOOLS` in `engine/wyrd/catalog.py`, matching
      contracts/cli.md
- [ ] T013 [P] [US2] Add `extended-task-interval` to `TOOLS` in `catalog.py`, matching
      contracts/cli.md
- [ ] T014 [P] [US1] Implement the `group_test` verb wrapper in `engine/wyrd/verbs.py`
- [ ] T015 [P] [US2] Implement the `resolve_extended_interval` verb wrapper in `verbs.py`
- [ ] T016 [P] [US1] Add the `group-test` subcommand to `engine/wyrd/client.py`: `--member-skills`
      a comma-separated list (empty entries parse as `None`, per contracts/cli.md's example),
      `--mode` required, `--opponent` required int, `--seed` optional; wrap `ValueError` into
      the structured `{"error": ...}` shape
- [ ] T017 [P] [US2] Add the `extended-task-interval` subcommand to `client.py`: `--skill`,
      `--opponent`, `--progress`, `--target` required ints, `--seed` optional
- [ ] T018 Add `to_text` cases for `group-test` and `extended-task-interval` results in
      `engine/wyrd/render.py`

**Checkpoint**: `python3 -m unittest discover -s tests/engine` passes.

---

## Phase 4: Polish

- [ ] T019 Run every step of `specs/078-group-tests-extended-tasks/quickstart.md` by hand and
      confirm
- [ ] T020 [P] Run `ruff check engine/ tests/engine/` and `ruff format --check engine/
      tests/engine/`, fix anything flagged
- [ ] T021 Update the epic tracking: this is the last of #208's four children (#221, #222, #223,
      #224) — after this PR merges, check whether #208 itself should be closed (all its
      acceptance criteria met) as part of wrapping up, not as a task this PR's code touches

---

## Dependencies & Execution Order

- Phase 2: T001, T005, T007, T012 (US1) and T003, T006, T008, T013 (US2) chains are independent
  of each other. T002 (group_test test) needs T001's function to exist conceptually to call
  meaningfully but is still written before T009/T010 land, same as any pre-implementation test.
  T004 similarly precedes T011.
- Phase 3: T009 before T010 (T010 calls T009). T011 is independent of T009/T010. T012-T018 can
  proceed in parallel once T009-T011 exist.
- Phase 4 depends on Phase 3.

## Implementation Strategy

US1 (group tests) and US2 (extended tasks) can be built as two genuinely independent increments
if desired — unlike #223's US3, neither depends on the other's function existing. Still delivered
as one PR here since both are small and both are the last two subsections of the same source
document section.
