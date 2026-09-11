# Data Model: Chronicle intent's lethality is validated against the mortality vocabulary

## `state.py` change

```python
_LETHALITY_LEVELS = frozenset({"low", "standard", "high"})
```

`validate_chronicle` (existing function): after filling `intent` from `_INTENT_DEFAULTS`, add:

```python
if result["intent"]["lethality"] not in _LETHALITY_LEVELS:
    raise StateError(
        f"intent.lethality {result['intent']['lethality']!r} is not one of "
        f"{sorted(_LETHALITY_LEVELS)}"
    )
```
