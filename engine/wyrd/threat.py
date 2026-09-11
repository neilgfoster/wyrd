"""Threats: campaign-length antagonists that act on their own schedule (#334).

docs/design/19-campaign.md: a Threat is not an entity type. It is an *aspect* attached to the
frontmatter of a `character`, `organisation` or `place` entity -- forcing a choice between them
would lose information (a threat may be a person, a conspiracy or a poisoned valley). This module
is the runtime implementation `journey.py` already assumed exists ("No... Threat concept has any
runtime implementation elsewhere in `engine/wyrd/` yet") and reuses its exact activation-roll
shape (`d100 <= imminence * 10`) and its convention of taking dice as arguments rather than rolling
internally (matching `resolution.py`'s split between randomness and banding).

Four pure functions, no I/O, matching `journey.py`/`economy.py`'s own division of labour:

- `active_threats` -- the active set is a query over a collection of entities, not a file
  (FR-001, FR-002).
- `check_activation` -- the weekly percentile check (FR-003).
- `resolve_effects` -- bands a supplied effects-table roll, mirroring `journey.roll_hazard`'s
  sub-table matching (FR-004).
- `promote` -- attaches a new `threat` block and objective to an entity that doesn't carry one
  yet; nothing is created (FR-005, FR-006).

A Threat's `effects`/`ambient`/`counters`/`weakness`/`connection` entries are prose -- what
actually happens is GM narration (docs/design/13-diegesis.md) -- so this module surfaces a
matched effects-table entry, it never interprets or applies it. Fading (an entity's `imminence`
falling to `0`) needs no dedicated function here: `active_threats` excludes it on the very next
call, and the `threat` block itself is never deleted (FR-007) -- the caller (GM action or
`advance-time`, #338) simply lowers `imminence` on the entity dict it already owns.

Python 3.11+, standard library only.
"""

from __future__ import annotations


def active_threats(entities: list[dict]) -> list[dict]:
    """The active set: entities carrying a `threat` block with `imminence > 0` (FR-001, FR-002).

    A query, not a file -- any entity type may carry a `threat` block, so this makes no
    assumption about `entities`' own types. An entity with no `threat` block, or one whose
    `imminence` is `0`, is excluded.
    """
    return [
        entity
        for entity in entities
        if (threat := entity.get("threat")) is not None and threat.get("imminence", 0) > 0
    ]


def check_activation(imminence: int, wyrd_roll: int) -> bool:
    """The weekly percentile check (FR-003): activates when `wyrd_roll <= imminence * 10`.

    An `imminence` of `0` (or less) never activates, matching `journey.roll_hazard`'s own
    `hazard_rating <= 0` guard.
    """
    return imminence > 0 and wyrd_roll <= imminence * 10


def _parse_range(key: str) -> tuple[int, int]:
    if "-" in key:
        low, high = key.split("-", 1)
        return int(low), int(high)
    value = int(key)
    return value, value


def resolve_effects(effects: dict, table_roll: int) -> dict:
    """Band a supplied effects-table roll against `effects`' range-keyed entries (FR-004).

    Mirrors `journey.roll_hazard`'s own sub-table matching exactly: a roll matching no entry --
    including on an empty table -- is a no-op (`{"matched": None}`), never an error.
    """
    for key, entry in effects.items():
        low, high = _parse_range(str(key))
        if low <= table_roll <= high:
            return {"matched": entry}
    return {"matched": None}


def promote(entity: dict, threat: dict, objective: str) -> dict:
    """Attach a new `threat` block and `objective` to `entity` (FR-005).

    Nothing is created: the returned dict is `entity` with `threat` and `objective` added, every
    other field unchanged. Rejects (`ValueError`) an entity that already carries a `threat` block
    -- promotion targets one that does not yet have one -- and rejects a `threat` whose
    `imminence` is not `> 0` (FR-006): a Threat is born active, or it isn't a Threat at all.
    """
    if entity.get("threat") is not None:
        raise ValueError(f"entity {entity.get('id', entity)!r} already carries a threat block")
    if threat.get("imminence", 0) <= 0:
        raise ValueError("a promoted threat's imminence must be greater than 0")
    return {**entity, "threat": threat, "objective": objective}
