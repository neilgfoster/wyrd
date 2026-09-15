# Tasks: Chronicle CLI Verbs

**Input**: Design documents from `/specs/153-chronicle-cli-verbs/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-verbs.md,
quickstart.md

**Tests**: Explicitly requested (spec.md SC-002, issue #402's acceptance criteria) — included.

**Organization**: Tasks are grouped by user story (spec.md priorities P1/P1/P2/P3/P2/P3) to
enable independent implementation and testing of each.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1..US6)

## Path Conventions

Single project: `engine/wyrd/`, `tests/engine/` at repository root (plan.md's Project
Structure).

---

## Phase 1: Setup

- [x] T001 Confirm `engine/wyrd/log.py` does not already exist and stub its module docstring
      (per research.md's log-format decision) at `engine/wyrd/log.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The one shared routine every entity-reading verb (US1, US2, US3) needs — building
the effective entity set — plus the new `log.py` functions US4 needs. Must complete before US1,
US2, US3, US4 begin; US5 and US6 do not depend on this phase.

- [x] T002 Add `load_effective_entities(chronicle_dir: pathlib.Path) -> dict[str, dict]` to
      `engine/wyrd/verbs.py`: loads `setting/**/*.md` and `overlay/**/*.md` via
      `entity.load_set`, resolves each via `entity.resolve_entity`, merges in
      `entities/**/*.md` unchanged (research.md's "effective entity set assembly" decision).
- [x] T003 [P] Add `append_beat(chronicle_dir: pathlib.Path, record: dict) -> None` and
      `read_log(chronicle_dir: pathlib.Path, *, last: int | None = None, since: str | None =
      None) -> list[dict]` to `engine/wyrd/log.py`, per research.md's log-format decision
      (JSON Lines, `{"beat_id","mode","resolved_at"}`, `log/<chronicle-name>.jsonl`).
- [x] T004 [P] Add `find_entities(entities: dict[str, dict], *, type: str, status: str | None =
      None, tag: str | None = None) -> dict[str, dict]` to `engine/wyrd/verbs.py` — the general
      `find` predicate (research.md's "find's filter semantics" decision).
- [x] T005 [P] Add `open_threads_by_heat(entities: dict[str, dict]) -> list[dict]` to
      `engine/wyrd/verbs.py` — the full `status: open` set sorted by `heat` descending (broader
      than `loadtier._hottest_open_threads`'s capped slice).
- [x] T006 [P] Add `companions_with_party(entities: dict[str, dict]) -> dict[str, dict]` to
      `engine/wyrd/verbs.py` — the `role: companion` + `status: with-party` predicate `party`
      needs (spec.md Clarifications).

**Checkpoint**: Foundation ready — US1, US2, US3, US4 can now proceed; US5, US6 could already
have started in parallel with this phase.

---

## Phase 3: User Story 1 - Load a session's working context in one call (Priority: P1) 🎯 MVP

**Goal**: `session-context` returns the Always-loaded tier in one call.

**Independent Test**: Call `session-context` against a fixture chronicle with a player
character, a with-party companion, an absent companion, threads at heat 5/3/1, a recap, and a
contract; confirm the result matches spec.md's Acceptance Scenario 1.

### Tests for User Story 1

- [x] T007 [P] [US1] Test `verbs.session_context` returns exactly the Always-loaded composition
      (player character, only with-party companions, only `heat >= 3` threads, recap text,
      contract text) in `tests/engine/test_verbs.py`.
- [x] T008 [P] [US1] Test `verbs.session_context` against a chronicle with no open threads
      returns an empty threads collection, not an error, in `tests/engine/test_verbs.py`.

### Implementation for User Story 1

- [x] T009 [US1] Implement `session_context(chronicle_dir: pathlib.Path) -> dict` in
      `engine/wyrd/verbs.py`: calls `load_effective_entities` (T002), `loadtier.always_tier`,
      reads `recap.md` and the engine contract text, returns the `{"verb": "session-context",
      ...}` shape from data-model.md.
- [x] T010 [US1] Register `session-context` in `engine/wyrd/catalog.py`'s `TOOLS` (no required
      args, per contracts/cli-verbs.md).
- [x] T011 [US1] Add the `session-context` subparser and `_run_session_context` dispatch to
      `engine/wyrd/client.py`, following the `find-noun` pattern.

**Checkpoint**: User Story 1 fully functional and independently testable.

---

## Phase 4: User Story 2 - Fetch or query any entity on demand (Priority: P1)

**Goal**: `get <id>` and `find --type T [--status S] [--tag G]` work per spec.md.

**Independent Test**: Call `get` on a known id (overlay-resolved) and an unresolvable id;
call `find` with each filter combination against a fixture set.

### Tests for User Story 2

- [x] T012 [P] [US2] Test `verbs.get` returns the overlay-resolved effective form for an id
      with a chronicle overlay, in `tests/engine/test_verbs.py`.
- [x] T013 [P] [US2] Test `verbs.get` raises (a `state.StateError` or equivalent, distinct from
      an empty result) for an id resolving in neither setting, overlay, nor chronicle entities,
      in `tests/engine/test_verbs.py`.
- [x] T014 [P] [US2] Test `verbs.find` returns exactly the entities matching every given filter,
      and an empty result (not an error) for a combination matching nothing, in
      `tests/engine/test_verbs.py`.

### Implementation for User Story 2

- [x] T015 [US2] Implement `get(entity_id: str, chronicle_dir: pathlib.Path) -> dict` in
      `engine/wyrd/verbs.py`: calls `load_effective_entities` (T002) then looks up `entity_id`
      directly (raising if absent, since `resolve_entity` already raises `state.StateError` for
      an unknown id) — returns the `{"verb": "get", ...}` shape from data-model.md.
- [x] T016 [US2] Implement `find(chronicle_dir: pathlib.Path, *, type: str, status: str | None =
      None, tag: str | None = None) -> dict` in `engine/wyrd/verbs.py`: calls
      `load_effective_entities` (T002) then `find_entities` (T004) — returns the `{"verb":
      "find", ...}` shape.
- [x] T017 [US2] Register `get` and `find` in `engine/wyrd/catalog.py`'s `TOOLS` (per
      contracts/cli-verbs.md's required/optional args).
- [x] T018 [US2] Add the `get`/`find` subparsers and `_run_get`/`_run_find` dispatch to
      `engine/wyrd/client.py`.

**Checkpoint**: User Stories 1 and 2 both fully functional and independently testable.

---

## Phase 5: User Story 3 - Reach for a named query instead of building a filter (Priority: P2)

**Goal**: `party`, `threads`, `threats` work per spec.md, each matching its documented
predicate.

**Independent Test**: Confirm each named verb's result against a fixture exercising its own
predicate (spec.md Acceptance Scenarios 1-3 for this story).

### Tests for User Story 3

- [x] T019 [P] [US3] Test `verbs.party` returns only `role: companion` + `status: with-party`
      entities, in `tests/engine/test_verbs.py`.
- [x] T020 [P] [US3] Test `verbs.threads` returns the full `status: open` set ordered by `heat`
      descending (including entries below the `heat >= 3` Always-loaded threshold), in
      `tests/engine/test_verbs.py`.
- [x] T021 [P] [US3] Test `verbs.threats` returns only entities with an active threat block
      (`imminence > 0`), in `tests/engine/test_verbs.py`.

### Implementation for User Story 3

- [x] T022 [US3] Implement `party(chronicle_dir: pathlib.Path) -> dict` in
      `engine/wyrd/verbs.py`: calls `load_effective_entities` (T002), `companions_with_party`
      (T006) — returns the `{"verb": "party", ...}` shape. (Implementation note: `party.roster`
      is a pure list pass-through and does not fit this verb's dict-keyed return shape, so it
      is not called here; the predicate itself, not `roster`, was the missing piece.)
- [x] T023 [US3] Implement `threads(chronicle_dir: pathlib.Path) -> dict` in
      `engine/wyrd/verbs.py`: calls `load_effective_entities` (T002) then `open_threads_by_heat`
      (T005) — returns the `{"verb": "threads", ...}` shape.
- [x] T024 [US3] Implement `threats(chronicle_dir: pathlib.Path) -> dict` in
      `engine/wyrd/verbs.py`: calls `load_effective_entities` (T002) then
      `threat.active_threats` — returns the `{"verb": "threats", ...}` shape.
- [x] T025 [US3] Register `party`, `threads`, `threats` in `engine/wyrd/catalog.py`'s `TOOLS`.
- [x] T026 [US3] Add their subparsers and `_run_party`/`_run_threads`/`_run_threats` dispatch to
      `engine/wyrd/client.py`.

**Checkpoint**: User Stories 1-3 fully functional and independently testable.

---

## Phase 6: User Story 4 - Read recent history without loading the whole log (Priority: P3)

**Goal**: `log --last N | --since <beat>` works per spec.md.

**Independent Test**: Call both forms against a fixture log with entries in known beat order
(spec.md Acceptance Scenarios 1-2 for this story).

### Tests for User Story 4

- [x] T027 [P] [US4] Test `log.read_log(..., last=N)` returns exactly the N most recent entries
      in beat order, in `tests/engine/test_log.py` (new file).
- [x] T028 [P] [US4] Test `log.read_log(..., since=<beat>)` returns only entries from that beat
      onward, inclusive, in `tests/engine/test_log.py`.
- [x] T029 [P] [US4] Test `log.append_beat` appends one well-formed JSON Lines record per call,
      and `read_log` sees it immediately after, in `tests/engine/test_log.py`.

### Implementation for User Story 4

- [x] T030 [US4] Implement `log(chronicle_dir: pathlib.Path, *, last: int | None = None, since:
      str | None = None) -> dict` in `engine/wyrd/verbs.py`: validates exactly one of
      `last`/`since` is given, calls `log.read_log` (T003) — returns the `{"verb": "log", ...}`
      shape from data-model.md.
- [x] T031 [US4] Register `log` in `engine/wyrd/catalog.py`'s `TOOLS` (mutually-exclusive
      `--last`/`--since`, per contracts/cli-verbs.md).
- [x] T032 [US4] Add the `log` subparser (enforcing the mutual-exclusion) and `_run_log`
      dispatch to `engine/wyrd/client.py`.

**Checkpoint**: User Stories 1-4 fully functional and independently testable.

---

## Phase 7: User Story 5 - Persist, validate, and recap chronicle state (Priority: P2)

**Goal**: `save`, `load`, `validate`, `recap` work per spec.md, each a thin wrapper over
existing `state.py`/`loadtier.py` functions.

**Independent Test**: Save then load a modified state and confirm equality; validate a
conformant and a non-conformant state; regenerate a recap and confirm it reflects current
state (spec.md Acceptance Scenarios 1-3 for this story).

### Tests for User Story 5

- [x] T033 [P] [US5] Test `verbs.save` then `verbs.load` round-trips an in-memory state
      unchanged, in `tests/engine/test_verbs.py`.
- [x] T034 [P] [US5] Test `verbs.validate` reports the specific violation for a
      schema-nonconformant state, and success with no findings for a conformant one, in
      `tests/engine/test_verbs.py`.
- [x] T035 [P] [US5] Test `verbs.recap` regenerates `recap.md` to reflect current entities and
      chronicle content, in `tests/engine/test_loadtier.py`.

### Implementation for User Story 5

- [x] T036 [US5] Implement `save(state: dict, chronicle_dir: pathlib.Path) -> dict`,
      `load(chronicle_dir: pathlib.Path) -> dict`, `validate(chronicle_dir: pathlib.Path) ->
      dict` in `engine/wyrd/verbs.py`, wrapping `state.save_chronicle`/`load_chronicle`/
      `validate_chronicle` respectively — return the shapes from data-model.md, with `validate`
      catching `state.StateError` and reporting it as `{"valid": False, "error": ...}` rather
      than raising.
- [x] T037 [US5] Implement `recap(chronicle_dir: pathlib.Path, *, where: str | None = None,
      changes: list[str] | None = None, body_mind: str | None = None) -> dict` in
      `engine/wyrd/verbs.py`: calls `load_effective_entities` (T002),
      `loadtier.generate_recap`, writes via `state.write_text_atomic` — returns the `{"verb":
      "recap", ...}` shape.
- [x] T038 [US5] Register `save`, `load`, `validate`, `recap` in `engine/wyrd/catalog.py`'s
      `TOOLS`.
- [x] T039 [US5] Add their subparsers and `_run_save`/`_run_load`/`_run_validate`/`_run_recap`
      dispatch to `engine/wyrd/client.py`.

**Checkpoint**: User Stories 1-5 fully functional and independently testable.

---

## Phase 8: User Story 6 - Advance the calendar and resolve threats (Priority: P3)

**Goal**: `advance-time <days>` and `threat-check` work per spec.md.

**Independent Test**: Advance time across a span guaranteeing threat activation and confirm
both the calendar and the threat activated; run `threat-check` against one threat and a fixed
seed and confirm a deterministic result (spec.md Acceptance Scenarios 1-2 for this story).

### Tests for User Story 6

- [x] T040 [P] [US6] Test `verbs.advance_time` advances the calendar by exactly the given days
      and activates a threat whose imminence guarantees activation over that span, in
      `tests/engine/test_advance_time.py`.
- [x] T041 [P] [US6] Test `verbs.threat_check` returns a definite activated/not-activated result
      derived from one seeded roll against a given imminence, in `tests/engine/test_threat.py`.

### Implementation for User Story 6

- [x] T042 [US6] Implement `advance_time(chronicle_dir: pathlib.Path, days: int, *, seed: int |
      None = None) -> dict` in `engine/wyrd/verbs.py`: loads the calendar and active threats
      (via `load_effective_entities` (T002) + `threat.active_threats`), calls
      `advance_time.advance_time`, persists the advanced calendar via `state.save_chronicle` —
      returns the `{"verb": "advance-time", ...}` shape.
- [x] T043 [US6] Implement `threat_check(chronicle_dir: pathlib.Path, threat_id: str, *, seed:
      int | None = None) -> dict` in `engine/wyrd/verbs.py`: resolves the named threat via
      `load_effective_entities` (T002), draws one roll via the existing seeded dice tool, calls
      `threat.check_activation` — returns the `{"verb": "threat-check", ...}` shape; raises for
      an unknown threat id.
- [x] T044 [US6] Register `advance-time` and `threat-check` in `engine/wyrd/catalog.py`'s
      `TOOLS`.
- [x] T045 [US6] Add their subparsers and `_run_advance_time`/`_run_threat_check` dispatch to
      `engine/wyrd/client.py`.

**Checkpoint**: All six user stories fully functional and independently testable.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [x] T046 Run `python3 -m ruff check .` and `python3 -m ruff format --check .` repo-wide and
      fix any findings introduced by this feature.
- [x] T047 Run `PYTHONPATH=engine python3 -m unittest discover -s tests/engine` and confirm
      every new and existing test passes.
- [x] T048 Walk through quickstart.md's "Exercise each verb by hand" section against a real
      fixture chronicle and confirm every command's output matches data-model.md's documented
      shape.
- [x] T049 Update docs/design/02-architecture.md's verb-list section, if implementation
      surfaced any wording drift from what was actually built (e.g. an argument name), per
      CLAUDE.md's "update the design document when the change lands" rule — otherwise confirm
      no drift and make no edit.

---

## Dependencies & Execution Order

- **Setup (Phase 1)**: T001 — no dependencies.
- **Foundational (Phase 2)**: T002-T006 — depend on T001; block every user-story phase except
  none directly (US5 and US6 don't call `load_effective_entities` for `save`/`load`/`validate`,
  but `recap` and `advance-time`/`threat-check` do, so treat Phase 2 as blocking overall).
- **User Story 1 (Phase 3)**: depends on T002. Independent of US2-US6.
- **User Story 2 (Phase 4)**: depends on T002, T004. Independent of US1, US3-US6.
- **User Story 3 (Phase 5)**: depends on T002, T005, T006. Independent of US1, US2, US4-US6.
- **User Story 4 (Phase 6)**: depends on T003. Independent of US1-US3, US5-US6.
- **User Story 5 (Phase 7)**: `save`/`load`/`validate` have no dependency on Phase 2; `recap`
  depends on T002. Independent of US1-US4, US6.
- **User Story 6 (Phase 8)**: depends on T002. Independent of US1-US5.
- **Polish (Phase 9)**: depends on all prior phases.

Every user-story phase after Phase 2 can proceed in parallel with the others, since none reads
or writes another's `verbs.py` functions or `catalog.py`/`client.py` entries (each adds its own
distinct verb).

## Parallel Execution Examples

- Phase 2: T003, T004, T005, T006 can all run in parallel (distinct functions, T002 is the only
  serial prerequisite for later phases but not for T003-T006 themselves).
- Within any user-story phase, its `[P]`-marked test tasks can run in parallel with each other
  (distinct test methods in the same or different files), before that phase's implementation
  tasks begin.
- Phases 3-8 (US1-US6) can be implemented by different contributors in parallel once Phase 2 is
  merged, since each phase's `catalog.py`/`client.py` additions are independent registry entries
  (a merge-order convention, not a code dependency, avoids simultaneous edits to the same file).

## Implementation Strategy

**MVP first**: Phase 3 (User Story 1, `session-context`) alone delivers the single most-used
verb — the whole Always-loaded tier in one call — and is independently testable and shippable.

**Incremental delivery**: land Phases 1-2, then each user-story phase in priority order (US1,
US2 as the two P1s; US3 and US5 as P2; US4 and US6 as P3), running Phase 9's polish pass once
after the last phase lands rather than after each one, since ruff/test-suite checks are
inexpensive to re-run but only need to be clean once, at the end.
