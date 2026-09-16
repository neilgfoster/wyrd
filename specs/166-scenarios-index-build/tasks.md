# Tasks: Scenarios Index Build and Bootstrap Wiring

**Input**: `spec.md`, `plan.md`

## Phase 1: Engine repo (this repo)

- [x] T001 [P1] Write `tools/setting_scenarios.py`: `plan` verb (FR-001, FR-003, FR-004).
- [x] T002 [P1] Add `commit` verb to `tools/setting_scenarios.py`: injected-record lookup,
      validation, all-or-nothing write (FR-002, FR-005).
- [x] T003 [P1] Write `tools/test_setting_scenarios.py` covering spec.md's Acceptance Scenarios 1-5
      and Edge Cases, against fixtures under `tools/fixtures/setting_scenarios/`.
- [x] T004 Run `ruff check .`/`ruff format --check .` on the new files.

## Phase 2: wyrd-chronicle-template (sibling repo)

- [ ] T005 [P1] Rewrite Step 3 of
      `wyrd-chronicle-template/.claude/skills/wyrd-bootstrap/SKILL.md` to prefer
      `index/scenarios.json` + `scenario_selection.select_scenario` when present and non-empty,
      falling back to today's `entities/`-reading text otherwise (FR-006, FR-007).

## Phase 3: wyrd-setting-titan (sibling repo)

- [ ] T006 [P1] Read enough of at least five of Titan's `library/03 - adventures/` gamebooks'
      `corpus/` text to ground a real scenario record for each (FR-008).
- [ ] T007 [P1] Run `tools/setting_scenarios.py commit` from this repo against
      `wyrd-setting-titan`, producing real `index/scenarios.json` /
      `index/scenario_build_cache.json` (SC-004).
- [ ] T008 Commit the built index in `wyrd-setting-titan`.

## Phase 4: Verification

- [ ] T009 Re-run `commit` with the same records file against Titan; confirm no regeneration and
      byte-identical output (SC-001).
- [ ] T010 Manually walk `/wyrd-bootstrap` Step 3's new logic against the real Titan index and
      confirm more than one real candidate is considered (spec.md's Definition of Done).
