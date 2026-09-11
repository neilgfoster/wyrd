# Phase 1 Data Model: Chronicle state invariants

No new entity types or schema fields. This feature validates existing fields; it defines two new
functions and the data each one reads.

## `_load_chronicle_entities(any_touched_path: pathlib.Path) -> dict[str, dict]`

**Purpose**: assemble the chronicle's full *effective* entity set (setting + overlay merged, plus
chronicle-invented entities — the same shape `entity.py`'s `resolve_entity`/`load_set` already
produce) so FR-001/002/003 can check a proposal's mutations against every entity the chronicle
knows about, not just the ones the proposal directly touches.

- **Input**: one path from the proposal's own mutations (`commit()` already has these) — used only
  to locate the chronicle root. A chronicle root is identified by walking up from the given path
  until a directory containing `entities/`, `overlay/`, and `setting/` subdirectories (or
  `chronicle.yaml`) is found — the layout `22-state.md` § Where things live already fixes.
- **Output**: `dict[str, dict]` keyed by entity id, frontmatter only (bodies are not needed for
  validation) — `setting/*.md` entities resolved against `overlay/*.md` via `entity.resolve_entity`,
  plus every `entities/*.md` file merged in directly (chronicle-invented entities have no setting
  counterpart to resolve against).
- **Failure mode**: if no chronicle root can be located from the given path (e.g. a proposal built
  directly against loose entity files, outside a full `entities/`/`overlay/`/`setting/` layout),
  returns `{}` rather than raising — `_validate_proposal` then checks the proposal's mutations
  for internal consistency (parent cycles and references among the entities it touches, plus the
  numeric rules) without being able to catch a duplicate id or reference against an entity outside
  what the proposal itself loaded. This keeps every existing caller and test that builds a
  proposal without a full chronicle directory working unchanged, while chronicles that do have the
  full layout get the complete cross-entity checks.

This function lives in `resolution.py` (it is a `commit`-internal helper, not a generally useful
export) and is the *only* new I/O this feature performs — everything else operates on the
in-memory proposal and the entity set this function returns.

## `_validate_proposal(mutations: list[dict], entities: dict[str, dict]) -> None`

**Purpose**: the single validation pass FR-001 through FR-005 describe, run once against a
proposal's full mutation list (including cascade-produced mutations) immediately before `commit`
applies anything.

- **Input**: `mutations` — the proposal's flat mutation list (as `commit()` already extracts it
  from `proposal["mutations"]`); `entities` — the chronicle's effective entity set from
  `_load_chronicle_entities`, further overlaid with a scratch copy of each mutation's target field
  applied in-memory (the same "apply to scratch state, read back" pattern `_cascade_from_mutation`
  already uses), so a check sees the proposal's *final* per-entity state, not its state before any
  mutation.
- **Output**: `None` on success; raises `ProposalError` naming the specific violated rule and the
  offending entity/field on the first violation found (order: duplicate id, unresolved reference,
  parent cycle, fortune/fate, tracker bounds — cheapest/most structural checks first, so a
  malformed id is reported before a numeric comparison that might not even apply).
- **No disk access**: this function is pure computation over its two arguments — `commit()` is
  responsible for calling it *before* touching any entity file, so a raised `ProposalError`
  guarantees FR-007 (nothing written) trivially, by ordering rather than by rollback.

### Passive rule → existing/new check mapping

| Rule (spec FR) | Mechanism |
|---|---|
| FR-001 duplicate id | new: membership test — does a mutation introduce/rename to an id already in `entities` (excluding the entity's own prior id, if this is an update not a create) |
| FR-002 unresolved reference | existing: `entity.unresolved_references(entities)` — the scratch-merged set |
| FR-003 parent cycle | existing: `entity.check_containment(entities)` — the scratch-merged set |
| FR-004 fortune ≤ fate.max | new: `_get_nested(state, "fortune.current") <= _get_nested(state, "fate.max")`, skipped if either path is absent |
| FR-005 tracker 0..max | new: `0 <= _get_nested(state, "value") <= _get_nested(state, "max")` for any entity/mutation touching a `value`/`max` pair |

## `is_spent(character_state: dict) -> bool`

**Purpose**: User Story 3's read-time Spent accessor (ADR 0049).

- **Input**: a character's frontmatter dict (already loaded — this function performs no I/O).
- **Output**: `bool` — `resolve.current <= max(taint, trauma)`, with each axis exempted (excluded
  from the `max(...)` comparison) when it is `0`, per ADR 0049. If *both* axes are `0`, the
  character cannot be Spent (nothing to compare `resolve.current` against) — `False`.
- **Placement**: `resolution.py`, alongside `rolls_aftermath` (an existing precedent for a small,
  pure read-time predicate over character state in this module).

## No changes to on-disk schema

- No entity gains a new field.
- No `spent` field is ever written (FR-009, SC-003).
- `commit()`'s signature is unchanged from the caller's perspective (`commit(proposal_id: str)`) —
  entity-set discovery is internal, not a new required parameter, so `verbs.py`/`client.py`'s
  existing `commit` call sites need no change.
