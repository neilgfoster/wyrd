"""Threads: open loops that give a sequence of scenarios continuity (#335).

docs/design/19-campaign.md: a thread is an open loop -- a debt, an enemy who escaped, a promise,
a companion's unresolved arc. Every scenario consumes threads (it needs hooks that match live
ones) and emits new ones; selecting the next scenario means finding one whose hooks match threads
that are currently hot. `entity.py` already lists `"thread"` among its ten entity types; this
module is the heat/decay mechanic that type has not had a runtime implementation of yet.

Three pure functions, no I/O, matching `threat.py` (#334) and `journey.py`'s own division of
labour:

- `new_thread` -- creates a thread record at a validated starting heat (FR-001, FR-002, FR-003).
- `touch` -- raises heat by one when a scenario picks the thread back up, capped at the schema's
  own 0-5 bound (FR-004).
- `decay` -- lowers heat by one point per whole elapsed game-year, closing the thread ("never
  resolved") once decay is applied again while already at the floor (FR-005, FR-006, FR-007).

`decay` takes a caller-supplied elapsed-days span rather than reading a chronicle's calendar
itself, matching `threat.py`/`journey.py`'s convention of taking dice/spans as arguments instead
of doing date arithmetic internally -- the caller (`advance-time`, #338) already owns the
chronicle's calendar.

Python 3.11+, standard library only.
"""

from __future__ import annotations

_MIN_HEAT = 0
_MAX_HEAT = 5
_DEFAULT_DAYS_PER_POINT = 365


def new_thread(id: str, opened: dict, summary: str, hooks: list[str], heat: int = 0) -> dict:
    """Create a thread record (FR-001), defaulting to `heat: 0` (FR-002).

    Rejects (`ValueError`) a supplied `heat` outside the schema's `0-5` bound (FR-003).
    """
    if not (_MIN_HEAT <= heat <= _MAX_HEAT):
        raise ValueError(f"heat must be between {_MIN_HEAT} and {_MAX_HEAT}, got {heat!r}")
    return {"id": id, "opened": opened, "summary": summary, "hooks": hooks, "heat": heat}


def touch(thread: dict) -> dict:
    """Raise `thread`'s heat by one, capped at 5 (FR-004). Every other field is unchanged."""
    return {**thread, "heat": min(_MAX_HEAT, thread["heat"] + 1)}


def decay(thread: dict, elapsed_days: int, days_per_point: int = _DEFAULT_DAYS_PER_POINT) -> dict:
    """Decay `thread`'s heat by one point per whole elapsed game-year (FR-005, FR-007).

    A decay call covering less than one whole year is a no-op. A thread already at `heat: 0`
    that receives at least one whole elapsed year closes instead of going negative (FR-006),
    returned with `status: "closed"` and `close_reason: "never resolved"`.
    """
    years = elapsed_days // days_per_point
    if years <= 0:
        return dict(thread)
    if thread["heat"] <= _MIN_HEAT:
        return {**thread, "status": "closed", "close_reason": "never resolved"}
    return {**thread, "heat": max(_MIN_HEAT, thread["heat"] - years)}
