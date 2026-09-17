---

description: "Task list for Chronicle friction harvest"
---

# Tasks: Chronicle friction harvest

**Input**: Design documents from `/specs/172-chronicle-friction-harvest/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Included — plan.md's Technical Context names `python3 -m unittest discover -s tools -p
'test_harvest_friction.py'` (stdlib unittest, per `docs/design/27-tooling.md` §6 — no pytest) as
this feature's testing approach, and this repo's `tools/` convention pairs every
`check_*.py`/`backlog.py` script with its own `test_*.py`.

**Organization**: Tasks are grouped by user story (spec.md) to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single script inside the existing `tools/` tree (plan.md's Project Structure):
`tools/harvest_friction.py`, `tools/test_harvest_friction.py`, `tools/fixtures/friction/`.

---

## Phase 1: Setup

**Purpose**: Lay down the module skeleton and fixtures every story's tests read.

- [X] T001 Create `tools/fixtures/friction/` with three fixture `log/friction.md`-shaped files:
      `qualifying.md` (one entry matching `docs/design/16-session.md`'s qualifying worked
      example — a difficulty-table result), `color_only.md` (one entry matching its
      non-qualifying coat-catching-on-a-nail example), and `malformed.md` (one entry missing its
      `what the GM did` field).
- [X] T002 Create `tools/harvest_friction.py` with module docstring, imports (`argparse`,
      `dataclasses`, `subprocess`, `pathlib`, `re`), and empty `if __name__ == "__main__":` CLI
      entry point stub.
- [X] T003 [P] Create `tools/test_harvest_friction.py` with the unittest.TestCase-based test module with a fixture
      helper that loads a file from `tools/fixtures/friction/` by name.

**Checkpoint**: `python3 -m unittest discover -s tools -p 'test_harvest_friction.py'` runs (no tests yet, or only
trivial ones) without import errors.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The parsing/data-model layer every user story's behavior sits on top of. No user
story can be implemented before this phase completes.

- [X] T004 In `tools/harvest_friction.py`, define the `FrictionEntry` and `MalformedEntry`
      dataclasses per `data-model.md` (fields: `mechanic`, `what_happened`, `what_gm_did`,
      `source_repo`, `raw_index` for `FrictionEntry`; `source_repo`, `raw_index`,
      `missing_fields`, `raw_text` for `MalformedEntry`).
- [X] T005 In `tools/harvest_friction.py`, implement `parse_friction_log(text: str, source_repo:
      str) -> tuple[list[FrictionEntry], list[MalformedEntry]]` that parses the
      `docs/design/16-session.md` bullet format (`- mechanic: ... what happened: ... what the GM
      did: ...`), producing a `MalformedEntry` (never a `FrictionEntry` with a blank field) when
      any of the three fields is missing.
- [X] T006 [P] In `tools/test_harvest_friction.py`, write `test_parse_friction_log_qualifying`
      and `test_parse_friction_log_malformed` against the T001 fixtures, asserting
      `parse_friction_log` returns the right dataclass with the right fields for each.
- [X] T007 In `tools/harvest_friction.py`, implement `read_chronicle_friction_log(chronicle: str)
      -> str | None` that reads `log/friction.md` from a local path (if `chronicle` resolves to
      an existing directory) or via `gh api repos/<chronicle>/contents/log/friction.md`
      (base64-decoded) otherwise per research.md's decision; returns `None` (not an error) when
      the file does not exist (FR-006).
- [X] T008 [P] In `tools/test_harvest_friction.py`, write
      `test_read_chronicle_friction_log_missing_file_returns_none` using a temp directory with no
      `log/friction.md`, and a test for the local-path branch reading a real fixture file copied
      into a temp chronicle directory's `log/` subdirectory. The `gh api` branch is exercised via
      dependency injection (a passed-in reader callable), not a real network call.

**Checkpoint**: Parsing and reading are fully tested in isolation before any triage/proposal logic
is written.

---

## Phase 3: User Story 1 - Harvest one chronicle's friction log into proposed issues (P1) 🎯 MVP

**Goal**: Given one chronicle's friction log, produce a reviewable proposal list — qualifying
entries become proposals, color-only entries do not, and nothing is filed automatically.

**Independent Test**: `python3 tools/harvest_friction.py --chronicle
tools/fixtures/friction/qualifying.md`-shaped input yields one proposal; the color-only fixture
yields none; a chronicle with no `log/friction.md` reports nothing without erroring.

- [X] T009 [US1] In `tools/harvest_friction.py`, implement `triage(entry: FrictionEntry) ->
      TriageVerdict` per `data-model.md` / research.md's triage decision: return `"qualifies"`
      when `what_happened`/`what_gm_did` names a mechanic-shaped surprise/wrong-feeling
      result/improvisation gap (the three `docs/design/16-session.md` conditions), `"does_not_
      qualify"` when the text touches no rule/table/mechanic at all, `"needs_review"` otherwise —
      each with a short `reason` string.
