# Phase 0 Research: Chronicle state invariants

No NEEDS CLARIFICATION markers were left in the Technical Context — this feature is additive
code against an already-understood, already-implemented surface. The research below records why
each design choice reuses existing machinery instead of introducing new mechanism.

## Decision: reuse `entity.py`'s existing reference/cycle checks, don't reimplement them

- **Decision**: FR-001/002/003 (duplicate id, unresolved reference, parent cycle) call
  `entity.py`'s existing `check_containment()` and `unresolved_references()` against the
  chronicle's full entity set, rather than writing new traversal logic inside `resolution.py`.
- **Rationale**: these functions already exist, are already tested (`tests/engine/test_entity.py`),
  and already implement exactly the rules `22-state.md` states (cycle detection via `parent`,
  wikilink resolution across `parent`/`links`/`connections[].to`/`allegiances`/`cast`/`members`/
  `based_at`). Reimplementing them inside `resolution.py` would be the "two documents describing
  one thing differently" fault class `CLAUDE.md` calls out — a second traversal that can drift
  from the first.
- **Alternatives considered**: writing a resolution-local check restricted to just the entities a
  proposal touches, for speed — rejected, because a proposal's mutation can introduce a *new*
  entity (an id that didn't exist before) whose duplicate-ness or cycle membership can only be
  known against the full set; scoping the check to only the touched entities would miss a
  duplicate against an entity the proposal never mentions.
- **Duplicate-id check**: neither `check_containment` nor `unresolved_references` checks id
  uniqueness directly — that's a plain "does this id already exist in the entity set" check
  against `entity.py`'s `load_set`-assembled mapping, added directly in the new validation pass
  (no existing function covers it, so this one piece is new but trivial: membership test on a
  dict).

## Decision: `fortune.current ≤ fate.max` and tracker `0..max` are new, small checks

- **Decision**: these two rules have no existing implementation anywhere in the repo (confirmed by
  grep across `engine/wyrd/*.py` for `fortune`/`fate`/tracker bound logic) — they are written new,
  as straightforward field reads via the same dotted-path convention (`_get_nested`) `resolution.py`
  already uses for mutation application.
- **Rationale**: `_get_nested`/`_apply_mutation` already exist and already understand dotted paths
  like `stamina.current`; reusing them for the read-back after applying a proposal's mutations to
  an in-memory scratch copy (the same pattern `_cascade_from_mutation` already uses) keeps this
  feature's new code down to the comparison itself.
- **Alternatives considered**: checking each mutation individually as it's applied, rather than
  the final post-mutation state — rejected per spec.md's Edge Cases: fortune must be checked
  against the value *after* all of a proposal's mutations to that entity land, matching how
  `commit` already treats a proposal's mutations to one entity as a single scoped batch.

## Decision: `is_spent()` is a pure accessor, not a write path

- **Decision**: add a small `is_spent(character_state: dict) -> bool` function to `resolution.py`
  (or `character.py` — see Data Model for the final placement call) that reads `resolve.current`,
  `taint`, `trauma` and applies ADR 0049's formula. Nothing calls it from `commit`.
- **Rationale**: `22-state.md` is explicit that Spent is "not a write-time check at all... it is
  read off... whenever asked." Grepping the repo confirms nothing currently writes a `spent`
  field, so this is purely additive — no existing write path to touch or guard.
- **Alternatives considered**: caching Spent as a computed field written at commit time for cheap
  reads — rejected outright; the design document forbids exactly this ("derived, not stored"), and
  a cached value that can silently drift from resolve/taint/trauma reintroduces the "two documents
  describing one thing differently" fault class.

## Decision: validation runs once, in `commit()`, after `propose()`'s cascades have already staged

- **Decision**: the new validation pass lives inside `commit()`, immediately before mutations are
  applied to entity files, and validates the *proposal's final shape* — including whatever
  `_cascade_from_mutation` already staged during `propose()`.
- **Rationale**: `22-state.md` states "a write" means a commit, not a propose — nothing is checked
  against an unconfirmed proposal. Running the check once, at commit, rather than incrementally
  during staging, also means a cascade's own mutation gets checked by the exact same code path as
  a directly-requested one (FR-006) — there is only one validation pass to keep correct, not one
  per staging call-site.
- **Alternatives considered**: validating incrementally inside `propose()`'s staging functions —
  rejected because it would require every staging call-site (`_stage_transformation_chain`,
  `_stage_trauma_test_chain`, `_stage_combat_attack`, …) to independently call the same checks,
  multiplying the surface area for exactly the kind of drift `CLAUDE.md`'s fault-class list warns
  about, for no benefit (nothing is written until `commit` regardless).
