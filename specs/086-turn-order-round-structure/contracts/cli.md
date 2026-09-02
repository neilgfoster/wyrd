# Contract: library API (no CLI subcommand this feature — plan.md's Structure Decision)

```python
def determine_first_actor(
    started_by: str | None, armed: dict[str, bool], player_side: str
) -> str: ...

def start_combat(
    sides: dict[str, dict], started_by: str | None, player_side: str,
    *, state_path: pathlib.Path = ...,
) -> dict:
    """sides: {"<name>": {"armed": bool, "surprised": bool (default False),
    "ambush": bool (default False)}}. Raises ValueError if started_by/player_side names a side
    not in `sides`."""

def advance_round(*, state_path: pathlib.Path = ...) -> dict: ...
def can_act(side: str, *, state_path: pathlib.Path = ...) -> bool: ...
def attack_modifier(side: str, *, state_path: pathlib.Path = ...) -> int: ...
```
