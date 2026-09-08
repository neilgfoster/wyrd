# Implementation Plan: Systems of power resolution

**Branch**: `107-systems-of-power` | **Spec**: [spec.md](spec.md) | **Issue**: #286

## Summary

Add a new `"system-of-power"` mechanic to `engine/wyrd/resolution.py`'s existing
resolve/mutate dispatch table (`_MECHANICS`), the same shape every other mechanic there already
uses (`ordinary-test`, `exposure`, `terror`). Resolution is `_resolve_test` unchanged — no new
dice, no new table (docs/design/09-systems-of-power.md, FR-009). The mutate function computes:
failure-only Strain/Resolve cost scaled by a declared intensity tier; the ADR 0047
Strain-threshold-crossing Trauma check, staged as ordinary `trauma` mutations so the existing
cascade (`_cascade_from_mutation`) runs its usual Trauma-test chain on them unchanged; and an
Ill-Omen Taint gain (plus tier bonus) as an ordinary `taint` mutation, so the existing cascade
triggers a transformation roll on threshold crossing exactly as Exposure/Bargain/Invocation
already do. No new persistent state beyond the `strain`/`taint`/`trauma`/`resolve` fields
`character.py`/`creation.py` already declare.

## Technical Context

- **Language**: Python 3.11+, standard library only (docs/design/27-tooling.md §2).
- **Existing modules**: `engine/wyrd/resolution.py` (`_resolve_test`, `_MECHANICS`,
  `_cascade_from_mutation`, `_apply_mutation`, `_crossed_threshold`, `TAINT_THRESHOLD_SPACING`),
  `engine/wyrd/character.py` (field list, includes `strain`), `engine/wyrd/creation.py` (default
  `strain: 0`), `tools/check_power_systems.py` (already validates a setting's `power.yaml`
  declarations — this feature only consumes an already-valid declaration, it does not re-validate
  schema shape).
- **Testing**: `tests/` mirrors `tests/test_resolution.py`'s existing conventions for a mechanic
  (propose against a fixture state, assert the returned steps/mutations).
- **`strain` is presently an inert field** — no existing mechanic reads or writes it. This feature
  is the first to give it a resolution-time meaning.

## Design decisions

- **`"system-of-power"` joins `_MECHANICS`, not a separate cascade path.** Its `resolve_fn`
  (`_resolve_system_of_power`) is a thin wrapper around the shared `_resolve_test`, exactly like
  `_resolve_exposure`/`_resolve_terror` — the caller passes the invoked system's declared `skill`,
  and the difficulty the GM set (or the declared tier's `difficulty`, if the caller declares one).
  `requires_training: true` is enforced by rejecting the proposal before any roll when the actor's
  skill entry is absent/untrained (`ValueError`, matching how `_resolve_ordinary_test` already
  raises for a missing required `skill`), rather than resolving an untrained roll and discarding
  it.
- **Cost, Trauma-threshold, and Ill Omen all live in `_mutate_system_of_power`, one function,
  returning a list of ordinary field mutations** — the same shape `_mutate_exposure`/
  `_mutate_terror` already return. No new step type, no new cascade branch:
  1. On failure, append a `strain` (`+`) mutation of `strain_cost * multiplier`, and a `resolve`
     (`-`) mutation of `resolve_cost * multiplier` if the system declares `resolve_cost` — where
     `multiplier` is the declared tier's `cost_multiplier` if one was declared, else `1`
     (FR-003/FR-004).
  2. Still on failure, read the actor's current `strain` plus the just-computed gain against their
     `stamina.max` (or equivalent max-Stamina field character.py already declares) using ADR
     0047's `(strain − 1) // max_stamina`, and append that many `trauma` (`+1`) mutations — the
     same "N mutations, one per point" shape `_mutate_terror` uses for its own single Trauma point,
     just computed rather than fixed at 1 (FR-005). This reads the cumulative post-cost total, not
     a delta, matching the design doc's explicit correction of the superseded ADR 0045 approach.
  3. On any outcome, if `roll_data["wyrd_die"] == "ill_omen"`, append a `taint` (`+`) mutation of
     `ill_omen_taint + tier_bonus` (FR-006) — letting the existing `_cascade_from_mutation`
     threshold check trigger `_stage_transformation_chain` exactly as it already does for
     Exposure/Bargain/Invocation; no power-specific transformation path is added.
  4. Steps 1-3 read `overrides.disable` (the mechanism `19-campaign.md`/`24-authoring-a-setting.md`
     already define) to skip Strain/Trauma or Taint mutations outright when a setting has disabled
     those tracks (FR-007/FR-008) — the same graceful-degradation check other Taint/Trauma-feeding
     mutate functions already make.
- **Intensity tier is a resolve-time parameter, not new schema.** The caller passing a `tier`
  label (validated against the system's own declared `intensity_tiers`, `ValueError` if absent)
  is exactly how `_resolve_exposure` already validates its own `tier` against `EXPOSURE_TIERS` —
  no new validation shape needed.
- **The system-of-power declaration itself (`skill`, `strain_cost`, `resolve_cost`,
  `requires_training`, `ill_omen_taint`, `intensity_tiers`) is passed into the mechanic by the
  caller** (the same layer `verbs.py`/the CLI already resolves a setting's `power.yaml` against),
  not looked up inside `resolution.py` — `resolution.py` has no existing pattern of reading
  setting-declared YAML directly, and every other mechanic here is likewise handed its already-
  resolved parameters rather than doing its own lookup.

## Project Structure

```
engine/wyrd/resolution.py   # _resolve_system_of_power, _mutate_system_of_power, _MECHANICS entry
engine/wyrd/verbs.py        # thin wrapper exposing the new mechanic, resolving a power.yaml
                             # declaration + tier into the parameters resolution.py expects
tests/test_resolution.py    # extended: both worked examples (ember-craft with tiers,
                             # signal-attunement without), requires_training gate, Strain-
                             # threshold Trauma crossing, overrides.disable graceful degradation
```

## Constitution Check

- Setting-agnostic: no setting/system vocabulary introduced — `skill`, `strain_cost`,
  `ill_omen_taint`, `intensity_tiers` are already the engine's own descriptive schema fields
  (docs/design/09-systems-of-power.md); this plan adds no new engine-facing label.
- Deterministic over inference: the Strain-threshold Trauma count and tier-scaled cost are
  computed via the same integer-division/multiplication ADR 0047 and the design doc's worked
  examples already specify, asserted by tests against those exact worked-example figures rather
  than eyeballed.
- No second resolution mechanic, no second table (FR-009, ADR 0036): this plan adds one entry to
  the existing `_MECHANICS` dispatch table and reuses `_resolve_test`/`_cascade_from_mutation`
  unchanged — confirmed by design, since neither is modified.
- Docs stay the present-tense description: `docs/design/09-systems-of-power.md` already describes
  this behaviour fully; no design-doc change is needed, only the engine catching up to what it
  already specifies.
- Capability change: `specs/107-systems-of-power/` is committed alongside the code, per the Spec
  Kit gate.

No violations to track.
