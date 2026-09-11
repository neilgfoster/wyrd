# Data Model: Threads: open-loop tracking, heat and decay

## Thread record

`docs/design/19-campaign.md`'s schema, treated as a plain `dict` — no schema-validating class,
matching `threat.py`'s convention.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | `str` | yes | thread identifier. |
| `opened` | `dict` | yes | `{year, month}` — when the thread was opened. |
| `summary` | `str` | yes | one line describing the open loop. |
| `hooks` | `list[str]` | yes | matched against scenario hooks by selection (#339). |
| `heat` | `int` | yes | `0-5`. Defaults to `0` at creation if not supplied. |
| `status` | `"closed"` | only after closure | absent while the thread is open. |
| `close_reason` | `str` | only after closure | `"never resolved"` for this feature's decay path. |

## Function signatures (pure, no I/O)

- `new_thread(id: str, opened: dict, summary: str, hooks: list[str], heat: int = 0) -> dict`
  Returns a thread record with the given fields (FR-001, FR-002). Raises `ValueError` if `heat`
  is outside `0-5` (FR-003).

- `touch(thread: dict) -> dict`
  Returns a new dict with `heat` raised by one, capped at `5` (FR-004). Every other field is
  unchanged.

- `decay(thread: dict, elapsed_days: int, days_per_point: int = 365) -> dict`
  Returns a new dict reflecting `elapsed_days // days_per_point` whole years of decay (FR-005,
  FR-007). If the thread's `heat` is already `0` and at least one whole year has elapsed, returns
  the thread with `status: "closed"` and `close_reason: "never resolved"` instead of lowering
  `heat` further (FR-006). Otherwise lowers `heat` by the computed number of points, floored at
  `0`, and returns the thread unchanged if `elapsed_days < days_per_point`.

## State transitions

```
new_thread() -> {heat: 0-5}
  --touch()--> {heat: heat+1, capped at 5}
  --decay(elapsed >= 1 year, heat > 0)--> {heat: heat - years, floored at 0}
  --decay(elapsed >= 1 year, heat == 0)--> {status: "closed", close_reason: "never resolved"}
```

A closed thread has no further transition in this feature's scope (spec.md's Edge Cases).
