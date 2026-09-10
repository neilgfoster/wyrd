"""The Downtime phase: Destination, Upkeep, Advances, Undertaking and Rest, plus Mend.

docs/design/16-session.md "Downtime": a phase with its own rules, not a skip between adventures.
Its five steps -- Destination (where the time is spent), Upkeep (time costs something, away from
home), Advances (spending what was earned), Undertaking (choose exactly one), and Rest (Stamina
returns to maximum, unconditionally, not itself an undertaking) -- are modelled here as a linear
loop state, mirroring `wyrd.session`'s own `new_loop_state`/`advance_loop` pair at a smaller scale
(no self-loop -- Downtime's steps do not repeat the way a beat can).

Mend (docs/design/16-session.md "Mend", ADR 0021) is the one undertaking this module implements in
full: naming one wound by its `id`, stepping that wound's `effect` one grade toward nothing per a
fixed ladder, and never touching a `recurring` wound. It reads and mutates the wound-record shape
`wyrd.character` already owns (`WOUND_EFFECT_KEYS`, `validate_wound`) without redefining it.

Every function here is pure -- no I/O, no mutation of its inputs -- matching `rally.py`'s,
`advancement.py`'s and `economy.py`'s own division of labour. Advances-spending itself is not
reimplemented here; it goes through `wyrd.career`/`wyrd.advancement`'s existing spend verbs
unchanged (#311's own scope note) -- this module's "advances" step is a pass-through checkpoint in
the loop, not a new spend path.

Python 3.11+, standard library only.
"""

from __future__ import annotations

#: docs/design/16-session.md's Downtime table, in the order that table states it. Strictly
#: linear -- unlike `session.LOOP_STEPS`'s "beat", no step here repeats.
DOWNTIME_STEPS = ("destination", "upkeep", "advances", "undertaking", "rest")

#: docs/design/16-session.md's undertaking list, in the order that document states it. A closed
#: vocabulary, matching `advancement.TRIGGERS`'s own convention -- a setting cannot add a seventh.
UNDERTAKINGS = ("recover", "mend", "pursue", "cultivate", "learn", "ask")

#: ADR 0021's ladder, exactly: `skill` has two rungs before closed (`-10` and `-5` are the
#: difficulty ladder's own rungs, docs/design/03-rules.md section 1), `stamina_max` and `dread`
#: have one. A literal table, not a formula -- see specs/116-downtime-mend/research.md.
MEND_LADDER = {
    "skill": (-10, -5),
    "stamina_max": (-1,),
    "dread": (1,),
}

_UPKEEP_TRADES = ("standing", "coin")

# The step a given step may legally advance to. Every DOWNTIME_STEPS entry must appear as a key,
# checked below -- matching session.py's own self-check for the same failure mode.
_TRANSITIONS = {
    "destination": ("upkeep",),
    "upkeep": ("advances",),
    "advances": ("undertaking",),
    "undertaking": ("rest",),
    "rest": (),
}
assert set(_TRANSITIONS) == set(DOWNTIME_STEPS)


def new_downtime_state() -> dict:
    """A fresh Downtime state, sitting before "destination" with no undertaking chosen."""
    return {"step": None, "undertaking": None, "undertaking_chosen": False}


def advance_downtime(state: dict, to_step: str, *, undertaking: str | None = None) -> dict:
    """Transition `state` to `to_step`, returning a new state (input is left unmodified).

    Enforces destination -> upkeep -> advances -> undertaking -> rest, strictly linear. Moving to
    "undertaking" requires `undertaking` to be one of UNDERTAKINGS, and raises if an undertaking
    has already been chosen this period -- the exactly-one gate docs/design/16-session.md states
    ("The constraint is that you choose one") is enforced here, not left to the caller to police.
    Raises ValueError naming the illegal transition otherwise.
    """
    current = state["step"]
    if to_step == "destination":
        if current is not None:
            raise ValueError("illegal transition: destination is only the first step")
    elif to_step not in _TRANSITIONS.get(current, ()):
        raise ValueError(f"illegal transition: {current} -> {to_step}")

    if to_step == "undertaking":
        if state["undertaking_chosen"]:
            raise ValueError(
                f"illegal transition: an undertaking ({state['undertaking']!r}) "
                "has already been chosen this Downtime period"
            )
        if undertaking not in UNDERTAKINGS:
            raise ValueError(
                f"invalid undertaking: {undertaking!r} (must be one of {UNDERTAKINGS})"
            )

    new_state = dict(state)
    new_state["step"] = to_step
    if to_step == "undertaking":
        new_state["undertaking"] = undertaking
        new_state["undertaking_chosen"] = True
    return new_state


