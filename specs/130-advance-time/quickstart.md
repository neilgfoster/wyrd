# Quickstart: Elapsed time and the advance-time command

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import advance_time

calendar = {"year": 1, "month": None, "day": 100}
threats = [
    {"id": "the-drowned-count", "threat": {"imminence": 4, "effects": {"1-10": "grows stronger"}}},
]

result = advance_time.advance_time(calendar, threats, elapsed_days=21, seed=42)

assert result["calendar"] == {"year": 1, "month": None, "day": 121}
assert result["activations"][0]["id"] == "the-drowned-count"
assert result["activations"][0]["activation_count"] == 1  # round(3 * 4 / 10) = round(1.2) = 1
assert len(result["activations"][0]["effects"]) == 1

# Same seed, same result -- deterministic.
again = advance_time.advance_time(calendar, threats, elapsed_days=21, seed=42)
assert again == result
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_advance_time -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_advance_time.py`, including the year-boundary wrap, the expected-value
formula's exact output at specific values, and seed reproducibility.
