"""Standing and coin as one material position (#279), plus the other growing tracks (#280).

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

#280 adds four more verbs over docs/design/03-rules.md section 6, "What actually grows":
`gain_allegiance`/`lose_allegiance` and `gain_holding`/`lose_holding` are set-membership
operations over the existing `allegiances`/`holdings` list fields (docs/design/22-state.md); none
of the four touch a skill or difficulty value, matching the section's own "None of them improves
a die roll". `roll_standing` bands an already-rolled d100 against `reputation.score` into one of
three social-recognition outcomes -- the roll itself stays at the caller's boundary, same split
`resolution.py`'s own `roll()` already keeps between randomness and banding. Knowledge and Bonds
are out of scope here (spec.md's Edge Cases): Bonds is the companion track #57/ADR 0034 already
delivered, and Knowledge carries no tracked field anywhere in the design corpus.

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


def _gain(item_id: str, current: list[str]) -> dict:
    """Add `item_id` to `current`, idempotently -- present exactly once either way."""
    if item_id in current:
        return {"success": True, "list": list(current)}
    return {"success": True, "list": [*current, item_id]}


def _lose(item_id: str, current: list[str], noun: str) -> dict:
    """Remove `item_id` from `current`, refusing when it is not present."""
    if item_id not in current:
        return {"success": False, "reason": f"{noun} not held: {item_id}", "list": list(current)}
    return {"success": True, "list": [entry for entry in current if entry != item_id]}


def gain_allegiance(allegiance_id: str, allegiances: list[str]) -> dict:
    """Add `allegiance_id` to `allegiances`, idempotently."""
    result = _gain(allegiance_id, allegiances)
    return {"success": result["success"], "allegiances": result["list"]}


def lose_allegiance(allegiance_id: str, allegiances: list[str]) -> dict:
    """Remove `allegiance_id` from `allegiances`, refusing when it is not held."""
    result = _lose(allegiance_id, allegiances, "allegiance")
    out = {"success": result["success"], "allegiances": result["list"]}
    if not result["success"]:
        out["reason"] = result["reason"]
    return out


def gain_holding(holding_id: str, holdings: list[str]) -> dict:
    """Add `holding_id` to `holdings`, idempotently."""
    result = _gain(holding_id, holdings)
    return {"success": result["success"], "holdings": result["list"]}


def lose_holding(holding_id: str, holdings: list[str]) -> dict:
    """Remove `holding_id` from `holdings`, refusing when it is not held."""
    result = _lose(holding_id, holdings, "holding")
    out = {"success": result["success"], "holdings": result["list"]}
    if not result["success"]:
        out["reason"] = result["reason"]
    return out


def standing_bands(standing: int) -> tuple[int, int, int]:
    """The (favourable, neutral, unfavourable) row-width triple for a given Standing score.

    Widths always sum to 100 (asserted by `tools/check_reputation_roll.py`, not eyeballed):
    favourable and unfavourable each grow 5 rows per point of Standing in their favour, capped at
    45 -- since `standing` is signed, only one of the two is ever above its floor of 5 at once, so
    neutral never falls below 50.
    """
    favourable = min(45, 5 + 5 * max(standing, 0))
    unfavourable = min(45, 5 + 5 * max(-standing, 0))
    neutral = 100 - favourable - unfavourable
    return favourable, neutral, unfavourable


def roll_standing(standing: int, roll: int) -> dict:
    """Band an already-rolled d100 `roll` against `standing` into a social-recognition outcome.

    Never reads or writes a skill percentage or difficulty value -- Standing does not touch the
    resolution mechanic (docs/design/03-rules.md section 6, FR-006).
    """
    favourable, neutral, _unfavourable = standing_bands(standing)
    if roll <= favourable:
        outcome = "favourable"
    elif roll <= favourable + neutral:
        outcome = "neutral"
    else:
        outcome = "unfavourable"
    return {"outcome": outcome}
