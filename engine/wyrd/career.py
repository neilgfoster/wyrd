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
