# Quickstart: Every seeded Threat carries a personal connection

## Try it

```python
from wyrd import threat

threats = [
    {"id": "the-drowned-count", "threat": {"connection": "he drowned your brother"}},
    {"id": "an-empty-scenery-threat", "threat": {"connection": ""}},
]
problems = threat.validate_connections(threats)
assert len(problems) == 1
assert "an-empty-scenery-threat" in problems[0]
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_threat -v
```
