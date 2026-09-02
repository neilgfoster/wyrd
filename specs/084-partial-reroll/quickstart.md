# Quickstart: Partial reroll

## Reproduce the independent-branch worked example (research.md)

```python
from wyrd import resolution

result = resolution.propose_batch(
    [
        {"actor": senna_path, "mechanic": "exposure", "skill": "bargaining", "tier": "minor"},
        {"actor": senna_path, "mechanic": "exposure", "skill": "stealth", "tier": "minor"},
    ],
    seed=20260854,
)
pid = result["proposal_id"]
revised = resolution.reroll(pid, step=0, resource="bargain", seed=5)
# revised["steps"][1] (or wherever step 1 sits) is byte-for-byte the original step 1.
resolution.commit(pid)
```

## Run the tests

```bash
python3 -m pytest tests/engine/test_resolution.py -q
ruff check engine/wyrd/resolution.py
ruff format --check engine/wyrd/resolution.py
```
