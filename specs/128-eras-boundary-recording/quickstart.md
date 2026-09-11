# Quickstart: Eras: named periods and boundary recording

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import era

eras = [
    {"id": "the-long-thaw", "name": "The Long Thaw", "ambient": "hope returning, guardedly"},
    {"id": "the-second-winter", "name": "The Second Winter", "ambient": "the cold came back"},
]

# Before any crossing, era is null.
assert era.ambient_register(eras, None) is None

# Cross into the chronicle's first era.
result = era.cross_era(eras, None, to="the-long-thaw", at={"year": 1, "month": 3})
assert result == {
    "era": "the-long-thaw",
    "crossing": {"from": None, "to": "the-long-thaw", "at": {"year": 1, "month": 3}},
}

# Now the ambient register is queryable.
assert era.ambient_register(eras, "the-long-thaw") == "hope returning, guardedly"

# A later boundary.
result = era.cross_era(eras, "the-long-thaw", to="the-second-winter", at={"year": 4, "month": None})
assert result["era"] == "the-second-winter"
assert result["crossing"]["from"] == "the-long-thaw"
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_era tests.engine.test_state -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test,
including both rejection cases (undeclared target, no-op target) and the schema defaults added to
`state.py`.
