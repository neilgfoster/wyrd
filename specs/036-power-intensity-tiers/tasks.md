# Tasks: Optional intensity tiers for a system of power

**Input**: Design documents from `/specs/036-power-intensity-tiers/`
**Prerequisites**: plan.md, spec.md, data-model.md, quickstart.md

Single-project structure (no [P] parallel markers needed — every task touches one of two files,
in sequence, with the doc read before the validator is written against it).

## Phase 1: Documentation (User Stories 1 & 2 — P1)

- [X] T001 Add `intensity_tiers` to the schema table and document it in
  `docs/design/14-systems-of-power.md`: the field itself (optional, list), each tier's four
  sub-fields (`label`, `difficulty`, `cost_multiplier`, `ill_omen_taint_bonus`), the resolution
  rule (`effective cost = base * cost_multiplier`, `effective Ill Omen Taint = base +
  ill_omen_taint_bonus`, both still applied through the existing win-or-lose/Taint-accrual rules
  — no new resolution path), and an explicit statement that the field is optional and does not
  require any existing declared system of power to change (FR-001–FR-004, FR-007, FR-008; SC-004)
- [X] T002 Extend the worked example in `docs/design/14-systems-of-power.md` (or add a second
  worked example) showing ember-craft with a three-tier `intensity_tiers` declaration
  (minor/moderate/major) and walk through resolution at one non-default tier, mirroring the
  existing worked-example prose style (FR-004; SC-001)
- [X] T003 Run `python3 tools/check_docs.py` and confirm it still passes (link/reachability
  check unaffected by this doc edit, but must not regress)

## Phase 2: Validation (User Stories 1, 2 & 3 — P1/P2)

- [X] T004 In `tools/check_power_systems.py`, add `"intensity_tiers"` to `OPTIONAL_FIELDS` and
  define the six recognised difficulty rungs as a module-level set (mirroring
  `docs/design/03-rules.md` §1's table) for tier validation to check `difficulty` against
  (data-model.md)
- [X] T005 In `tools/check_power_systems.py`, add a tier-validation function (or extend
  `check_entry`) that, when `intensity_tiers` is present, checks each tier for: missing/empty
  `label`, `difficulty` not in the recognised rung set, `cost_multiplier` not a positive number,
  `ill_omen_taint_bonus` not a non-negative integer — each failure named with the system of
  power and the tier's list position, one problem line per fault, matching the existing
  `check_entry` failure-reporting shape (FR-005; data-model.md Validation summary)
- [X] T006 Confirm (by inspection — no code change expected) that a `power.yaml` with no
  `intensity_tiers` field takes none of the new branches added in T004/T005 — the field is
  read only when present (FR-003, FR-006)
- [X] T007 Extend `resolution_trace()` in `tools/check_power_systems.py` to optionally accept a
  tier (by label or index) and return the effective (multiplied/bonus-added) cost and Ill Omen
  Taint figures per data-model.md's derived-values formulas, without changing its existing
  no-tier return shape

## Phase 3: Self-test fixtures (User Story 3 — P2)

- [X] T008 [depends on T004, T005] Add a `TIERED_EMBER_CRAFT_YAML` self-test fixture (three
  tiers, all valid) to `tools/check_power_systems.py` and assert it validates clean
- [X] T009 [depends on T005] Add four malformed-tier fixtures to `tools/check_power_systems.py`
  — bad `difficulty` label, non-positive `cost_multiplier`, negative `ill_omen_taint_bonus`,
  missing `label` — and assert each is rejected with a problem line naming the tier (spec User
  Story 3 Acceptance Scenarios 1–4; SC-003)
- [X] T010 [depends on T007, T008] Assert `resolution_trace()` against the tiered fixture at a
  non-default tier returns the correct multiplied cost and bonus-added Ill Omen Taint,
  matching data-model.md's derived-values formulas by hand-computed expected values (not just
  re-deriving the same formula the code uses — assert against numbers computed independently,
  per CLAUDE.md's "assert prior numbers" practice)

## Phase 4: Verification (all user stories)

- [X] T011 [depends on T001–T010] Run `python3 tools/check_power_systems.py` (self-test, no
  path argument) and confirm it passes, including the new fixtures
- [X] T012 [depends on T001–T010] Run the quickstart.md scenarios by hand (or a throwaway
  script covering the same four checks) and confirm each matches its documented expected
  outcome — validates SC-001 through SC-004 end-to-end, not just via the embedded self-test
- [X] T013 Run `ruff check . && ruff format --check .` and `python3 -m pytest -q` (repository-
  wide gate, per CLAUDE.md/kord-loop-feature's own required checks before `kord-pr-raise`)

## Dependencies

- Phase 1 (docs) has no code dependency and can be done first — it establishes the vocabulary
  (`intensity_tiers`, `label`, `difficulty`, `cost_multiplier`, `ill_omen_taint_bonus`) the
  validator in Phase 2 must match exactly.
- Phase 2 depends on Phase 1 only for naming consistency, not for any artefact Phase 2 reads
  programmatically (the validator does not parse the markdown doc).
- Phase 3 depends on Phase 2 (the validation logic it's asserting against must exist first).
- Phase 4 depends on all prior phases.

## Implementation strategy

MVP = User Stories 1 & 2 (Phase 1 + the additive, non-regressing parts of Phase 2/T004/T006) —
a setting author can declare tiers and a setting author who doesn't is unaffected. User Story 3
(malformed-tier rejection, Phase 3) is the safety net on top and is P2, but given the total scope
here is one doc section and one script extension, all phases are implemented together in this
feature rather than staged across separate PRs.
