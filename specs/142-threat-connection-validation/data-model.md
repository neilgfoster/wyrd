# Data Model: Every seeded Threat carries a personal connection

## `threat.py` addition

- `validate_connections(threats: list[dict]) -> list[str]`
  For each entity in `threats`: if `entity.get("threat", {}).get("connection")` is `None`,
  absent, or (after `.strip()`) empty, append a problem string naming
  `entity.get("id", entity)` (FR-001, FR-002, FR-004). Returns `[]` for an all-passing or empty
  input (FR-003). Never raises.

## Example

```python
threats = [
    {"id": "the-drowned-count", "threat": {"connection": "he drowned your brother"}},
    {"id": "an-empty-scenery-threat", "threat": {"connection": ""}},
    {"id": "no-connection-field", "threat": {}},
]
validate_connections(threats)
# -> ["an-empty-scenery-threat: threat has no connection", "no-connection-field: threat has no connection"]
```
