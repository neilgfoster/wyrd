#!/usr/bin/env python3
"""Report fleet drift and roll out engine/template changes across the wyrd-* repos.

CLAUDE.md: sixteen wyrd-setting-* repos, a wyrd-setting-template and a wyrd-chronicle-template
exist, and nothing propagates a change to any of them -- a repo created last week and one
created next month diverge permanently, silently, and the drift is only found at play time in
someone's chronicle. This is the same fault class tools/backlog.py already exists to fix (state
that lives in many places with nothing tracking whether the copies agree), one level up: here
the copies are whole repositories.

Two verbs:

    status    read-only. For every fleet repo, its recorded version and what it is missing.
    rollout   for every repo `status` reports as behind, open one PR bundling every
              outstanding change -- never a direct push, never a duplicate PR.

A fleet repo tracks the source repo it was created from (`wyrd-setting-template` or
`wyrd-chronicle-template`) via a committed `.wyrd-version` marker file, and the source repo
declares its own rollout-eligible changes as an ordered manifest under `rollout/changes/`, one
YAML file per change, each declaring a class (`additive` | `structural`) per
design/09-evolution.md's two relevant change classes. See specs/032-fleet-rollout/data-model.md
for the exact schema of both.

Deliberately never reads a target repo's `library/`, `corpus/` or `index/` content -- that is
where copyrighted setting material lives, and this tool has no reason to touch it (a manifest
entry naming a path under one of those is a load error, not a warning, the same posture
design/07-tooling.md section 4 takes for a setting override naming something outside the
closed overridable set).

Usage:
    python3 tools/fleet_rollout.py status
    python3 tools/fleet_rollout.py status --format json
    python3 tools/fleet_rollout.py status --repo wyrd-setting-hemmelfurt
    python3 tools/fleet_rollout.py rollout --dry-run
    python3 tools/fleet_rollout.py rollout
    python3 tools/fleet_rollout.py rollout --repo wyrd-setting-hemmelfurt

Requires the `gh` CLI, authenticated with read access to the fleet and write access to open
pull requests against it.
Python 3.11+, standard library only (design/07-tooling.md).
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path

OWNER = "neilgfoster"

# A fleet repo is a downstream target this tool tracks and can roll changes out to. The engine
# repo (this one) and live chronicle repos are deliberately excluded -- see
# specs/032-fleet-rollout/spec.md's Assumptions.
FLEET_PREFIX = "wyrd-setting-"
FLEET_EXTRA_NAMES = {"wyrd-chronicle-template"}

# The two source repos a fleet repo's .wyrd-version can point at.
SOURCE_REPOS = {"wyrd-setting-template", "wyrd-chronicle-template"}

# design/07-tooling.md section 4's "an override naming something outside the closed set is a
# load error" posture, applied here: a manifest entry may never name a path under setting-
# authored content, because the template never owns any.
FORBIDDEN_PATH_PREFIXES = ("library/", "corpus/", "index/")

VERSION_MARKER_PATH = ".wyrd-version"
MANIFEST_DIR = "rollout/changes"


class GhError(RuntimeError):
    """A `gh` call failed. Raised rather than swallowed -- an unreadable repo is reported as
    unreachable, not silently treated as absent."""


class YamlParseError(RuntimeError):
    """A `.wyrd-version` or manifest entry did not match the restricted subset this reader
    understands."""


class ManifestError(RuntimeError):
    """A manifest entry is malformed or violates the closed set of things it may declare."""


class _MarkerAbsent:
    """Sentinel: the repo carries no `.wyrd-version` at all, distinct from a parse failure."""

    def __repr__(self) -> str:
        return "MARKER_ABSENT"


MARKER_ABSENT = _MarkerAbsent()


def gh(args: list[str]) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise GhError(f"gh {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}")
    return proc.stdout


# --------------------------------------------------------------------------------------------
# The restricted YAML subset: flat `key: value` pairs, plus one level of `key:` -> list of
# `- item` lines. No nesting beyond that, no third-party dependency (design/07-tooling.md
# section 2). `.wyrd-version` and a manifest entry both fit this shape exactly.
# --------------------------------------------------------------------------------------------


def _parse_scalar(value: str) -> str | None:
    if value in ("null", "~", ""):
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def parse_simple_yaml(text: str) -> dict:
    lines = text.splitlines()
    result: dict = {}
    i, n = 0, len(lines)
    while i < n:
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if stripped.startswith("- "):
            raise YamlParseError(f"unexpected list item outside a key: {lines[i]!r}")
        if ":" not in stripped:
            raise YamlParseError(f"expected 'key: value' or 'key:', got {lines[i]!r}")
        key, _, rest = stripped.partition(":")
        key = key.strip()
        value = rest.strip()
        if value:
            result[key] = _parse_scalar(value)
            i += 1
            continue
        # Empty value: gather any indented `- item` lines that follow as a list.
        items: list[str] = []
        j = i + 1
        while j < n:
            nxt = lines[j].strip()
            if not nxt:
                j += 1
                continue
            if nxt.startswith("- "):
                items.append(_parse_scalar(nxt[2:].strip()))
                j += 1
                continue
            break
        result[key] = items if items else None
        i = j
    return result


# --------------------------------------------------------------------------------------------
# Manifest entries
# --------------------------------------------------------------------------------------------


def validate_manifest_entry(entry: dict, source_repo: str) -> dict:
    """Raise ManifestError on anything outside the closed additive/structural shape.

    Returns the entry unchanged when valid -- the caller decides what to do with it.
    """
    entry_id = entry.get("id")
    if not entry_id:
        raise ManifestError(f"{source_repo}: a manifest entry is missing 'id'")
    if not entry.get("sha"):
        raise ManifestError(f"{source_repo}: entry {entry_id!r} is missing 'sha'")
    cls = entry.get("class")
    if cls not in ("additive", "structural"):
        raise ManifestError(f"{source_repo}: entry {entry_id!r} has invalid class {cls!r}")
    add = entry.get("add")
    migrate = entry.get("migrate")
    if cls == "additive":
        if not add:
            raise ManifestError(f"{source_repo}: additive entry {entry_id!r} has no 'add' paths")
        if migrate:
            raise ManifestError(
                f"{source_repo}: additive entry {entry_id!r} must not declare 'migrate'"
            )
        for path in add:
            if any(path.startswith(prefix) for prefix in FORBIDDEN_PATH_PREFIXES):
                raise ManifestError(
                    f"{source_repo}: entry {entry_id!r} names {path!r}, under a directory "
                    "the template never owns setting-authored content in"
                )
    else:
        if not migrate:
            raise ManifestError(f"{source_repo}: structural entry {entry_id!r} has no 'migrate' step")
        if add:
            raise ManifestError(f"{source_repo}: structural entry {entry_id!r} must not declare 'add'")
    return entry


def _entry_sequence(entry_id: str) -> int:
    """The `NNN` sequence prefix of a `NNN-slug` entry id, for ordering."""
    prefix = entry_id.split("-", 1)[0]
    return int(prefix)


def sort_manifest(entries: list[dict]) -> list[dict]:
    return sorted(entries, key=lambda e: _entry_sequence(e["id"]))


def fetch_manifest(source_repo: str) -> list[dict]:
    """The ordered, validated manifest for one source repo, read live via `gh`."""
    if source_repo not in SOURCE_REPOS:
        raise ValueError(f"{source_repo!r} is not a known source repo")
    listing = json.loads(gh(["api", f"repos/{OWNER}/{source_repo}/contents/{MANIFEST_DIR}"]))
    entries = []
    for item in listing:
        if not item["name"].endswith(".yaml"):
            continue
        raw = gh(["api", f"repos/{OWNER}/{source_repo}/contents/{item['path']}"])
        payload = json.loads(raw)
        text = base64.b64decode(payload["content"]).decode("utf-8")
        entry = parse_simple_yaml(text)
        entries.append(validate_manifest_entry(entry, source_repo))
    return sort_manifest(entries)


# --------------------------------------------------------------------------------------------
# Version markers
# --------------------------------------------------------------------------------------------


def read_version_marker(repo: str) -> dict | _MarkerAbsent:
    """The parsed `.wyrd-version` marker, or MARKER_ABSENT if the repo carries none.

    Any other `gh` failure (auth, rate limit, a repo that no longer exists) propagates as
    GhError rather than being folded into "absent" -- those are tool-level failures, not an
    unversioned repo.
    """
    try:
        raw = gh(["api", f"repos/{OWNER}/{repo}/contents/{VERSION_MARKER_PATH}"])
    except GhError as exc:
        if "404" in str(exc) or "Not Found" in str(exc):
            return MARKER_ABSENT
        raise
    payload = json.loads(raw)
    text = base64.b64decode(payload["content"]).decode("utf-8")
    return parse_simple_yaml(text)


# --------------------------------------------------------------------------------------------
# Fleet discovery
# --------------------------------------------------------------------------------------------


def is_fleet_repo(name: str) -> bool:
    return name.startswith(FLEET_PREFIX) or name in FLEET_EXTRA_NAMES


def filter_fleet_repos(repos: list[dict]) -> list[dict]:
    """`repos` is the shape `gh repo list --json name,visibility,isArchived` returns.

    Archived repos are kept, not dropped -- an archived fleet repo is reported as
    unreachable (see compute_repo_state), which is the spec's edge case for a repo renamed or
    archived since it was last seen, rather than silently vanishing from the report.
    """
    return [r for r in repos if is_fleet_repo(r["name"])]


def list_fleet_repos() -> list[dict]:
    raw = gh(["repo", "list", OWNER, "--json", "name,visibility,isArchived", "--limit", "200"])
    return filter_fleet_repos(json.loads(raw))


# --------------------------------------------------------------------------------------------
# Repo state -- pure, no I/O. Everything status/rollout decide is computed from a marker and a
# manifest, both already fetched.
# --------------------------------------------------------------------------------------------


def _index_by_sha(manifest: list[dict], sha: str) -> int | None:
    for idx, entry in enumerate(manifest):
        if entry["sha"] == sha:
            return idx
    return None


def _index_by_id(manifest: list[dict], entry_id: str) -> int | None:
    for idx, entry in enumerate(manifest):
        if entry["id"] == entry_id:
            return idx
    return None


def compute_repo_state(
    marker: dict | _MarkerAbsent, manifest: list[dict], *, reachable: bool = True
) -> dict:
    """The Fleet repo record (data-model.md) for one repo, given its marker and its source's
    manifest -- pure function, so every state transition is testable without a live `gh` call.

    `state` is one of: unreachable, unversioned, unresolvable, current, diverged, behind.
    """
    if not reachable:
        return {"state": "unreachable", "missing": [], "diverged_at": None}
    if marker is MARKER_ABSENT:
        return {"state": "unversioned", "missing": [], "diverged_at": None}

    diverged_at = marker.get("diverged_at")
    recorded_sha = marker.get("template_sha")

    if recorded_sha is None:
        # Pre-manifest baseline: the repo predates any recorded change, so everything in the
        # manifest is outstanding.
        applied_idx = -1
    else:
        applied_idx = _index_by_sha(manifest, recorded_sha)
        if applied_idx is None:
            # A SHA that matches no known entry -- upstream history was rewritten, or the
            # marker is simply wrong. Reported distinctly rather than guessing a distance
            # (spec Edge Cases).
            return {"state": "unresolvable", "missing": [], "diverged_at": diverged_at}

    outstanding = manifest[applied_idx + 1 :]
    if not outstanding:
        return {"state": "current", "missing": [], "diverged_at": diverged_at}

    diverged_idx = _index_by_id(manifest, diverged_at) if diverged_at else None
    if diverged_idx is not None and diverged_idx > applied_idx:
        remaining = manifest[diverged_idx + 1 :]
        if not remaining:
            return {"state": "diverged", "missing": [], "diverged_at": diverged_at}
        return {"state": "behind", "missing": remaining, "diverged_at": diverged_at}

    return {"state": "behind", "missing": outstanding, "diverged_at": diverged_at}


def fleet_repo_record(repo: dict, marker: dict | _MarkerAbsent, manifest: list[dict], *, reachable: bool = True) -> dict:
    computed = compute_repo_state(marker, manifest, reachable=reachable)
    return {
        "repo": repo["name"],
        "visibility": repo.get("visibility"),
        "template_source": None if marker is MARKER_ABSENT else marker.get("template_source"),
        "recorded_sha": None if marker is MARKER_ABSENT else marker.get("template_sha"),
        "state": computed["state"],
        "missing": [
            {"id": e["id"], "class": e["class"], "summary": e.get("summary")}
            for e in computed["missing"]
        ],
        "diverged_at": computed["diverged_at"],
    }


# --------------------------------------------------------------------------------------------
# Rollout planning -- pure. Turns a `behind` record's outstanding entries into the ordered set
# of actions a PR would carry; opening the PR itself is a separate, I/O-heavy step.
# --------------------------------------------------------------------------------------------


def plan_rollout(marker: dict | _MarkerAbsent, manifest: list[dict]) -> list[dict]:
    """The ordered list of actions a rollout PR for this repo would contain. Empty if the
    repo has nothing outstanding (current, diverged, unreachable) or cannot be planned for
    (unversioned, unresolvable -- those need a maintainer decision, not an automatic bundle).
    """
    state = compute_repo_state(marker, manifest)
    if state["state"] != "behind":
        return []
    actions = []
    for entry in state["missing"]:
        if entry["class"] == "additive":
            actions.append(
                {"id": entry["id"], "class": "additive", "sha": entry["sha"], "add": entry["add"]}
            )
        else:
            actions.append(
                {
                    "id": entry["id"],
                    "class": "structural",
                    "sha": entry["sha"],
                    "migrate": entry["migrate"],
                }
            )
    return actions


def find_existing_rollout_pr(repo: str, latest_entry_id: str) -> str | None:
    """The URL of an already-open rollout PR targeting this exact bundle, if one exists."""
    branch = f"wyrd-fleet-rollout/{latest_entry_id}"
    raw = gh(
        [
            "pr", "list", "--repo", f"{OWNER}/{repo}",
            "--head", branch, "--state", "open", "--json", "url",
        ]
    )
    matches = json.loads(raw)
    return matches[0]["url"] if matches else None


def find_closed_rollout_pr(repo: str, latest_entry_id: str) -> str | None:
    """The URL of a rollout PR for this exact bundle that was closed without merging, if any.

    A rejected bundle is never reopened identically (spec Edge Cases) -- distinguished from
    "already open" so `rollout` can report it rather than attempting a push that would
    collide with the closed PR's still-existing remote branch.
    """
    branch = f"wyrd-fleet-rollout/{latest_entry_id}"
    raw = gh(
        [
            "pr", "list", "--repo", f"{OWNER}/{repo}",
            "--head", branch, "--state", "closed", "--json", "url,mergedAt",
        ]
    )
    matches = [m for m in json.loads(raw) if not m.get("mergedAt")]
    return matches[0]["url"] if matches else None


def apply_rollout(repo: str, source_repo: str, actions: list[dict]) -> str:
    """Clone the target repo, apply every action as a commit on a fresh branch, and open a PR
    against it. Never pushes to the repo's default branch.

    This is the one function this feature cannot exercise without live `gh`/`git` access --
    see specs/032-fleet-rollout/quickstart.md for how a human validates it end to end.
    """
    if not actions:
        raise ValueError("apply_rollout called with no actions")
    latest_id = actions[-1]["id"]
    branch = f"wyrd-fleet-rollout/{latest_id}"
    with tempfile.TemporaryDirectory(prefix="wyrd-fleet-rollout-") as tmp:
        target_dir = Path(tmp) / repo
        gh(["repo", "clone", f"{OWNER}/{repo}", str(target_dir)])
        subprocess.run(["git", "checkout", "-b", branch], cwd=target_dir, check=True)

        for action in actions:
            if action["class"] == "additive":
                for rel_path in action["add"]:
                    _copy_path_from_source(source_repo, action["sha"], rel_path, target_dir)
            else:
                _apply_migration(source_repo, action["migrate"], target_dir)
            subprocess.run(["git", "add", "-A"], cwd=target_dir, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Fleet rollout: {action['id']}"],
                cwd=target_dir, check=True,
            )

        _write_version_marker(target_dir, source_repo, latest_id_sha=actions[-1]["sha"])
        subprocess.run(["git", "add", "-A"], cwd=target_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Update .wyrd-version"], cwd=target_dir, check=True
        )
        subprocess.run(["git", "push", "-u", "origin", branch], cwd=target_dir, check=True)

        body_lines = ["Bundled changes:", ""]
        for action in actions:
            body_lines.append(f"- `{action['id']}` ({action['class']})")
        raw = gh(
            [
                "pr", "create", "--repo", f"{OWNER}/{repo}",
                "--head", branch,
                "--title", f"Fleet rollout: {latest_id}",
                "--body", "\n".join(body_lines),
            ]
        )
        return raw.strip().splitlines()[-1]


def _copy_path_from_source(source_repo: str, sha: str, rel_path: str, target_dir: Path) -> None:
    payload = json.loads(
        gh(["api", f"repos/{OWNER}/{source_repo}/contents/{rel_path}?ref={sha}"])
    )
    content = base64.b64decode(payload["content"])
    dest = target_dir / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)


def _apply_migration(source_repo: str, migrate_ref: str, target_dir: Path) -> None:
    # A structural entry's `migrate` names a script or instructions living in the source
    # repo; applying it is deliberately left as an operator-reviewed step for the maintainer
    # to run before merging, per plan.md's "some structural changes may need the repo owner's
    # judgment before merging" assumption. We stage a note rather than guessing a transform.
    note = target_dir / "FLEET_ROLLOUT_MIGRATION.md"
    existing = note.read_text() if note.exists() else "# Fleet rollout migrations to review\n\n"
    note.write_text(existing + f"- from `{source_repo}`: {migrate_ref}\n")


def _write_version_marker(target_dir: Path, source_repo: str, latest_id_sha: str) -> None:
    marker_path = target_dir / VERSION_MARKER_PATH
    lines = [f"template_source: {source_repo}", f"template_sha: {latest_id_sha}"]
    marker_path.write_text("\n".join(lines) + "\n")


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------


def render_text_table(records: list[dict]) -> str:
    lines = [f"{'REPO':<32} {'VISIBILITY':<10} {'STATE':<12} MISSING"]
    for r in records:
        missing = ", ".join(e["id"] for e in r["missing"]) or "-"
        state = "diverged (accepted)" if r["state"] == "diverged" else r["state"]
        lines.append(f"{r['repo']:<32} {str(r['visibility']):<10} {state:<12} {missing}")
    return "\n".join(lines)


def cmd_status(args: argparse.Namespace) -> int:
    repos = list_fleet_repos()
    if args.repo:
        repos = [r for r in repos if r["name"] == args.repo]
    manifests: dict[str, list[dict]] = {}
    records = []
    for repo in repos:
        reachable = not repo.get("isArchived", False)
        marker: dict | _MarkerAbsent = MARKER_ABSENT
        if reachable:
            try:
                marker = read_version_marker(repo["name"])
            except GhError:
                reachable = False
        source = None if marker is MARKER_ABSENT else marker.get("template_source")
        manifest: list[dict] = []
        if reachable and source in SOURCE_REPOS:
            if source not in manifests:
                manifests[source] = fetch_manifest(source)
            manifest = manifests[source]
        records.append(fleet_repo_record(repo, marker, manifest, reachable=reachable))

    if args.format == "json":
        print(json.dumps(records, indent=2))
    else:
        print(render_text_table(records))
    return 0


def cmd_rollout(args: argparse.Namespace) -> int:
    repos = list_fleet_repos()
    if args.repo:
        repos = [r for r in repos if r["name"] == args.repo]
    manifests: dict[str, list[dict]] = {}

    for repo in repos:
        if repo.get("isArchived", False):
            print(f"{repo['name']}: unreachable, skipped")
            continue
        try:
            marker = read_version_marker(repo["name"])
        except GhError as exc:
            print(f"{repo['name']}: unreachable ({exc}), skipped")
            continue
        source = None if marker is MARKER_ABSENT else marker.get("template_source")
        if source not in SOURCE_REPOS:
            print(f"{repo['name']}: no rollout source recorded, skipped")
            continue
        if source not in manifests:
            manifests[source] = fetch_manifest(source)
        manifest = manifests[source]
        actions = plan_rollout(marker, manifest)
        if not actions:
            continue
        latest_id = actions[-1]["id"]
        existing = find_existing_rollout_pr(repo["name"], latest_id)
        if existing:
            print(f"{repo['name']}: skipped: already open at {existing}")
            continue
        rejected = find_closed_rollout_pr(repo["name"], latest_id)
        if rejected:
            print(f"{repo['name']}: skipped: previously closed without merging ({rejected})")
            continue
        if args.dry_run:
            ids = ", ".join(a["id"] for a in actions)
            print(f"{repo['name']}: would open PR bundling {ids}")
            continue
        url = apply_rollout(repo["name"], source, actions)
        print(f"{repo['name']}: opened {url}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    status_p = sub.add_parser("status", help="report the fleet's drift, read-only")
    status_p.add_argument("--format", choices=["text", "json"], default="text")
    status_p.add_argument("--repo", help="restrict to a single repo")
    status_p.set_defaults(func=cmd_status)

    rollout_p = sub.add_parser("rollout", help="open a PR against every repo that is behind")
    rollout_p.add_argument("--dry-run", action="store_true", help="show what would happen, write nothing")
    rollout_p.add_argument("--repo", help="restrict to a single repo")
    rollout_p.set_defaults(func=cmd_rollout)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except GhError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
