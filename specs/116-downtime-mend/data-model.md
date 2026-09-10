# Phase 1 data model: Downtime phase, including Mend

All entities below are plain `dict`s, matching every sibling module (`rally.py`, `session.py`,
`advancement.py`, `economy.py`). No new persisted schema field is introduced; Mend adds no field
beyond `closed`, which `character.py`/ADR 0021 already define.

## Downtime state

Analogous to `session.new_loop_state()`/`advance_loop`, scoped to one Downtime period.

```python
{
    "step": "destination",        # one of DOWNTIME_STEPS
    "undertaking": None,          # str | None -- set once, by "undertaking" step
    "undertaking_chosen": False,  # guards the exactly-one gate
}
```

`DOWNTIME_STEPS = ("destination", "upkeep", "advances", "undertaking", "rest")` — a strictly
linear sequence (no self-loop, unlike `session.py`'s `beat` step).

**Transitions**: `advance_downtime(state, to_step, *, undertaking=None)` enforces
`destination -> upkeep -> advances -> undertaking -> rest`, raises `ValueError` on any other
target. Moving to `"undertaking"` requires `undertaking` to be one of the fixed vocabulary below,
and raises if `undertaking_chosen` is already `True` (FR-005's exactly-one gate).

## Undertaking vocabulary

```python
UNDERTAKINGS = ("recover", "mend", "pursue", "cultivate", "learn", "ask")
```

A closed vocabulary, matching `advancement.TRIGGERS`'s own convention — a setting cannot add a
seventh undertaking any more than it can add a fifth advance trigger.

## Upkeep result

```python
{
    "standing": <int>,   # unchanged if at home; else per the trade chosen
    "coin": <int>,       # unchanged if at home or Standing-loss trade chosen
    "trade": "none" | "standing" | "coin",
}
```

`apply_upkeep(destination, standing, coin, *, trade=None)`:
- `destination == "home"`: `trade` must be `None` (or is ignored); returns unchanged
  `{"standing": standing, "coin": coin, "trade": "none"}`.
- `destination != "home"`: `trade` must be `"standing"` or `"coin"` — anything else (including
  `None`) is rejected (FR-002's "neither" case). `"standing"` returns `standing - 1`, coin
  unchanged. `"coin"` returns `coin - standing` (rejected if `coin < standing`, per the spec's
  Edge Cases), standing unchanged.

## Wound record (unchanged — read from `character.py`)

```python
{
    "id": "the-knee-that-never-set",
    "effect": {"skill": -10},   # or {"stamina_max": -1} or {"dread": 1}
    "bears_on": "...",          # required iff effect has "skill"
    "recurring": False,
    "closed": None,             # or a beat/date marker once closed
}
```

Mend reads and, where legal, mutates only `effect` and `closed` on one record; `id`, `bears_on`,
`recurring`, and any narrative fields (origin/description text held in the entity body, not this
dict) are untouched.

## Mend result

```python
{
    "success": True,
    "wounds": [...],   # full new wounds list, target record updated
    "closed": False,   # True iff this Mend closed the wound
}
```

or, on rejection:

```python
{
    "success": False,
    "reason": "unknown_wound" | "recurring" | "already_closed",
    "wounds": [...],   # unchanged
}
```

`apply_mend(wound_id, wounds)`:
1. Look up `wound_id` in `wounds`; `reason: "unknown_wound"` if absent.
2. `reason: "recurring"` if `wound["recurring"]` is `True`.
3. `reason: "already_closed"` if `wound["closed"] is not None`.
4. Otherwise, step the wound's `effect` one rung per the fixed ladder
   (`MEND_LADDER`, from research.md's Decision) and return the new list with that one record
   replaced — either its `effect` value stepped down, or, if the current rung is the last one,
   `effect` cleared to `{}` and `closed` set to a caller-supplied marker (e.g. current beat id or
   timestamp), matching ADR 0021's "closed, not deleted."

## Rest

```python
def apply_rest(stamina_max: int) -> int:
    return stamina_max
```

Matches `rally.apply_recovery`'s existing "cap at `stamina_max`" convention, but unconditional —
Rest sets Stamina to the maximum outright rather than incrementing it.

## Calendar-advance fact

```python
{"calendar_advanced": True}
```

Returned by the "rest"/close step of `advance_downtime`, or by a dedicated
`close_downtime(state) -> dict` — exposing the fact without this module computing or storing an
actual date (out of scope, per spec.md's Assumptions).
