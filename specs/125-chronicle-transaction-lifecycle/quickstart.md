# Quickstart: Chronicle transaction lifecycle

Prerequisites: `PYTHONPATH=engine`, Python 3.11+, stdlib only.

## Resume a mid-beat interruption

```python
from wyrd import chronicle

pending = {"beat": "open-the-door", "awaiting": "the lock-picking roll", "rolled": None}
resumed = chronicle.resume_state(pending)
assert resumed == {"beat": "open-the-door", "awaiting": "the lock-picking roll"}

assert chronicle.resume_state(None) is None
assert chronicle.resume_state({"beat": None, "awaiting": None, "rolled": None}) is None
```

## Discard a proposal that survived to the next Rally

```python
from wyrd import chronicle, resolution

result = resolution.propose(actor="chars/senna.md", mechanic="exposure", skill="bargaining",
                             tier="moderate")
proposal_id = result["proposal_id"]

pending = {"beat": None, "awaiting": None, "rolled": proposal_id}
outcome = chronicle.discard_at_rally(pending)
if outcome["to_discard"]:
    resolution.discard(outcome["to_discard"])
new_pending = outcome["pending"]
assert new_pending["rolled"] is None
```

## Explicitly discard a moot in-session proposal

```python
outcome = chronicle.discard_moot(pending)
# same shape as discard_at_rally's outcome; caller discards `outcome["to_discard"]` if present
```

## At most one open proposal per actor

```python
pending = chronicle.record_rolled({"beat": None, "awaiting": None, "rolled": None}, "p-1")
try:
    chronicle.record_rolled(pending, "p-2")
    assert False, "expected ValueError: an open proposal already exists"
except ValueError:
    pass
```

## Verification

```bash
PYTHONPATH=engine python3 -m pytest tests/engine/test_chronicle.py -q
python3 -m ruff check .
python3 -m ruff format --check .
```
