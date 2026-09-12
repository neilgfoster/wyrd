#!/usr/bin/env python3
"""Check that settings.yaml agrees with the live wyrd-setting-* fleet.

CLAUDE.md: settings.yaml went stale twice -- a naming convention it recorded stopped being the
one in use, and six of the fourteen live setting repos were entirely absent from it. Both read as
authoritative and were not (fault class 4, and the exact reason CLAUDE.md warns that tables are
where staleness hides). This script is the drift check specs/032-settings-catalogue-realignment
asked for, in tools/backlog.py's shape: read-only, stdlib-only, checked rather than asserted.

Three things it reports:

  missing from the catalogue   a live wyrd-setting-* repo with no settings.yaml entry
  dangling catalogue entries   a settings.yaml entry whose repo: matches no live repository
  relation problems            a relations: entry that is malformed -- see check_relations()

The relation checks are pure local-file consistency (specs/145-related-settings-kinship) and do
not require `gh`; they run and are reported even when the fleet-drift check below can't reach
GitHub.

Usage:
    python3 tools/check_settings_catalogue.py
    python3 tools/check_settings_catalogue.py --format json

Requires the `gh` CLI. Python 3.11+, standard library only (docs/design/27-tooling.md).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

OWNER = "neilgfoster"
CATALOGUE_PATH = pathlib.Path(__file__).resolve().parent.parent / "settings.yaml"

# The skeleton repo, not a setting -- correctly absent from settings.yaml.
NOT_A_SETTING = {"wyrd-setting-template"}


class GhError(RuntimeError):
    """A `gh` call failed. Raised rather than swallowed: an unreadable fleet is not an empty one."""


def gh(args: list[str]) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise GhError(f"gh {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}")
    return proc.stdout


def _parse_scalar(value: str) -> str | None:
    if value in ("null", "~", ""):
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _parse_flat_list(text: str, section: str) -> list[dict]:
    """One top-level `<section>:` list of flat mappings.

    A restricted-subset reader, not a general YAML parser (docs/design/27-tooling.md section 2: no
    third-party YAML dependency). Each entry is a `- key: value` line starting a new mapping,
    followed by indented `key: value` lines until the next `- ` or a blank/comment line at the
    same indent ends it. Comments and blank lines are skipped everywhere. Entries end at the next
    unindented, non-list top-level key (another `<name>:` section) or end of file.
    """
    entries: list[dict] = []
    current: dict | None = None
    in_section = False
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == f"{section}:":
            in_section = True
            continue
        if not raw.startswith((" ", "-")) and stripped.endswith(":"):
            # A different top-level section starting -- this one is over.
            in_section = False
            if current is not None:
                entries.append(current)
                current = None
            continue
        if not in_section:
            continue
        if stripped.startswith("- "):
            if current is not None:
                entries.append(current)
            current = {}
            stripped = stripped[2:].strip()
        if current is None:
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        current[key.strip()] = _parse_scalar(value.strip())
    if current is not None:
        entries.append(current)
    return entries


def parse_catalogue(text: str) -> list[dict]:
    """The `settings:` list of flat mappings -- id, title, repo, visibility, status."""
    return _parse_flat_list(text, "settings")


def parse_relations(text: str) -> list[dict]:
    """The `relations:` list of flat mappings -- a, b, kind (specs/145-related-settings-kinship)."""
    return _parse_flat_list(text, "relations")


def load_catalogue(path: pathlib.Path = CATALOGUE_PATH) -> list[dict]:
    return parse_catalogue(path.read_text())


def load_relations(path: pathlib.Path = CATALOGUE_PATH) -> list[dict]:
    return parse_relations(path.read_text())


def live_setting_repos() -> list[str]:
    raw = gh(["repo", "list", OWNER, "--json", "name", "--limit", "200"])
    return [
        r["name"]
        for r in json.loads(raw)
        if r["name"].startswith("wyrd-setting-") and r["name"] not in NOT_A_SETTING
    ]


RELATION_KINDS = {"same-world", "kindred-tone"}


def check_relations(catalogue_entries: list[dict], relations: list[dict]) -> list[str]:
    """Validate `relations:` against `settings:` (specs/145-related-settings-kinship).

    Local-file consistency only -- no `gh` call, so this runs even when the fleet-drift check
    below can't. Four problems, each reported by name rather than merely failing:

      an unknown setting id in a/b, a self-relation (a == b), an unordered pair {a, b} declared
      more than once (regardless of field order or repeated kind), and a pair declared under
      both `same-world` and `kindred-tone` at once.
    """
    problems: list[str] = []
    known_ids = {e.get("id") for e in catalogue_entries}
    seen_pairs: dict[frozenset[str], set[str]] = {}

    for rel in relations:
        a, b, kind = rel.get("a"), rel.get("b"), rel.get("kind")
        label = f"{a} <-> {b}"

        if kind not in RELATION_KINDS:
            problems.append(f"{label}: kind {kind!r} is not one of {sorted(RELATION_KINDS)}")
        if a not in known_ids:
            problems.append(f"{label}: {a!r} is not a known setting id")
        if b not in known_ids:
            problems.append(f"{label}: {b!r} is not a known setting id")
        if a == b:
            problems.append(f"{label}: a setting cannot be its own kin")
            continue
        if a not in known_ids or b not in known_ids:
            continue

        pair = frozenset({a, b})
        kinds_seen = seen_pairs.setdefault(pair, set())
        if kind in kinds_seen:
            problems.append(f"{label}: declared more than once as {kind}")
        kinds_seen.add(kind)

    for pair, kinds_seen in seen_pairs.items():
        if len(kinds_seen) > 1:
            a, b = sorted(pair)
            problems.append(
                f"{a} <-> {b}: declared as both {' and '.join(sorted(kinds_seen))} -- "
                "a pair cannot hold both relations at once"
            )

    return problems


def compute_drift(catalogue_entries: list[dict], live_repos: list[str]) -> dict:
    catalogue_repos = {e.get("repo") for e in catalogue_entries}
    missing = sorted(r for r in live_repos if r not in catalogue_repos)
    dangling = sorted(
        (e for e in catalogue_entries if e.get("repo") not in live_repos),
        key=lambda e: e.get("id") or "",
    )
    return {
        "missing_from_catalogue": missing,
        "dangling_catalogue_entries": [
            {"id": e.get("id"), "repo": e.get("repo")} for e in dangling
        ],
        "clean": not missing and not dangling,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    catalogue = load_catalogue()
    relations = load_relations()
    relation_problems = check_relations(catalogue, relations)

    try:
        live = live_setting_repos()
    except GhError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    drift = compute_drift(catalogue, live)
    drift["relation_problems"] = relation_problems
    drift["clean"] = drift["clean"] and not relation_problems

    if args.format == "json":
        print(json.dumps(drift, indent=2))
        return 0 if drift["clean"] else 1

    if drift["clean"]:
        print(f"ok    settings.yaml matches the live fleet ({len(live)} settings)")
        return 0

    if drift["missing_from_catalogue"]:
        print("Live repos missing from settings.yaml:")
        for repo in drift["missing_from_catalogue"]:
            print(f"  {repo}")
    if drift["dangling_catalogue_entries"]:
        print("Catalogue entries naming a repo that does not exist:")
        for entry in drift["dangling_catalogue_entries"]:
            print(f"  {entry['id']}  ->  {entry['repo']}")
    if relation_problems:
        print("relations: problems:")
        for problem in relation_problems:
            print(f"  {problem}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
