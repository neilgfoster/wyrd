# Tasks: Systems of power resolution

**Input**: plan.md, spec.md in this directory.

- [X] T001 Add `_resolve_system_of_power` and `_mutate_system_of_power` to
      `engine/wyrd/resolution.py`, per plan.md's design decisions: `_resolve_system_of_power`
      wraps `_resolve_test` and enforces `requires_training`; `_mutate_system_of_power` returns
      the failure-only `strain`/`resolve` cost mutations (tier-scaled), the ADR 0047
      Strain-threshold `trauma` mutations, and the Ill-Omen `taint` mutation (tier-scaled),
      each respecting `overrides.disable`.
- [X] T002 Register `"system-of-power": (_resolve_system_of_power, _mutate_system_of_power)` in
      `_MECHANICS`.
- [X] T003 Wire a `system-of-power` verb wrapper into `engine/wyrd/verbs.py` that resolves a
      setting's `power.yaml` declaration (+ optional declared tier) into the parameters
      `resolution.py` expects.
- [X] T004 [P] `tests/test_resolution.py`: cover spec.md's acceptance scenarios — failure-only
      cost (US1), the `requires_training` gate (US1), both worked examples end-to-end
      (ember-craft with tiers, signal-attunement without — SC-001), tier cost/Taint scaling vs.
      the untiered baseline (US2), the Strain-threshold Trauma check reading the cumulative total
      rather than a per-invocation delta and applying identically whether retried on the same
      system or rotated across two different systems (US3), Ill Omen on a success still applying
      Taint while cost is skipped (Edge Cases), and `overrides.disable` skipping each
      disabled track's consequence without substituting another (US3).
- [X] T005 `ruff check . && ruff format --check .` clean; `PYTHONPATH=engine pytest -q` green.
