# Tasks: Damage-type critical tables

**Input**: Design documents from `specs/090-damage-type-criticals/`
**Prerequisites**: plan.md, data-model.md, contracts/api.md, quickstart.md, research.md

## Phase 1: The three new tables and the cross-check script

- [x] **T001** [P] `specs/090-damage-type-criticals/check_criticals_engine.py`: a standalone
      script that will import `engine/wyrd/resolution.py`'s `CRITICAL_PIERCING_TABLE`,
      `CRITICAL_BLUNT_TABLE`, `CRITICAL_SEARING_TABLE` (and the unchanged
      `CRITICAL_SLASHING_TABLE`) and assert each row-for-row against
      `specs/015-damage-type-criticals/check_criticals.py`'s own `TABLES` dict (SC-001, SC-002,
      SC-003). Written first so it fails until T002 lands, per the design doc's own row data.
- [x] **T002** In `engine/wyrd/resolution.py`, add `CRITICAL_PIERCING_TABLE`,
      `CRITICAL_BLUNT_TABLE`, `CRITICAL_SEARING_TABLE` module constants, same shape as
      `CRITICAL_SLASHING_TABLE`, with the exact rows from `docs/design/05-criticals.md`
      (FR-002, FR-003, FR-004).

## Phase 2: Table selection and the load error

- [x] **T003** In `engine/wyrd/resolution.py`, generalize `_critical_slashing_band` into
      `_critical_band(damage_type, total)` that looks up the table for `damage_type` (a module
      dict mapping the four keys to their table constant and mortal row key/table name) and
      raises `ValueError` naming the value for anything outside the closed set (FR-001, FR-006).
- [x] **T004** Update `_stage_critical` to accept `damage_type` (default `"slashing"`), call
      `_critical_band`, and record the correct `table` name in the staged step's `roll` dict
      instead of the hardcoded `"critical-slashing"` (FR-001, FR-001b, FR-005).
- [x] **T005** Thread `damage_type` through `_stage_combat_attack` (new kwarg, forwarded to
      `_stage_critical`) and `_normalize_request`/`_stage_request` (new optional request field,
      same pattern as `weapon_dice`/`armour_dice`) (FR-001a).

## Phase 3: Callers

- [x] **T006** [P] `combat.py`: add optional `damage_type` kwarg to `crowd_attack`,
      `_crowd_attack_request`, `crowd_parting_blow`, `resolve_ranged_attack`, forwarded
      unchanged into the request dict (FR-001a).
- [x] **T007** [P] `verbs.py`: add optional `damage_type` kwarg to the combat-attack-facing
      function, forwarded unchanged (FR-001a).
- [x] **T008** [P] `client.py`: add `--damage-type {slashing,piercing,blunt,searing}` CLI arg,
      forwarded unchanged (no CLI-level default — omission stays `None`) (FR-001a).
- [x] **T009** [P] `catalog.py`: add `damage_type` (string enum of the four) to `propose`'s MCP
      `inputSchema.properties`, not in `required` (FR-001a).

## Phase 4: Tests

- [x] **T010** [P] `tests/engine/test_resolution.py`: for each of `critical-piercing`,
      `critical-blunt`, `critical-searing`, a boundary-total test on both sides of every row
      transition resolves to the documented row (mirrors the existing slashing boundary test)
      (SC-002, User Story 1 Scenario 4).
- [x] **T011** [P] `tests/engine/test_resolution.py`: for each of the three new tables, a total
      landing in the open-ended top row stages `mortal: true` and no wound-record mutation,
      mirroring the existing slashing-mortal test (User Story 1 Scenario 5).
- [x] **T012** [P] `tests/engine/test_resolution.py`: `propose(..., mechanic="combat-attack",
      damage_type="acid", ...)` raises `ValueError` naming `"acid"` (User Story 2, both
      scenarios: an unrecognized type and a required-but-missing case already covered by
      default-to-slashing in T013).
- [x] **T013** [P] `tests/engine/test_resolution.py`: a `combat-attack` request with no
      `damage_type` supplied still resolves against `critical-slashing`, reproducing the
      existing slashing test's own seed/expected values unchanged (FR-001b, Edge Cases).
- [x] **T014** [P] `tests/engine/test_combat.py`: `crowd_attack`/`resolve_ranged_attack` forward
      a supplied `damage_type` into the resulting `combat-attack` request's staged critical step
      (when the scenario drives a critical), and omit it cleanly when not supplied.

## Phase 5: Polish

- [x] **T015** `python3 specs/090-damage-type-criticals/check_criticals_engine.py` passes
      (SC-001, SC-002, SC-003).
- [x] **T016** `ruff check . && ruff format --check . && python3 -m pytest -q` (SC-004 and the
      full existing suite, unregressed): the full test suite is clean (397 passed, up from 389);
      `ruff check`/`format --check` report 68/40 pre-existing findings on `main` already, entirely
      outside this feature's touched files (verified by diffing against `main` before this
      branch) — none of this feature's own files (`resolution.py`, `combat.py`, `verbs.py`,
      `client.py`, `catalog.py`, the two test files, `check_criticals_engine.py`) appear in
      either report.
- [x] **T017** `python3 tools/check_docs.py` still passes (no design document is touched by this
      feature — `05-criticals.md` already describes all four tables as present tense).

## Dependencies

- T001 is written before T002 lands (fails first, per plan.md's reuse-not-re-derive intent), but
  both must land together before T015 can pass.
- T002 blocks T003.
- T003 blocks T004.
- T004 blocks T005.
- T005 blocks Phase 3 (T006–T009).
- Phase 3 blocks T014.
- T002–T005 block T010–T013.
- T015–T017 run last.