def apply_upkeep(destination: str, standing: int, coin: int, *, trade: str | None = None) -> dict:
    """Resolve Upkeep: time costs something, away from home only.

    `destination == "home"` costs nothing -- `trade` is ignored, both values pass through
    unchanged. Otherwise exactly one of `trade="standing"` (Standing -1) or `trade="coin"` (coin
    -= current Standing) must be given; any other value, including None, is rejected -- choosing
    neither is not a legal Upkeep outcome away from home (docs/design/16-session.md). The coin
    trade is rejected outright if coin is insufficient, rather than going negative.

    Returns {"standing": ..., "coin": ..., "trade": "none" | "standing" | "coin"} on success, or
    {"standing": standing, "coin": coin, "trade": None, "reason": ...} on rejection.
    """
    if destination == "home":
        return {"standing": standing, "coin": coin, "trade": "none"}

    if trade not in _UPKEEP_TRADES:
        return {
            "standing": standing,
            "coin": coin,
            "trade": None,
            "reason": f"Upkeep away from home requires a trade, one of {_UPKEEP_TRADES}",
        }
    if trade == "standing":
        return {"standing": standing - 1, "coin": coin, "trade": "standing"}
    if coin < standing:
        return {
            "standing": standing,
            "coin": coin,
            "trade": None,
            "reason": f"insufficient coin: Upkeep costs {standing}, have {coin}",
        }
    return {"standing": standing, "coin": coin - standing, "trade": "coin"}


def apply_rest(stamina_max: int) -> int:
    """Rest: Stamina returns to maximum, unconditionally -- not itself an undertaking.

    docs/design/16-session.md: "Stamina is not on that list, deliberately... it returns to maximum
    whether or not the period is spent on it." Independent of which undertaking, if any, was
    chosen.
    """
    return stamina_max


def close_downtime(state: dict) -> dict:
    """The fact that this Downtime period advanced the calendar.

    docs/design/16-session.md: "Downtime advances the calendar... which means Threats activate."
    This module exposes only the fact, per #311's own scope note -- Threat activation is
    triggered elsewhere, not duplicated here, and no concrete date/season value is computed.
    """
    return {"calendar_advanced": True}


def apply_mend(wound_id: str, wounds: list[dict], *, closed_marker: object = True) -> dict:
    """Mend: name one wound by its `id`, step its effect one grade toward nothing.

    Rejects, leaving `wounds` unchanged, when: `wound_id` is not present ("unknown_wound"); the
    wound is `recurring` ("recurring" -- ADR 0021: "a recurring wound never closes... whatever is
    spent"); or the wound is already closed ("already_closed" -- Mend only ever moves an active
    wound).

    Otherwise steps the wound's one `effect` entry one rung down MEND_LADDER's fixed table for
    that effect's key. A wound at the ladder's last rung is closed instead: `effect` cleared and
    `closed` set to `closed_marker` (`True` by default; a caller may pass a beat/date value to
    name what closed it -- this module invents no such value itself, only that it must be
    something other than `None`, per `character.validate_wound`'s own "closed is not None" check)
    -- the record is kept, never deleted (docs/design/29-evolution.md). Every other field (`id`,
    `bears_on`, `recurring`) is left exactly as it was.

    Returns {"success": True, "wounds": <new list>, "closed": <bool>} or
    {"success": False, "reason": ..., "wounds": <unchanged>}.
    """
    target = next((wound for wound in wounds if wound.get("id") == wound_id), None)
    if target is None:
        return {"success": False, "reason": "unknown_wound", "wounds": list(wounds)}
    if target.get("recurring"):
        return {"success": False, "reason": "recurring", "wounds": list(wounds)}
    if target.get("closed") is not None:
        return {"success": False, "reason": "already_closed", "wounds": list(wounds)}

    effect = target.get("effect") or {}
    # Mend's own scope is one wound with one effect entry, per docs/design/16-session.md's ladder
    # table -- every wound the Aftermath table hands out carries exactly one.
    ((effect_key, current_value),) = effect.items()
    ladder = MEND_LADDER[effect_key]
    rung = ladder.index(current_value)

    new_wound = dict(target)
    closed = False
    if rung + 1 < len(ladder):
        new_wound["effect"] = {effect_key: ladder[rung + 1]}
    else:
        new_wound["effect"] = {}
        new_wound["closed"] = closed_marker
        closed = True

    new_wounds = [new_wound if wound is target else wound for wound in wounds]
    return {"success": True, "wounds": new_wounds, "closed": closed}
