# Tasks: Character, downtime and session-close skills

**Input**: Design documents from `/specs/154-session-close-skills/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-verbs.md,
contracts/skills.md, quickstart.md

**Tests**: Explicitly requested for part 1 (spec.md FR-009/SC-004; matches every other
`catalog.py` verb addition in this repo, e.g. #402/PR #407) — included for the two new verbs.
Part 2 has no test harness available (research.md) — its tasks are documentation/prose tasks
verified by the quickstart.md manual walkthrough instead.

**Organization**: Tasks are grouped by user story (spec.md priorities P1/P2/P3). Part 1 (this
repo, `wyrd`) supplies the two new CLI verbs User Story 2 depends on; User Stories 1 and 3 need
no new engine code. Part 2 (`wyrd-chronicle-template`, a separate PR/repo) builds the three
`SKILL.md` files themselves and is listed here for completeness of the design record, per
plan.md's repo split.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3)

## Path Conventions

Part 1: `engine/wyrd/`, `tests/engine/` at this repo's root (plan.md's Project Structure).
Part 2: `.claude/skills/<name>/SKILL.md` at `wyrd-chronicle-template`'s root.

---

## Phase 1: Setup (this repo)

- [ ] T001 Confirm no `downtime`/`rally` catalog entry already exists in
      `engine/wyrd/catalog.py` (research.md's premise) before adding one.

---

## Phase 2: Foundational — none

No shared prerequisite exists across US1/US2/US3: US1 and US3 need no new code (they reuse
`spend-advance`/`character-load`/`save`/`recap` unchanged); US2 is the only story needing new
verbs, and its two verbs (`downtime`, `rally`) do not depend on each other.

---

## Phase 3: User Story 1 - Inspect or advance the player character (Priority: P1)

**Goal**: The character skill can be built entirely on existing verbs.

**Independent Test**: `wyrd character-load`/`wyrd spend-advance` already exist and are already
covered by their own tests (#402/PR #407 and earlier advancement work) — no new engine test is
needed for this story.

- [ ] T002 [US1] (part 2, `wyrd-chronicle-template`) Write
      `.claude/skills/wyrd-character/SKILL.md` per contracts/skills.md's `/wyrd-character`
      contract: view the sheet via `character-load`/`session-context`; gather the player's spend
      choice and call `spend-advance`; report its result verbatim, success or refusal.

**Checkpoint**: `/wyrd-character` is independently usable once part 2 lands, with no dependency
on US2/US3.

---

## Phase 4: User Story 2 - Run a downtime phase (Priority: P2)

**Goal**: Wire `downtime` and `rally` CLI verbs, then build the downtime skill on top of them.

**Independent Test**: `wyrd downtime --action upkeep|mend|rest` and `wyrd rally` each return
exactly what `apply_upkeep`/`apply_mend`/`apply_rest`/`apply_rally` compute, verified by unit
tests before any skill prose is written.

### Tests (write first, confirm they fail against the unmodified catalog)

- [ ] T003 [P] [US2] Add `TestDowntimeVerb` to `tests/engine/test_verbs.py`: covers
      `--action upkeep` (home no-op, away/standing, away/coin, away/insufficient-coin refusal),
      `--action mend` (success one-step, success-closes-at-ladder-end, unknown_wound, recurring,
      already_closed), `--action rest` (returns `stamina_max` unconditionally).
- [ ] T004 [P] [US2] Add `TestRallyVerb` to `tests/engine/test_verbs.py`: covers recovery
      without a trigger, recovery with an accepted trigger (award present), recovery with a
      refused trigger, and the pending-discard behaviour `apply_rally` already implements —
      confirming the wrapper passes `commit=None` and never calls a commit callback.

### Implementation

- [ ] T005 [US2] Add the `downtime` entry to `engine/wyrd/catalog.py`'s `TOOLS` dict per
      contracts/cli-verbs.md (inputSchema covering `action`, `destination`, `standing`, `coin`,
      `trade`, `wound-id`, `wounds-json`, `stamina-max`).
- [ ] T006 [US2] Add the `rally` entry to `engine/wyrd/catalog.py`'s `TOOLS` dict per
      contracts/cli-verbs.md (inputSchema covering `strain`, `stamina`, `stamina-max`,
      `advancement-record-json`, `trigger`, `pending-json`).
- [ ] T007 [US2] Add `downtime(...)` to `engine/wyrd/verbs.py`: dispatches on `action` to
      `downtime_module.apply_upkeep`/`apply_mend`/`apply_rest`, merging `{"verb": "downtime",
      "action": action}` into whichever result it returns, raising `ValueError` for an unknown
      `action` or a missing required parameter for the chosen one.
- [ ] T008 [US2] Add `rally(...)` to `engine/wyrd/verbs.py`: calls `rally_module.apply_rally`
      with `commit=None`, merging `{"verb": "rally"}` into its result.
- [ ] T009 [US2] Add the `downtime` subparser and `_run_downtime` dispatcher to
      `engine/wyrd/client.py`, following the `spend-advance`/`recap` pattern (flags per
      contracts/cli-verbs.md; JSON-decode errors on `--wounds-json` caught and reported as
      `{"error": {"verb": "downtime", "reason": ...}}`).
- [ ] T010 [US2] Add the `rally` subparser and `_run_rally` dispatcher to
      `engine/wyrd/client.py`, matching T009's error-handling convention for
      `--advancement-record-json`/`--pending-json`.
- [ ] T011 [US2] Run `PYTHONPATH=engine python3 -m unittest tests.engine.test_verbs -v`,
      confirm T003/T004's new tests pass, then `python3 -m ruff check .` and
      `python3 -m ruff format --check .` clean repo-wide.

### Part 2 (separate PR, `wyrd-chronicle-template`)

- [ ] T012 [US2] Write `.claude/skills/wyrd-downtime/SKILL.md` per contracts/skills.md's
      `/wyrd-downtime` contract: walk Destination, Upkeep (calling `downtime --action upkeep`
      only away from home), the Undertaking choice (all six named, only Mend calling `downtime
      --action mend`), and Rest (always calling `downtime --action rest`); persist via
      `character-save`.

**Checkpoint**: `/wyrd-downtime` is independently testable once T005-T011 (this repo) and T012
(the sibling repo) both land — T012 cannot be verified end-to-end until T005-T011 are released
into a chronicle's vendored `engine/` copy, which this feature's Assumptions section already
notes as a cross-repo dependency.

---

## Phase 5: User Story 3 - Close a session (Priority: P3)

**Goal**: The end-session skill can be built entirely on existing verbs.

**Independent Test**: `wyrd save`/`wyrd recap` already exist and are already covered by their
own tests (#402/PR #407) — no new engine test is needed for this story.

- [ ] T013 [US3] (part 2, `wyrd-chronicle-template`) Write
      `.claude/skills/wyrd-end-session/SKILL.md` per contracts/skills.md's `/wyrd-end-session`
      contract: call `save`, then `recap`, write the returned text to `recap.md` (already done
      by the `recap` verb itself), then run `git add`/`git commit` covering the changed
      chronicle files; write a `pending:` marker per docs/design/16-session.md when the session
      stops mid-beat, never asking the player to decide.

**Checkpoint**: `/wyrd-end-session` is independently usable once part 2 lands, with no
dependency on US1/US2.

---

## Phase 6: Polish & Cross-Cutting

- [ ] T014 [P] Update docs/design/02-architecture.md's skills list bullets (already present) —
      confirm no wording change is needed now that `/wyrd-character`, `/wyrd-downtime` and
      `/wyrd-end-session` exist; this design document already described the target state, so no
      edit is expected. Verify via `python3 tools/check_docs.py`.
- [ ] T015 Run the full quickstart.md validation for part 1 (verb outputs matching the pure
      functions' own results) before opening the `wyrd` PR.

---

## Dependencies & Execution Order

- **US1** (T002): no dependency on US2/US3; part 2 only.
- **US2** (T003-T012): T003/T004 (tests) before T005-T010 (implementation) before T011
  (verification) before T012 (the sibling-repo skill, which depends on T005-T011 having
  released engine verbs a chronicle can vendor).
- **US3** (T013): no dependency on US1/US2; part 2 only.
- **Polish** (T014-T015): after all of the above.

## Parallel Example

```
T003 [P] [US2] and T004 [P] [US2] can be written together (different test classes, same file —
run sequentially within the file, but drafted in parallel).
T005 [US2] and T006 [US2] touch the same catalog.py dict but different entries — draft together,
land as one commit.
```

## Implementation Strategy

**MVP**: User Story 1 (`/wyrd-character`) — smallest, zero engine dependency, delivers standalone
value (viewing and advancing a character) without waiting on the verb-wiring work.

**Incremental delivery**: US1 → US3 (also zero engine dependency) → US2 (needs T005-T011 first).
This repo's own PR (T001-T011, T014-T015) can land independently of any `wyrd-chronicle-template`
PR; the sibling repo's skills PR (T002, T012, T013) depends on this repo's PR having merged for
US2's `/wyrd-downtime` skill specifically (US1/US3's skills need only already-merged #402 verbs).
