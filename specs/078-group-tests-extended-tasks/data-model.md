# Phase 1 data model: Group tests and extended tasks

No chronicle state. Two new composed shapes, both extending #222/#223's opposed-test result.

## Group test result

All fields from #222/#223's opposed-test result, plus:

| Field | Type | Description |
|---|---|---|
| `member_skills` | list[int \| null] | As supplied; `null` entries are untrained members |
| `mode` | string | `"most_capable"` or `"least_capable"` |
| `selected_skill` | int | The value actually tested (10 for a selected untrained member) |

Validation:
- `member_skills` MUST be non-empty (FR-004).
- `mode` MUST be one of the two closed values (FR-005).
- Exactly one call to `opposed_test` occurs regardless of `len(member_skills)` (SC-002).

## Extended task interval result

All fields from #222/#223's opposed-test result, plus:

| Field | Type | Description |
|---|---|---|
| `progress` | int | Updated progress (input `progress` + `gained`) |
| `target` | int | As supplied |
| `gained` | int | Degrees actually added this interval: `max(1, degrees)` on success, `1` on a `no_roll` automatic success, `0` on failure |
| `done` | bool | `progress >= target` |

Validation:
- `gained` is never negative and is `0` if and only if the interval failed (FR-007, FR-008).
- `done` is computed from the *updated* `progress`, not the input one (SC-005).
- Progress is not persisted by this function — the caller carries `progress`/`done` into the
  next interval's call if the task is not yet done.
