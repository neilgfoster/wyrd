# Quickstart: Scenario selection by thread heat and hooks

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import scenario_selection as sel

threads = [
    {"id": "the-one-who-paid", "hooks": ["money", "influence"], "heat": 4},
    {"id": "an-old-debt", "hooks": ["debt"], "heat": 1},
]
candidates = [
    {"id": "the-corrupt-official", "hooks": ["money", "corruption"], "written_for": 4,
     "encounters": [{"written_count": 4}]},
    {"id": "the-unrelated-heist", "hooks": ["heist"], "written_for": 4, "encounters": []},
]

ranked = sel.rank_by_heat(threads)
assert [t["id"] for t in ranked] == ["the-one-who-paid", "an-old-debt"]

selected = sel.select_scenario(threads, candidates)
assert selected["id"] == "the-corrupt-official"

scaled = sel.scale_encounters(selected, danger=4, party=6)
final = sel.record_source(scaled, adapted_from="a fanzine six-pager", changed="renamed the official")
assert final["source"]["adapted_from"] == "a fanzine six-pager"
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_scenario_selection -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_scenario_selection.py`, including the deterministic tie-break and the
no-match-at-all `None` result.
