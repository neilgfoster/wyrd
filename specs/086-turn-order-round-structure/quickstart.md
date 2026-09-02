# Quickstart: Turn order and round structure

```python
from wyrd import combat

scene = combat.start_combat(
    sides={"party": {"armed": True}, "opposition": {"armed": False, "surprised": True}},
    started_by=None, player_side="party", state_path=path,
)
assert scene["first_actor"] == "party"
assert combat.can_act("opposition", state_path=path) is False
combat.advance_round(state_path=path)
assert combat.can_act("opposition", state_path=path) is True
```

## Run the tests

```bash
python3 -m pytest tests/engine/test_combat.py -q
ruff check engine/wyrd/combat.py
ruff format --check engine/wyrd/combat.py
```
