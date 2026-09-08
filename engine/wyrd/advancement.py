"""The award side of the advance economy: four triggers, one session ceiling.

docs/design/03-rules.md section 6 "Advances are the currency": 1-3 advances per session, each
awarded against a named trigger and never against an XP total, "so the engine can verify an award
rather than the GM being generous by accident". This module verifies exactly that -- whether a
claimed award is legal -- and never judges whether the fiction met the trigger, which stays the
GM's call (spec.md FR-008).

Spending is here too (#277): the three purchases docs/design/03-rules.md section 6 prices at 1
advance each. Every legality question a spend asks -- what a career grants, to what cap, whether a
career is complete, whether a change is reachable -- is answered by `career.py`, which owns the
career graph; this module owns the currency.

And what completing a career buys (#278): the advance that carries the last granted skill to the
cap pays +1 maximum Stamina, to a ceiling of 10, and a permanent Mark -- once per career-instance.
That is a consequence of a spend rather than a spend of its own, so it has no verb: a caller
cannot claim a completion the engine did not watch happen.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import career as career_module
from wyrd import creation, rules

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


#: docs/design/03-rules.md section 6's spending table, in the order that table states them. Closed
#: the same way `TRIGGERS` is -- a setting renames a spend, it never adds a fourth.
SPENDS = ("raise", "open", "change_career")

#: Every row of that table costs 1. There is no discount and no scaling with career depth.
ADVANCE_COST = 1

#: docs/design/03-rules.md section 6: "Maximum Stamina stops climbing at 10." Not chosen here --
#: `tools/check_advancement.py` computes it as the largest Stamina at which a further +1 is still
#: a 10% gain, and the tests assert this constant equals what that script computes.
STAMINA_MAX_CEILING = 10


def _view(
    career: str,
    career_history,
    skills: dict,
    advances_unspent: int,
    stamina_max: int,
    marks,
    career_completed: bool,
) -> dict:
    return {
        "career": career,
        "career_history": [dict(entry) for entry in career_history],
        "skills": dict(skills),
        "advances_unspent": advances_unspent,
        "stamina_max": stamina_max,
        "marks": [dict(mark) for mark in marks],
        "career_completed": career_completed,
    }


def _read(view: dict) -> dict:
    """The view's fields, with #278's three defaulted so a #277-era caller still works."""
    return {
        "career": view["career"],
        "career_history": view["career_history"],
        "skills": view["skills"],
        "advances_unspent": view["advances_unspent"],
        "stamina_max": view.get("stamina_max", creation.STARTING_STAMINA),
        "marks": view.get("marks") or [],
        "career_completed": bool(view.get("career_completed")),
    }


def new_view(
    career: str,
    skills: dict,
    advances_unspent: int = 0,
    career_history=None,
    stamina_max: int = creation.STARTING_STAMINA,
    marks=None,
    career_completed: bool = False,
) -> dict:
    """The character view a spend reads and returns (data-model.md).

    `stamina_max`, `marks` and `career_completed` are what a completion pays into; a caller that
    omits them gets a character at the creation-time maximum with nothing yet earned.
    """
    return _view(
        career,
        career_history or [],
        skills,
        advances_unspent,
        stamina_max,
        marks or [],
        career_completed,
    )


def _refuse(view: dict, refusal: str, error: str) -> dict:
    f = _read(view)
    unchanged = _view(
        f["career"],
        f["career_history"],
        f["skills"],
        f["advances_unspent"],
        f["stamina_max"],
        f["marks"],
        f["career_completed"],
    )
    return {"spent": False, "refusal": refusal, "error": error, "view": unchanged}


def _apply_skill_spend(view: dict, spend: str, career: dict, skills: dict) -> dict:
    """Return the accepted result of a `raise`/`open`, paying out if it completed the career.

    docs/design/03-rules.md section 6 makes completing a career -- every granted skill at the cap
    -- "the only durable toughening": +1 maximum Stamina and a permanent Mark. It fires here, on
    the advance that finished the last skill, rather than when the career is later left: a
    character who completes a career and stays in it is toughened all the same (research.md R1).

    Once per career-instance. `career_completed` is what makes it once -- it is set here and
    cleared only by a change of career, so a further spend inside a finished career pays nothing
    and a career finished twice across a lifetime pays twice.
    """
    f = _read(view)
    stamina_max, marks, completed = f["stamina_max"], f["marks"], f["career_completed"]

    if not completed and career_module.career_complete(skills, career):
        completed = True
        marks = [*marks, {"career": career["id"]}]
        #: A completion past the ceiling still grants its Mark; it grants no further Stamina.
        stamina_max = min(stamina_max + 1, STAMINA_MAX_CEILING)

    return {
        "spent": True,
        "spend": spend,
        "view": _view(
            f["career"],
            f["career_history"],
            skills,
            f["advances_unspent"] - ADVANCE_COST,
            stamina_max,
            marks,
            completed,
        ),
    }


