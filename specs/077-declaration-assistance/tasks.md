# Tasks: Declaration and assistance bonuses

**Input**: Design documents from `/specs/077-declaration-assistance/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included, same rationale as #221/#222.

**Organization**: US1 (declaration) and US2 (assistance) are independent pure lookups and can be
built in parallel. US3 (wiring both into `opposed_test`) depends on both.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Extends the existing `engine/wyrd/` and `tests/engine/` — no new files.

---

## Phase 1: Setup

None needed — extends #221/#222's existing modules directly.

---

## Phase 2: Tests (write first, confirm they fail)

- [x] T001 [P] [US1] Add to `tests/engine/test_rules.py`: `declaration_bonus("specific")` == 10,
      `declaration_bonus("specific_leveraging")` == 20, `declaration_bonus("brief")` == 0,
      `declaration_bonus("against_nature")` == -20, `declaration_bonus("removes_risk")` is
      `None` (SC-001); `declaration_bonus("bogus")` raises `ValueError` (FR-002)
- [x] T002 [P] [US2] Add to `tests/engine/test_rules.py`: `assistance_bonus(30)` == 3,
      `assistance_bonus(45)` == 4, `assistance_bonus(100)` == 10 (cap binds, not coincidence —
      also check `assistance_bonus(90)` == 9 to confirm the cap isn't hit early), across all of
      0/10/.../100 (SC-002); `assistance_bonus(100, can_attempt=False)` == 0
- [x] T003 [US3] Add to `tests/engine/test_rules.py`: `opposed_test(skill=70, opponent=30,
      seed=1)` (no new kwargs) produces byte-identical output to the pre-#223 call across 100
      (skill, opponent, seed) triples, proving no behavior change for existing callers (SC-003,
      FR-005) — depends on T001/T002 existing so `opposed_test`'s signature already has the new
      parameters to call without them
- [x] T004 [US3] Add to `tests/engine/test_rules.py`: `opposed_test(skill=50, opponent=50,
      declaration="specific", helper_skill=45, seed=1)` has `effective_pct == 64` (50+10+4,
      clipped as #222 already clips); `declaration="removes_risk"` produces `no_roll: True,
      success: True, roll: None, effective_pct: None, degrees: None` and calls the dice
      primitive zero times (mock `rules.roll_d100` and assert not called, SC-004); an
      unrecognized `declaration` raises before any roll happens
- [x] T005 [P] [US1] Add to `tests/engine/test_verbs.py`: `verbs.declaration_bonus("specific")`
      returns the shape from data-model.md
- [x] T006 [P] [US2] Add to `tests/engine/test_verbs.py`: `verbs.assistance_bonus(45)` returns
      the shape from data-model.md
- [x] T007 [P] [US1] Add to `tests/engine/test_client.py`: `describe --name declaration-bonus`
      matches contracts/cli.md; `declaration-bonus --category specific_leveraging` returns
      `{"bonus": 20, ...}`; `declaration-bonus --category bogus` returns a structured error
- [x] T008 [P] [US2] Add to `tests/engine/test_client.py`: `describe --name assistance-bonus`
      matches contracts/cli.md; `assistance-bonus --helper-skill 45` returns `{"bonus": 4, ...}`;
      `--can-attempt false` zeroes the bonus
- [x] T009 [US3] Add to `tests/engine/test_client.py`: `opposed-test --skill 50 --opponent 50
      --declaration specific --helper-skill 45 --seed 1` returns `effective_pct: 64`;
      `--declaration removes_risk` returns `no_roll: true, roll: null`

---

## Phase 3: Implementation

- [x] T010 [P] [US1] Implement `DECLARATION_BONUSES` dict and `declaration_bonus(category: str)
      -> int | None` in `engine/wyrd/rules.py`, raising `ValueError` for an unrecognized category
- [x] T011 [P] [US2] Implement `assistance_bonus(helper_skill: int, can_attempt: bool = True) ->
      int` in `engine/wyrd/rules.py`: `min(helper_skill // 10, 10)` if `can_attempt` else `0`
- [x] T012 [US3] Extend `opposed_test` in `engine/wyrd/rules.py` with `declaration: str | None =
      None`, `helper_skill: int | None = None`, `helper_can_attempt: bool = True`: when
      `declaration == "removes_risk"`, return immediately with `no_roll: True` and no call to
      `roll_d100`; otherwise sum `declaration_bonus(declaration)` (if supplied) and
      `assistance_bonus(helper_skill, helper_can_attempt)` (if `helper_skill` supplied) into the
      skill used for `effective_pct`, and include `declaration`/`helper_skill`/`no_roll: False`
      in the result — depends on T010, T011
- [x] T013 [P] [US1] Add `declaration-bonus` to `TOOLS` in `engine/wyrd/catalog.py`, matching
      contracts/cli.md
- [x] T014 [P] [US2] Add `assistance-bonus` to `TOOLS` in `engine/wyrd/catalog.py`, matching
      contracts/cli.md
- [x] T015 [US3] Extend the `opposed-test` entry's `inputSchema` in `catalog.py` with the three
      new optional properties, per contracts/cli.md
- [x] T016 [P] [US1] Implement `declaration_bonus(category)` verb wrapper in
      `engine/wyrd/verbs.py`
- [x] T017 [P] [US2] Implement `assistance_bonus(helper_skill, can_attempt=True)` verb wrapper in
      `engine/wyrd/verbs.py`
- [x] T018 [US3] Extend the `opposed_test` verb wrapper in `verbs.py` to pass the three new
      kwargs through to `rules.opposed_test` — depends on T012
- [x] T019 [P] [US1] Add the `declaration-bonus` subcommand to `engine/wyrd/client.py`: `wrap
      ValueError` from an unrecognized category into the structured `{"error": ...}` shape, per
      contracts/cli.md
- [x] T020 [P] [US2] Add the `assistance-bonus` subcommand to `client.py`: `--helper-skill`
      required int, `--can-attempt` optional bool (default true)
- [x] T021 [US3] Extend the `opposed-test` subcommand in `client.py` with `--declaration`,
      `--helper-skill`, `--helper-cannot-attempt` (store-true) — depends on T018
- [x] T022 Add `to_text` cases for `declaration-bonus` and `assistance-bonus` results in
      `engine/wyrd/render.py`, and update the `opposed-test` case to include declaration/
      assistance context when present

**Checkpoint**: `python3 -m unittest discover -s tests/engine` passes.

---

## Phase 4: Polish

- [x] T023 Run every step of `specs/077-declaration-assistance/quickstart.md` by hand and confirm
- [x] T024 [P] Run `ruff check engine/ tests/engine/` and `ruff format --check engine/
      tests/engine/`, fix anything flagged

---

## Dependencies & Execution Order

- Phase 2's US1/US2 tests (T001, T002, T005-T008) are independent and parallelizable.
- Phase 2's US3 tests (T003, T004, T009) need `opposed_test`'s signature already extended to
  call it meaningfully, so they're written last within Phase 2 even though they're still
  "before implementation" in spirit — they'll fail against the current (unmodified) signature
  until T012 lands, same as any other pre-implementation test.
- Phase 3: T010/T011 (declaration/assistance) are independent; T012 (extend opposed_test)
  depends on both. T013/T014 (catalog) are independent of each other and of T010-T012. T015
  depends on T012 existing conceptually (matches its parameters) but not on catalog ordering.
  T016/T017 depend on T010/T011 respectively; T018 depends on T012.

## Implementation Strategy

Single increment, same as #222 — no meaningful MVP smaller than "all three lookups wired
together," since US3's whole point is confirming composition, not adding new logic of its own.
