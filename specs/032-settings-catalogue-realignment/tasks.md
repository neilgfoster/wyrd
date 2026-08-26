---
description: "Task list for settings catalogue realignment (issue #35)"
---

# Tasks: Realign the settings catalogue with reality

**Input**: Design documents from `/specs/032-settings-catalogue-realignment/`

## Phase 1: Setup

- [X] T001 Confirm the live fleet list (`gh repo list neilgfoster --json name,visibility`,
  filtered to `wyrd-setting-*`) and each repo's `library/`/`index/` state, per research.md
- [X] T002 [P] Create `tools/fixtures/settings_catalogue.json`: a small synthetic `gh
  repo-list`-shaped array plus a sample `settings.yaml`-shaped text blob, covering a clean
  match, a repo missing from the catalogue, and a catalogue entry naming a dead repo

## Phase 2: Catalogue and doc correction (User Stories 1 & 2)

- [X] T003 [US1] Rewrite `settings.yaml`: fourteen entries, correct `repo:` values
  (`wyrd-setting-<name>`), `status: library-loaded` for all fourteen (per research.md's live
  inspection), optional `group:` for `wh40k`/`maelstrom` entries, `id` values kept short and
  independent of repo name
- [X] T004 [US1] Correct `CLAUDE.md`'s repository table row from `wyrd-<setting>` to
  `wyrd-setting-<name>`
- [X] T005 [US2] Add a one-line comment block atop `settings.yaml` documenting the `status:`
  vocabulary (`stub | library-loaded | indexed | playable`) and the optional `group:` field,
  next to the existing `note:` comment

## Phase 3: Drift check (User Story 3)

- [X] T006 [P] [US3] Implement a minimal `settings.yaml` reader in
  `tools/check_settings_catalogue.py`: parses the `settings:` list of flat mappings (id, title,
  repo, visibility, status, optional group) — no third-party YAML dependency
  (`docs/design/20-tooling.md` §2)
- [X] T007 [US3] Implement `live_setting_repos()`: `gh repo list neilgfoster --json name` filtered
  to `wyrd-setting-*` (excluding `wyrd-setting-template`, which is the skeleton, not a setting)
- [X] T008 [US3] Implement `compute_drift(catalogue_entries, live_repos)` — pure function
  returning the `missing_from_catalogue` / `dangling_catalogue_entries` / `clean` shape from
  data-model.md (depends on T006, T007's output shapes)
- [X] T009 [US3] Wire the script's `main()`: read `settings.yaml`, call `live_setting_repos()`,
  call `compute_drift`, print a report, exit 0 if clean else 1
- [X] T010 [P] [US3] `tools/test_check_settings_catalogue.py`: unit tests for the reader
  (T006) and `compute_drift` (T008) against `tools/fixtures/settings_catalogue.json` — clean
  match, a live repo missing from the catalogue, a catalogue entry naming a dead repo

## Phase 4: Polish

- [X] T011 Run `python3 -m unittest discover -s tools -p 'test_*.py'` and confirm the full
  `tools/` suite passes together
- [X] T012 Run `python3 tools/check_settings_catalogue.py` against the live fleet and confirm a
  clean pass (SC-001, SC-003)
- [X] T013 [P] Run `python3 tools/check_docs.py` — this feature adds no `design/` document, so
  confirm it still reports no gap
