# Quickstart: Downtime phase, including Mend

Validates the feature end-to-end once implemented, mirroring the acceptance scenarios in
[spec.md](spec.md). Run from the repo root.

## Prerequisites

```bash
export PYTHONPATH=engine
```

## Run the unit tests

```bash
python3 -m unittest tests.engine.test_downtime -v
```

## Manual walkthrough — a full Downtime period spending Mend

```python
from wyrd import downtime

state = downtime.new_downtime_state()

state = downtime.advance_downtime(state, "destination")

# Upkeep, away from home, spending Standing:
standing, coin = 3, 10
upkeep = downtime.apply_upkeep("away", standing, coin, trade="standing")
assert upkeep == {"standing": 2, "coin": 10, "trade": "standing"}
state = downtime.advance_downtime(state, "upkeep")

state = downtime.advance_downtime(state, "advances")  # spend-advance calls go through
                                                        # career.py/advancement.py, unchanged

state = downtime.advance_downtime(state, "undertaking", undertaking="mend")
assert state["undertaking"] == "mend"

# A second undertaking selection in the same period is rejected:
try:
    downtime.advance_downtime(state, "undertaking", undertaking="recover")
    raise AssertionError("expected rejection")
except ValueError:
    pass

wounds = [{"id": "the-knee-that-never-set", "effect": {"skill": -10},
           "bears_on": "athletics", "recurring": False, "closed": None}]
result = downtime.apply_mend("the-knee-that-never-set", wounds)
assert result["success"] and result["wounds"][0]["effect"] == {"skill": -5}

state = downtime.advance_downtime(state, "rest")
stamina = downtime.apply_rest(stamina_max=8)
assert stamina == 8

fact = downtime.close_downtime(state)
assert fact["calendar_advanced"] is True
```

## Expected outcome

Every acceptance scenario in spec.md's User Story 1 and User Story 2 is satisfiable by the calls
above with the stated assertions — none require any not-yet-existing persistence layer.

## Regression check for published figures

If any change touches Mend's ladder or the wound-record shape:

```bash
python3 specs/014-stamina-recovery/check_recovery.py > /tmp/after.txt
git stash && python3 specs/014-stamina-recovery/check_recovery.py > /tmp/before.txt && git stash pop
diff /tmp/before.txt /tmp/after.txt   # expect no diff, per spec.md SC-004
```
