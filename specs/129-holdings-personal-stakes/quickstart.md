# Quickstart: Holdings: accumulated stakes

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import holding, threat

entities = [
    {"id": "the-drowned-mill", "type": "place", "threat": {"imminence": 4, "effects": {}}},
    {"id": "quiet-hollow", "type": "place", "threat": {"imminence": 2, "effects": {}}},
]

active = threat.active_threats(entities)
character_holdings = ["the-drowned-mill"]  # from economy.gain_holding, elsewhere

flagged = holding.flag_personal_stakes(active, character_holdings)
assert flagged[0]["personal"] is True   # the mill -- the character's own
assert flagged[1]["personal"] is False  # not held
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_holding -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_holding.py`, including the no-`id` and empty-`holdings` edge cases.
