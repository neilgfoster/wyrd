#!/usr/bin/env python3
"""Check that the documents hold together: reachable from the hub, linked, indexed, on-policy.

Every index in this repo had gone stale silently before this existed. The README's reading
order was missing the Aftermath family, design/README.md's decision-record index was three
records behind, the repositories table named a convention no repo had used for days, and the
status section linked a directory that did not exist while asserting the design was complete.
None of that was found by reading. All of it was found by script in ten minutes.

So the hub is a checked invariant rather than a courtesy (design/adr/0011, and
design/07-tooling.md section 1: where a claim can be checked, check it).

Four checks:

1. **Reachable** -- every design/**.md is reachable from README.md by some chain of relative
   links. A document nothing links to is a document nobody reads.
2. **Linked** -- every relative link target exists on disk, anywhere in the repo.
3. **Indexed** -- every file in design/adr/ appears in design/README.md.
4. **On policy** -- no [[wikilink]] in prose. Prose links like GitHub, data links like
   Obsidian; the rule is only worth having if something enforces it.

Usage:
    python3 tools/check_docs.py
    python3 tools/check_docs.py --format json

Python 3.11+, standard library only (design/07-tooling.md). Reads the filesystem, nothing else.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

HUB = "README.md"
ADR_DIR = "design/adr"
ADR_INDEX = "design/README.md"

# Trees that are not ours to police: vendored substrates, tooling caches, git internals.
SKIP_PARTS = {".git", ".specify", ".claude", ".pytest_cache", "node_modules", "__pycache__"}
SKIP_PREFIXES = (".github/ISSUE_TEMPLATE",)

# Documents that must be reachable from the hub. specs/ is deliberately exempt at file level:
# a spec is the record of one past change rather than current design, so an index entry per
# spec file would be noise -- and noise is how an index stops being read. specs/ is still
# reachable as a directory, and its links are still checked for rot.
REACHABLE_REQUIRED = ("design/",)

MD_LINK = re.compile(r"\[([^\]]*)\]\(\s*<?([^)>\s]+)>?\s*\)")
WIKILINK = re.compile(r"\[\[[^\]]+\]\]")
FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
EXTERNAL = ("http://", "https://", "mailto:", "#")


class Problem(str):
    """A human-readable failure. Subclassing str keeps JSON output trivial."""


def is_skipped(path: pathlib.Path, root: pathlib.Path) -> bool:
    if SKIP_PARTS & set(path.parts):
        return True
    rel = path.relative_to(root).as_posix()
    return rel.startswith(SKIP_PREFIXES)


def markdown_files(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(p for p in root.rglob("*.md") if not is_skipped(p, root))


def strip_code(text: str) -> str:
    """Remove fenced blocks and inline spans.

    Wikilinks legitimately appear in design/14-entities.md, 06-state.md, 07-tooling.md and
    08-maintenance.md -- always inside a YAML example or an inline span describing the
    convention. Allowing them exactly there, and nowhere else, is checkable without an
    allowlist of filenames that would itself go stale.
    """
    out, in_fence = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        out.append("" if in_fence else INLINE_CODE.sub("", line))
    return "\n".join(out)


def links_in(path: pathlib.Path) -> list[str]:
    """Relative link targets in one document, anchors stripped, external schemes dropped."""
    text = path.read_text(encoding="utf-8", errors="replace")
    targets = []
    for _, target in MD_LINK.findall(text):
        if target.startswith(EXTERNAL):
            continue
        targets.append(target.split("#", 1)[0])
    return [t for t in targets if t]


def resolve(source: pathlib.Path, target: str, root: pathlib.Path) -> pathlib.Path | None:
    """Where a relative link points, or None if it escapes the repo."""
    try:
        dest = (source.parent / target).resolve()
        dest.relative_to(root.resolve())
    except (ValueError, OSError):
        return None
    return dest


def reachable_from_hub(root: pathlib.Path) -> set[pathlib.Path]:
    """Every document reachable from README.md by a chain of relative links.

    Directory links count as reaching the directory, not its contents -- linking `specs/`
    does not make every file inside it reachable. That distinction is the whole reason the
    decision-record index is load-bearing rather than decorative: it is the only edge from
    the hub to the individual records.
    """
    hub = root / HUB
    if not hub.exists():
        return set()
    seen, queue = {hub.resolve()}, [hub]
    while queue:
        current = queue.pop()
        if current.is_dir() or current.suffix != ".md":
            continue
        for target in links_in(current):
            dest = resolve(current, target, root)
            if dest is None or not dest.exists() or dest.resolve() in seen:
                continue
            seen.add(dest.resolve())
            queue.append(dest)
    return seen


def check_reachable(root: pathlib.Path) -> list[Problem]:
    seen = reachable_from_hub(root)
    problems = []
    for path in markdown_files(root):
        rel = path.relative_to(root).as_posix()
        if not rel.startswith(REACHABLE_REQUIRED):
            continue
        if path.resolve() not in seen:
            problems.append(Problem(
                f"{rel} is not reachable from {HUB}; nothing links to it, directly or through "
                "an index"
            ))
    return problems


def check_links(root: pathlib.Path) -> list[Problem]:
    problems = []
    for path in markdown_files(root):
        rel = path.relative_to(root).as_posix()
        for target in links_in(path):
            dest = resolve(path, target, root)
            if dest is None:
                problems.append(Problem(f"{rel} links to {target}, which escapes the repository"))
            elif not dest.exists():
                problems.append(Problem(f"{rel} links to {target}, which does not exist"))
    return problems


def check_adr_index(root: pathlib.Path) -> list[Problem]:
    adr_dir = root / ADR_DIR
    index = root / ADR_INDEX
    if not adr_dir.is_dir() or not index.exists():
        return []
    listed = index.read_text(encoding="utf-8", errors="replace")
    problems = []
    for record in sorted(adr_dir.glob("*.md")):
        if record.name not in listed:
            problems.append(Problem(
                f"{record.relative_to(root).as_posix()} is not listed in {ADR_INDEX}; the index "
                "has drifted behind the records on disk"
            ))
    return problems


def check_link_policy(root: pathlib.Path) -> list[Problem]:
    """No wikilinks in prose (design/adr/0011). GitHub renders them as literal text."""
    problems = []
    for path in markdown_files(root):
        rel = path.relative_to(root).as_posix()
        text = strip_code(path.read_text(encoding="utf-8", errors="replace"))
        for match in WIKILINK.findall(text):
            problems.append(Problem(
                f"{rel} uses {match} in prose; prose links with markdown so it renders on "
                "GitHub (design/adr/0011). Wikilinks belong in entity data."
            ))
    return problems


CHECKS = [
    ("reachable from the hub", check_reachable),
    ("links resolve", check_links),
    ("decision records indexed", check_adr_index),
    ("link policy", check_link_policy),
]


def find_problems(root: pathlib.Path) -> list[Problem]:
    """Every problem, in check order. Pure over the tree, so the tests call this."""
    problems: list[Problem] = []
    for _, check in CHECKS:
        problems += check(root)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--root", default=".", help="repository root (default: cwd)")
    args = parser.parse_args(argv)

    root = pathlib.Path(args.root).resolve()

    if args.format == "json":
        problems = find_problems(root)
        print(json.dumps({"problems": list(map(str, problems))}, indent=2))
        return 1 if problems else 0

    total, failed = 0, []
    for name, check in CHECKS:
        found = check(root)
        total += len(found)
        failed += found
        print(f"  {'FAIL' if found else 'ok  '}  {name}" + (f"  ({len(found)})" if found else ""))

    print()
    if failed:
        print(f"FAILED: {total} problem(s)")
        for problem in failed:
            print(f"  - {problem}")
        return 1
    docs = len(markdown_files(root))
    print(f"All checks passed. {docs} documents, all reachable and linked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
