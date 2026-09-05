"""Career/ancestry shapes and the 8-advance allocation validator.

docs/design/11-character-creation.md section 3: creation spends 8 advances inside a starting
career (optionally widened by an ancestry), opening a skill at 25% or raising an already-open
skill by +5% toward the career's cap, with at least two skills opened. Per ADR 0014, a
character is chosen, not rolled -- this module validates a caller's allocation, it never
generates one.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import rules

MIN_ADVANCES = 8
MIN_SKILLS_OPENED = 2


def effective_cap(skill: str, career: dict, ancestry: dict | None = None) -> int | None:
    """The cap that binds `skill`, from whichever of career/ancestry grants it (the higher, if
    both do -- an ancestry widens eligibility, never narrows what the career already permits).
    `None` if neither grants it.
    """
    caps = [d["skills"][skill] for d in (career, ancestry) if d and skill in d["skills"]]
    return max(caps) if caps else None


def validate_allocation(actions: list[dict], career: dict, ancestry: dict | None = None) -> dict:
    """Validate an 8-advance allocation against `career` (and optionally `ancestry`).

    Returns `{"valid": True, "skills": {...}}` with the resulting percentages on success, or
    `{"valid": False, "error": "..."}` naming the first rule violated.
    """
    if len(actions) != MIN_ADVANCES:
        return {
            "valid": False,
            "error": f"allocation must spend exactly {MIN_ADVANCES} advances, got {len(actions)}",
        }

    opened_count = sum(1 for a in actions if a["action"] == "open")
    if opened_count < MIN_SKILLS_OPENED:
        return {
            "valid": False,
            "error": (f"at least {MIN_SKILLS_OPENED} skills must be opened, got {opened_count}"),
        }

    skills: dict[str, int] = {}
    for entry in actions:
        action, skill = entry["action"], entry["skill"]
        cap = effective_cap(skill, career, ancestry)
        if cap is None:
            return {"valid": False, "error": f"{skill!r} is not granted by this career/ancestry"}
        if action == "open":
            if skill in skills:
                return {"valid": False, "error": f"{skill!r} is already open"}
            skills[skill] = rules.SKILL_OPEN_VALUE
        elif action == "raise":
            if skill not in skills:
                return {"valid": False, "error": f"{skill!r} must be open before it can be raised"}
            new_value = skills[skill] + rules.SKILL_ADVANCE_STEP
            if new_value > cap:
                return {
                    "valid": False,
                    "error": f"raising {skill!r} to {new_value}% exceeds its cap of {cap}%",
                }
            skills[skill] = new_value
        else:
            return {"valid": False, "error": f"no such action: {action!r}"}

    return {"valid": True, "skills": skills}


def is_entry(career: dict) -> bool:
    """Whether `career` is an entry career -- one a character may take with no history at all.

    docs/design/24-authoring-a-setting.md: a career "is either an entry point or names one or more
    predecessors, never both and never neither", so an entry career declares no prerequisites.
    """
    return bool(career.get("entry"))


def career_complete(skills: dict, career: dict) -> bool:
    """Whether `career` is complete for a character holding `skills`.

    docs/design/03-rules.md section 6: "every skill it grants at that 70% cap". Ancestry is not
    consulted -- an ancestry widens what a character may spend on, never what a career grants, so
    completion is a property of the career's own list.
    """
    return all(skills.get(skill, 0) >= cap for skill, cap in career["skills"].items())


def find_career(career_id: str, careers: list[dict]) -> dict | None:
    """The career in `careers` with that id, or `None`."""
    return next((c for c in careers if c["id"] == career_id), None)


def completed_career_ids(career_history: list[dict]) -> set[str]:
    """The ids of careers a character has actually finished, from their recorded history.

    Completion is read off the record written when a career was left, never re-derived from the
    live skills: a later career may have raised a skill past a former career's cap, and a wound
    may have lowered one since (docs/design/29-evolution.md -- history is never recomputed).
    """
    return {entry["career"] for entry in career_history if entry.get("completed")}


def change_career_legality(target: str, careers: list[dict], career_history: list[dict]) -> dict:
    """Whether a character with `career_history` may change career to `target`.

    Returns `{"legal": True}` or `{"legal": False, "refusal": ..., "error": ...}`.

    docs/design/03-rules.md section 6: any entry career is a free choice whatever the history --
    starting over from a fresh entry point is always legal -- and a non-entry career is reachable
    once *any one* of its declared prerequisites is complete (they are OR, not AND).
    """
    career = find_career(target, careers)
    if career is None:
        return {
            "legal": False,
            "refusal": "unknown_career",
            "error": f"no such career: {target!r}",
        }
    if is_entry(career):
        return {"legal": True}

    prerequisites = career.get("prerequisites") or []
    if completed_career_ids(career_history) & set(prerequisites):
        return {"legal": True}
    return {
        "legal": False,
        "refusal": "prerequisites_unmet",
        "error": (
            f"{target!r} requires completing one of {', '.join(prerequisites)}, "
            "and none of them is complete"
        ),
    }
