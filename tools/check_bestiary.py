#!/usr/bin/env python3
"""Validate a setting's bestiary against the adversary block.

docs/design/26-authoring-a-setting.md named `setting/bestiary.yaml` as a setting file for as long as
that document has existed, and never said what went in it. So a setting author had no contract to
fill, and five separate rules had been reading fields off an opponent that belonged to no schema
-- most sharply the crowd rule (docs/adr/0019), which calls itself "a lookup, and nothing else"
over three of them.

This is the validator for docs/design/06-the-adversary.md. It fails loudly on four classes:

1. **A missing required field.** The block is what the ruleset reads; a block missing a field is
   an opponent the GM has to improvise, which is the fault the block exists to remove.
2. **An unrecognised field.** Rejected rather than ignored. A setting may extend, retune, rename
   or disable, and may never add a mechanism (docs/design/26-authoring-a-setting.md); an unrecognised
   field is the quiet path by which one gets added anyway.
3. **A value outside the range the ruleset can absorb** -- an armour rank outside the published
   set, a damage type outside the closed four (docs/adr/0022), a percentage off the scale.
4. **A trait effect outside the closed vocabulary**, for the same reason as 2.

Every failure is reported, not just the first, and every one names the entry and the field.

Usage:
    python3 tools/check_bestiary.py <path-to-bestiary.yaml> [...]
    python3 tools/check_bestiary.py --format json <path>

Python 3.11+, standard library only (docs/design/20-tooling.md section 2). YAML is read by the small
internal reader below, for the restricted subset Wyrd uses -- there is deliberately no
third-party YAML dependency.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re

# --- The block, from docs/design/06-the-adversary.md ----------------------------

REQUIRED_FIELDS = {"id", "name", "baseline", "stamina_max", "armour", "skills"}
OPTIONAL_FIELDS = {"damage", "damage_type", "ranged", "traits", "notes"}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

ARMOUR_RANKS = ("none", "light", "modest", "heavy")        # docs/design/03-rules.md section 2
DAMAGE_TYPES = ("slashing", "piercing", "blunt", "searing")  # docs/adr/0022, closed

# docs/design/04-the-character.md section 2: a percentage is what the engine rolls against. 0 is
# legal -- section 7's scaling floor reaches it -- and nothing rolls above 100.
SKILL_MIN, SKILL_MAX = 0, 100
STAMINA_MIN = 1

# The closed trait vocabulary. Every effect acts on a mechanism that already exists.
TRAIT_EFFECTS = {
    "difficulty": "shifts the difficulty of a named class of test, in ladder rungs",
    "damage": "adds or removes damage dice on this opponent's blows",
    "damage_type": "fixes the damage type of this opponent's blows",
    "stamina_max": "raises or lowers maximum Stamina",
    "armour_rank": "raises or lowers the armour rank by whole ranks",
    "wyrd": "widens the Ill Omen or Fair Omen band on tests against this opponent",
}

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")            # docs/design/27-entities.md: kebab-case
DAMAGE_RE = re.compile(r"^\d*d\d+([+-]\d+)?$")


# --- The small internal reader ----------------------------------------------
# The restricted subset: nested mappings, lists of mappings or scalars, scalars, comments,
# blank lines. Indentation must be consistent within a block, but its width is free, and a
# sequence may sit either indented under its key or at the key's own indentation -- both are
# legal YAML and both get written. Anything outside the subset is an error rather than a guess.


class YamlError(Exception):
    pass


def _scalar(text: str):
    text = text.strip()
    if text in ("true", "false"):
        return text == "true"
    if text in ("null", "~", ""):
        return None
    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    return text


def _parse_block(lines: list[tuple[int, int, str]], start: int, indent: int):
    """Parse one block at the given indentation. Returns (value, next_index)."""
    i = start
    items: list = []
    mapping: dict = {}
    while i < len(lines):
        lineno, ind, text = lines[i]
        if ind < indent:
            break
        if ind > indent:
            raise YamlError(f"line {lineno}: unexpected indentation")
        if items and not text.startswith("- "):
            # A sequence sitting at its parent key's indentation ends where the parent's next
            # key begins. Without this the next key would be read as part of the list.
            break
        if text.startswith("- "):
            rest = text[2:].strip()
            if ":" in rest and not rest.startswith(("\"", "'")):
                # a list item that opens a mapping: rewrite it as the first key of a block
                key, _, val = rest.partition(":")
                sub_lines = [(lineno, indent + 2, f"{key.strip()}:{val}")]
                j = i + 1
                while j < len(lines) and lines[j][1] > indent:
                    sub_lines.append(lines[j])
                    j += 1
                value, _ = _parse_block(sub_lines, 0, indent + 2)
                items.append(value)
                i = j
                continue
            items.append(_scalar(rest))
            i += 1
            continue
        if ":" not in text:
            raise YamlError(f"line {lineno}: expected 'key: value' or '- item'")
        key, _, val = text.partition(":")
        key = key.strip()
        val = val.strip()
        if val:
            mapping[key] = _scalar(val)
            i += 1
            continue
        # a nested block follows
        j = i + 1
        if j < len(lines) and lines[j][1] > indent:
            value, j = _parse_block(lines, j, lines[j][1])
            mapping[key] = value
        elif j < len(lines) and lines[j][1] == indent and lines[j][2].startswith("- "):
            # YAML lets a sequence share its parent key's indentation, and plenty of people
            # write it that way. Rejecting it fails closed, but it rejects a correct file with
            # a message pointing nowhere near the cause.
            value, j = _parse_block(lines, j, indent)
            mapping[key] = value
        else:
            mapping[key] = None
        i = j
    if items and mapping:
        raise YamlError("a block is either a list or a mapping, never both")
    return (items if items else mapping), i


def read_yaml(path: pathlib.Path):
    raw = path.read_text(encoding="utf-8").splitlines()
    lines: list[tuple[int, int, str]] = []
    for lineno, line in enumerate(raw, 1):
        if "#" in line:
            line = line.split("#", 1)[0]
        if not line.strip():
            continue
        if line.lstrip().startswith("---"):
            continue
        lines.append((lineno, len(line) - len(line.lstrip()), line.strip()))
    if not lines:
        return {}
    value, _ = _parse_block(lines, 0, lines[0][1])
    return value


# --- The checks --------------------------------------------------------------


def check_entry(entry, where: str) -> list[str]:
    problems: list[str] = []

    if not isinstance(entry, dict):
        return [f"{where}: entry is not a mapping"]

    ident = entry.get("id")
    label = f"{where}[{ident}]" if isinstance(ident, str) else where

    def bad2(field: str, why: str) -> None:
        problems.append(f"{label}: {field}: {why}")

    for field in sorted(REQUIRED_FIELDS - set(entry)):
        bad2(field, "required field is missing")
    for field in sorted(set(entry) - ALL_FIELDS):
        bad2(field, "field is not defined by the adversary block")

    if isinstance(ident, str) and not ID_RE.match(ident):
        bad2("id", f"{ident!r} is not a stable kebab-case identifier")

    baseline = entry.get("baseline")
    if "baseline" in entry:
        if not isinstance(baseline, int) or isinstance(baseline, bool):
            bad2("baseline", f"{baseline!r} is not a percentage")
        elif not SKILL_MIN <= baseline <= SKILL_MAX:
            bad2("baseline", f"{baseline} is outside {SKILL_MIN}-{SKILL_MAX}")

    stamina = entry.get("stamina_max")
    if "stamina_max" in entry:
        if not isinstance(stamina, int) or isinstance(stamina, bool):
            bad2("stamina_max", f"{stamina!r} is not a whole number")
        elif stamina < STAMINA_MIN:
            bad2("stamina_max", f"{stamina} is below the minimum of {STAMINA_MIN}")

    armour = entry.get("armour")
    if "armour" in entry and armour not in ARMOUR_RANKS:
        bad2("armour", f"{armour!r} is not one of {', '.join(ARMOUR_RANKS)}")

    skills = entry.get("skills")
    if "skills" in entry:
        if not isinstance(skills, dict) or not skills:
            bad2("skills", "must be a non-empty mapping of skill name to percentage")
        else:
            for name, value in skills.items():
                if not isinstance(value, int) or isinstance(value, bool):
                    bad2(f"skills.{name}", f"{value!r} is not a percentage")
                elif not SKILL_MIN <= value <= SKILL_MAX:
                    bad2(f"skills.{name}", f"{value} is outside {SKILL_MIN}-{SKILL_MAX}")

    if "damage" in entry and not (isinstance(entry["damage"], str)
                                  and DAMAGE_RE.match(entry["damage"])):
        bad2("damage", f"{entry['damage']!r} is not a dice expression")

    if "damage_type" in entry and entry["damage_type"] not in DAMAGE_TYPES:
        bad2("damage_type", f"{entry['damage_type']!r} is not one of "
                            f"{', '.join(DAMAGE_TYPES)}")

    # An opponent that deals damage must say what kind, or the critical table cannot be
    # selected without a judgement call -- which is the whole point of the block.
    if "damage" in entry and "damage_type" not in entry:
        bad2("damage_type", "an opponent that deals damage must declare its type")

    if "ranged" in entry and not isinstance(entry["ranged"], bool):
        bad2("ranged", f"{entry['ranged']!r} is not true or false")

    traits = entry.get("traits")
    if "traits" in entry:
        if not isinstance(traits, list):
            bad2("traits", "must be a list")
        else:
            for n, trait in enumerate(traits):
                if not isinstance(trait, dict):
                    bad2(f"traits[{n}]", "is not a mapping")
                    continue
                if not isinstance(trait.get("name"), str):
                    bad2(f"traits[{n}].name", "a trait needs a display name")
                effect = trait.get("effect")
                if not isinstance(effect, dict) or not effect:
                    bad2(f"traits[{n}].effect", "a trait needs a non-empty effect")
                    continue
                for key in effect:
                    if key not in TRAIT_EFFECTS:
                        bad2(f"traits[{n}].effect.{key}",
                             "is not in the closed trait vocabulary "
                             f"({', '.join(sorted(TRAIT_EFFECTS))})")
    return problems


def check_file(path: pathlib.Path) -> list[str]:
    try:
        data = read_yaml(path)
    except YamlError as exc:
        return [f"{path}: {exc}"]
    except OSError as exc:
        return [f"{path}: {exc}"]

    if not isinstance(data, dict) or "creatures" not in data:
        return [f"{path}: expected a top-level 'creatures:' list"]
    creatures = data["creatures"]
    if not isinstance(creatures, list) or not creatures:
        return [f"{path}: 'creatures' must be a non-empty list"]

    problems: list[str] = []
    seen: dict[str, int] = {}
    for n, entry in enumerate(creatures):
        problems.extend(check_entry(entry, f"{path}:creatures[{n}]"))
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            if entry["id"] in seen:
                problems.append(
                    f"{path}:creatures[{n}][{entry['id']}]: id: duplicates "
                    f"creatures[{seen[entry['id']]}] -- an id is stable and unique"
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
        print(f"All bestiary entries hold. ({checked})")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
