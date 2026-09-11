# Quickstart: Threats aspect & activation

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import threat

entities = [
    {"id": "the-drowned-count", "type": "character", "threat": {"imminence": 4, "effects": {"1": "grows stronger", "3-6": "spreads"}}},
    {"id": "quiet-village", "type": "place", "threat": {"imminence": 0, "effects": {}}},
    {"id": "ordinary-npc", "type": "character"},
]

# Active set: only the live Threat.
active = threat.active_threats(entities)
assert [e["id"] for e in active] == ["the-drowned-count"]

# Activation: caller supplies the roll.
assert threat.check_activation(imminence=4, wyrd_roll=40) is True
assert threat.check_activation(imminence=4, wyrd_roll=41) is False

# Effects lookup on activation.
result = threat.resolve_effects({"1": "grows stronger", "3-6": "spreads"}, table_roll=5)
assert result == {"matched": "spreads"}

# Promotion: an existing entity gains a threat block.
companion = {"id": "left-for-dead", "type": "character", "role": "companion"}
nemesis = threat.promote(companion, {"imminence": 3, "effects": {}}, objective="hunts the player")
assert nemesis["threat"]["imminence"] == 3
assert nemesis["objective"] == "hunts the player"
assert nemesis["role"] == "companion"  # untouched
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m pytest tests/engine/test_threat.py -q
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_threat.py`, including the exact activation boundary (SC-002) and the empty/unmatched
effects-table edge cases.
