# Phase 1 Data Model: Partial reroll

## Step (extended again)

Adds one field to #236's Step shape:

| Field | Type | Notes |
|---|---|---|
| `inputs` | `dict \| None` | The originating request (see below) for a top-level step; `None` for a step a cascade produced internally (`transformation`/`weapon-damage`/`armour`/`critical`) — never directly rerollable. |

## Request (new, the shape stored as `inputs` and passed to `propose_batch`)

| Field | Type | Notes |
|---|---|---|
| `actor` | `str` | Entity path, normalized. |
| `mechanic` | `str` | `ordinary-test`, `exposure`, or `combat-attack`. |
| `skill` | `str \| None` | |
| `target` | `str \| None` | Entity path, normalized, or `None`. |
| `difficulty` | `str` | Defaults `"average"`. |
| `declaration_bonus` | `int` | Defaults `0`. |
| `tier` | `str \| None` | Exposure tier. |
| `weapon_dice` | `str \| None` | Combat only. |
| `armour_dice` | `str \| None` | Combat only. |

## Reroll resource (new)

| Resource | `effective_pct` modifier | Cost mutation |
|---|---|---|
| `resolve` | `+20` | `resolve.current -1` |
| `fortune` | `0` (plain reroll) | `fortune.current -1` |
| `bargain` | `0` (plain reroll) | `taint +1` |

## Relationships

```text
propose_batch([request_0, request_1, ...], seed=...)
  -> shared _SeedCursor, shared scratch-state cache across all requests
  -> for each request: _stage_request(steps, request, state_cache, seed_cursor)
       -> resolves the top-level step (tagging it inputs=request), cascades under #236's rule
  -> one Proposal, all requests' steps concatenated

reroll(proposal_id, step, resource)
  -> find the named step; its inputs is the request that made it (error if None/missing)
  -> downstream = _downstream_set(steps, step)   # step itself + transitive dependents
  -> kept_steps = steps not in downstream
  -> scratch state: fresh load + replay every kept step's own mutations
  -> fresh _SeedCursor; _stage_request(new_steps=[], inputs, ..., declaration_bonus_delta=modifier)
  -> append the resource's own cost mutation to new_steps[0]
  -> _renumber_and_merge(kept_steps, new_steps, original step id)
       -> new_steps[0] keeps the original step id; any further new step gets a fresh id
  -> proposal["steps"], proposal["mutations"] updated in place; proposal stays open
```
