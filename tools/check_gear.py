#!/usr/bin/env python3
"""Validate a setting's gear against the weapon and armour schema.

docs/design/26-authoring-a-setting.md named `setting/gear.yaml` as a setting file for as long as that
document has existed, promising "weapons, armour, prices, what is legal to carry where," and
never said what a gear entry declares -- even though docs/design/03-rules.md section 2 already reads
weapon damage, armour rank and the casual/martial distinction off it. This is the validator for
that schema (specs/023-standing-material-economy/data-model.md), in the same shape as
tools/check_bestiary.py -- reused here rather than reinvented, since gear reads into the same
combat fields (damage, damage type, armour rank) the adversary block already validates.

It fails loudly on the same four classes check_bestiary.py does:

1. **A missing required field.**
2. **An unrecognised field** -- rejected rather than ignored (docs/design/26-authoring-a-setting.md: a
   setting may extend, retune, rename or disable, and may never add a mechanism).
3. **A value outside the range the ruleset can absorb** -- an armour rank outside the published
   set, a damage type outside the closed four (docs/adr/0022), a negative price.
4. **A `class` outside the closed casual/martial vocabulary.**

Every failure is reported, not just the first, and every one names the entry and the field.

Usage:
    python3 tools/check_gear.py <path-to-gear.yaml> [...]
    python3 tools/check_gear.py --format json <path>

Python 3.11+, standard library only (docs/design/20-tooling.md section 2). The YAML reader is
tools/check_bestiary.py's own -- imported, not copied, so the two files can't drift on how they
read the same restricted subset.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_bestiary import YamlError, read_yaml  # noqa: E402

# --- The schema, from specs/023-standing-material-economy/data-model.md -----

WEAPON_REQUIRED = {"id", "name", "kind", "damage", "damage_type", "class", "price",
                    "availability"}
ARMOUR_REQUIRED = {"id", "name", "kind", "rank", "price", "availability"}
COMMON_OPTIONAL = {"notes"}

ARMOUR_RANKS = ("none", "light", "modest", "heavy")          # docs/design/03-rules.md section 2
DAMAGE_TYPES = ("slashing", "piercing", "blunt", "searing")  # docs/adr/0022, closed
WEAPON_CLASSES = ("casual", "martial")                        # docs/design/03-rules.md section 2

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")               # docs/design/27-entities.md: kebab-case
DAMAGE_RE = re.compile(r"^\d*d\d+([+-]\d+)?$")


def check_entry(entry, where: str) -> list[str]:
    problems: list[str] = []

    if not isinstance(entry, dict):
        return [f"{where}: entry is not a mapping"]

    ident = entry.get("id")
    label = f"{where}[{ident}]" if isinstance(ident, str) else where

    def bad(field: str, why: str) -> None:
        problems.append(f"{label}: {field}: {why}")

    kind = entry.get("kind")
    if kind not in ("weapon", "armour"):
        bad("kind", f"{kind!r} is not one of weapon, armour")
        return problems  # nothing else can be checked without knowing which schema applies

    required = WEAPON_REQUIRED if kind == "weapon" else ARMOUR_REQUIRED
    all_fields = required | COMMON_OPTIONAL

    for field in sorted(required - set(entry)):
        bad(field, "required field is missing")
    for field in sorted(set(entry) - all_fields):
        bad(field, "field is not defined by the gear schema")

    if isinstance(ident, str) and not ID_RE.match(ident):
        bad("id", f"{ident!r} is not a stable kebab-case identifier")

    if "price" in entry:
        price = entry["price"]
        if isinstance(price, bool) or not isinstance(price, (int, float)):
            bad("price", f"{price!r} is not a number")
        elif price < 0:
            bad("price", f"{price} is negative")

    if "availability" in entry and not isinstance(entry["availability"], str):
        bad("availability", f"{entry['availability']!r} is not a string")

    if kind == "weapon":
        if "damage" in entry and not (isinstance(entry["damage"], str)
                                      and DAMAGE_RE.match(entry["damage"])):
            bad("damage", f"{entry['damage']!r} is not a dice expression")
        if "damage_type" in entry and entry["damage_type"] not in DAMAGE_TYPES:
            bad("damage_type", f"{entry['damage_type']!r} is not one of "
                                f"{', '.join(DAMAGE_TYPES)}")
        if "class" in entry and entry["class"] not in WEAPON_CLASSES:
            bad("class", f"{entry['class']!r} is not one of {', '.join(WEAPON_CLASSES)}")
    else:
        if "rank" in entry and entry["rank"] not in ARMOUR_RANKS:
            bad("rank", f"{entry['rank']!r} is not one of {', '.join(ARMOUR_RANKS)}")

    return problems


def check_file(path: pathlib.Path) -> list[str]:
    try:
        data = read_yaml(path)
    except YamlError as exc:
        return [f"{path}: {exc}"]
    except OSError as exc:
        return [f"{path}: {exc}"]

    if not isinstance(data, dict) or "gear" not in data:
        return [f"{path}: expected a top-level 'gear:' list"]
    gear = data["gear"]
    if not isinstance(gear, list) or not gear:
        return [f"{path}: 'gear' must be a non-empty list"]

    problems: list[str] = []
    seen: dict[str, int] = {}
    for n, entry in enumerate(gear):
        problems.extend(check_entry(entry, f"{path}:gear[{n}]"))
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            if entry["id"] in seen:
                problems.append(
                    f"{path}:gear[{n}][{entry['id']}]: id: duplicates "
                    f"gear[{seen[entry['id']]}] -- an id is stable and unique"
                )
            seen[entry["id"]] = n
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
        print(f"All gear entries hold. ({checked})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
