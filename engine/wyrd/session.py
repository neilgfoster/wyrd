"""Beat/arc structure and the session loop.

docs/design/16-session.md: arcs organise (nest freely, entry/exit conditions, children), beats
are played (the atomic unit -- one goal, attempted, resolved, persisted). `wyrd.entity` already
gives the *shape* of this distinction (`arc` is in `entity.RECURSIVE_TYPES`, `beat` is not, and
`entity.children_of`/`entity.check_containment` already resolve the `parent` tree); this module
adds what `entity.py` deliberately leaves out: the enforcement that a beat given a child is
rejected, per-narration `mode` recording (played/summarised) independent of the beat's own
frontmatter, the six-step session loop as a checkable state machine, the `pending:` mid-beat
marker, and session-shape classification kept out of player-facing text.

The Rally mechanic (Strain/Stamina recovery, advance award, commit) and the Downtime phase's own
internal steps (upkeep, undertakings, Mend) are out of scope here -- see #310 and #311.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import time

from wyrd import entity

LOOP_STEPS = ("load", "orient", "recap", "beat", "close")
SESSION_SHAPES = ("single_beat", "interlude", "downtime", "extended")

_MODES = ("played", "summarised")

# This module's containment enforcement (assert_beat_has_no_children) only makes sense because
# "beat" is not recursive -- if that ever changed, the enforcement below would need to change
# with it rather than silently becoming a no-op.
assert "beat" not in entity.RECURSIVE_TYPES

# The loop step a given step may legally advance to. "beat" may repeat (self-loop) or proceed to
# close; every other step has exactly one legal successor.
_LOOP_TRANSITIONS = {
    "load": ("orient",),
    "orient": ("recap",),
    "recap": ("beat",),
    "beat": ("beat", "close"),
    "close": (),
}


def assert_beat_has_no_children(entities: dict[str, dict]) -> dict:
    """Check that no entity of type "beat" in `entities` has a child.

    Returns {"valid": True} or {"valid": False, "beat": <id>, "child": <id>} for the first
    violation found (in `entities`' own iteration order). A beat is never a container, regardless
    of how few children the arc above it has.
    """
    for candidate_id, frontmatter in entities.items():
        if frontmatter.get("type") != "beat":
            continue
        children = entity.children_of(candidate_id, entities)
        if children:
            return {"valid": False, "beat": candidate_id, "child": children[0]}
    return {"valid": True}


def narrate_beat(beat_id: str, mode: str) -> dict:
    """A beat resolution record: {"beat_id", "mode", "resolved_at"}.

    `mode` must be "played" or "summarised"; raises ValueError otherwise. This never reads or
    writes any field on the beat entity's own frontmatter -- `mode` lives only on the returned
    record, so the same `beat_id` narrated again (in this or another chronicle) produces an
    independent record, never a shared or overwritten one.
    """
    if mode not in _MODES:
        raise ValueError(f"invalid beat mode: {mode!r} (must be one of {_MODES})")
    return {"beat_id": beat_id, "mode": mode, "resolved_at": time.time()}


def new_loop_state() -> dict:
    """A fresh session loop state, sitting at "load" with nothing yet recorded."""
    return {
        "step": "load",
        "elapsed_applied": False,
        "beats_this_session": [],
        "closed": False,
    }


def advance_loop(loop_state: dict, to_step: str) -> dict:
    """Transition `loop_state` to `to_step`, returning a new state (input is left unmodified).

    Enforces load -> orient -> recap -> beat -> (beat | close): `to_step` must be a legal
    successor of the current step (per `_LOOP_TRANSITIONS`), recap is only reachable once orient
    has actually run (`elapsed_applied`), and close is terminal -- no further transition is legal
    once `closed` is True. Raises ValueError naming the illegal transition otherwise.
    """
    if loop_state["closed"]:
        raise ValueError(f"illegal transition: session already closed, cannot move to {to_step}")
    current = loop_state["step"]
    if to_step not in _LOOP_TRANSITIONS.get(current, ()):
        raise ValueError(f"illegal transition: {current} -> {to_step}")
    if to_step == "recap" and not loop_state["elapsed_applied"]:
        raise ValueError("illegal transition: recap before orient has run")

    new_state = dict(loop_state)
    new_state["beats_this_session"] = list(loop_state["beats_this_session"])
    new_state["step"] = to_step
    if to_step == "orient":
        new_state["elapsed_applied"] = True
    if to_step == "close":
        new_state["closed"] = True
    return new_state


def set_pending(beat_id: str, action: str) -> dict:
    """A pending marker naming the specific unresolved action inside an interrupted beat."""
    return {"beat_id": beat_id, "action": action, "set_at": time.time()}


def resume_from_pending(pending: dict) -> str:
    """The action to resume from, given a pending marker."""
    return pending["action"]


def classify_shape(beats_this_session: list[str], used_dice: bool, ran_downtime: bool) -> str:
    """One of SESSION_SHAPES, computed from this session's own recorded facts.

    This is a pacing read for the GM/engine, never consulted by anything that produces
    player-facing narration text -- no function in this module that narrates a beat or a recap
    takes a shape as input, and none should ever be added that does (docs/design/16-session.md:
    "the player does not get told they are in an Interlude").

    An input matching no shape cleanly still returns a definite label (never raises) -- this is a
    best-fit classification, not a strict validator.
    """
    if ran_downtime:
        return "downtime"
    if len(beats_this_session) >= 3:
        return "extended"
    if len(beats_this_session) <= 1 and not used_dice:
        return "interlude"
    return "single_beat"
