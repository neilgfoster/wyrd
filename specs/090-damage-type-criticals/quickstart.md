# Quickstart: Damage-type critical tables

## Prerequisites

- Repo checked out on branch `090-damage-type-criticals`.
- `python3 -m pytest -q` currently green on `main` before starting.

## Validate the engine's own tables against the already-validated model

```bash
python3 specs/090-damage-type-criticals/check_criticals_engine.py
```

Expected: `All checks pass.` — the engine's `CRITICAL_PIERCING_TABLE`,
`CRITICAL_BLUNT_TABLE`, `CRITICAL_SEARING_TABLE` (and the unchanged `CRITICAL_SLASHING_TABLE`)
match `specs/015-damage-type-criticals/check_criticals.py`'s own `TABLES` dict row-for-row.

## Validate resolution end-to-end (once implemented)

```python
from wyrd import resolution

# A piercing blow that lands and drops the target below 0 Stamina resolves against
# critical-piercing, not critical-slashing.
result = resolution.propose(
    actor="companions/bounty-hunter.md",
    mechanic="combat-attack",
    target="pc.md",
    skill="melee",
    weapon_dice="2d6",
    armour_dice="none",
    damage_type="piercing",
    seed=1,
)
critical_step = [s for s in result["steps"] if s["mechanic"] == "critical"][0]
assert critical_step["roll"]["table"] == "critical-piercing"
```

An unrecognized type fails loudly:

```python
try:
    resolution.propose(
        actor="a.md", mechanic="combat-attack", target="b.md", skill="melee",
        weapon_dice="1d6", armour_dice="none", damage_type="acid", seed=1,
    )
except ValueError as e:
    assert "acid" in str(e)
```

## Run the full suite

```bash
ruff check . && ruff format --check . && python3 -m pytest -q
```

Expected: all green, including the new cases in `tests/engine/test_resolution.py` and
`tests/engine/test_combat.py` covering each new table's boundaries, the mortal row, the
unrecognized-type load error, and the default-to-slashing behaviour for every existing caller.
