# Tasks: Systems of power

**Input**: Design documents from `specs/030-supernatural-power-mechanism/`
**Prerequisites**: plan.md (required)

**Tests**: this feature's own verification is `tools/check_power_systems.py`, which embeds its
worked-example fixtures and asserts against them directly — matching every prior Wyrd
rules-with-a-schema feature. No separate contract/integration test suite applies.

## Phase 1: Setup

- [ ] T001 Confirm branch `030-supernatural-power-mechanism` is checked out and
      `specs/030-supernatural-power-mechanism/{spec.md,plan.md}` exist (already done by prior
      pipeline steps; no file changes).

## Phase 2: Foundational

- [ ] T002 Write `docs/adr/0036-one-configurable-power-mechanism.md` recording the load-bearing
      fork: one configurable system-of-power schema vs. a closed set of engine-side mechanism
      shapes, decided in favour of one schema, with the rejected alternative and its reasoning
      (mirrors plan.md's "The load-bearing decision" section and the existing ADR format, e.g.
      `docs/adr/0035-opposed-tests-generalise-to-the-player-facing-roll.md`).

**Checkpoint**: ADR 0036 exists and is internally consistent with plan.md before any schema or
document work depends on it.

## Phase 3: User Story 1 - A setting declares a system of power (Priority: P1)

**Goal**: A setting author can declare a system of power against a published schema and validate
it.

**Independent Test**: run `tools/check_power_systems.py` against its own embedded fixtures and
confirm it accepts a well-formed declaration and rejects a missing/unrecognised field.

