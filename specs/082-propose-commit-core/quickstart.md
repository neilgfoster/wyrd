# Quickstart: Propose/commit/discard core

## Prerequisites

- Python 3.11+, repo checked out, no extra dependencies (`engine/wyrd/` is stdlib-only).
- A character entity file loadable via `engine/wyrd/character.py`/`state.py`, with a `taint`
  field and the skill named in the `propose` call.

## Reproduce the design document's worked example

`docs/design/31-action-resolution.md` § "A worked example": Senna Vask, `bargaining: 40`, a
moderate (2) Exposure source, seed `20260852`.

```python
from wyrd import resolution

result = resolution.propose(
    actor="senna", mechanic="exposure", skill="bargaining",
    tier="moderate", seed=20260852,
)
assert result["roll"]["roll"] == 77
assert result["roll"]["effective_pct"] == 40
assert result["roll"]["outcome"] == "fail"
assert result["mutations"] == [{"entity": "senna", "field": "taint", "op": "+", "value": 2}]

# State unchanged so far:
before = character.load(senna_path)

resolution.commit(result["proposal_id"])
after = character.load(senna_path)
assert after[0]["taint"] == before[0]["taint"] + 2
```

## Run the tests

```bash
python3 -m pytest tests/engine/test_resolution.py -q
ruff check engine/wyrd/resolution.py
ruff format --check engine/wyrd/resolution.py
```

## Try the CLI

```bash
wyrd propose --actor senna --mechanic exposure --skill bargaining --tier moderate
# -> {"proposal_id": "p-...", "roll": {...}, "mutations": [...]}
wyrd commit p-...
wyrd discard p-...   # error: already resolved
```
