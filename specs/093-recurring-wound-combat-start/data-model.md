# Data Model: The recurring wound's combat-start effect

No new persisted entity type. This feature adds one field to the existing combat scene dict
(`combat.py`'s `scene`, already persisted under chronicle state's `combat` key) and reads, without
modifying, the existing wound record shape.

## Existing shapes read (unchanged)

**Wound record** (docs/design/22-state.md, `character.py`'s `WOUND_EFFECT_KEYS`/`validate_wound`):

```json
{
  "id": "w3",
  "recurring": true,
  "effect": {"skill": -10},
  "bears_on": "close-combat",
  "closed": null
}
```

A recurring wound always has `closed: null` (`validate_wound` rejects `recurring: true` with
`closed` set), `effect: {"skill": <int>}`, and `bears_on: <skill name>`.

## New/changed shape: combat scene penalties

`combat.py`'s `scene` dict (`start_combat`'s return value / the `combat` state key) gains one new
field:

```json
{
  "sides": {"...": "..."},
  "round": 1,
  "first_actor": "party",
  "engaged": [],
  "acted": [],
  "wound_penalties": {
    "<combatant>": {"<skill>": -20}
  }
}
```

- **`wound_penalties`**: `{combatant_name: {skill_name: total_penalty}}`. Present for every
  combatant supplied to `start_combat` that carries at least one active recurring wound bearing
  on a skill; a combatant with none is simply absent from the outer dict (not present with an
  empty inner dict), matching `active_wound_effects`'s own "skip it" convention for inactive
  effects.
- **`total_penalty`**: the sum of `CHALLENGING_MODIFIER` once per active recurring wound the
  combatant carries that bears on that skill (FR-004's stacking rule). Always a negative multiple
  of the Challenging modifier (e.g. two stacked wounds on the same skill → `-20`).
- Computed once, at `start_combat`, from the wound data the caller supplies for that combatant
  (research.md's "caller supplies wound data" decision) -- never recomputed by `advance_round` or
  any other later call, and never written back onto a character's stored skill value (spec.md
  Assumptions).

## Validation rules

- A combatant name key in `wound_penalties` MUST also be a key in `sides` (the same combatants
  `start_combat` already validates).
- Every value in the innermost `{skill: penalty}` dict MUST be a negative integer that is an
  integer multiple of `CHALLENGING_MODIFIER` (i.e. `-10`, `-20`, `-30`, ... for 1, 2, 3, ...
  stacked recurring wounds on that skill) -- never a distinct hand-set literal.

## State transitions

None beyond what `start_combat` already does: `wound_penalties` is set once when the scene is
created and is never mutated by `advance_round` or any other existing combat function. It does
not persist past the combat scene's own lifetime (spec.md FR-007) because it lives inside the
`combat` state key, which -- per existing `combat.py` behavior -- represents only the
currently-active scene.
