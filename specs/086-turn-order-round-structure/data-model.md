# Phase 1 Data Model: Turn order and round structure

## Combat scene (persisted, chronicle-state key `combat`)

| Field | Type | Notes |
|---|---|---|
| `sides` | `dict[str, dict]` | Side name -> `{"armed": bool, "surprised": bool, "ambush": bool}`. |
| `round` | `int` | Starts at `1`; incremented by `advance_round`. |
| `first_actor` | `str` | Computed once, at `start_combat`, per `determine_first_actor`. |

## Functions

| Function | Signature | Notes |
|---|---|---|
| `determine_first_actor` | `(started_by: str \| None, armed: dict[str, bool], player_side: str) -> str` | Pure; no persisted state. |
| `start_combat` | `(sides: dict[str, dict], started_by: str \| None, player_side: str, *, state_path=...) -> dict` | Validates `started_by`/`player_side` name real sides; computes `first_actor`; writes the `combat` key; returns the scene. |
| `advance_round` | `(*, state_path=...) -> dict` | Increments `round`; returns the updated scene. |
| `can_act` | `(side: str, *, state_path=...) -> bool` | `False` only if `sides[side]["surprised"]` and `round == 1`. |
| `attack_modifier` | `(side: str, *, state_path=...) -> int` | `20` only if `sides[side]["ambush"]` and `round == 1`, else `0`. |

## Relationships

```text
start_combat(sides={"party": {"armed": True}, "opp": {"armed": False, "surprised": True}},
             started_by=None, player_side="party")
  -> first_actor = determine_first_actor(None, {"party": True, "opp": False}, "party") = "party"
  -> writes {"combat": {"sides": {...}, "round": 1, "first_actor": "party"}} to chronicle state

can_act("opp")          -> False (surprised, round 1)
advance_round()          -> round becomes 2
can_act("opp")          -> True (round no longer 1)
```
