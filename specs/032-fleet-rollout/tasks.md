---

description: "Task list for fleet rollout (issue #31)"
---

# Tasks: Fleet rollout of engine and template changes

**Input**: Design documents from `/specs/032-fleet-rollout/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md, quickstart.md

**Tests**: Included — `tools/` already tests every script this way (`test_backlog.py`,
`test_check_docs.py`), per `design/07-tooling.md` §6.

**Organization**: Tasks are grouped by user story (spec.md) to enable independent
implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single project extending the existing `tools/` catalog (plan.md's Structure Decision):
`tools/fleet_rollout.py`, `tools/test_fleet_rollout.py`, `tools/fixtures/fleet.json`.

---

## Phase 1: Setup

**Purpose**: Scaffold the script and its fixture, matching `tools/backlog.py`'s shape

- [X] T001 Create `tools/fleet_rollout.py` with the module docstring (purpose, usage, `gh`
  requirement, "Python 3.11+, stdlib only" per `design/07-tooling.md`) and an argparse
  skeleton with `status` and `rollout` subcommands that both currently print "not implemented"
  and exit 1
- [X] T002 [P] Create `tools/fixtures/fleet.json` capturing: a small `gh repo list`-shaped
  array of repo objects (name, visibility, isArchived) for a handful of synthetic
  `wyrd-setting-*` repos plus `wyrd-setting-template`; a set of sample `.wyrd-version` file
  contents keyed by repo name; and a sample ordered manifest (`rollout/changes/*.yaml` shape)
  for `wyrd-setting-template`, per `data-model.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared reading/parsing logic every verb and every user story needs

**⚠️ CRITICAL**: No user story task can start until this phase is complete

- [X] T003 Implement a minimal YAML reader in `tools/fleet_rollout.py` for the flat
  key/value + list shapes used by `.wyrd-version` and manifest entries (no third-party YAML
  dependency, per `design/07-tooling.md` §2 — reuse or adapt the existing internal reader
  pattern if one already exists under `tools/` or `engine/`; otherwise write the small
  restricted-subset parser directly)
- [X] T004 Implement `list_fleet_repos()` in `tools/fleet_rollout.py`: wraps
  `gh repo list neilgfoster --json name,visibility,isArchived --limit 200` via `subprocess`
  (mirroring `tools/backlog.py`'s `gh()` helper) and filters to names matching
  `^wyrd-setting-.*$`, `wyrd-setting-template`, or `wyrd-chronicle-template`
- [X] T005 Implement `read_version_marker(repo)` in `tools/fleet_rollout.py`: reads
  `.wyrd-version` from a repo via `gh api repos/{owner}/{repo}/contents/.wyrd-version`,
  parses it with T003's reader into the fields from `data-model.md` (`template_source`,
  `template_sha`, `engine_sha`, `diverged_at`), and returns a sentinel for "file absent"
  distinct from a parse error
- [X] T006 Implement `read_manifest(source_repo)` in `tools/fleet_rollout.py`: lists and reads
  every `rollout/changes/*.yaml` entry from `source_repo` (`wyrd-setting-template` or
  `wyrd-chronicle-template`) via `gh api`, parses each with T003's reader, validates exactly
  one of `add`/`migrate` is present matching `class` and that no `add` path falls under
  `library/`, `corpus/`, or `index/` (research.md's defense-in-depth rule; a violating entry
  is a load error), and returns entries ordered by their `NNN` sequence prefix
- [X] T007 [P] Add `tools/test_fleet_rollout.py` scaffold: stdlib `unittest`, loads
  `tools/fixtures/fleet.json` the way `tools/test_backlog.py` loads `board.json`, injects it so
  no test makes a live `gh` call
- [X] T008 [P] [Foundational] Unit tests in `tools/test_fleet_rollout.py` for T003's YAML
  reader, T005's marker parser (present / absent / malformed), and T006's manifest reader
  (valid entries; an entry naming a forbidden path is rejected; entries come back ordered)

**Checkpoint**: repo discovery, version-marker reading, and manifest reading are all tested
against the fixture — user story work can begin

---

## Phase 3: User Story 1 - See which repos are behind (Priority: P1) 🎯 MVP

**Goal**: `status` reports every fleet repo's current/behind/unversioned/unreachable state
against the manifest, read-only.

**Independent Test**: run `python3 tools/fleet_rollout.py status` against the fixture-backed
test double with no rollout tooling in the repos yet; it reports each repo's recorded state
correctly using only read access (per `contracts/cli.md`).

### Tests for User Story 1

- [X] T009 [P] [US1] Test in `tools/test_fleet_rollout.py`: a repo whose `.wyrd-version`
  matches the manifest's latest entry SHA reports `current` (spec Acceptance Scenario 1)
- [X] T010 [P] [US1] Test in `tools/test_fleet_rollout.py`: a repo recorded at an older SHA
  reports `behind`, naming the missing entry ids in manifest order (Acceptance Scenario 2)
- [X] T011 [P] [US1] Test in `tools/test_fleet_rollout.py`: a repo with no `.wyrd-version` at
  all reports `unversioned` rather than being skipped or raising (Acceptance Scenario 3)
- [X] T012 [P] [US1] Test in `tools/test_fleet_rollout.py`: a repo whose recorded
  `template_sha` does not exist in the source repo's history reports an unresolvable/unknown
  state rather than guessing a distance (Edge Case)
- [X] T013 [P] [US1] Test in `tools/test_fleet_rollout.py`: a repo that cannot be read
  (renamed/archived/deleted in the fixture) reports `unreachable` rather than being silently
  dropped from the output (Edge Case, FR-009)

### Implementation for User Story 1

- [X] T014 [US1] Implement `compute_repo_state(repo, marker, manifest)` in
  `tools/fleet_rollout.py`: given T005's marker and T006's manifest, returns the Fleet repo
  record shape from `data-model.md` with `state` in
  `{current, behind, unversioned, diverged, unreachable}` (depends on T005, T006)
- [X] T015 [US1] Wire the `status` subcommand in `tools/fleet_rollout.py`: for each repo from
  T004, call T014 and collect records; support `--repo <name>` to restrict to one repo per
  `contracts/cli.md` (depends on T014)
- [X] T016 [US1] Implement `--format json` (raw list of records) and the default text table
  (repo, visibility, state, missing entry ids) for `status`, per `contracts/cli.md`
- [X] T017 [US1] Exit-code handling for `status`: 0 for any completed read (including
  `behind`/`unreachable` repos — those are normal results, not failures); non-zero only for a
  tool-level failure such as `gh` not authenticated (FR-010, `contracts/cli.md`)

**Checkpoint**: `status` is fully functional and independently testable — SC-001 and SC-005 are
achievable end to end (modulo live `gh` access, exercised via `quickstart.md`)

---

## Phase 4: User Story 2 - Propose a change to every affected repo (Priority: P2)

**Goal**: `rollout` opens one bundled PR per behind repo, using additive copy or structural
migration per manifest entry, never pushing directly and never touching setting-authored
content.

**Independent Test**: with US1's status logic in place, run `rollout` after an additive
manifest entry is added; it opens one PR per repo missing that entry and none against a repo
that already has it (per `contracts/cli.md`).

### Tests for User Story 2

- [X] T018 [P] [US2] Test in `tools/test_fleet_rollout.py`: an additive-only bundle produces a
  PR-content plan naming every path from each entry's `add:` list, sourced from that entry's
  `sha` (Acceptance Scenario 1)
- [X] T019 [P] [US2] Test in `tools/test_fleet_rollout.py`: a bundle containing a structural
  entry produces a PR-content plan that runs that entry's `migrate` step rather than a raw
  file copy, and the plan's manifest-order is preserved when both classes are bundled
  (Acceptance Scenario 2)
- [X] T020 [P] [US2] Test in `tools/test_fleet_rollout.py`: a repo already at the manifest's
  latest entry produces no PR-content plan at all (Acceptance Scenario 3)
- [X] T021 [P] [US2] Test in `tools/test_fleet_rollout.py`: a repo with an existing open PR
  targeting the same latest entry id is skipped rather than duplicated, and is reported as
  such (Acceptance Scenario 5, FR-007)
- [X] T022 [P] [US2] Test in `tools/test_fleet_rollout.py`: building a PR-content plan never
  invokes any read of a path under `library/`, `corpus/`, or `index/` for any entry in the
  fixture manifest (FR-006)

### Implementation for User Story 2

- [X] T023 [US2] Implement `plan_rollout(repo, marker, manifest)` in `tools/fleet_rollout.py`:
  given a `behind` record from T014, returns the ordered list of manifest entries to bundle
  and, per entry, its class-specific action (additive: source paths + `sha` to copy from;
  structural: the `migrate` reference) — pure function, no `gh` writes (depends on T014)
- [X] T024 [US2] Implement `find_existing_rollout_pr(repo, latest_entry_id)` in
  `tools/fleet_rollout.py`: checks via `gh pr list` whether an open PR already targets this
  repo for this latest entry id, to satisfy FR-007's no-duplicate rule
- [X] T025 [US2] Implement `apply_rollout(repo, plan)` in `tools/fleet_rollout.py`: creates a
  branch named `wyrd-fleet-rollout/<latest-entry-id>`, applies each planned action (additive:
  copy paths from the entry's `sha`; structural: apply the `migrate` step) as commits, and
  opens a PR via `gh pr create` against the target repo — never `git push` to its default
  branch (depends on T023)
- [X] T026 [US2] Wire the `rollout` subcommand in `tools/fleet_rollout.py`: iterate `behind`
  repos from `status`'s logic, skip via T024, otherwise call T025; support `--repo <name>` and
  `--dry-run` (compute and print the plan from T023 without calling T025) per `contracts/cli.md`
- [X] T027 [US2] Per-repo result reporting for `rollout`: PR URL opened, "skipped: already
  open", or "skipped: previously closed without merging" (Edge Case: a rejected rollout PR
  must not be silently reopened identically)

**Checkpoint**: `rollout` is fully functional and independently testable — SC-002 and SC-003
are achievable end to end

---

## Phase 5: User Story 3 - Recognize a deliberate divergence (Priority: P3)

**Goal**: a repo carrying `diverged_at` in its `.wyrd-version` is reported and treated
distinctly from ordinary drift, without exempting it from later changes.

**Independent Test**: mark one fixture repo's `.wyrd-version` with `diverged_at` set to a
specific manifest entry id, then run `status` and `rollout`; that repo is reported as
`diverged (accepted)` and receives no PR for that entry, but still receives one for a later
entry (per `contracts/cli.md`).

### Tests for User Story 3

- [X] T028 [P] [US3] Test in `tools/test_fleet_rollout.py`: a repo with `diverged_at` set to
  its latest outstanding entry id reports `diverged` (not `behind`) from `compute_repo_state`
  (Acceptance Scenario 1)
- [X] T029 [P] [US3] Test in `tools/test_fleet_rollout.py`: `plan_rollout` produces no
  PR-content plan for a repo whose only outstanding entry matches its `diverged_at`
  (Acceptance Scenario 2)
- [X] T030 [P] [US3] Test in `tools/test_fleet_rollout.py`: a repo diverged at entry N still
  reports `behind` (not `diverged`) once a later, unrelated entry N+1 is added to the
  manifest, and `plan_rollout` bundles N+1 for it (Acceptance Scenario 3 — divergence does not
  exempt everything after it)

### Implementation for User Story 3

- [X] T031 [US3] Extend `compute_repo_state` (T014) in `tools/fleet_rollout.py` to check
  `marker.diverged_at` against the outstanding entries: if every outstanding entry is at or
  before `diverged_at`, state is `diverged`; if any outstanding entry is after it, state is
  `behind` and the diverged entry itself is excluded from `missing` but later entries are
  included (depends on T014)
- [X] T032 [US3] Extend `plan_rollout` (T023) in `tools/fleet_rollout.py` to exclude any entry
  at or before the repo's `diverged_at` from the bundle, while still including later entries
  (depends on T023, T031)
- [X] T033 [US3] Render `diverged (accepted)` distinctly from `behind` in both `status`'s text
  table and its `--format json` output (T016)

**Checkpoint**: all three user stories are independently functional; FR-008 is fully satisfied

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T034 [P] Run `python3 tools/check_docs.py` and confirm this feature added no design
  document requiring a hub link (this feature only adds `specs/` and `tools/` content, per
  `CLAUDE.md`'s doc-graph rule)
- [X] T035 Run `python3 -m unittest discover -s tools -p 'test_*.py'` and confirm the full
  `tools/` suite (including the new `test_fleet_rollout.py`) passes together
- [X] T036 Walk `quickstart.md` end to end against a disposable test repo (or note in the PR
  description that this step requires live `gh` access the automated loop does not have, and
  what a human reviewer should run to confirm it)
- [X] T037 [P] Add a short module-level note to `tools/fleet_rollout.py`'s docstring pointing
  at `specs/032-fleet-rollout/data-model.md` for the `.wyrd-version` and manifest-entry schema,
  so a future reader does not have to reconstruct it from code

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: no dependencies
- **Foundational (Phase 2)**: depends on Setup — BLOCKS all user stories
- **User Story 1 (Phase 3)**: depends on Foundational only
- **User Story 2 (Phase 4)**: depends on Foundational and on US1's `compute_repo_state`
  (T014) to identify `behind` repos — not independently implementable before US1, but
  independently *testable* once both exist, per `contracts/cli.md`'s separation of `status`
  and `rollout`
- **User Story 3 (Phase 5)**: depends on Foundational and extends US1's `compute_repo_state`
  (T014→T031) and US2's `plan_rollout` (T023→T032) — implemented last because it modifies
  functions the first two stories introduce, but each of its acceptance scenarios is testable
  independently of US2's PR-opening mechanics (T024–T027)
- **Polish (Phase 6)**: depends on all three stories

### Parallel Opportunities

- T002 (fixture) can run alongside T001 (skeleton)
- All tests within a story's "Tests for User Story N" block are `[P]` — different test
  functions in the same file, but independent of each other's outcome
- T034 and T037 in Polish are `[P]`

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Phase 1 → Phase 2 → Phase 3 (US1)
2. **STOP and VALIDATE**: `status` reports correctly against the fixture and, per
   `quickstart.md`, against the live fleet
3. This alone satisfies SC-001 and SC-005 and is a complete, demonstrable increment even
   before any rollout mechanism exists

### Incremental Delivery

1. Foundational → US1 (`status`) → demo
2. US2 (`rollout`) → demo — SC-002, SC-003
3. US3 (divergence) → demo — SC-004
4. Polish

### Note on this PR's scope

Given the loop this issue is driven through targets one open PR per pass, all three user
stories are included here as one coherent delivery — `status` alone would leave FR-004
through FR-008 unimplemented from an issue whose Definition of Done explicitly names both the
status read and the rollout mechanism. Reviewer feedback may still split this into staged PRs
if the diff proves too large to review at once.
