# Data Model: Scenario selection by thread heat and hooks

## Candidate scenario (caller-supplied, minimal shape this feature reads)

| Field | Type | Notes |
|---|---|---|
| `hooks` | `list[str]` | matched against live threads' own `hooks`. |
| `written_for` | `int` | the party size the scenario was written for. |
| `encounters` | `list[dict]` | each with at least `written_count: int`; scaled in place by `scale_encounters`. |

## Function signatures (pure, no I/O) — `engine/wyrd/scenario_selection.py`

- `rank_by_heat(threads: list[dict]) -> list[dict]`
  Returns `threads` sorted by `heat` descending, stable on ties (FR-001) — Python's `sorted` is
  already stable, so equal-heat threads keep their input order.

- `select_scenario(threads: list[dict], candidates: list[dict]) -> dict | None`
  For each candidate, in order, sums the `heat` of every thread in `threads` whose `hooks` share
  at least one entry with the candidate's own `hooks` (FR-002); returns the candidate with the
  highest sum, ties broken by earliest position (FR-003). Returns `None` when every candidate's
  sum is `0`, or when `threads`/`candidates` is empty (FR-004).

- `scale_encounters(scenario: dict, danger: int, party: int) -> dict`
  Returns a new scenario dict whose `encounters` list has each entry's `written_count` replaced
  by `adversary.scaled_count(written_count, danger, party, scenario["written_for"])` under a new
  `scaled_count` key, `written_count` itself left untouched for reference (FR-005). Every other
  field of `scenario` and of each encounter is unchanged.

- `record_source(scenario: dict, adapted_from: str, changed: str) -> dict`
  Returns a new scenario dict with `source: {"adapted_from": adapted_from, "changed": changed}`
  attached, every other field unchanged (FR-006).

## Example

```python
threads = [
    {"id": "the-one-who-paid", "hooks": ["money", "influence"], "heat": 4},
    {"id": "an-old-debt", "hooks": ["debt"], "heat": 1},
]
candidates = [
    {"id": "the-corrupt-official", "hooks": ["money", "corruption"], "written_for": 4,
     "encounters": [{"written_count": 4}]},
    {"id": "the-unrelated-heist", "hooks": ["heist"], "written_for": 4, "encounters": []},
]

selected = select_scenario(threads, candidates)
# selected["id"] == "the-corrupt-official"  -- matches "money" (heat 4) vs. no match at all

scaled = scale_encounters(selected, danger=4, party=6)
# scaled["encounters"][0]["scaled_count"] == adversary.scaled_count(4, 4, 6, 4)

final = record_source(scaled, adapted_from="a fanzine six-pager", changed="renamed the official")
# final["source"] == {"adapted_from": "a fanzine six-pager", "changed": "renamed the official"}
```
