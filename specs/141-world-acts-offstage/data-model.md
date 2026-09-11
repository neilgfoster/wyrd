# Data Model: world_acts_offstage gates threat activation while the character is elsewhere

## `advance_time.advance_time` signature change

```python
def advance_time(
    calendar: dict,
    threats: list[dict],
    elapsed_days: int,
    seed: int | None = None,
    *,
    world_acts_offstage: bool = True,
    witnessed: bool = True,
) -> dict:
```

Logic: `suppressed = not world_acts_offstage and not witnessed`. When `suppressed`, each
threat's activation entry is `{"id": entity.get("id"), "activation_count": 0, "effects": []}` —
no call to `expected_activation_count`/`rules.roll_d100`/`threat.resolve_effects`, and the
running `offset` counter is left untouched (FR-005). `advance_calendar` is called exactly as
before, unaffected by `suppressed` (FR-003).