def _spend_raise(view: dict, career: dict, ancestry: dict | None, skill: str) -> dict:
    cap = career_module.effective_cap(skill, career, ancestry)
    if cap is None:
        return _refuse(view, "not_granted", f"{skill!r} is not granted by this career/ancestry")
    if skill not in view["skills"]:
        return _refuse(view, "not_open", f"{skill!r} must be open before it can be raised")
    new_value = view["skills"][skill] + rules.SKILL_ADVANCE_STEP
    if new_value > cap:
        return _refuse(
            view, "at_cap", f"raising {skill!r} to {new_value}% exceeds its cap of {cap}%"
        )
    skills = {**view["skills"], skill: new_value}
    return _apply_skill_spend(view, "raise", career, skills)


def _spend_open(view: dict, career: dict, ancestry: dict | None, skill: str) -> dict:
    if career_module.effective_cap(skill, career, ancestry) is None:
        return _refuse(view, "not_granted", f"{skill!r} is not granted by this career/ancestry")
    if skill in view["skills"]:
        return _refuse(view, "already_open", f"{skill!r} is already open")
    skills = {**view["skills"], skill: rules.SKILL_OPEN_VALUE}
    return _apply_skill_spend(view, "open", career, skills)


def _spend_change_career(view: dict, career: dict, careers: list[dict], target: str) -> dict:
    legality = career_module.change_career_legality(target, careers, view["career_history"])
    if not legality["legal"]:
        return _refuse(view, legality["refusal"], legality["error"])

    f = _read(view)
    #: What the departing instance actually paid out, not a fresh look at the sheet. A wound that
    #: lowered a skill since the career was finished must not revoke a completion the character
    #: earned -- history is never recomputed (docs/design/29-evolution.md), which is what
    #: `career.completed_career_ids` already claimed and #277's recompute here quietly broke.
    departed = {"career": career["id"], "completed": f["career_completed"]}
    return {
        "spent": True,
        "spend": "change_career",
        "view": _view(
            target,
            [*f["career_history"], departed],
            f["skills"],
            f["advances_unspent"] - ADVANCE_COST,
            f["stamina_max"],
            f["marks"],
            #: A fresh instance, unpaid: entering a career is not completing it, even one whose
            #: every granted skill the character already holds at cap.
            False,
        ),
    }


def spend_advance(
    spend: str,
    view: dict,
    career: dict,
    careers: list[dict] | None = None,
    ancestry: dict | None = None,
    skill: str | None = None,
    target: str | None = None,
) -> dict:
    """Spend one advance on `spend`, given the character `view` and their current `career`.

    Returns `{"spent": True, "spend": ..., "view": ...}` with the advance taken and exactly one of
    the skills or the career changed, or `{"spent": False, "refusal": ..., "error": ...,
    "view": ...}` with the view returned unchanged. Nothing passed in is ever mutated (FR-012).

    An unknown spend is refused first -- that is a caller bug, not a play-time answer -- and an
    empty purse next: a character with no advance cannot make any spend, so naming the chosen
    skill's own fault first would only invite them to pick a different one and be refused again
    for the real reason (research.md).

    The engine never judges the fictional reason offered for a career change, exactly as
    `award_advance` never judges whether a trigger's fiction fired.
    """
    if spend not in SPENDS:
        return _refuse(
            view,
            "unknown_spend",
            f"no such spend: {spend!r} -- expected one of {', '.join(SPENDS)}",
        )
    if view["advances_unspent"] < ADVANCE_COST:
        return _refuse(view, "no_advance", "no unspent advance to spend")

    if spend == "raise":
        return _spend_raise(view, career, ancestry, skill)
    if spend == "open":
        return _spend_open(view, career, ancestry, skill)
    return _spend_change_career(view, career, careers or [], target)