- [ ] T003 [US1] Write `docs/design/14-systems-of-power.md`: the schema table (`id`, `name`,
      `skill`, `strain_cost`, `requires_training` required; `resolve_cost`, `ill_omen_taint`,
      `description` optional), the unrecognised-field rejection rule (mirroring
      `13-authoring-a-setting.md`'s bestiary/gear wording), and a worked example declaration.
- [ ] T004 [US1] Add a link to `docs/design/14-systems-of-power.md` from `docs/README.md`'s index
      so `tools/check_docs.py`'s reachability check passes.
- [ ] T005 [US1] Write `tools/check_power_systems.py`: the restricted YAML reader (reused/adapted
      from `tools/check_bestiary.py`'s pattern), `REQUIRED_FIELDS`/`OPTIONAL_FIELDS` per T003's
      schema, kebab-case `id` validation, positive-int cost validation, and the missing-field /
      unrecognised-field / out-of-range rejections — every failure reported, not just the first.
- [ ] T006 [US1] Embed two worked-example fixtures in `tools/check_power_systems.py` (a
      mythic-fantasy system of power and a structurally different far-future/psionic one, per
      SC-003) and assert both validate clean; add fixtures for each rejection class (missing
      field, unrecognised field, bad `id` shape, non-positive cost) and assert each is rejected
      with a message naming the entry and field.
- [ ] T007 [US1] Run `python3 tools/check_power_systems.py` and confirm it exits 0 against its own
      embedded fixtures.

**Checkpoint**: User Story 1 is independently complete — a setting can declare and validate a
system of power.

## Phase 4: User Story 2 - A character invokes a system of power (Priority: P1)

**Goal**: Casting resolves as the engine's ordinary d100 test, with the declared Strain/Resolve
cost paid on resolution and the training gate enforced.

**Independent Test**: read `docs/design/14-systems-of-power.md`'s resolution section against
`docs/design/03-rules.md` §1 and confirm no new dice mechanism, difficulty rule, or assistance rule is
introduced — the only new behaviour is cost application and the training gate.

- [ ] T008 [US2] Add the resolution section to `docs/design/14-systems-of-power.md`: invocation is
      an ordinary d100 test against the declared `skill` (difficulty, declaration, assistance
      unchanged from `03-rules.md` §1); the declared `strain_cost` is paid on resolution
      regardless of outcome; the declared `resolve_cost`, if present, is paid identically;
      `requires_training: true` removes the untrained attempt entirely, mirroring the existing
      untrained-skill rule.
- [ ] T009 [US2] Add a one-line cross-reference at the end of `docs/design/03-rules.md` §1 pointing to
      `docs/design/14-systems-of-power.md`, matching how other consequence chains are
      cross-referenced elsewhere in that document.
- [ ] T010 [US2] Extend `tools/check_power_systems.py`'s worked examples to show the resolution
      trace (skill test → cost applied) for both fixtures from T006, asserting the cost figures
      match what the fixture declares.

**Checkpoint**: User Story 2 is independently complete — casting a declared system of power is
fully specified and consistent with `03-rules.md` §1.

## Phase 5: User Story 3 - An Ill Omen turns the working against the caster (Priority: P2)

**Goal**: A power test's Ill Omen applies the declared Taint gain through the existing
transformation-threshold path, with no new table and correct behaviour when Taint is disabled.

**Independent Test**: read the Ill Omen section against `docs/design/10-transformations.md` and
confirm the Taint gain routes through the same accrual path Exposure/the Bargain already use, and
that disabling Taint (`overrides.disable: [taint]`) suppresses it without affecting the base roll
or the Strain/Resolve costs.

- [ ] T011 [US3] Add the Ill Omen section to `docs/design/14-systems-of-power.md`: on Ill Omen, the
      caster gains the declared `ill_omen_taint` (default 1) via the engine's existing
      Taint-accrual path, a transformation-table roll follows immediately if a threshold is
      crossed, and disabling Taint suppresses this consequence entirely while leaving the base
      roll, Strain and Resolve costs unaffected.
- [ ] T012 [US3] Extend `tools/check_power_systems.py`'s worked examples with an Ill-Omen trace for
      one fixture, asserting the applied Taint gain matches the fixture's declared
      `ill_omen_taint` (or the default of 1 when omitted).

**Checkpoint**: User Story 3 is independently complete — the failure/backlash mode is fully
specified and reuses the existing consequence chain.

## Phase 6: Polish & cross-cutting concerns

- [ ] T013 [P] Run `python3 tools/check_docs.py` and confirm `docs/design/14-systems-of-power.md` is
      reachable from `README.md` and the ADR index picks up ADR 0036.
- [ ] T014 [P] Run `python3 tools/check_dangling_mechanics.py` and confirm no dangling reference
      is introduced by the new document.
- [ ] T015 [P] Run `python3 tools/backlog.py check` and confirm no drift.
- [ ] T016 Run `ruff check . && ruff format --check . && python3 -m pytest -q` and confirm the
      repo-wide suite is green.
- [ ] T017 Re-read `docs/design/14-systems-of-power.md` end to end for the recurring fault classes in
      `CLAUDE.md`'s checklist (setting vocabulary, tone baked into a mechanic, staleness against
      `03-rules.md`/`03a-3-transformations.md`) before raising the PR.

## Dependencies & execution order

- Phase 1 (Setup) has no dependencies.
- Phase 2 (T002, the ADR) blocks every later phase — the schema and its documents are derived from
  the ADR's decision, not the reverse.
- Phase 3 (US1) depends only on Phase 2. It is the MVP: a setting can declare and validate a
  system of power even before resolution/failure semantics are written up.
- Phase 4 (US2) depends on Phase 3 (T003's schema table must exist before T008 can add the
  resolution section to the same document).
- Phase 5 (US3) depends on Phase 4 (the Ill Omen section follows the resolution section in the
  same document, and reuses the same fixtures T006/T010 established).
- Phase 6 (Polish) depends on all prior phases.

## Parallel execution examples

- Within Phase 3: T004 (README link) can run in parallel with T005/T006 (validator) once T003
  (schema table) is written, since they touch different files.
- Within Phase 6: T013, T014, T015 are independent read-only checks and can run in parallel with
  each other; T016 and T017 should run after them.

## Implementation strategy

**MVP first**: Phase 1 + Phase 2 + Phase 3 (User Story 1) delivers a validated, declarable schema
— already enough for a setting author to start writing a system of power, even before the
resolution and Ill Omen write-ups land. Phases 4 and 5 add the mechanical weight the issue's Goal
calls for and are additive to the same document, not a rewrite of Phase 3's output.
