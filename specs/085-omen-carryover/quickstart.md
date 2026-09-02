# Quickstart: Omen carryover

## Reproduce the worked example (research.md)

```python
from wyrd import resolution

result = resolution.propose_batch(
    [
        {"actor": char_path, "mechanic": "ordinary-test", "skill": "alertness"},
        {"actor": char_path, "mechanic": "ordinary-test", "skill": "climbing"},
    ],
    seed=40,
)
assert result["steps"][0]["roll"]["wyrd_die"] == "fair_omen"
assert result["steps"][1]["roll"]["effective_pct"] == 55  # 45 + 10
assert result["steps"][1]["depends_on"] == [0]

revised = resolution.reroll(result["proposal_id"], step=0, resource="resolve", seed=1)
# step 1 in `revised` is a fresh result, not the original -- see it no longer depends_on step 0
# if the fresh roll produced no Omen.
resolution.commit(result["proposal_id"])
```

## Run the tests

```bash
python3 -m pytest tests/engine/test_resolution.py -q
ruff check engine/wyrd/resolution.py
ruff format --check engine/wyrd/resolution.py
```
