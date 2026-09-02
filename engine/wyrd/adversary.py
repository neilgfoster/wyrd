"""The adversary block: loading one bestiary entry into a validated in-memory shape.

docs/design/12-the-adversary.md section 2 ("The block"): what a character's own reading of an
opponent is thinner than -- an adversary carries only what a published rule reads off it, and
nothing else. This module gives the engine the play-time counterpart of
`tools/check_bestiary.py`'s authoring-time validator, playing the same role `character.py`'s
`load`/`validate_character` play for a player character (specs/094-adversary-block-loading).

The validation rules here mirror `tools/check_bestiary.py`'s `check_entry` exactly (required
fields, unrecognised fields, the damage/damage_type pairing, the closed trait vocabulary), but
are a separate implementation rather than an import: `engine/` is the shipped engine and `tools/`
is repository-maintenance scripts, and the two must not depend on each other
(`engine/wyrd/state.py`'s own precedent, for its YAML reader).

Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib
import re

from wyrd import state

#: docs/design/12-the-adversary.md section 2: the first six fields are required; an opponent
#: missing one is an opponent the GM has to improvise.
REQUIRED_FIELDS = {"id", "name", "baseline", "stamina_max", "armour", "skills"}
OPTIONAL_FIELDS = {"damage", "damage_type", "ranged", "traits", "notes"}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

#: docs/design/03-rules.md section 2.
ARMOUR_RANKS = ("none", "light", "modest", "heavy")
#: docs/adr/0022 -- closed.
DAMAGE_TYPES = ("slashing", "piercing", "blunt", "searing")

#: docs/design/10-the-character.md section 2: a percentage is what the engine rolls against.
SKILL_MIN, SKILL_MAX = 0, 100
STAMINA_MIN = 1

#: docs/design/12-the-adversary.md section 5: the closed trait vocabulary -- every effect acts
#: on a mechanism that already exists.
TRAIT_EFFECTS = {
    "difficulty",
    "damage",
    "damage_type",
    "stamina_max",
    "armour_rank",
    "wyrd",
}

#: docs/design/25-entities.md: kebab-case.
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DAMAGE_RE = re.compile(r"^\d*d\d+([+-]\d+)?$")


def validate_adversary(entry: dict) -> None:
    """Enforce docs/design/12-the-adversary.md section 2's block rules against `entry`.

    Raises `state.StateError`, naming the entry's `id` (if present) and the first rule
    violated -- mirrors `tools/check_bestiary.py`'s `check_entry`, re-expressed here since
    `engine/` must not import `tools/`.
    """
    ident = entry.get("id")
    label = f"adversary {ident!r}" if isinstance(ident, str) else "adversary"

    def fail(field: str, why: str) -> None:
        raise state.StateError(f"{label}: {field}: {why}")

    for field in sorted(REQUIRED_FIELDS - set(entry)):
        fail(field, "required field is missing")
    for field in sorted(set(entry) - ALL_FIELDS):
        fail(field, "field is not defined by the adversary block")

    if not isinstance(ident, str) or not ID_RE.match(ident):
        fail("id", f"{ident!r} is not a stable kebab-case identifier")

    baseline = entry.get("baseline")
    if not isinstance(baseline, int) or isinstance(baseline, bool):
        fail("baseline", f"{baseline!r} is not a percentage")
    elif not SKILL_MIN <= baseline <= SKILL_MAX:
        fail("baseline", f"{baseline} is outside {SKILL_MIN}-{SKILL_MAX}")

    stamina = entry.get("stamina_max")
    if not isinstance(stamina, int) or isinstance(stamina, bool):
        fail("stamina_max", f"{stamina!r} is not a whole number")
    elif stamina < STAMINA_MIN:
        fail("stamina_max", f"{stamina} is below the minimum of {STAMINA_MIN}")

    armour = entry.get("armour")
    if armour not in ARMOUR_RANKS:
        fail("armour", f"{armour!r} is not one of {', '.join(ARMOUR_RANKS)}")

    skills = entry.get("skills")
    if not isinstance(skills, dict) or not skills:
        fail("skills", "must be a non-empty mapping of skill name to percentage")
    else:
        for name, value in skills.items():
            if not isinstance(value, int) or isinstance(value, bool):
                fail(f"skills.{name}", f"{value!r} is not a percentage")
            elif not SKILL_MIN <= value <= SKILL_MAX:
                fail(f"skills.{name}", f"{value} is outside {SKILL_MIN}-{SKILL_MAX}")

    if "damage" in entry and not (
        isinstance(entry["damage"], str) and DAMAGE_RE.match(entry["damage"])
    ):
        fail("damage", f"{entry['damage']!r} is not a dice expression")

    if "damage_type" in entry and entry["damage_type"] not in DAMAGE_TYPES:
        fail("damage_type", f"{entry['damage_type']!r} is not one of {', '.join(DAMAGE_TYPES)}")

    # docs/design/12-the-adversary.md section 2: "damage and damage_type travel together."
    if "damage" in entry and "damage_type" not in entry:
        fail("damage_type", "an opponent that deals damage must declare its type")
    if "damage_type" in entry and "damage" not in entry:
        fail("damage", "an opponent that declares a damage type must also declare its damage")

    if "ranged" in entry and not isinstance(entry["ranged"], bool):
        fail("ranged", f"{entry['ranged']!r} is not true or false")

    if "traits" in entry:
        traits = entry["traits"]
        if not isinstance(traits, list):
            fail("traits", "must be a list")
        for n, trait in enumerate(traits):
            if not isinstance(trait, dict):
                fail(f"traits[{n}]", "is not a mapping")
            if not isinstance(trait.get("name"), str):
                fail(f"traits[{n}].name", "a trait needs a display name")
            effect = trait.get("effect")
            if not isinstance(effect, dict) or not effect:
                fail(f"traits[{n}].effect", "a trait needs a non-empty effect")
            for key in effect:
                if key not in TRAIT_EFFECTS:
                    fail(
                        f"traits[{n}].effect.{key}",
                        "is not in the closed trait vocabulary "
                        f"({', '.join(sorted(TRAIT_EFFECTS))})",
                    )


def load(adversary_id: str, path: pathlib.Path) -> dict:
    """Load and validate the bestiary entry named `adversary_id` from `path`.

    Raises `state.StateError` if `path` cannot be parsed, holds no `creatures:` list, names no
    entry matching `adversary_id`, or that entry fails `validate_adversary`.

    `ranged`, when the entry omits it, defaults to `False` (docs/design/12-the-adversary.md
    section 2: "the default is published rather than assumed").
    """
    path = pathlib.Path(path)
    if not path.exists():
        raise state.StateError(f"{path}: no such bestiary file")
    text = path.read_text(encoding="utf-8")
    try:
        data = state.parse_yaml(text)
    except state.StateError as exc:
        raise state.StateError(f"{path}: {exc}") from exc

    creatures = data.get("creatures") if isinstance(data, dict) else None
    if not isinstance(creatures, list):
        raise state.StateError(f"{path}: expected a top-level 'creatures:' list")

    for entry in creatures:
        if isinstance(entry, dict) and entry.get("id") == adversary_id:
            validate_adversary(entry)
            block = dict(entry)
            block.setdefault("ranged", False)
            return block

    raise state.StateError(f"{path}: no adversary {adversary_id!r} in bestiary")


def resolve_skill(block: dict, skill: str) -> int:
    """docs/design/12-the-adversary.md section 3 ("The baseline"): an adversary tests any skill
    its block does not list at its `baseline`. A listed skill is never raised to the baseline
    -- the baseline answers a question about an absent skill only (specs/095-adversary-baseline-
    resolution).

    Deliberately independent of `rules.UNTRAINED_SKILL`/`select_group_skill` -- the baseline is
    not the untrained rate, and this function shares no constant or code path with that one.
    """
    if skill in block["skills"]:
        return block["skills"][skill]
    return block["baseline"]
