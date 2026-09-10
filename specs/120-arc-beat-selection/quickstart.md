# Quickstart: Beat/arc entry and exit conditions, and thread-matched selection

## Prerequisites

- Python 3.11+, stdlib only.
- From repo root: `PYTHONPATH=engine python3 -c "..."` or via the test suite below.

## Validate an entry/exit block

```python
from wyrd import arc_selection

beat = {
    "id": "the-cut-page", "type": "beat", "name": "The cut page",
    "setting": "example", "status": "drafted",
    "entry": {"requires_threads": ["records"], "requires_state": [], "hooks": ["the player asks about the ledger"]},
    "exit": {"emits_threads": [{"tag": "the-hinge", "if": "the player character recalls the door"}],
             "changes": ["the gap is public knowledge"], "leads_to": "[[the-tavern]]"},
}
result = arc_selection.validate_entry_exit(beat)
assert result["valid"]
```

## Select the next beat by live threads

```python
candidates = [beat, other_beat, stub_arc]
selected = arc_selection.select(live_threads={"records"}, candidates=candidates)
# -> [beat]  (its requires_threads is a subset of {"records"})
```

## `leads_to` fallback

```python
selected = arc_selection.select(live_threads=set(), candidates=[other_beat], current=beat)
# no thread match against other_beat -> falls back to beat's exit.leads_to ("the-tavern"),
# resolved against `candidates` if present there, else [] per FR-008.
```

## Run the tests

```bash
PYTHONPATH=engine python3 -m unittest tests.engine.test_arc_selection -v
```

Expected: all four user stories' acceptance scenarios pass (schema validation, thread-match
selection, leads_to fallback ordering, stub selectability at any nesting level).
