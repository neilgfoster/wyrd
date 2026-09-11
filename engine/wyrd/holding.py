"""Holdings: converting accumulated investment into stakes (#337).

docs/design/19-campaign.md: "A threat to a settlement is a problem; a threat to a settlement
where the character owns the mill is personal, and requires no invention on the GM's part to make
it so." Holding recording itself -- `economy.gain_holding`/`lose_holding`, kept a distinct list
field from `allegiances` -- already exists (#276-280, epic #216); this module is the still-missing
read-side connection: flagging which of a Threat set touches something the character holds.

One pure function, no I/O, matching `threat.py`/`thread.py`/`era.py`'s own division of labour.
Deliberately does not import `threat.py` -- it operates on whatever shape
`threat.active_threats` already produces (a list of entity dicts), the same way `journey.py`'s
`resolve_leg` takes a `threats` argument rather than importing the Threat module directly.

Python 3.11+, standard library only.
"""

from __future__ import annotations


def flag_personal_stakes(threats: list[dict], holdings: list[str]) -> list[dict]:
    """Annotate each of `threats` with `personal: bool` (FR-001, FR-002).

    `personal` is `True` when the entity's `id` appears in `holdings`, `False` otherwise --
    including an entity with no `id` field or an empty `holdings` list (FR-003), never raised.
    Returns a new list, same length and order as `threats`; every other field is unchanged.
    """
    held = set(holdings)
    return [{**entity, "personal": entity.get("id") in held} for entity in threats]
