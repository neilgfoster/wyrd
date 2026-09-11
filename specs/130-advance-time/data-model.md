# Data Model: Elapsed time and the advance-time command

## Function signatures (pure, no I/O) — `engine/wyrd/advance_time.py`

- `advance_calendar(calendar: dict, elapsed_days: int, days_per_year: int = 365) -> dict`
  Returns a new calendar dict with `day` advanced by `elapsed_days`, wrapping into `year` at the
  365-day boundary (FR-001, SC-001). `month` is passed through unchanged (spec.md's Assumptions).

- `expected_activation_count(imminence: int, elapsed_days: int, days_per_week: int = 7) -> int`
  `round(weeks * imminence / 10)`, `weeks = elapsed_days // days_per_week` (FR-002, SC-002).
  Pure arithmetic, no randomness.

- `advance_time(calendar: dict, threats: list[dict], elapsed_days: int, seed: int | None = None) -> dict`
  Returns `{"calendar": <advanced calendar>, "activations": [<one entry per threat>]}` (FR-003,
  FR-004). Each `threats` entry is a Threat entity dict (as `threat.active_threats` produces);
  each activations entry is `{"id": <threat id>, "activation_count": int, "effects": [<matched
  entry from threat.resolve_effects>, ...]}`, with exactly `activation_count` entries in
  `effects` (SC-004) -- `0` when the computed count is `0` (spec.md's Edge Cases).

  Internally: for each threat, in order, `expected_activation_count` gives the count; for each
  activation in that count, a table roll is drawn via `rules.roll_d100(seed=seed + offset)`
  (`offset` a running counter starting at `0`, incremented once per roll across the whole call --
  research.md) and resolved via `threat.resolve_effects`. When `seed` is `None`, rolls are drawn
  from the platform's default randomness (not reproducible), matching `rules.roll_d100`'s own
  convention.

## Example

```python
calendar = {"year": 1, "month": None, "day": 100}
threats = [{"id": "the-drowned-count", "threat": {"imminence": 4, "effects": {"1-5": "grows"}}}]

result = advance_time(calendar, threats, elapsed_days=21, seed=42)
# result["calendar"] == {"year": 1, "month": None, "day": 121}
# result["activations"] == [
#     {"id": "the-drowned-count", "activation_count": 1, "effects": [{"matched": "grows"} or {"matched": None}]}
# ]
```
