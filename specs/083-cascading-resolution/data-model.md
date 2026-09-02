# Phase 1 Data Model: Cascading resolution

## Step (extends #235's implicit single-step Proposal)

| Field | Type | Notes |
|---|---|---|
| `step_id` | `int` | 0-based, in resolution order. |
| `kind` | `str` | Always `"roll"` in this feature (matches `docs/design/31-action-resolution.md`'s own step shape; a non-roll `kind` is not needed by either worked example). |
| `mechanic` | `str` | e.g. `combat-attack`, `weapon-damage`, `armour`, `critical`, `transformation`, plus #235's `ordinary-test`/`exposure`. |
| `roll` | `dict` | The resolved roll data for this step. |
| `mutations` | `list[dict]` | This step's own staged mutations, each tagged `produced_by_step: step_id`. |
| `depends_on` | `list[int]` | `step_id`s this step was staged because of. |

## Proposal (extended)

| Field | Type | Notes |
|---|---|---|
| `proposal_id` | `str` | Unchanged from #235. |
| `steps` | `list[Step]` | New — the full cascade, in resolution order. |
| `roll` | `dict` | Unchanged in shape — `steps[0]["roll"]`, kept for #235 backward compatibility. |
| `mutations` | `list[dict]` | Unchanged in shape — the concatenation of every step's own `mutations`, in step order. |
| `open` | `bool` | Unchanged. |

`commit`/`discard` are unchanged: they still operate on `mutations` (now possibly drawn from
several steps) and `open`.

## Threshold rule (new, internal)

| Field | Type | Notes |
|---|---|---|
| `field` | `str` | The mutated field this rule watches (`taint`, and — only inside the combat chain's own combining step — `stamina.current`). |
| `crosses` | `Callable[[old, new], bool \| int]` | Given the field's value before and after one mutation, returns the crossed threshold value (or `None`/falsy if none crossed). |
| `stage` | `Callable[..., list[Step]]` | Given the crossing and the actor's current state, produces the further step(s) (recursively resolving them, including their own further crossings). |

Registered entries: `taint` → the Transformation cascade (FR-007/FR-008); `stamina.current` →
the critical roll (FR-005/FR-006), the latter wired only inside the combat chain's own
mutation-combining step (spec.md's Key Entities note: this one is not a general top-level
registry entry, since Stamina's mutation in this feature only ever arises from that specific
combining step, not from an arbitrary `propose` call naming a `stamina` mechanic).

## Relationships

```text
propose(actor, mechanic="combat-attack", target, weapon_dice, armour_dice, seed, ...)
  -> step 0: resolve combat-attack (opposed test against target)
     if landed:
       -> step 1 (depends_on [0]): weapon-damage, doubled if step 0 read telling (degrees >= 6)
       -> step 2 (depends_on [0]): armour
       -> combine: stamina mutation = max(1, step1.damage - step2.armour), produced_by_step: 2
       -> threshold-check(stamina.current, before, after):
            if crosses below 0:
              -> step 3 (depends_on [2]): critical (critical-slashing), wound-record mutation

propose(actor, mechanic="exposure", tier, seed, ...)
  -> step 0: resolve exposure
     mutation: taint += tier_value, produced_by_step: 0
     threshold-check(taint, before, after):
       if crosses a multiple of 3:
         -> step 1 (depends_on [0]): transformation
            mutations: taint -= severity, dread += severity, produced_by_step: 1
                       (+ hidden_threshold set, only on first Transformation)
            threshold-check(taint, ..., ...) again:
              if still >= the crossed threshold:
                -> step 2 (depends_on [1]): transformation (different table row)
                   ... repeats until taint clears the threshold
```
