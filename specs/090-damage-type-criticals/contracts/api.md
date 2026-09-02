# Contract: `resolution.py`'s `combat-attack` request, plus its callers

```python
def propose(
    *, actor, mechanic, skill=None, target=None, difficulty="average", declaration_bonus=0,
    tier=None, weapon_dice=None, armour_dice=None, damage_type=None, seed=None,
) -> dict: ...

def propose_batch(requests: list[dict], *, seed=None) -> dict: ...
    """Each request dict may now carry `damage_type` (str), same optionality as `weapon_dice`/
    `armour_dice`. Unset or `None` defaults to `"slashing"` — every existing caller/test is
    unaffected."""
```

**New**: `damage_type` — one of `"slashing"`, `"piercing"`, `"blunt"`, `"searing"`. Any other
non-`None` string raises `ValueError` naming the unrecognized type, raised at the point a critical
is staged (same timing as every other request-shape `ValueError` in this module — `propose`
itself does not eagerly validate it before the attack roll, since the attack may miss and never
reach a critical at all).

## `combat.py` (unchanged signatures except one new optional kwarg each)

```python
def crowd_attack(
    crowd, target, skill, weapon_dice, armour_dice, *, damage_type=None, seed=None, state_path=...,
) -> dict: ...

def crowd_parting_blow(
    crowd, actor, skill, weapon_dice, armour_dice, *, damage_type=None, seed=None, state_path=...,
) -> dict: ...

def resolve_ranged_attack(
    shooter, target, skill, weapon_dice, armour_dice, *, damage_type=None, seed=None,
    state_path=...,
) -> dict: ...
```

Each forwards `damage_type` unchanged to the `combat-attack` request it builds. Omitting it
preserves today's slashing-only behaviour exactly.

## `verbs.py` / `client.py` (CLI)

`verbs.py`'s combat-attack-facing function gains the same optional `damage_type` kwarg, forwarded
straight through. `client.py`'s CLI parser gains `--damage-type {slashing,piercing,blunt,searing}`
(optional, no default flag value — omission means `None`, which resolves to `slashing` inside
`resolution.py`, not a CLI-level default, so the single source of truth for the default stays in
one place).

## `catalog.py` (MCP tool schema)

`propose`'s `inputSchema.properties` gains:

```json
"damage_type": {"type": "string", "enum": ["slashing", "piercing", "blunt", "searing"]}
```

Not added to `required` — omission is valid and defaults to `slashing`.
