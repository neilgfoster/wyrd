"""Engine runtime support for a journey arc (#287).

docs/design/20-journeys.md: the subsystem for a setting whose story is travel. A journey is an
arc (`scale: journey`) whose children are legs, deliberately reusing existing machinery rather
than inventing new mechanics: containment ("arcs contain arcs", docs/design/18-arcs-and-beats.md),
the existing `mode: played | summarised` beat field, the Threat activation-roll shape
(`d100 <= imminence * 10`, docs/design/19-campaign.md) for the once-per-leg hazard check, and the
existing material economy for consequences.

No arc, beat, or Threat concept has any runtime implementation elsewhere in `engine/wyrd/` yet
(spec.md's Assumptions) -- this module is deliberately the minimal slice each needs for journey
resolution, not a general campaign engine. Journey/leg/Threat records are plain dicts, matching
every other module here: no entity/file loading, which stays the setting repo's concern.

Four pure functions, no I/O, matching `economy.py`/`advancement.py`'s own division of labour:

- `legs_for` -- derives a journey's ordered legs from its schema (FR-001).
- `resolve_leg` -- dispatches a leg by its own declared `mode`, and surfaces a crossed Threat's
  `ambient` cost when the caller has flagged one (FR-002, FR-007).
- `roll_hazard` -- the once-per-leg hazard check and its sub-table match, resolved against the
  matched entry's skill through the engine's existing core-roll request shape rather than a new
  mechanic (FR-003, FR-004, FR-005).
- `close_journey` -- partitions already-produced leg results into what was reached and what
  wasn't, so an early ending's consequences cover only the legs actually reached (FR-006).

No hazard/Threat consequence is applied here as a numeric delta: a hazard's `effect` and a
Threat's `ambient` list are prose in their own schema (docs/design/19-campaign.md), so this module
surfaces them for the caller/GM to route through the existing material economy (`economy.py`),
the same separation the engine already keeps between mechanical resolution and GM narration
(docs/design/13-diegesis.md). No per-item inventory or logistics ledger is introduced (FR-008).

Python 3.11+, standard library only.
"""

from __future__ import annotations


def legs_for(journey: dict) -> list[dict]:
    """The journey's ordered legs (FR-001, SC-001).

    A journey with no `pace` runs as a single leg spanning the whole route -- "mechanically as
    light as ordinary narrated travel" (docs/design/20-journeys.md) -- inheriting the journey's
    own `mode` if it declared one, else defaulting to `played` (the design doc gives no other
    default for an unstructured journey). A journey with `pace` uses its declared `children`, in
    order, unchanged.
    """
    if journey.get("pace") is None:
        return [
            {
                "id": journey["id"],
                "from": journey.get("from"),
                "to": journey.get("to"),
                "mode": journey.get("mode", "played"),
            }
        ]
    return list(journey.get("children", []))


def resolve_leg(leg: dict, *, threats: dict | None = None) -> dict:
    """Dispatch `leg` by its own `mode` field (FR-002); never chosen at runtime.

    `mode: played` resolves as an ordinary beat -- this module tags it `kind: "beat"` and leaves
    running the actual scene to the caller's existing beat machinery. `mode: summarised` resolves
    via elapsed-time -- tagged `kind: "elapsed-time"`, carrying the leg's span through unchanged;
    the expected-value `wyrd advance-time` machinery itself has no runtime yet (spec.md's
    Assumptions), so this module only tags and routes.

    When `leg["crosses_threat"]` names a key in `threats`, that Threat's `ambient` cost list is
    surfaced alongside the leg's own outcome (FR-007) -- reported, not auto-applied, since
    `ambient` entries are prose. A leg with no such crossing carries no `ambient` entry.
    """
    mode = leg.get("mode")
    if mode == "played":
        result: dict = {"kind": "beat", "leg": leg}
    elif mode == "summarised":
        result = {"kind": "elapsed-time", "leg": leg, "span": leg.get("span")}
    else:
        raise ValueError(f"leg {leg.get('id', leg)!r} has no recognised mode: {mode!r}")

    threat_key = leg.get("crosses_threat")
    if threat_key is not None and threats is not None and threat_key in threats:
        result["ambient"] = list(threats[threat_key].get("ambient", []))
    return result


def _parse_range(key: str) -> tuple[int, int]:
    if "-" in key:
        low, high = key.split("-", 1)
        return int(low), int(high)
    value = int(key)
    return value, value


def roll_hazard(journey: dict, wyrd_roll: int, table_roll: int | None = None) -> dict:
    """The once-per-leg hazard check (FR-003) and its sub-table match (FR-004, FR-005).

    Takes the hazard-activation roll and (when needed) the sub-table roll as arguments rather
    than calling `random` itself, matching `resolution.py`'s own split between randomness and
    banding -- callers supply dice, this function bands them.

    Activates when `wyrd_roll <= hazard_rating * 10`; a `hazard_rating` of `0` (the default)
    never activates. On activation, `table_roll` is matched against the journey's `hazards`
    range-keyed table; a roll matching no entry -- including on an empty table -- is a no-op
    (`matched: None`). A matched entry naming a `skill` is returned with a `request` dict shaped
    for `resolution.propose`, so it resolves through the engine's existing core roll rather than
    a new mechanic; a matched entry with no skill is narration only.
    """
    hazard_rating = journey.get("hazard_rating", 0)
    if wyrd_roll > hazard_rating * 10 or hazard_rating <= 0:
        return {"activated": False}

    hazards = journey.get("hazards", {})
    for key, entry in hazards.items():
        low, high = _parse_range(str(key))
        if table_roll is not None and low <= table_roll <= high:
            if entry.get("skill"):
                request = {
                    "mechanic": "ordinary-test",
                    "skill": entry["skill"],
                    "difficulty": entry["difficulty"],
                }
                return {"activated": True, "matched": entry, "kind": "test", "request": request}
            return {"activated": True, "matched": entry, "kind": "narration"}

    return {"activated": True, "matched": None}


def close_journey(journey: dict, legs_reached: list[dict]) -> dict:
    """Partition an (early-)ended journey's legs into reached vs. not (FR-006).

    Consequences for `legs_reached` are whatever `resolve_leg`/`roll_hazard` already produced for
    them -- this function computes nothing new, it only reports which legs of the journey's full
    `legs_for` set were actually reached and which lapse.
    """
    all_legs = legs_for(journey)
    reached_ids = {result["leg"]["id"] for result in legs_reached}
    not_reached = [leg for leg in all_legs if leg.get("id") not in reached_ids]
    return {"reached": legs_reached, "not_reached": not_reached}