- [X] T010 [P] [US1] In `tools/test_harvest_friction.py`, write `test_triage_qualifying_example`
      and `test_triage_color_only_example` using `docs/design/16-session.md`'s own two worked
      examples verbatim (SC-002), asserting the expected verdicts.
- [X] T011 [US1] In `tools/harvest_friction.py`, implement `build_proposal(entries:
      list[FrictionEntry]) -> HarvestProposal` per `data-model.md`: title built only from
      `mechanic`, body built only from `what_happened`/`what_gm_did`/`mechanic`/`source_repo` —
      never any other text (FR-005).
- [X] T012 [P] [US1] In `tools/test_harvest_friction.py`, write
      `test_build_proposal_excludes_narrative_leakage` asserting the built proposal's title and
      body contain no substring absent from the source entry's three fields.
- [X] T013 [US1] In `tools/harvest_friction.py`, implement `harvest_chronicle(chronicle: str) ->
      HarvestReport` (a small dataclass or dict bundling: new-candidate proposals before dedup,
      malformed entries, does-not-qualify entries, needs-review entries) wiring T005/T007/T009/
      T011 together for one chronicle, handling the "no `log/friction.md`" case from T007 as "no
      entries, no error" (FR-006).
- [X] T014 [P] [US1] In `tools/test_harvest_friction.py`, write
      `test_harvest_chronicle_end_to_end` against the qualifying/color_only/malformed fixtures
      combined into one temp `log/friction.md`, asserting the report buckets each entry
      correctly.
- [X] T015 [US1] In `tools/harvest_friction.py`, implement the CLI entry point (`argparse` with
      repeatable `--chronicle`) that runs `harvest_chronicle` for each and prints a
      human-readable report per quickstart.md Step 2 (new proposals / malformed / non-qualifying
      / needs-review, per chronicle) without filing anything.

**Checkpoint**: User Story 1 is independently functional — running the script against one
chronicle checkout produces a correct, non-filing report.

---

## Phase 4: User Story 2 - Harvest across multiple chronicle repos in one pass (P2)

**Goal**: One invocation sweeps several chronicles, attributing each proposal to its source repo
without merging findings across chronicles.

**Independent Test**: Point the CLI at two chronicle inputs (one with a qualifying entry, one
without); confirm the output attributes the proposal to the correct chronicle and reports the
other as empty.

- [X] T016 [US2] Confirm (and adjust if needed) that `harvest_chronicle`'s `source_repo` tagging
      from T005/T013 already threads through to the printed report per-chronicle — this story is
      primarily a CLI-loop and reporting-format concern once T015's `--chronicle` is already
      repeatable (Phase 3 already made `--chronicle` an `append` argument); add explicit
      per-chronicle section headers to the CLI output in `tools/harvest_friction.py` if not
      already present.
- [X] T017 [P] [US2] In `tools/test_harvest_friction.py`, write
      `test_multi_chronicle_attribution` running the harvest across two in-memory/temp
      chronicles and asserting proposals are correctly attributed and not merged across
      `source_repo` values even when `mechanic` text matches.

**Checkpoint**: Multi-chronicle sweeps produce correctly attributed, unmerged output.

---

## Phase 5: User Story 3 - Avoid re-proposing an already-known gap (P2)

**Goal**: A candidate already represented by an existing `wyrd` issue is reported as a likely
duplicate instead of a fresh proposal.

**Independent Test**: Run the harvest twice against equivalent friction entries with a real
`wyrd` issue filed for the first between runs; confirm the second run reports a match instead of
a duplicate proposal.

- [X] T018 [US3] In `tools/harvest_friction.py`, implement `check_duplicate(proposal:
      HarvestProposal, repo: str = "neilgfoster/wyrd", runner=subprocess.run) -> DedupVerdict` that
      shells out to kord's `client.py github-issue-dedup-check --repo <repo> --text "<title>\n\n
      <body>"` (path resolved the same way `tools/backlog.py` locates/invokes `gh`, i.e. an
      injectable `runner` so tests never shell out for real) and parses its JSON result into a
      `DedupVerdict`.
