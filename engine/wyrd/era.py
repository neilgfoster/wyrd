"""`chronicle.yaml`'s `era`/`eras`/`era_crossings` fields: real semantics (#336).

docs/design/19-campaign.md: a chronicle is divided into named eras, each with its own ambient
register -- declared in advance, and crossed explicitly, never inferred. docs/design/22-state.md
already reserved a bare `era: null` scalar; `state.py` now also carries `eras` (the
declared-in-advance list, default `[]`) and `era_crossings` (an append-only log of boundary
crossings, default `[]`, mirroring `migrations`'s own immutability convention).

This module owns the semantics of those fields as pure functions with no I/O, matching
`chronicle.py`'s (#328) division of labour: a caller (session/arc-boundary logic, out of scope
here) decides *when* to cross and is responsible for persisting the returned `era` pointer and
appending the returned crossing record via `wyrd.state`'s existing `save_chronicle`.

Python 3.11+, standard library only.
"""

from __future__ import annotations


def ambient_register(eras: list[dict], era: str | None) -> str | None:
    """The ambient register of the era `era` names, or `None` (FR-001, FR-002).

    Returns `None` -- never raises -- when `era` is `None` or when no entry in `eras` has that
    id (including an empty `eras` list).
    """
    if era is None:
        return None
    for entry in eras:
        if entry.get("id") == era:
            return entry.get("ambient")
    return None


def cross_era(eras: list[dict], era: str | None, to: str, at: dict) -> dict:
    """Record a boundary crossing from `era` to `to` (FR-003).

    Returns `{"era": to, "crossing": {"from": era, "to": to, "at": at}}`. Raises `ValueError` if
    `to` is not present in the declared `eras` list (FR-004) -- an era must be named in advance
    -- or if `to` equals the current `era` (FR-005) -- crossing into the era already current is
    not a boundary. The caller appends the returned `crossing` to `era_crossings`, never editing
    or removing an existing entry (FR-006).
    """
    if to == era:
        raise ValueError(f"already in era {to!r}; crossing must name a different era")
    if not any(entry.get("id") == to for entry in eras):
        raise ValueError(f"era {to!r} is not declared in advance in this chronicle's eras list")
    return {"era": to, "crossing": {"from": era, "to": to, "at": at}}
