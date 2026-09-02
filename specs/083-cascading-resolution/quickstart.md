# Quickstart: Cascading resolution

## Reproduce the combat chain (research.md)

```python
from wyrd import resolution

result = resolution.propose(
    actor=attacker_path, mechanic="combat-attack", skill="swordplay", target=target_path,
    weapon_dice="1d8", armour_dice="1d3", seed=2,
)
assert result["steps"][0]["roll"]["degrees"] == 6          # telling
assert result["steps"][-1]["mechanic"] == "critical"
resolution.commit(result["proposal_id"])
```

## Reproduce the Taint-into-Transformation chain

```python
result = resolution.propose(
    actor=character_path, mechanic="exposure", skill="bargaining", tier="major", seed=5,
)
assert result["steps"][1]["mechanic"] == "transformation"
resolution.commit(result["proposal_id"])
```

## Run the tests

```bash
python3 -m pytest tests/engine/test_resolution.py -q
ruff check engine/wyrd/resolution.py
ruff format --check engine/wyrd/resolution.py
```
