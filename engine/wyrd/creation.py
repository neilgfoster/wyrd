"""The character-creation procedure: docs/design/11-character-creation.md.

Turns a chosen career, a validated advance allocation (#231), a Loyalty, and the caller's
fiction (name, Drives, Misfortune, Fault Line) into a complete player-character entity. Per
ADR 0014, nothing here is rolled or generated -- creation composes and validates already-made
choices, it never makes them.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib

from wyrd import career as career_module
from wyrd import character

#: docs/design/11-character-creation.md section 2, "Why Fate rises with mortality."
MORTALITY_FATE = {"low": 2, "standard": 3, "high": 4}

#: docs/design/11-character-creation.md section 2's "Why Stamina is 6" -- computed and checked
#: in specs/008-character-creation/check_creation.py, not a taste choice.
STARTING_STAMINA = 6


def create_character(
    path: pathlib.Path,
    name: str,
    career: dict,
    actions: list[dict],
    loyalty: str,
    mortality: str,
    fault_line: str,
    ancestry: dict | None = None,
    drives: list | None = None,
    misfortune=None,
    body: str = "",
    id: str | None = None,
) -> dict:
    """Run the creation procedure, saving the result via `character.save`.

    Validates the advance allocation first (`career_module.validate_allocation`); on
    rejection, returns `{"valid": False, "error": ...}` without writing anything at all. On
    success, builds the full player-character frontmatter and saves it.
    """
    allocation = career_module.validate_allocation(actions, career, ancestry)
    if not allocation["valid"]:
        return {"valid": False, "error": allocation["error"]}

    fate = MORTALITY_FATE[mortality]
    frontmatter = {
        "id": id if id is not None else pathlib.Path(path).stem,
        "type": "character",
        "role": "player",
        "name": name,
        "loyalty": loyalty,
        "career": career,
        "career_history": [],
        "skills": allocation["skills"],
        "stamina": {"current": STARTING_STAMINA, "max": STARTING_STAMINA},
        "fate": {"current": fate, "max": fate},
        "fortune": {"current": fate},
        "resolve": {"current": 0},
        "taint": 0,
        "trauma": 0,
        "strain": 0,
        "pending_omen": None,
        "hidden_threshold": None,
        "fault_line": fault_line,
        "transformations": [],
        "afflictions": [],
        "dread": 0,
        "reputation": {"score": 0, "label": None},
        "drives": drives or [],
        "misfortune": misfortune,
        "wounds": [],
        "holdings": [],
        "allegiances": [],
        "marks": [],
        "advances_unspent": 0,
    }
    character.save(frontmatter, body, path)
    return {"valid": True, "path": str(path), "frontmatter": frontmatter}
