"""Standing and coin as one material position (#279).

docs/design/03-rules.md section 2 "Gear and coin": coin is a stated total spent against a
`gear.yaml` price, never a ledger of transactions. Standing (`reputation.score`,
docs/design/22-state.md) is what a character's position owes them; it moves at Upkeep (#219, not
here) and also outside Upkeep, as a direct scene consequence -- the martial-weapon rule is one
fixed-size case of that, and the GM may apply others.

Three verbs, three pure functions -- no I/O, matching `advancement.py`'s own division of labour:

- `spend_coin` -- buy a gear entry, given the loaded catalogue as data (the caller reads
  `gear.yaml`, same division `spend_advance` already uses for career data).
- `martial_weapon_sighting` -- the one Standing trigger the design fixes at a size (-1) and a
  cause. `already_applied` is caller-supplied rather than engine-tracked: the engine has no scene
  detection of its own (spec.md's Assumptions), so the caller/session log is what knows whether
  this sighting was already charged.
- `adjust_standing` -- the general scene-consequence case, an arbitrary delta with no floor or
  ceiling the engine invents, matching how Taint and Trauma are already unbounded accruals.

Encumbrance is deliberately absent from this module: no weight field, no carrying-capacity score
(FR-005) -- `03-rules.md` section 2 keeps it a question asked of the fiction.

Python 3.11+, standard library only.
"""

from __future__ import annotations

#: The martial-weapon sighting cost (docs/design/03-rules.md section 2): fixed at 1, never a
#: setting choice.
MARTIAL_WEAPON_STANDING_COST = 1


def spend_coin(gear_id: str, coin: int, catalog: list[dict]) -> dict:
    """Spend `coin` against `gear_id`'s price in `catalog`.

    Returns `{"success": True, "coin": <new total>, "item": <entry>}` or
    `{"success": False, "reason": ..., "coin": coin}` with coin unchanged.
    """
    item = next((entry for entry in catalog if entry.get("id") == gear_id), None)
    if item is None:
        return {"success": False, "reason": f"unknown gear id: {gear_id!r}", "coin": coin}

    price = item["price"]
    if price > coin:
        return {
            "success": False,
            "reason": f"insufficient coin: costs {price}, have {coin}",
            "coin": coin,
        }
    return {"success": True, "coin": coin - price, "item": item}


def martial_weapon_sighting(standing: int, already_applied: bool) -> dict:
    """Apply the martial-weapon Standing cost, once per open sighting.

    `already_applied` is the caller's own record of whether this sighting has already been
    charged this scene -- the engine does not detect scenes.
    """
    if already_applied:
        return {"standing": standing, "applied": False}
    return {"standing": standing - MARTIAL_WEAPON_STANDING_COST, "applied": True}


def adjust_standing(standing: int, delta: int) -> dict:
    """Apply a scene-consequence Standing `delta` -- positive, negative, or zero, unbounded."""
    return {"standing": standing + delta}
