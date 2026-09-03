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

import math
import pathlib
import re
from fractions import Fraction

from wyrd import resolution, state

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
DAMAGE_RE = re.compile(r"^(\d*)d(\d+)([+-]\d+)?$")

#: docs/design/03-rules.md section 1's difficulty ladder, in order -- reused rather than
#: re-declared, so this module's ladder can never drift from resolution.py's own
#: (specs/096-adversary-trait-effects research.md).
DIFFICULTY_LADDER = tuple(resolution.DIFFICULTY_BONUSES)


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


def _trait_effect_values(traits: list[dict] | None, key: str) -> list:
    """Every value a `traits` list carries for one effect `key`, in order -- shared by every
    trait computation below (specs/096-adversary-trait-effects)."""
    return [trait["effect"][key] for trait in (traits or []) if key in trait.get("effect", {})]


def shift_difficulty(base: str, rungs: int) -> str:
    """docs/design/12-the-adversary.md section 5: a `difficulty` trait "shifts the difficulty
    of a named class of test, in ladder rungs." Steps `base` along `DIFFICULTY_LADDER` by
    `rungs` positions -- mirroring `DIFFICULTY_BONUSES`'s own sign (a harder step carries a more
    negative bonus), a negative `rungs` moves toward the ladder's harder end, a positive one
    toward its easier end -- clamped at either end rather than raising: overshooting the ladder
    simply floors/ceilings (specs/096-adversary-trait-effects).
    """
    index = DIFFICULTY_LADDER.index(base) - rungs
    index = max(0, min(len(DIFFICULTY_LADDER) - 1, index))
    return DIFFICULTY_LADDER[index]


def wyrd_band_width(block: dict) -> int:
    """docs/design/12-the-adversary.md section 5: a `wyrd` trait "widens the Ill Omen or Fair
    Omen band on tests against this opponent." The total width to pass as
    `rules.opposed_test`'s `omen_width` (specs/096-adversary-trait-effects) -- never negative."""
    return max(0, sum(_trait_effect_values(block.get("traits"), "wyrd")))


def _adjust_damage_dice(expression: str, delta: int) -> str:
    """Adjust `expression`'s dice count by `delta`, floored at one die; die size and any flat
    modifier are unchanged (specs/096-adversary-trait-effects, docs/design/12-the-adversary.md
    section 5's `damage` trait)."""
    match = DAMAGE_RE.match(expression)
    count_text, size, modifier = match.group(1), match.group(2), match.group(3) or ""
    count = int(count_text) if count_text else 1
    count = max(1, count + delta)
    return f"{count}d{size}{modifier}"


def effective_block(block: dict) -> dict:
    """docs/design/12-the-adversary.md section 5: fold `block`'s active traits' `stamina_max`/
    `armour_rank`/`damage`/`damage_type` effects into a new block -- never mutating `block`
    itself. Multiple traits naming the same effect stack (sum); a `damage`/`damage_type` trait
    with nothing to adjust (no `damage` on the block at all) is simply inert
    (specs/096-adversary-trait-effects).

    `difficulty` and `wyrd` traits are not folded in here -- see `shift_difficulty` and
    `wyrd_band_width`, applied by the caller at the point each is actually needed.
    """
    traits = block.get("traits")
    result = dict(block)

    stamina_delta = sum(_trait_effect_values(traits, "stamina_max"))
    if stamina_delta:
        result["stamina_max"] = max(STAMINA_MIN, block["stamina_max"] + stamina_delta)

    armour_delta = sum(_trait_effect_values(traits, "armour_rank"))
    if armour_delta:
        index = ARMOUR_RANKS.index(block["armour"]) + armour_delta
        result["armour"] = ARMOUR_RANKS[max(0, min(len(ARMOUR_RANKS) - 1, index))]

    if "damage" in block:
        damage_delta = sum(_trait_effect_values(traits, "damage"))
        if damage_delta:
            result["damage"] = _adjust_damage_dice(block["damage"], damage_delta)

    damage_type_overrides = _trait_effect_values(traits, "damage_type")
    if damage_type_overrides:
        result["damage_type"] = damage_type_overrides[-1]

    return result


