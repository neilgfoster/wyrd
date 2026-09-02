"""Turn order and round structure: the scene-level state machine around WHEN a combatant may
act, not how a roll resolves (that stays `resolution.py`'s own job).

docs/design/03-rules.md section 2 "Rounds and turn order" / "Surprise and ambush": whoever
started the exchange acts first; where neither side started it, the armed side acts first, or
the player's side if both/neither are armed (ADR 0018 -- the one rule here decided from outside
the fiction). A surprised side does not act in round 1 but still defends normally. An ambush
eases the ambushing side's round-1 attacks by +20, and nothing after.

A combat scene is chronicle-scoped, not per-entity (specs/086-turn-order-round-structure/spec.md
Assumptions) -- it lives under a `combat` key in the same chronicle state `state.py` already
reads/writes atomically.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib

from wyrd import state

#: docs/design/03-rules.md section 2 "Surprise and ambush": the ambush bonus, and the round it
#: stops applying after.
AMBUSH_BONUS = 20
AMBUSH_ROUNDS = 1


def determine_first_actor(started_by: str | None, armed: dict[str, bool], player_side: str) -> str:
    """docs/design/03-rules.md section 2 "Rounds and turn order": the exchange-starter, if one
    is named, wins outright. Otherwise (a mutual encounter): the sole armed side acts first; if
    both or neither side is armed, the designated player side acts first (ADR 0018). Pure --
    no persisted state, no randomness (docs/design/27-tooling.md: deterministic over inference).
    """
    if started_by is not None:
        return started_by
    armed_sides = [side for side, is_armed in armed.items() if is_armed]
    if len(armed_sides) == 1:
        return armed_sides[0]
    return player_side


def start_combat(
    sides: dict[str, dict],
    started_by: str | None,
    player_side: str,
    *,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """Start a combat scene: validate `started_by`/`player_side` name real sides, compute the
    first actor, and persist the scene under chronicle state's `combat` key.

    `sides`: `{"<name>": {"armed": bool, "surprised": bool (default False),
    "ambush": bool (default False)}}`.

    Raises `ValueError` if `started_by` or `player_side` names a side not in `sides`.
    """
    if started_by is not None and started_by not in sides:
        raise ValueError(f"no such side: {started_by}")
    if player_side not in sides:
        raise ValueError(f"no such side: {player_side}")

    armed = {name: bool(flags.get("armed", False)) for name, flags in sides.items()}
    first_actor = determine_first_actor(started_by, armed, player_side)

    normalized_sides = {
        name: {
            "armed": bool(flags.get("armed", False)),
            "surprised": bool(flags.get("surprised", False)),
            "ambush": bool(flags.get("ambush", False)),
        }
        for name, flags in sides.items()
    }
    scene = {"sides": normalized_sides, "round": 1, "first_actor": first_actor}

    current = state.load(state_path)
    current["combat"] = scene
    state.save(current, state_path)
    return scene


def _load_scene(state_path: pathlib.Path) -> dict:
    current = state.load(state_path)
    scene = current.get("combat")
    if scene is None:
        raise ValueError("no combat scene in progress -- call start_combat first")
    return scene


def advance_round(*, state_path: pathlib.Path = state.DEFAULT_STATE_PATH) -> dict:
    """Advance the current combat scene to its next round."""
    current = state.load(state_path)
    scene = current.get("combat")
    if scene is None:
        raise ValueError("no combat scene in progress -- call start_combat first")
    scene["round"] += 1
    state.save(current, state_path)
    return scene


def can_act(side: str, *, state_path: pathlib.Path = state.DEFAULT_STATE_PATH) -> bool:
    """docs/design/03-rules.md section 2: a surprised side does not act in round 1 -- false only
    for a surprised side while the scene's round is still 1; true otherwise (and always true for
    a side that was never marked surprised)."""
    scene = _load_scene(state_path)
    if side not in scene["sides"]:
        raise ValueError(f"no such side: {side}")
    if scene["sides"][side]["surprised"] and scene["round"] == 1:
        return False
    return True


def attack_modifier(side: str, *, state_path: pathlib.Path = state.DEFAULT_STATE_PATH) -> int:
    """docs/design/03-rules.md section 2: an ambushing side's round-1 attacks carry +20, and
    nothing after."""
    scene = _load_scene(state_path)
    if side not in scene["sides"]:
        raise ValueError(f"no such side: {side}")
    if scene["sides"][side]["ambush"] and scene["round"] <= AMBUSH_ROUNDS:
        return AMBUSH_BONUS
    return 0
