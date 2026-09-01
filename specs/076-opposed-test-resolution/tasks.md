# Tasks: Core opposed-test resolution

**Input**: Design documents from `/specs/076-opposed-test-resolution/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included, per the same rationale as #221 — the spec's success criteria are only
meaningfully verified by automated tests (a large sample of skill/opponent pairs, all ten Wyrd
die digits crossed with both outcomes), not manual inspection.

**Organization**: A single user-story-ordered phase set. Unlike #221, these three user stories
(effective%/success, degrees, Wyrd die) all live in one function and cannot be built as
separately-shippable increments — US2 and US3 are properties of the same roll US1 produces, not
separate code paths. Phases below still follow spec.md's priority order for the *order tests are
written and reviewed in*, not for independent delivery.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Extends #221's existing `engine/wyrd/` and `tests/engine/` — no new files.

---

## Phase 1: Setup

No setup needed — #221's package skeleton, dice primitive, catalog, and CLI dispatch already
exist and this feature extends them directly.

---

## Phase 2: Tests (write first, confirm they fail)

- [ ] T001 [P] [US1] Add to `tests/engine/test_rules.py`: `effective_pct` matches
      `clip(50 + (skill - opponent), 5, 95)` across a spread of (skill, opponent) pairs including
      an even match (50/50 → 50), a wide gap clipped high (95/5 → 95) and low (5/95 → 5), and at
      least 1000 generated pairs asserted against the formula computed independently in the test
      itself (SC-001)
- [ ] T002 [P] [US1] Add to `tests/engine/test_rules.py`: success is `true` iff `roll <=
      effective_pct`, for both a passing and failing seed at a fixed `effective_pct`
- [ ] T003 [P] [US2] Add to `tests/engine/test_rules.py`: on success, `degrees` equals
      `tens(effective_pct) - tens(roll)` exactly, for several seeds (SC-002); on failure,
      `degrees` is `None` (FR-005)
- [ ] T004 [P] [US3] Add to `tests/engine/test_rules.py`: for all ten units digits 0-9, crossed
      with both a success and a failure case (20 total), `wyrd` matches the table (`0` →
      `"ill_omen"`, `9` → `"fair_omen"`, else `"none"`) regardless of `success` (SC-003, FR-007)
- [ ] T005 [P] [US1] Add to `tests/engine/test_verbs.py`: `verbs.opposed_test(skill=70,
      opponent=30, seed=1)` returns the shape from data-model.md and performs no state write
      (assert no `chronicle_state.yaml` is created in a clean temp cwd)
- [ ] T006 [P] [US1] Add to `tests/engine/test_client.py`: `describe --name opposed-test` returns
      the catalog entry from contracts/cli.md; `opposed-test --skill 70 --opponent 30 --seed 1`
      returns the documented JSON shape; `--format text` renders the documented line; a missing
      required argument exits non-zero (argparse's own behavior)

---

## Phase 3: Implementation

- [ ] T007 [US1] Implement `opposed_test(skill: int, opponent: int, seed: int | None = None) ->
      dict` in `engine/wyrd/rules.py`: compute `effective_pct = max(5, min(95, 50 + (skill -
      opponent)))`; call `roll_d100(sides=100, seed=seed)` for the single roll (reusing #221's
      primitive, never re-rolling); determine `success = roll <= effective_pct`
- [ ] T008 [US3] In the same function, read the Wyrd die from `roll % 10` as a single shared step
      before branching on `success` (research.md's independence decision): `0` → `"ill_omen"`,
      `9` → `"fair_omen"`, else `"none"`
- [ ] T009 [US2] In the same function, set `degrees = tens(effective_pct) - tens(roll)` only when
      `success` is `true`, else `degrees = None`; return the full result shape from
      data-model.md
- [ ] T010 [US1] Add the `opposed-test` entry to `TOOLS` in `engine/wyrd/catalog.py`, matching
      contracts/cli.md's `describe` shape exactly (`readOnlyHint: true`, since this verb performs
      no state write)
- [ ] T011 [US1] Implement `opposed_test(skill: int, opponent: int, seed: int | None = None) ->
      dict` in `engine/wyrd/verbs.py`: a thin wrapper calling `rules.opposed_test` directly, with
      **no** `state.save`/`state.load` call (unlike `verbs.roll`)
- [ ] T012 [US1] Add the `opposed-test` subcommand to `engine/wyrd/client.py`: `--skill` and
      `--opponent` required ints, `--seed` optional int, dispatching to `verbs.opposed_test`; no
      structured-error path is needed for this verb (any integer skill/opponent pair is valid
      input, per contracts/cli.md's exit-code note) — a missing required argument is argparse's
      own usage error
- [ ] T013 [US3] Add a `to_text` case for `opposed-test` results in `engine/wyrd/render.py`,
      matching contracts/cli.md's documented text format for both success and failure

**Checkpoint**: `python3 -m unittest discover -s tests/engine` passes, including all new cases.

---

## Phase 4: Polish

- [ ] T014 Run every step of `specs/076-opposed-test-resolution/quickstart.md` by hand from the
      repo root and confirm each expected result matches
- [ ] T015 [P] Run `ruff check engine/ tests/engine/` and `ruff format --check engine/
      tests/engine/` (config now exists, per #221's follow-up) and fix anything flagged
- [ ] T016 Update `docs/design/02-architecture.md`'s `engine/` tree comment if this feature
      changes what's true about the engine's build status (likely no change needed — #221
      already moved it to "build underway"; only revisit if this feature's landing changes that
      wording's accuracy)

---

## Dependencies & Execution Order

- Phase 2 (tests) can all be written in parallel — different assertions in shared files, but
  each targets a distinct new function that doesn't exist yet, so no test depends on another
  test's code existing.
- Phase 3 (implementation) is necessarily sequential within `rules.py` (T007 → T008 → T009 build
  one function incrementally) but T010 (catalog), T011 (verb), T012 (CLI), T013 (render) can
  proceed in parallel once T007-T009 give them a function to call.
- Phase 4 depends on Phase 3 being complete.

## Implementation Strategy

Single increment — write all tests (Phase 2), confirm they fail against #221's code alone (no
`opposed_test` function exists yet), then implement (Phase 3) until they pass, then polish
(Phase 4). Unlike #221, there's no meaningful MVP subset smaller than "the whole function,"
since degrees and the Wyrd die are properties of the one roll US1 already makes.
