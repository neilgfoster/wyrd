# Phase 1 Data Model: Omen carryover

## `pending_omen` (existing character field, first read/written by this feature)

Already part of `engine/wyrd/character.py`'s `PLAYER_CHARACTER_FIELDS`. Value: `None` | `10` |
`-10`. Persists across committed proposals; this feature is the first to read or stage a mutation
against it.

## Omen token (new, internal to one `_stage_requests` call — not persisted directly)

| Field | Type | Notes |
|---|---|---|
| `token` | `int \| None` | The actor's currently-pending modifier for this call. |
| `producing_step` | `int \| None` | The id of whatever step produced `token`. Local (a plain, non-negative id built within *this* call) when the most recent change happened here; encoded as a negative sentinel `-(id + 1)` when it was inherited from a still-present *kept* step outside this call (`reroll`'s `initial_producing_step`) — the two id spaces must never be confused (see Relationships). `None` if no step anywhere has ever produced the current token. |

## Step (unchanged shape, `depends_on` now also carries Omen-consumption edges)

No new fields — the Omen-consumption edge uses the exact same `depends_on: list[int]` #236/#237
already defined. A step's `depends_on` may now include an id for either reason (a cascade
dependency, or consuming that step's own Omen) — the two are not distinguished in the stored
shape, matching `docs/design/31-action-resolution.md`: "the same `depends_on` edge ... already
uses for any other kind of dependency."

## Relationships

```text
_stage_requests(steps, ordered_requests, state_cache, seed_cursor,
                 resource_deltas={}, initial_producing_step={})
  -> per-actor omen tracking, lazily initialized:
       token = state_cache[actor]["pending_omen"]
       producing_step = -(initial_producing_step[actor] + 1) if token is not None
                         and actor in initial_producing_step else None
  -> for each request, in order:
       modifier = current token (or 0)
       extra_depends_on = [producing_step] if modifier and producing_step is not None else []
       _stage_request(..., declaration_bonus_delta=modifier + resource_deltas.get(index, 0),
                       extra_depends_on=extra_depends_on)
       fresh_omen = read the built step's own roll's wyrd_die
       new_token = fresh_omen if fresh_omen is not None
                   else (None if modifier else current token)
       if new_token != current token:
         token = new_token; producing_step = base_id (a real *local* id) if new_token is not None
                             else None
         stage a pending_omen `set` mutation on THIS step, immediately -- every real
         transition is staged, not only the call's own net effect (research.md's own
         worked example of why: a reroll later replaying kept steps' mutations needs every
         intermediate value, not just whichever one happened to be true at the end)

propose_batch(requests, seed=...)
  -> ordered_requests = requests, in the order given
  -> _stage_requests(steps, ordered_requests, state_cache, seed_cursor)   # no initial_producing_step

reroll(proposal_id, step, resource, seed=...)
  -> downstream = _downstream_set(steps, step)   # may span >1 top-level request
  -> requests_to_redo = every downstream step's own `inputs`, in step_id order
     (step's own request is always requests_to_redo[0] -- nothing in the downstream set can
     have a smaller step_id than step itself)
  -> replay kept steps' own mutations onto scratch state; while doing so, track
     last_omen_producer[actor] = the kept step's own (real, outer) step_id whenever one of its
     mutations sets pending_omen to a non-None value (cleared from the map on a None set)
  -> _stage_requests(new_steps, requests_to_redo, state_cache, seed_cursor,
                     resource_deltas={0: RESOURCE_MODIFIERS[resource]},
                     initial_producing_step=last_omen_producer)
  -> resource's own cost mutation appended to new_steps[0]
  -> _renumber_and_merge(kept_steps, new_steps, step):
       new_steps' own local ids (0-based) get remapped via id_map (0 -> step's own original id,
       the rest -> fresh ids after the highest already in use); a depends_on entry encoded as a
       negative sentinel is decoded back to the real kept-step id it always was, never looked up
       in id_map -- this is what keeps a redone request's edge to an untouched kept step correct.
```
