# Quickstart: Action economy and engagement

```python
from wyrd import combat

combat.start_combat(sides={"party": {"armed": True}}, started_by="party", player_side="party",
                     state_path=path)
combat.close(fighter, foe, state_path=path)
assert combat.has_acted(fighter, state_path=path)

result = combat.break_off(
    fighter, {str(foe): {"skill": "swordplay", "weapon_dice": "1d8", "armour_dice": "1d3"}},
    state_path=path,
)
# result["steps"] holds foe's own parting-blow combat-attack against fighter.

shot = combat.resolve_ranged_attack(
    archer, target, "archery", "1d8", "1d3", state_path=path,
)
```

## Run the tests

```bash
python3 -m pytest tests/engine/test_combat.py tests/engine/test_resolution.py -q
ruff check engine/wyrd/combat.py engine/wyrd/resolution.py
ruff format --check engine/wyrd/combat.py engine/wyrd/resolution.py
```
