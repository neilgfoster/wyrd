# Data Model: Eras: named periods and boundary recording

## `chronicle.yaml` schema additions (`state.py`)

| Field | Type | Default | Notes |
|---|---|---|---|
| `eras` | `list[dict]` | `[]` | declared in advance; each entry `{id: str, name: str, ambient: str}`. |
| `era_crossings` | `list[dict]` | `[]` | append-only; each entry `{from: str \| None, to: str, at: dict}`, mirroring `migrations`'s existing immutability convention. |
| `era` | `str \| None` | `None` | already existing; this feature is what gives it real read/write semantics via `cross_era`'s returned pointer. |

Both new fields are filled by `validate_chronicle` the same way `migrations`/`intent` already
are (`result.setdefault(...)` / list coercion) — no new required field, fully backward compatible
with a chronicle written before this feature landed.

## Function signatures (pure, no I/O) — `engine/wyrd/era.py`

- `ambient_register(eras: list[dict], era: str | None) -> str | None`
  Returns the `ambient` field of the entry in `eras` whose `id == era` (FR-001). Returns `None`
  when `era` is `None` or when no entry matches (FR-002) — never raises.

- `cross_era(eras: list[dict], era: str | None, to: str, at: dict) -> dict`
  Returns `{"era": to, "crossing": {"from": era, "to": to, "at": at}}` (FR-003). Raises
  `ValueError` if `to` is not present in `eras` (FR-004), or if `to == era` (FR-005) — a crossing
  is always a real move to a different, already-declared era. The caller appends the returned
  `crossing` to `era_crossings` and sets `era` to the returned pointer (FR-006, append-only —
  this function never mutates or removes an existing entry, it only ever proposes one new one).

## State transitions

```
era: null, eras: [{id: "the-long-thaw", ...}, ...], era_crossings: []
  --cross_era(to="the-long-thaw")--> era: "the-long-thaw"
                                      era_crossings: [{from: null, to: "the-long-thaw", at: ...}]
  --cross_era(to="the-long-thaw")--> ValueError (no-op target)
  --cross_era(to="undeclared-id")--> ValueError (not in eras)
  --cross_era(to="the-second-era")--> era: "the-second-era"
                                       era_crossings: [..., {from: "the-long-thaw", to: "the-second-era", at: ...}]
```
