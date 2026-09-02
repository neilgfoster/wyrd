# Quickstart: Adversary trait effects

## Prerequisites

Python 3.11+, stdlib only. Run from the repo root with `PYTHONPATH=engine`.

## Scenario 1: effective block folds in stacked traits

```python
from wyrd import adversary

block = {
    "id": "the-hunter", "name": "A named antagonist",
    "baseline": 35, "stamina_max": 7, "armour": "modest",
    "skills": {"blade": 55}, "damage": "1d6", "damage_type": "slashing",
    "ranged": False,
    "traits": [
        {"name": "Tough", "effect": {"stamina_max": 1}},
        {"name": "Tougher", "effect": {"stamina_max": 2}},
        {"name": "Heavy blows", "effect": {"damage": 1}},
        {"name": "Fire-touched", "effect": {"damage_type": "searing"}},
        {"name": "Lightly armoured", "effect": {"armour_rank": -1}},
    ],
}

effective = adversary.effective_block(block)
assert effective["stamina_max"] == 10       # 7 + 1 + 2
assert effective["damage"] == "2d6"          # one die added
assert effective["damage_type"] == "searing"
assert effective["armour"] == "light"        # one rank down from modest
```

## Scenario 2: difficulty ladder shift clamps at either end

```python
assert adversary.shift_difficulty("average", -1) == "challenging"
assert adversary.shift_difficulty("very_hard", -1) == "very_hard"  # clamped
assert adversary.shift_difficulty("easy", 1) == "easy"              # clamped
```

## Scenario 3: wyrd band widening

```python
from wyrd import rules

assert rules._wyrd_die(50) == "none"
assert rules._wyrd_die(51, omen_width=1) == "ill_omen"   # units digit 1, width 1
assert rules._wyrd_die(58, omen_width=1) == "fair_omen"  # units digit 8, width 1
assert rules._wyrd_die(51) == "none"                      # width 0 (default) -- unchanged
```

## Running the real tests

```bash
PYTHONPATH=engine python3 -m pytest tests/engine/test_adversary.py tests/engine/test_rules.py -q
```
