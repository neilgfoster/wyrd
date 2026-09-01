"""The player-character entity: shape, wound validation, active-effects computation.

docs/design/10-the-character.md (what a character carries, the skill scale) and
docs/design/22-state.md (the exact frontmatter shape, the wound schema and its load-error
rules). This module holds character-domain validation; `state.py` stays a generic,
entity-agnostic persistence primitive any future entity type can reuse.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib

from wyrd import state

#: The fields docs/design/22-state.md's "The player's character" section documents. Reference
#: only -- not an enforced allow-list in this feature (spec.md's Assumptions: schema versioning
#: and migration are out of scope, so an unrecognized extra field is not itself rejected here).
PLAYER_CHARACTER_FIELDS = (
    "id",
    "type",
    "role",
    "loyalty",
    "career",
    "career_history",
    "skills",
    "stamina",
    "fate",
    "fortune",
    "resolve",
    "taint",
    "trauma",
    "strain",
    "pending_omen",
    "hidden_threshold",
    "fault_line",
    "transformations",
    "afflictions",
    "dread",
    "reputation",
    "drives",
    "misfortune",
    "wounds",
    "holdings",
    "allegiances",
    "marks",
    "advances_unspent",
)

#: docs/design/22-state.md "Wounds": a wound's `effect` names a mechanic the engine knows;
#: anything else is a load error.
WOUND_EFFECT_KEYS = ("stamina_max", "skill", "dread")


def validate_wound(wound: dict) -> None:
    """Enforce docs/design/22-state.md's wound rules, in the order that document states them.

    Raises `state.StateError` naming the wound's `id` for the first rule violated.
    """
    wound_id = wound.get("id", "<unknown>")
    effect = wound.get("effect") or {}
    for key in effect:
        if key not in WOUND_EFFECT_KEYS:
            raise state.StateError(f"wound {wound_id!r}: unrecognized effect {key!r}")
    if "skill" in effect and not wound.get("bears_on"):
        raise state.StateError(f"wound {wound_id!r}: effect 'skill' requires bears_on")
    if wound.get("recurring") and wound.get("closed") is not None:
        raise state.StateError(f"wound {wound_id!r}: a recurring wound must never carry closed")


def validate_character(frontmatter: dict) -> None:
    """Enforce every wound's rules for a loaded character's `wounds` list."""
    for wound in frontmatter.get("wounds") or []:
        validate_wound(wound)


def active_wound_effects(wounds: list[dict]) -> list[dict]:
    """The effects presently in force: every wound whose `closed` is `None`.

    A closed wound remains in `wounds` (docs/design/22-state.md: "kept, never deleted") but
    its effect is excluded here -- "readers skip it."
    """
    active = []
    for wound in wounds:
        if wound.get("closed") is not None:
            continue
        entry = {"wound_id": wound.get("id"), "effect": wound.get("effect")}
        if wound.get("bears_on"):
            entry["bears_on"] = wound["bears_on"]
        active.append(entry)
    return active


def load(path: pathlib.Path) -> tuple[dict, str]:
    """Load a player-character entity from `path`, validating its wounds."""
    frontmatter, body = state.load_entity(path)
    validate_character(frontmatter)
    return frontmatter, body


def save(frontmatter: dict, body: str, path: pathlib.Path) -> None:
    """Validate and save a player-character entity to `path`."""
    validate_character(frontmatter)
    state.save_entity(frontmatter, body, path)
