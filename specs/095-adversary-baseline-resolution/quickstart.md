# Quickstart: Adversary baseline skill resolution

## Prerequisites

Python 3.11+, stdlib only. Run from the repo root with `PYTHONPATH=engine`.

## Scenario: listed vs. unlisted skill

```python
from wyrd import adversary

block = {
    "id": "the-hunter", "name": "A named antagonist",
    "baseline": 35, "stamina_max": 7, "armour": "modest",
    "skills": {"blade": 55, "stealth": 20},
    "ranged": False,
}

assert adversary.resolve_skill(block, "blade") == 55       # listed -- its own value
assert adversary.resolve_skill(block, "stealth") == 20      # listed, below baseline -- unraised
assert adversary.resolve_skill(block, "tracking") == 35     # unlisted -- baseline
```

## Running the real tests

```bash
PYTHONPATH=engine python3 -m pytest tests/engine/test_adversary.py -q
```
