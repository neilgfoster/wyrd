"""The award side of the advance economy: four triggers, one session ceiling.

docs/design/03-rules.md section 6 "Advances are the currency": 1-3 advances per session, each
awarded against a named trigger and never against an XP total, "so the engine can verify an award
rather than the GM being generous by accident". This module verifies exactly that -- whether a
claimed award is legal -- and never judges whether the fiction met the trigger, which stays the
GM's call (spec.md FR-008).

Spending is not here: #277 spends what this module mints, and `career.py` holds the caps a spend
is validated against.

Python 3.11+, standard library only.
"""

from __future__ import annotations

#: docs/design/03-rules.md section 6's trigger table, in the order that table states them. A
#: closed vocabulary -- a setting cannot add a fifth trigger, the same way it cannot add a wound
#: effect (`character.WOUND_EFFECT_KEYS`).
TRIGGERS = ("learned", "drove", "practised", "endured")

#: docs/design/03-rules.md section 6: "1-3 per session". Four triggers exist and three is the
#: ceiling, so a session in which all four genuinely fired still awards three -- the ceiling binds
#: independently of the vocabulary's size (research.md).
SESSION_ADVANCE_CEILING = 3


def _record(triggers, advances_unspent: int) -> dict:
    return {"triggers": list(triggers), "advances_unspent": advances_unspent}


def new_record(advances_unspent: int = 0) -> dict:
    """A fresh session award record, optionally opening with an existing balance."""
    return _record((), advances_unspent)


def award_advance(trigger: str, record: dict) -> dict:
    """Award one advance against `trigger`, given this session's award `record`.

    Returns `{"awarded": True, "trigger": ..., "record": ...}` with the balance raised by one, or
    `{"awarded": False, "refusal": ..., "error": ..., "record": ...}` with the record unchanged.
    `record` is never mutated.

    The three refusals are checked most-specific first, so a caller mistyping a trigger at the
    session ceiling is told about the typo rather than the ceiling (data-model.md).
    """
    triggers = list(record["triggers"])
    unspent = record["advances_unspent"]

    if trigger not in TRIGGERS:
        return {
            "awarded": False,
            "refusal": "unknown_trigger",
            "error": (
                f"no such award trigger: {trigger!r} -- expected one of {', '.join(TRIGGERS)}"
            ),
            "record": _record(triggers, unspent),
        }
    if trigger in triggers:
        return {
            "awarded": False,
            "refusal": "already_awarded",
            "error": f"{trigger!r} has already been awarded this session",
            "record": _record(triggers, unspent),
        }
    if len(triggers) >= SESSION_ADVANCE_CEILING:
        return {
            "awarded": False,
            "refusal": "session_ceiling",
            "error": (
                f"this session has already awarded {SESSION_ADVANCE_CEILING} advances, "
                "which is all a session pays"
            ),
            "record": _record(triggers, unspent),
        }

    return {
        "awarded": True,
        "trigger": trigger,
        "record": _record([*triggers, trigger], unspent + 1),
    }


def begin_session(record: dict) -> dict:
    """Open a new session: every trigger is available again, the balance carries over untouched.

    docs/design/03-rules.md section 6 caps the *rate* at which advances are earned, never the
    balance -- an unspent advance is not lost at a session boundary (spec.md FR-006).
    """
    return new_record(record["advances_unspent"])
