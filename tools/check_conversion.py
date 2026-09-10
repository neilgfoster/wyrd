#!/usr/bin/env python3
"""Validate a setting's conversion table against the conversion.yaml schema.

docs/design/24-authoring-a-setting.md requires any setting derived from an existing system to
carry `setting/conversion.yaml` ("Conversion rules -- required for any derived setting"): without
it, on-demand conversion (docs/design/18-arcs-and-beats.md) is improvised each time, and the same
source converted twice produces different numbers. This is the validator for that schema, in the
same shape as tools/check_bestiary.py and tools/check_gear.py.

It fails loudly on the same classes those two do:

1. **A missing required field** -- `from` and `version` at the top level.
2. **An unrecognised field** -- rejected rather than ignored, at the top level and within each
   known section's own mapping.
3. **A value outside the range the ruleset can absorb** -- a `damage_type` outside the closed
   four (docs/adr/0022), a `method` outside `direct`/`scale`/`table`, a non-positive `version`.

Every failure is reported, not just the first, and every one names the file and the field.

Out of scope: performing an actual conversion (docs/design/18-arcs-and-beats.md's on-demand
conversion process), and per-entity `converted: {rules, on}` provenance stamping (a
chronicle-state concern, not a setting-authoring one).

Usage:
    python3 tools/check_conversion.py <path-to-conversion.yaml> [...]
    python3 tools/check_conversion.py --format json <path>

Python 3.11+, standard library only (docs/design/27-tooling.md section 2). The YAML reader is
tools/check_bestiary.py's own -- imported, not copied, so the two files can't drift on how they
read the same restricted subset.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_bestiary import YamlError, read_yaml  # noqa: E402

# --- The schema, from docs/design/24-authoring-a-setting.md's worked example ------------

TOP_REQUIRED = {"from", "version"}
TOP_OPTIONAL = {
    "skills",
    "difficulty",
    "damage",
    "armour",
    "danger",
    "rename",
    "arcs",
    "drop",
    "drop_note",
    "manual",
}

CONVERSION_METHODS = ("direct", "scale", "table")  # skills.method, armour.method
DAMAGE_TYPES = ("slashing", "piercing", "blunt", "searing")  # docs/adr/0022, closed

SKILLS_FIELDS = {"method", "note", "map"}
ARMOUR_FIELDS = {"method", "map"}
DAMAGE_FIELDS = {"method", "wounds_to_stamina"}
DIFFICULTY_FIELDS = {"map"}
DANGER_FIELDS = {"derive_from", "formula"}


def _is_string_mapping(value) -> bool:
    return isinstance(value, dict) and all(isinstance(k, str) for k in value)


def _is_string_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def check_file(path: pathlib.Path) -> list[str]:
    try:
        data = read_yaml(path)
    except YamlError as exc:
        return [f"{path}: {exc}"]
    except OSError as exc:
        return [f"{path}: {exc}"]

    if not isinstance(data, dict):
        return [f"{path}: expected a top-level mapping"]

    problems: list[str] = []

    def bad(field: str, why: str) -> None:
        problems.append(f"{path}: {field}: {why}")

    for field in sorted(TOP_REQUIRED - set(data)):
        bad(field, "required field is missing")
    for field in sorted(set(data) - TOP_REQUIRED - TOP_OPTIONAL):
        bad(field, "field is not defined by the conversion.yaml schema")

    if "version" in data:
        version = data["version"]
        if isinstance(version, bool) or not isinstance(version, int):
            bad("version", f"{version!r} is not an integer")
        elif version < 1:
            bad("version", f"{version} is not a positive integer")

    if "skills" in data:
        skills = data["skills"]
        if not isinstance(skills, dict):
            bad("skills", "must be a mapping")
        else:
            for field in sorted(set(skills) - SKILLS_FIELDS):
                bad(f"skills.{field}", "field is not defined by the skills schema")
            if "method" in skills and skills["method"] not in CONVERSION_METHODS:
                bad(
                    "skills.method",
                    f"{skills['method']!r} is not one of {', '.join(CONVERSION_METHODS)}",
                )
            if "map" in skills and not _is_string_mapping(skills["map"]):
                bad("skills.map", "must be a mapping of source skill to this setting's skill")

    if "difficulty" in data:
        difficulty = data["difficulty"]
        if not isinstance(difficulty, dict):
            bad("difficulty", "must be a mapping")
        else:
            for field in sorted(set(difficulty) - DIFFICULTY_FIELDS):
                bad(f"difficulty.{field}", "field is not defined by the difficulty schema")
            if "map" in difficulty and not isinstance(difficulty["map"], dict):
                bad("difficulty.map", "must be a mapping")

    if "damage" in data:
        damage = data["damage"]
        if not isinstance(damage, dict):
            bad("damage", "must be a mapping")
        else:
            for field in sorted(set(damage) - DAMAGE_FIELDS):
                bad(f"damage.{field}", "field is not defined by the damage schema")

    if "armour" in data:
        armour = data["armour"]
        if not isinstance(armour, dict):
            bad("armour", "must be a mapping")
        else:
            for field in sorted(set(armour) - ARMOUR_FIELDS):
                bad(f"armour.{field}", "field is not defined by the armour schema")
            if "method" in armour and armour["method"] not in CONVERSION_METHODS:
                bad(
                    "armour.method",
                    f"{armour['method']!r} is not one of {', '.join(CONVERSION_METHODS)}",
                )
            if "map" in armour and not isinstance(armour["map"], dict):
                bad("armour.map", "must be a mapping")

    if "danger" in data:
        danger = data["danger"]
        if not isinstance(danger, dict):
            bad("danger", "must be a mapping")
        else:
            for field in sorted(set(danger) - DANGER_FIELDS):
                bad(f"danger.{field}", "field is not defined by the danger schema")

    if "rename" in data and not _is_string_mapping(data["rename"]):
        bad("rename", "must be a mapping of string to string")

    if "arcs" in data and not _is_string_mapping(data["arcs"]):
        bad("arcs", "must be a mapping of string to string")

    if "drop" in data and not _is_string_list(data["drop"]):
        bad("drop", "must be a list of strings")

    if "drop_note" in data and not isinstance(data["drop_note"], str):
        bad("drop_note", "must be a string")

    if "manual" in data and not _is_string_list(data["manual"]):
        bad("manual", "must be a list of strings")

    # Any damage_type value appearing anywhere in the file is checked against the closed four
    # (docs/adr/0022) -- the schema names one specific spot (damage.wounds_to_stamina may itself
    # be a damage type when a source's wound categories map directly onto Wyrd's), but a setting
    # is free to fold damage_type into other blocks it defines, so this walks the whole document.
    def _walk_for_damage_types(value, where: str) -> None:
        if isinstance(value, dict):
            for key, sub in value.items():
                if key == "damage_type" and sub not in DAMAGE_TYPES:
                    bad(
                        f"{where}.damage_type" if where else "damage_type",
                        f"{sub!r} is not one of {', '.join(DAMAGE_TYPES)}",
                    )
                _walk_for_damage_types(sub, f"{where}.{key}" if where else key)
        elif isinstance(value, list):
            for n, item in enumerate(value):
                _walk_for_damage_types(item, f"{where}[{n}]")

    _walk_for_damage_types(data, "")

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    problems: list[str] = []
    for path in args.paths:
        problems.extend(check_file(path))

    if args.format == "json":
        print(json.dumps({"ok": not problems, "problems": problems}, indent=2))
    elif problems:
        print(f"FAILED ({len(problems)}):")
        for problem in problems:
            print(f"  - {problem}")
    else:
        checked = ", ".join(str(p) for p in args.paths)
        print(f"conversion.yaml holds. ({checked})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
