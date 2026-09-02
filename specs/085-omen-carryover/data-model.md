# Phase 1 Data Model: Omen carryover

## `pending_omen` (existing character field, first read/written by this feature)

Already part of `engine/wyrd/character.py`'s `PLAYER_CHARACTER_FIELDS`. Value: `None` | `10` |
`-10`. Persists across committed proposals; this feature is the first to read or stage a mutation
against it.

## Omen token (new, internal to one `_stage_requests` call — not persisted directly)

| Field | Type | Notes |
|---|---|---|
| `token` | `int \| None` | The actor's currently-pending modifier for this call. |
| `producing_step` | `int \| None` | The step id (within this call) that produced `token`, or `None` if it came from persisted state (no in-call producer to `depends_on`). |
| `original` | `int \| None` | The actor's `pending_omen` as read at the very start of this call — compared against the final `token` to decide whether a mutation is staged. |
| `last_change_step` | `int \| None` | Which step's own mutations the eventual `pending_omen` `set` mutation (if any) is attached to. |

## Step (unchanged shape, `depends_on` now also carries Omen-consumption edges)

No new fields — the Omen-consumption edge uses the exact same `depends_on: list[int]` #236/#237
already defined. A step's `depends_on` may now include an id for either reason (a cascade
dependency, or consuming that step's own Omen) — the two are not distinguished in the stored
shape, matching `docs/design/31-action-resolution.md`: "the same `depends_on` edge ... already
uses for any other kind of dependency."

## Relationships

```text
_stage_requests(steps, ordered_requests, state_cache, seed_cursor, resource_deltas={})
  -> per-actor omen tracking, lazily initialized from state_cache[actor]["pending_omen"]
  -> for each request, in order:
       modifier = current token (or 0)
       extra_depends_on = [producing_step] if modifier and producing_step is not None else []
       _stage_request(..., declaration_bonus_delta=modifier + resource_deltas.get(index, 0),
                       extra_depends_on=extra_depends_on)
       fresh_omen = read the built step's own roll's wyrd_die
       token, producing_step, last_change_step updated per FR-003/FR-004
  -> for each actor whose final token != original: stage one pending_omen `set` mutation,
     appended to that actor's own last_change_step

propose_batch(requests, seed=...)
  -> ordered_requests = requests, in the order given
  -> _stage_requests(...)

reroll(proposal_id, step, resource, seed=...)
  -> downstream = _downstream_set(steps, step)   # now may span >1 top-level request
  -> requests_to_redo = every downstream step's own `inputs`, in step_id order
     (step's own request is always requests_to_redo[0] -- nothing in the downstream set can
     have a smaller step_id than step itself)
  -> scratch state rebuilt from kept steps' replayed mutations (already includes any
     pending_omen changes a kept step made, for correct token seeding)
  -> _stage_requests(new_steps, requests_to_redo, state_cache, seed_cursor,
                     resource_deltas={0: RESOURCE_MODIFIERS[resource]})
  -> resource's own cost mutation appended to new_steps[0]
  -> _renumber_and_merge(kept_steps, new_steps, step)   # unchanged from #237
```
