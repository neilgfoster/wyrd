# Quickstart: world_acts_offstage gates threat activation while the character is elsewhere

## Try it

```python
from wyrd import advance_time

calendar = {"year": 1, "month": None, "day": 0}
threats = [{"id": "the-drowned-count", "threat": {"imminence": 4, "effects": {"1-100": "grows"}}}]

# Default: activates normally.
result = advance_time.advance_time(calendar, threats, elapsed_days=35, seed=1)
assert result["activations"][0]["activation_count"] > 0

# Setting opts out, and this span was unwitnessed: suppressed.
suppressed = advance_time.advance_time(
    calendar, threats, elapsed_days=35, seed=1,
    world_acts_offstage=False, witnessed=False,
)
assert suppressed["activations"][0]["activation_count"] == 0
assert suppressed["activations"][0]["effects"] == []
assert suppressed["calendar"] == result["calendar"]  # calendar still advances
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_advance_time -v
```