#: docs/design/03-rules.md section 7: "The adjustment is 15.5 x log2(ratio)" -- the published
#: coefficient a GM reads off the design document, not re-derived here (specs/098-encounter-
#: danger-scaling: `specs/017-adversary-model/check_adversary.py` already established that the
#: fitted and published coefficients agree to the precision the ladder rounds to).
SKILL_ADJUSTMENT_COEFFICIENT = 15.5

#: docs/design/03-rules.md section 1: the ladder's whole positive extent, and the symmetric clip
#: docs/design/03-rules.md section 7 puts on the skill adjustment.
SKILL_ADJUSTMENT_CLIP = 20

#: docs/design/03-rules.md section 6: the finest unit a skill moves by at all.
SKILL_ADJUSTMENT_STEP = 5


def effective_party_size(bodies: int) -> Fraction:
    """docs/design/03-rules.md section 7: "The k-th body is worth 1/k." The effective size of a
    party of `bodies` bodies is `1 + 1/2 + ... + 1/bodies`, exact -- never a rounded float
    (ADR 0024). `bodies <= 0` is a party of none, worth nothing (specs/098-encounter-danger-
    scaling)."""
    return sum((Fraction(1, k) for k in range(1, bodies + 1)), Fraction(0))


def danger_ratio(party: int, written_for: int | None) -> Fraction:
    """docs/design/03-rules.md section 7: "Both sides of the ratio are read through that same
    function." Where `written_for` is missing or zero, the content runs as written, so the
    ratio is exactly 1 rather than a division by zero (specs/098-encounter-danger-scaling)."""
    if not written_for:
        return Fraction(1)
    return effective_party_size(party) / effective_party_size(written_for)


def danger_effective(danger: int, party: int, written_for: int | None) -> Fraction:
    """docs/design/03-rules.md section 7: `danger_effective = danger x (party_effective /
    written_for_effective)`, carried exact and never rounded mid-calculation (ADR 0024)."""
    return danger * danger_ratio(party, written_for)


def scaled_count(written_count: int, danger: int, party: int, written_for: int | None) -> int:
    """docs/design/03-rules.md section 7: a written opponent count scaled to `danger_effective`,
    "round half up, and never below 1 where the written quantity was at least 1" -- a written
    count of 0 is an unused quantity and stays 0 (specs/098-encounter-danger-scaling)."""
    exact = Fraction(written_count) * danger_effective(danger, party, written_for) / danger
    rounded = math.floor(float(exact) + 0.5)
    return max(1, rounded) if written_count >= 1 else rounded


def skill_adjustment(party: int, written_for: int | None) -> int:
    """docs/design/03-rules.md section 7: "The adjustment is 15.5 x log2(ratio), rounded to the
    nearest 5 and clipped to +-20" -- the points added to an opponent's percentage when content
    is prepared for a party other than the one it was written for. A party of none (`party <= 0`)
    has a ratio of exactly 0, whose log is undefined -- that is the ladder's own bottom rung, so
    it clips to the same -20 an arbitrarily small positive ratio would (specs/098-encounter-
    danger-scaling)."""
    ratio = danger_ratio(party, written_for)
    if ratio <= 0:
        return -SKILL_ADJUSTMENT_CLIP
    raw = SKILL_ADJUSTMENT_COEFFICIENT * math.log2(float(ratio))
    rounded = math.floor(raw / SKILL_ADJUSTMENT_STEP + 0.5) * SKILL_ADJUSTMENT_STEP
    return max(-SKILL_ADJUSTMENT_CLIP, min(SKILL_ADJUSTMENT_CLIP, rounded))


def adjusted_skill(block: dict, skill: str, party: int, written_for: int | None) -> int:
    """docs/design/03-rules.md section 7: the opponent's percentage as it is actually tested --
    its baseline-resolved value (#260's `resolve_skill`) plus `skill_adjustment`, floored at 0
    (a percentage is not a negative number; docs/design/03-rules.md section 1). Never mutates
    `block` (docs/design/12-the-adversary.md section 6: "the block is absolute")."""
    return max(0, resolve_skill(block, skill) + skill_adjustment(party, written_for))
