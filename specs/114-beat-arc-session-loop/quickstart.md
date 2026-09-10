# Quickstart: Beat/arc structure and the session loop

## Prerequisites

```bash
export PYTHONPATH=engine
```

## A beat is never a container

```python
from wyrd import entity, session

arc = {"id": "search-the-crypt", "type": "arc", "name": "Search the crypt",
       "setting": "example-setting", "status": "stub"}
beat = {"id": "open-the-door", "type": "beat", "name": "Open the door",
        "setting": "example-setting", "status": "stub", "parent": "[[search-the-crypt]]"}
entities = {arc["id"]: arc, beat["id"]: beat}

assert session.check_beat_has_no_children(entities) == {"valid": True}

# now give the beat a child of its own
illegal_child = {"id": "check-for-traps", "type": "beat", "name": "Check for traps",
                  "setting": "example-setting", "status": "stub", "parent": "[[open-the-door]]"}
entities[illegal_child["id"]] = illegal_child
result = session.check_beat_has_no_children(entities)
assert result["valid"] is False
assert result["beat"] == "open-the-door"
```

## The same beat narrated played in one chronicle, summarised in another

```python
played = session.narrate_beat("open-the-door", "played")
summarised = session.narrate_beat("open-the-door", "summarised")
assert played["mode"] == "played"
assert summarised["mode"] == "summarised"
assert played is not summarised  # independent records, no shared state
```

## The session loop enforces its own order

```python
loop_state = session.new_loop_state()
loop_state = session.advance_loop(loop_state, "orient")
loop_state = session.advance_loop(loop_state, "recap")   # only legal once orient has run
loop_state = session.advance_loop(loop_state, "beat", beat_id="open-the-door")
loop_state = session.advance_loop(loop_state, "close")
assert loop_state["beats_this_session"] == ["open-the-door"]

# skipping orient is rejected
fresh = session.new_loop_state()
try:
    session.advance_loop(fresh, "recap")
    assert False, "should have raised"
except ValueError:
    pass

# a session with zero beats can still close (FR-006)
empty = session.new_loop_state()
empty = session.advance_loop(empty, "orient")
empty = session.advance_loop(empty, "recap")
empty = session.advance_loop(empty, "close")

session.run_close([lambda: None])  # sequences caller-supplied compaction/recap/commit steps
```

## A stopped mid-beat session persists a pending marker and resumes exactly

```python
pending = session.set_pending("open-the-door", "waiting on the lock-picking roll")
assert session.resume_from_pending(pending) == "waiting on the lock-picking roll"

# once the beat resolves cleanly, the caller replaces its stored marker with this:
pending = session.clear_pending()
assert pending is None
```

## Session shape never leaks into narration

```python
shape = session.classify_shape(beats_this_session=["open-the-door"], used_dice=False,
                                ran_downtime=False)
assert shape in session.SESSION_SHAPES
# no narration-producing function in this module ever takes `shape` as an input
```

## Verification

```bash
PYTHONPATH=engine python3 -m unittest tests.engine.test_session -v
python3 -m ruff check .
python3 -m ruff format --check .
```

All checks must be clean before this feature is considered done, per spec.md's Success Criteria.
