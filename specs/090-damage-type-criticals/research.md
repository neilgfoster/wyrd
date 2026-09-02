# Phase 0 Research: Damage-type critical tables

No `NEEDS CLARIFICATION` markers remain in `spec.md` — the design doc
(`docs/design/05-criticals.md`) fully specifies every table's rows, and the existing
`critical-slashing` implementation (`engine/wyrd/resolution.py`) and
`specs/015-damage-type-criticals/check_criticals.py` establish every pattern this feature extends.
The two open questions below were resolved by reading the existing codebase rather than asked of
the operator.

## Decision: `damage_type` threading

**Decision**: Add `damage_type` as a new optional string parameter on a `combat-attack` request,
threaded through the exact same call path `weapon_dice`/`armour_dice` already use:
`resolution.propose`/`propose_batch` → `_normalize_request` → `_stage_request` →
`_stage_combat_attack` → `_stage_critical`; and forwarded unchanged by every existing caller of
that path (`combat.py`'s `crowd_attack`/`resolve_ranged_attack`, `verbs.py`, `client.py`'s CLI
parsing, `catalog.py`'s MCP `propose` tool schema). Defaults to `"slashing"` when omitted.

**Rationale**: Grepping the whole engine (`resolution.py`, `combat.py`, `verbs.py`, `client.py`,
`catalog.py`) for `damage_type` finds no existing occurrence — the parameter genuinely does not
exist yet, contrary to an initial assumption in the spec's first draft (corrected before this
plan). `weapon_dice`/`armour_dice` are the closest existing precedent for "a per-attack value the
caller supplies and the engine threads through the whole chain to `_stage_combat_attack`," so
following that exact shape keeps this feature consistent with the rest of the module rather than
inventing a second pattern. Defaulting to `slashing` (rather than making it required) means every
one of the ~389 existing tests and every existing caller keeps working unchanged — matching
FR-005's "leave `critical-slashing`'s existing behaviour unchanged."

**Alternatives considered**:
- *Require `damage_type` on every `combat-attack` request.* Rejected — this would be a breaking
  change to every existing test and caller, forcing an unrelated migration into a feature whose
  own scope is "add three tables," not "audit every call site."
- *Read damage type off gear/weapon state instead of the request.* Rejected — no such field
  exists on a weapon entity today (checked `engine/wyrd/catalog.py`'s gear schema), and inventing
  one is a larger, setting-authoring-surface change out of this feature's scope; the request-level
  parameter matches how `weapon_dice`/`armour_dice` themselves are already supplied (by the
  caller, not read off a persisted weapon entity).

## Decision: the load-error exception class

**Decision**: An unrecognized `damage_type` raises `ValueError`, the same exception class
`resolution.py` already raises for every other closed-set/load-time violation in this module
(`no such difficulty`, `no such Exposure tier`, `no such mechanic`, `invalid dice spec`).

**Rationale**: `resolution.py` has no dedicated "load error" exception type of its own (unlike
`state.py`'s `StateError`) — `ValueError` is the module's established convention, confirmed by
grep. Introducing a new exception type here would be an unjustified inconsistency within the same
file.

**Alternatives considered**: A dedicated `DamageTypeError` subclass — rejected as unnecessary
ceremony; nothing downstream needs to distinguish this `ValueError` from any of the module's other
`ValueError`s, and every existing caller already handles this module's errors as plain
`ValueError`s.

## Reused, not re-derived

`specs/015-damage-type-criticals/check_criticals.py` already computes and asserts every
probability figure `docs/design/05-criticals.md` publishes for all four tables, from a
standalone `TABLES` dict (not the engine module itself). This feature's own check script
(`specs/090-damage-type-criticals/check_criticals_engine.py`) cross-checks the *engine's*
`CRITICAL_*_TABLE` constants against that already-validated `TABLES` dict for exact equality,
rather than re-deriving the probability model — CLAUDE.md's "check the maths" is already satisfied
by the existing script; this feature's job is to confirm the engine's own data matches it.
