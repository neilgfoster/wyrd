# Quickstart: Entity file format engine support

## Prerequisites

```bash
export PYTHONPATH=engine
```

## Validate a minimal entity of each type

```python
from wyrd import entity

place = {
    "id": "the-old-quarter",
    "type": "place",
    "name": "The Old Quarter",
    "setting": "example-setting",
    "status": "stub",
    "scale": "district",
}
assert entity.validate(place) == {"valid": True}
```

## Reject a malformed entity

```python
missing_name = {"id": "x", "type": "place", "setting": "s", "status": "stub"}
result = entity.validate(missing_name)
assert result["valid"] is False
assert "name" in result["error"]

bad_type = {**place, "type": "nation"}
assert entity.validate(bad_type)["valid"] is False
```

## Resolve containment by reverse lookup

```python
entities = {
    "the-river-city": {"id": "the-river-city", "type": "place", "name": "The River City",
                        "setting": "s", "status": "stub"},
    "the-old-quarter": {**place, "parent": "[[the-river-city]]"},
}
assert entity.children_of("the-river-city", entities) == ["the-old-quarter"]
assert entity.check_containment(entities) == {"valid": True}
```

## Detect a containment cycle

```python
cyclic = {
    "a": {"id": "a", "type": "place", "name": "A", "setting": "s", "status": "stub",
          "parent": "[[b]]"},
    "b": {"id": "b", "type": "place", "name": "B", "setting": "s", "status": "stub",
          "parent": "[[a]]"},
}
result = entity.check_containment(cyclic)
assert result["valid"] is False
```

## Load a connection with a hidden edge

```python
harbour = {
    **place,
    "id": "the-harbour",
    "connections": [
        {"to": "[[the-old-quarter]]", "via": "the coast road"},
        {"to": "[[the-undercroft]]", "via": "a stair behind the shrine", "hidden": True},
    ],
}
assert entity.validate(harbour) == {"valid": True}
assert harbour["connections"][1]["hidden"] is True
```

## Verification

```bash
PYTHONPATH=engine python3 -m pytest tests/engine/test_entity.py -q
python3 -m ruff check .
python3 -m ruff format --check .
```

All checks must be clean before this feature is considered done, per spec.md's Success Criteria.
