# Data Model: Damage-type critical tables

No persisted state schema changes. This feature adds one new in-memory request field and three
new module-level table constants; the wound-record shape it writes into (`character.py`'s
`wounds` list) is already fully defined and unchanged.

## `combat-attack` request (in-memory, `resolution.py`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `damage_type` | `str` | No, defaults to `"slashing"` | One of `slashing`, `piercing`, `blunt`, `searing`. Any other value raises `ValueError` at resolution time. New field — every other field on this request is unchanged. |

## Critical table constant (module-level, `resolution.py`)

Mirrors `CRITICAL_SLASHING_TABLE`'s existing shape exactly — a list of
`(low, high_or_None, key, effect_or_None)` tuples, one per row, the open-ended top row carrying
`high=None` and its own row handled by the existing mortal branch (no `effect` entry, since
`mortal` isn't staged as a wound-record mutation).

```python
CRITICAL_PIERCING_TABLE = [
    (2, 4, "piercing-grazed", None),
    (5, 8, "piercing-punctured", {"skill": -5}),
    (9, 12, "piercing-transfixed", {"stamina_max": -1}),
    (13, 15, "piercing-organ", {"stamina_max": -1, "skill": -5}),
    (16, 18, "piercing-collapsed", {"stamina_max": -2}),
]
# 19+ -> "piercing-mortal", handled by the existing mortal branch, same as slashing's 21+.
```

`CRITICAL_BLUNT_TABLE` and `CRITICAL_SEARING_TABLE` follow the same shape, with their own rows
from `docs/design/05-criticals.md`.

## Wound record (`character.py`, unchanged)

No change. A non-mortal row still produces exactly the same shape
`_stage_critical` already stages for slashing:

```yaml
id: critical-<step_id>
effect: <the row's effect dict, copied>
bears_on: <the skill the blow used>   # only present when effect has "skill"
closed: null
```

## Entity relationships

No new entities. `damage_type` is a plain string carried on the request/step, not a persisted
field on any character or weapon entity.