- [X] T019 [P] [US3] In `tools/test_harvest_friction.py`, write
      `test_check_duplicate_match` and `test_check_duplicate_no_match`, injecting a fake
      `runner` that returns canned JSON (a match, and a null match) instead of calling the real
      `client.py`.
- [X] T020 [US3] In `tools/harvest_friction.py`, wire `check_duplicate` into
      `harvest_chronicle`'s pipeline (per `data-model.md`'s relationships diagram) so the CLI
      report (T015) separates "new proposals" from "likely duplicates" — a duplicate's report
      line names the matched issue.
- [X] T021 [P] [US3] In `tools/test_harvest_friction.py`, write
      `test_harvest_chronicle_separates_new_from_duplicate` asserting the end-to-end report
      buckets a matched proposal under duplicates and an unmatched one under new candidates.

**Checkpoint**: Re-running the harvest after a genuine gap has already been filed does not
propose it again — User Story 3 fully satisfied, all three user stories now independently
verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Repo-wide hygiene and the edge cases spec.md calls out that span more than one
story.

- [X] T022 [P] In `tools/harvest_friction.py`, implement the same-log-repeat merge rule (spec.md
      Edge Cases: "the same finding appears twice within one friction log") inside
      `build_proposal`'s caller — group `qualifies` entries by normalized `mechanic` text before
      calling `build_proposal`, producing one `HarvestProposal` with multiple `source_entries`
      rather than duplicate proposals from a single run.
- [X] T023 [P] In `tools/test_harvest_friction.py`, write `test_same_log_repeat_merges_to_one_
      proposal` asserting two same-log entries sharing a mechanic collapse into one proposal.
- [X] T024 Run `python3 -m ruff check tools/harvest_friction.py tools/test_harvest_friction.py`
      and `python3 -m ruff format --check tools/harvest_friction.py
      tools/test_harvest_friction.py`; fix any findings.
- [X] T025 Run `python3 -m unittest discover -s tools -p 'test_harvest_friction.py'` and confirm all tests pass.
- [X] T026 Walk `quickstart.md` end to end by hand (Steps 1-5) against the fixtures, confirming
      SC-001 through SC-004 all hold as described.
- [X] T027 Update `docs/design/16-session.md`'s "Session friction capture" section with one
      sentence noting that a harvest step (this feature, `tools/harvest_friction.py`) now exists
      to mine `log/friction.md` into `wyrd` issue proposals — consistent with `CLAUDE.md`'s rule
      that a design document describes the present; keep the edit to that one addition, no
      other rewording.

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** → **Phase 2 (Foundational)**: fixtures and skeleton before parsing logic.
- **Phase 2** blocks all of Phases 3-5: triage/proposal/dedup all consume `FrictionEntry`/
  `MalformedEntry` and the file-reading function Phase 2 defines.
- **Phase 3 (US1)** is the MVP and has no dependency on Phases 4-5.
- **Phase 4 (US2)** depends on Phase 3's CLI loop and reporting shape (T013/T015) already
  existing to attribute and separate per-chronicle output.
- **Phase 5 (US3)** depends on Phase 3's `HarvestProposal`/`build_proposal` (T011) existing, but
  not on Phase 4 — US2 and US3 can be implemented in either order once Phase 3 is done.
- **Phase 6 (Polish)** depends on all of Phases 3-5 being complete.

## Parallel Execution Examples

- Within Phase 1: T001, T003 in parallel (different files); T002 can start alongside them.
- Within Phase 2: T006 and T008 (both test-writing tasks against already-defined functions) can
  run in parallel with each other once T004/T005/T007 land.
- Within Phase 3: T010 and T012 in parallel once T009/T011 land; T014 depends on T013.
- Phases 4 and 5 can be worked in parallel by different implementers once Phase 3 is merged,
  since neither depends on the other.
- Within Phase 6: T022/T023 in parallel with T024's lint pass on files not yet touched by T022;
  run T024-T026 sequentially at the end regardless, since each gates the next.

## Implementation Strategy

**MVP first**: Phase 1 → Phase 2 → Phase 3 (User Story 1) delivers the entire core value —
single-chronicle harvest with correct triage, proposal-building, and no auto-filing — and is
independently testable and demonstrable on its own (quickstart.md Steps 1-2 and 5).

**Incremental delivery**: Add Phase 4 (multi-chronicle) and Phase 5 (dedup) next, in either
order, each independently testable per their own Independent Test above; finish with Phase 6's
cross-cutting polish and the one-line design-doc update.
