# Implementation Plan: Journeys: engine support

**Branch**: `108-journeys-engine-support` | **Spec**: [spec.md](spec.md) | **Issue**: #287

## Summary

Add `engine/wyrd/journey.py`, a new pure-function module (no I/O, matching `economy.py`/
`advancement.py`'s own division of labour) that resolves a journey arc (`scale: journey`,
docs/design/20-journeys.md) into its ordered legs, dispatches each leg by its existing
`mode: played | summarised` field, rolls the once-per-leg hazard check
(`d100 ≤ hazard_rating × 10`, the same shape as a Threat's activation roll,
docs/design/19-campaign.md) and its sub-table match, and reports early-ending and
Threat's-reach-crossing outcomes. No new resolution mechanic and no per-item ledger (FR-008):
a hazard entry naming a skill resolves through `resolution.propose`/`commit` exactly like any
other test; a numeric cost (Standing, e.g.) lands through `economy.py`'s existing verbs; a
narrative-only consequence (a Threat's `ambient` cost, which the design doc defines as prose,
not a number) is surfaced in the result for the caller/GM to apply, the same separation the
engine already keeps between mechanical resolution and GM narration (docs/design/13-diegesis.md).

This is also the first runtime code for any arc/beat/Threat concept (spec.md's Assumptions) —
the plan below introduces only the minimal slice each needs for journey resolution, kept
narrow and reusable rather than a general campaign engine.

## Technical Context

- **Language**: Python 3.11+, standard library only (docs/design/27-tooling.md §2).
- **New module**: `engine/wyrd/journey.py`. No existing module owns arcs, beats, or Threats, so
  there is nothing to extend — this plan adds a new module rather than growing an unrelated one,
  matching how `economy.py`/`advancement.py` were each added as their own subsystem landed.
  Journey/leg/Threat records are plain dicts, exactly like every other module in `engine/wyrd/`
  (no entity/file loading here — that stays the setting-repo's concern, per `CLAUDE.md`'s
  engine/setting split).
- **Existing modules reused, not duplicated**:
  - `resolution.propose`/`resolution.commit` — the core roll a hazard entry's named skill
    resolves through (FR-005). `journey.py` builds the same request shape `_resolve_ordinary_test`
    already expects rather than calling any private `_resolve_*` helper directly.
  - `economy.adjust_standing` (and siblings) — where a hazard's `effect` or a Threat's `ambient`
    entry is a concrete numeric cost, `journey.py` returns a description the caller applies via
    the existing economy verb; `journey.py` itself never mutates Standing/coin directly, matching
    `economy.py`'s own callers-apply-the-delta pattern.
- **Testing**: `tests/test_journey.py`, new file, following `tests/test_economy.py`'s
  fixture-and-assert conventions (`PYTHONPATH=engine`). Hazard-roll probability is asserted via
  fixed die values (a seeded/injected roll), never live sampling — matching
  `docs/design/27-tooling.md`'s "deterministic over inference" and this repo's history of
  wrong-until-computed probability claims.
- **No new persistent state**: journey/leg progress is caller-tracked (which legs have been
  reached), matching the "engine has no scene detection of its own" pattern `economy.py` already
  documents for `martial_weapon_sighting`'s `already_applied` argument.

## Design decisions

- **Leg derivation is one function, `legs_for(journey)`**: if `journey` has no `pace`, returns a
  single synthetic leg spanning the whole route (`from`→`to`, inheriting the journey's own `mode`
  if declared, else defaulting to `played` — the design doc gives no other default and an
  unstructured journey is "mechanically as light as ordinary narrated travel"); if `pace` is
  present, returns `journey["children"]` in order, unchanged. This keeps FR-001/SC-001 a pure
  data transform with no roll involved.
- **Leg resolution dispatch, `resolve_leg(leg, ...)`**: reads `leg["mode"]`. `"played"` returns a
  result tagged `kind: "beat"` (the caller runs the ordinary beat/scene machinery; this module
  does not simulate a scene). `"summarised"` returns a result tagged `kind: "elapsed-time"` with
  the leg's span carried through unchanged (the actual `wyrd advance-time` expected-value
  machinery is out of scope here — no such runtime exists yet per spec.md's Assumptions; this
  module only tags and routes, it does not compute activation-over-a-span itself). Any other
  value is a hard error (`ValueError`) — mode is author-declared, per the design doc, and an
  unrecognised value is a data error, not a third mode to infer (FR-002).
- **Hazard roll, `roll_hazard(journey, wyrd_roll, table_roll)`**: takes the two d100/table rolls
  as arguments rather than calling `random` itself, matching `resolution.py`'s own `roll()` split
  between randomness and banding, and matching this repo's deterministic-testing convention.
  Returns `{"activated": False}` when `wyrd_roll > hazard_rating * 10` or `hazard_rating == 0`.
  On activation, matches `table_roll` against the journey's `hazards` dict of range keys
  (reusing the existing range-key parsing already needed for a Threat's `effects:` table shape —
  written once here since no shared range-table parser exists yet, e.g. `"1-2"`/`"6"`); a roll
  matching no key (including on an empty table) returns `{"activated": True, "matched": None}` —
  the no-op case (FR-004). A matched entry with `skill` is returned with a `request` shape ready
  to pass to `resolution.propose` (FR-005); a matched entry with `skill: null` is returned as
  `{"activated": True, "matched": entry, "kind": "narration"}`.
- **Early ending, `close_journey(journey, legs_reached)`**: takes the list of legs actually
  resolved and returns consequences (whatever `resolve_leg`/`roll_hazard` already produced for
  those legs) versus the remainder, reported as `not_reached` — no new consequence computation of
  its own, it only partitions what already happened (FR-006).
- **Threat's-reach crossing**: a leg's own record carries a caller-supplied flag/reference (per
  spec.md's Assumptions — the engine has no spatial model to derive this from), e.g.
  `leg["crosses_threat"]` naming the active Threat entity's data. `resolve_leg` looks for this key
  and, when present, includes the named Threat's `ambient` list in its result alongside the leg's
  own outcome (FR-007) — reported, not auto-applied as a numeric delta, since `ambient` entries
  are prose in the design doc's own schema.

## Project Structure

```
engine/wyrd/journey.py     # legs_for, resolve_leg, roll_hazard, close_journey
tests/test_journey.py      # leg derivation (paced/unpaced), mode dispatch, hazard activation
                            # at fixed rolls, sub-table match/no-op/gap, early-ending partition,
                            # Threat's-reach ambient surfacing
```

## Constitution Check

- Setting-agnostic: `journey.py`'s public names (`legs_for`, `resolve_leg`, `roll_hazard`,
  `close_journey`) are descriptive English already used by the design doc, no setting vocabulary.
- Deterministic over inference: hazard activation is asserted against the exact
  `hazard_rating × 10` threshold with fixed input rolls, not sampled; range-table matching is
  asserted against literal boundary values (e.g. roll `2` and `3` on a `1-2`/`3-5` split).
- No second resolution mechanic, no per-item ledger (FR-008, design doc's own constraint): this
  plan adds zero new dice-rolling code — `roll_hazard` bands caller-supplied rolls, and a matched
  skill entry is handed to the existing `resolution.propose`/`commit` pair unchanged.
- Docs stay the present-tense description: `docs/design/20-journeys.md` already describes this
  behaviour fully; no design-doc change needed, only the engine catching up to what it specifies.
- Capability change: `specs/108-journeys-engine-support/` is committed alongside the code.

No violations to track.
