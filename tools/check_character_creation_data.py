#!/usr/bin/env python3
"""Validate a setting's whole character-creation data surface, not one file at a time.

docs/design/11-character-creation.md section 4 lists what a setting must supply before creation
can run: entry careers, names, places, Drives, Misfortunes, and Loyalties (plus an optional
ancestry declaration, section 3). docs/design/24-authoring-a-setting.md schemas `careers.yaml` and
`gear.yaml`, but until this script existed nothing checked `careers.yaml` against its own
documented shape, and `loyalties.yaml`, `drives.yaml`, `misfortunes.yaml`, `names.yaml` and
`ancestries.yaml` had no schema at all -- only prose promises.
specs/146-setting-character-creation-data closes that gap: this is the validator for all six
files together, because character creation reads them together and a setting missing one of them
cannot run the procedure at all.

Checked, per specs/146-setting-character-creation-data/data-model.md:

- `careers.yaml` (required): every entry has id/entry/skills; entry:true carries no
  prerequisites and entry:false carries at least one; at least one entry career exists; every
  prerequisite names a career declared in the same file; the prerequisite graph is acyclic; no
  duplicate id.
- `loyalties.yaml` (required): at least one Loyalty; each relation names two distinct, declared
  Loyalties and a kind from the closed vocabulary (docs/adr/0015); no relation pair declared
  twice, in either order.
- `drives.yaml` / `misfortunes.yaml` (required): non-empty; each entry has a unique id and
  non-empty text.
- `names.yaml` (required): at least one culture; each culture has a unique id and at least one
  non-empty given/family/place list.
- `ancestries.yaml` (optional -- absence is not an error, docs/design/11-character-creation.md
  section 3): when present, each entry has a unique id and a non-empty skills list.

Every failure is reported, not just the first, and every one names the file and the field.

Usage:
    python3 tools/check_character_creation_data.py <path-to-setting-dir> [...]
    python3 tools/check_character_creation_data.py --format json <path-to-setting-dir>

This validates the *schema* a setting's files must satisfy -- it never populates one. Filling in
wyrd-setting-template's skeleton, or any real wyrd-setting-<name>'s actual careers/loyalties/
drives/misfortunes/names/ancestries, happens in those repositories, not this one (CLAUDE.md's
repository table).

Python 3.11+, standard library only (docs/design/27-tooling.md section 2). YAML is read by
tools/check_bestiary.py's own reader -- imported, not copied, so this script can't drift from the
others on how the same restricted subset is read.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from check_bestiary import YamlError, read_yaml  # noqa: E402

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # docs/design/25-entities.md: kebab-case

# docs/adr/0015-loyalty-has-three-relations-not-two.md: only the non-default pair is ever written
# down; "undeclared" is simply the absence of a relation entry, never a value of its own.
RELATION_KINDS = ("strained", "irreconcilable")

CAREERS_FILE = "careers.yaml"
LOYALTIES_FILE = "loyalties.yaml"
DRIVES_FILE = "drives.yaml"
MISFORTUNES_FILE = "misfortunes.yaml"
NAMES_FILE = "names.yaml"
ANCESTRIES_FILE = "ancestries.yaml"

REQUIRED_FILES = (CAREERS_FILE, LOYALTIES_FILE, DRIVES_FILE, MISFORTUNES_FILE, NAMES_FILE)
OPTIONAL_FILES = (ANCESTRIES_FILE,)


def _load(path: pathlib.Path) -> tuple[dict | None, list[str]]:
    """Read one YAML file, returning (data, problems). data is None on a read/parse failure."""
    try:
        data = read_yaml(path)
    except YamlError as exc:
        return None, [f"{path}: {exc}"]
    except OSError as exc:
        return None, [f"{path}: {exc}"]
    if not isinstance(data, dict):
        return None, [f"{path}: expected a top-level mapping"]
    return data, []


def _check_id(entry: dict, where: str, problems: list[str]) -> str | None:
    ident = entry.get("id")
    if not isinstance(ident, str):
        problems.append(f"{where}: id: missing or not a string")
        return None
    if not ID_RE.match(ident):
        problems.append(f"{where}: id: {ident!r} is not a stable kebab-case identifier")
    return ident


def _check_duplicate_ids(entries: list, path: pathlib.Path, label: str) -> list[str]:
    problems: list[str] = []
    seen: dict[str, int] = {}
    for n, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        ident = entry.get("id")
        if isinstance(ident, str):
            if ident in seen:
                problems.append(
                    f"{path}:{label}[{n}][{ident}]: id: duplicates {label}[{seen[ident]}]"
                )
            else:
                seen[ident] = n
    return problems


# --- careers.yaml ------------------------------------------------------------------------


def check_careers(path: pathlib.Path) -> list[str]:
    data, problems = _load(path)
    if data is None:
        return problems
    if "careers" not in data or not isinstance(data["careers"], list) or not data["careers"]:
        return [f"{path}: expected a top-level non-empty 'careers:' list"]

    careers = data["careers"]
    ids: set[str] = set()
    entry_flags: dict[str, bool] = {}
    prereqs: dict[str, list[str]] = {}
    has_entry_career = False

    for n, entry in enumerate(careers):
        where = f"{path}:careers[{n}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: entry is not a mapping")
            continue
        ident = _check_id(entry, where, problems)
        label = f"{path}:careers[{n}][{ident}]" if ident else where

        missing = {"id", "entry", "skills"} - set(entry)
        for field in sorted(missing):
            problems.append(f"{label}: {field}: required field is missing")

        skills = entry.get("skills")
        if "skills" in entry and (not isinstance(skills, list) or not skills):
            problems.append(f"{label}: skills: must be a non-empty list")

        is_entry = entry.get("entry")
        if "entry" in entry and not isinstance(is_entry, bool):
            problems.append(f"{label}: entry: {is_entry!r} is not a boolean")
        elif is_entry is True:
            has_entry_career = True
            if "prerequisites" in entry:
                problems.append(f"{label}: prerequisites: must be absent when entry is true")
        elif is_entry is False:
            prereq_list = entry.get("prerequisites")
            if not isinstance(prereq_list, list) or not prereq_list:
                problems.append(
                    f"{label}: prerequisites: required and non-empty when entry is false"
                )
            else:
                prereqs[ident] = [p for p in prereq_list if isinstance(p, str)]

        if ident:
            ids.add(ident)
            if isinstance(is_entry, bool):
                entry_flags[ident] = is_entry

    problems.extend(_check_duplicate_ids(careers, path, "careers"))

    if not has_entry_career:
        problems.append(f"{path}: no career declares entry: true -- creation has nowhere to start")

    for ident, plist in prereqs.items():
        for p in plist:
            if p not in ids:
                problems.append(
                    f"{path}:careers[{ident}]: prerequisites: {p!r} names no career in this file"
                )

    # Acyclic check: a career is unreachable only if every path through its prerequisites
    # eventually requires the career itself (docs/design/24-authoring-a-setting.md).
    def reachable_to_entry(start: str, seen: set[str]) -> bool:
        if entry_flags.get(start) is True:
            return True
        if start in seen:
            return False
        seen = seen | {start}
        for p in prereqs.get(start, []):
            if p in ids and reachable_to_entry(p, seen):
                return True
        return False

    for ident in prereqs:
        if not reachable_to_entry(ident, set()):
            problems.append(
                f"{path}:careers[{ident}]: prerequisites: unreachable -- every path cycles "
                "back to this career without ever reaching an entry career"
            )

    return problems


# --- loyalties.yaml ------------------------------------------------------------------------


def check_loyalties(path: pathlib.Path) -> list[str]:
    data, problems = _load(path)
    if data is None:
        return problems
    if "loyalties" not in data or not isinstance(data["loyalties"], list) or not data["loyalties"]:
        return [f"{path}: expected a top-level non-empty 'loyalties:' list"]

    loyalties = data["loyalties"]
    ids: set[str] = set()
    for n, entry in enumerate(loyalties):
        where = f"{path}:loyalties[{n}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: entry is not a mapping")
            continue
        ident = _check_id(entry, where, problems)
        if ident:
            ids.add(ident)
    problems.extend(_check_duplicate_ids(loyalties, path, "loyalties"))

    relations = data.get("relations", [])
    if relations and not isinstance(relations, list):
        problems.append(f"{path}: 'relations' must be a list")
        relations = []

    seen_pairs: set[frozenset] = set()
    for n, rel in enumerate(relations):
        where = f"{path}:relations[{n}]"
        if not isinstance(rel, dict):
            problems.append(f"{where}: entry is not a mapping")
            continue
        a, b, kind = rel.get("a"), rel.get("b"), rel.get("kind")
        missing = {"a", "b", "kind"} - set(rel)
        for field in sorted(missing):
            problems.append(f"{where}: {field}: required field is missing")
        if isinstance(a, str) and a not in ids:
            problems.append(f"{where}: a: {a!r} names no declared Loyalty")
        if isinstance(b, str) and b not in ids:
            problems.append(f"{where}: b: {b!r} names no declared Loyalty")
        if isinstance(a, str) and isinstance(b, str) and a == b:
            problems.append(f"{where}: a Loyalty cannot be {kind!r} with itself ({a!r})")
        if kind is not None and kind not in RELATION_KINDS:
            problems.append(f"{where}: kind: {kind!r} is not one of {', '.join(RELATION_KINDS)}")
        if isinstance(a, str) and isinstance(b, str):
            pair = frozenset((a, b))
            if pair in seen_pairs:
                problems.append(f"{where}: relation between {a!r} and {b!r} is declared twice")
            seen_pairs.add(pair)

    return problems


# --- drives.yaml / misfortunes.yaml ---------------------------------------------------------


def check_text_list(path: pathlib.Path, top_key: str) -> list[str]:
    data, problems = _load(path)
    if data is None:
        return problems
    if top_key not in data or not isinstance(data[top_key], list) or not data[top_key]:
        return [f"{path}: expected a top-level non-empty '{top_key}:' list"]

    entries = data[top_key]
    for n, entry in enumerate(entries):
        where = f"{path}:{top_key}[{n}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: entry is not a mapping")
            continue
        _check_id(entry, where, problems)
        text = entry.get("text")
        if "text" not in entry:
            problems.append(f"{where}: text: required field is missing")
        elif not isinstance(text, str) or not text.strip():
            problems.append(f"{where}: text: must be a non-empty string")
    problems.extend(_check_duplicate_ids(entries, path, top_key))
    return problems


# --- names.yaml ------------------------------------------------------------------------


NAME_POOL_FIELDS = ("given", "family", "place")


def check_names(path: pathlib.Path) -> list[str]:
    data, problems = _load(path)
    if data is None:
        return problems
    if "cultures" not in data or not isinstance(data["cultures"], list) or not data["cultures"]:
        return [f"{path}: expected a top-level non-empty 'cultures:' list"]

    cultures = data["cultures"]
    for n, entry in enumerate(cultures):
        where = f"{path}:cultures[{n}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: entry is not a mapping")
            continue
        _check_id(entry, where, problems)
        has_pool = False
        for field in NAME_POOL_FIELDS:
            if field in entry:
                pool = entry[field]
                if not isinstance(pool, list):
                    problems.append(f"{where}: {field}: must be a list")
                elif pool:
                    has_pool = True
        if not has_pool:
            problems.append(
                f"{where}: none of {', '.join(NAME_POOL_FIELDS)} is a non-empty list -- "
                "this culture cannot name anyone"
            )
    problems.extend(_check_duplicate_ids(cultures, path, "cultures"))
    return problems


# --- ancestries.yaml (optional) ---------------------------------------------------------


def check_ancestries(path: pathlib.Path) -> list[str]:
    data, problems = _load(path)
    if data is None:
        return problems
    if (
        "ancestries" not in data
        or not isinstance(data["ancestries"], list)
        or not data["ancestries"]
    ):
        return [f"{path}: expected a top-level non-empty 'ancestries:' list"]

    ancestries = data["ancestries"]
    for n, entry in enumerate(ancestries):
        where = f"{path}:ancestries[{n}]"
        if not isinstance(entry, dict):
            problems.append(f"{where}: entry is not a mapping")
            continue
        _check_id(entry, where, problems)
        skills = entry.get("skills")
        if "skills" not in entry:
            problems.append(f"{where}: skills: required field is missing")
        elif not isinstance(skills, list) or not skills:
            problems.append(f"{where}: skills: must be a non-empty list")
        unexpected = set(entry) - {"id", "skills"}
        for field in sorted(unexpected):
            problems.append(
                f"{where}: {field}: not part of an ancestry entry -- an ancestry is never an "
                "entry point and has no prerequisite chain (docs/adr/0040)"
            )
    problems.extend(_check_duplicate_ids(ancestries, path, "ancestries"))
    return problems


# --- driving the whole directory ---------------------------------------------------------

CHECKS = {
    CAREERS_FILE: check_careers,
    LOYALTIES_FILE: check_loyalties,
    DRIVES_FILE: lambda p: check_text_list(p, "drives"),
    MISFORTUNES_FILE: lambda p: check_text_list(p, "misfortunes"),
    NAMES_FILE: check_names,
    ANCESTRIES_FILE: check_ancestries,
}


def check_directory(setting_dir: pathlib.Path) -> tuple[list[str], list[str]]:
    """Returns (problems, summary_lines) for every file in one setting directory."""
    problems: list[str] = []
    summary: list[str] = []

    for filename in REQUIRED_FILES:
        path = setting_dir / filename
        if not path.exists():
            problems.append(f"{path}: required file is missing")
            summary.append(f"{filename}: MISSING (required)")
            continue
        file_problems = CHECKS[filename](path)
        problems.extend(file_problems)
        summary.append(f"{filename}: {'OK' if not file_problems else 'FAILED'}")

    for filename in OPTIONAL_FILES:
        path = setting_dir / filename
        if not path.exists():
            summary.append(f"{filename}: not present (optional)")
            continue
        file_problems = CHECKS[filename](path)
        problems.extend(file_problems)
        summary.append(f"{filename}: {'OK' if not file_problems else 'FAILED'}")

    return problems, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    all_problems: list[str] = []
    all_summaries: dict[str, list[str]] = {}
    for setting_dir in args.paths:
        problems, summary = check_directory(setting_dir)
        all_problems.extend(problems)
        all_summaries[str(setting_dir)] = summary

    if args.format == "json":
        print(json.dumps({"ok": not all_problems, "problems": all_problems}, indent=2))
    else:
        for setting_dir, summary in all_summaries.items():
            print(f"{setting_dir}:")
            for line in summary:
                print(f"  {line}")
        if all_problems:
            print(f"FAILED ({len(all_problems)}):")
            for problem in all_problems:
                print(f"  - {problem}")
        else:
            print("All character-creation data holds.")
    return 1 if all_problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
