# Quickstart: Threads: open-loop tracking, heat and decay

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import thread

# Open a thread at chronicle creation, or from a scenario's own emit.
t = thread.new_thread(
    id="the-one-who-paid",
    opened={"year": 0, "month": None},
    summary="whoever funded it walked away, and you would know them again",
    hooks=["money", "influence", "the-thing-they-funded"],
)
assert t["heat"] == 0

# Selecting a scenario that consumes this thread's hooks touches it.
t = thread.touch(t)
assert t["heat"] == 1

# A year passes with nobody following up.
t = thread.decay(t, elapsed_days=365)
assert t["heat"] == 0

# Another year passes, still untouched: it closes.
t = thread.decay(t, elapsed_days=365)
assert t["status"] == "closed"
assert t["close_reason"] == "never resolved"
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_thread -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_thread.py`, including the heat cap at 5, the whole-year decay stepping, and
close-on-floor behaviour.
