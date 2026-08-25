#!/usr/bin/env python3
"""Answer "what do I implement next?" from the board, by computation rather than by reading.

CLAUDE.md: work is tracked as GitHub issues via kord, and there is no backlog file, because
two lists of the same work drift. The priority order therefore lives on the board -- a
numeric `Rank` field on the wyrd Project (v2) -- and this script is only its reader. It
never writes to an issue, a field or the board.

kord records a dependency order inside an epic (`Depends on: #N`, written by
kord-epic-decompose) and no priority order anywhere. Ranking the roots supplies the missing
half; but with a handful of roots, a rank alone says which epic matters, not what to do
today. So `next` combines three sources that already exist --

    the board's Rank        which root comes first
    the sub-issue graph     GitHub's native parent/child links
    `Depends on: #N`        what cannot start yet

-- and walks them to a leaf that is genuinely ready to start.

Where priority and dependency disagree, dependency wins: a rank orders what you *choose*
between, it never authorises starting work whose prerequisites are still open. A blocked
top-ranked item is reported as blocked rather than silently skipped, so the answer explains
itself.

Usage:
    python3 tools/backlog.py next            # what to work on now
    python3 tools/backlog.py next --format json
    python3 tools/backlog.py list            # the whole ordered tree
    python3 tools/backlog.py check           # drift guard; non-zero exit on any problem

Requires the `gh` CLI, authenticated with the `project` scope.
Python 3.11+, standard library only (design/07-tooling.md).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

OWNER = "neilgfoster"
REPO = "wyrd"
PROJECT_NUMBER = 5
RANK_FIELD = "Rank"

# Only these are backlog items. A kord-task issue is a unit of work inside a feature and is
# not ranked.
TRACKED_LABELS = {"kord-epic", "kord-feature"}

# Ranks are seeded in tens so an item can be inserted between two others by setting one
# number, rather than renumbering the tail. The gaps carry no meaning.
RANK_STEP = 10

ISSUE_GRAPHQL = """
query($owner:String!, $repo:String!, $cursor:String) {
  repository(owner:$owner, name:$repo) {
    issues(states:OPEN, first:100, after:$cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number title url body state
        labels(first:20) { nodes { name } }
        parent { number }
        subIssues(first:100) { nodes { number state } }
      }
    }
  }
}
"""

# `Depends on:` as a DECLARATION -- the line starts with it, once list markers and bold are
# stripped. Anchoring matters: #6, #11 and #17 all contain prose that merely uses the word,
# and #11's ("R1.8 (the mob rule) depends on this landing") would otherwise be read as #11
# depending on #13 -- the exact inverse of the truth, since #13 declares `Depends on: #11`.
DEPENDS_PREFIX = re.compile(r"^\s*(?:[-*+]\s*)?(?:\*\*)?depends on(?:\*\*)?\s*:", re.I)
ISSUE_REF = re.compile(r"#(\d+)")


class GhError(RuntimeError):
    """A `gh` call failed. Raised rather than swallowed: an unknown board is not an empty one."""


def gh(args: list[str]) -> str:
    proc = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise GhError(
            f"gh {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout


def fetch_board() -> dict[int, dict]:
    """Project items keyed by issue number, carrying their Rank (None if unset)."""
    raw = gh([
        "project", "item-list", str(PROJECT_NUMBER),
        "--owner", OWNER, "--limit", "500", "--format", "json",
    ])
    items = json.loads(raw).get("items", [])
    board: dict[int, dict] = {}
    for item in items:
        number = (item.get("content") or {}).get("number")
        if number is None:
            continue  # a draft item, not an issue
        rank = item.get(RANK_FIELD.lower())
        board[number] = {
            "rank": int(rank) if isinstance(rank, (int, float)) else None,
            "repository": (item.get("content") or {}).get("repository"),
        }
    return board


def fetch_issues() -> dict[int, dict]:
    """Open issues keyed by number, with parentage, children and declared dependencies."""
    issues: dict[int, dict] = {}
    cursor = None
    while True:
        args = [
            "api", "graphql",
            "-f", f"query={ISSUE_GRAPHQL}",
            "-F", f"owner={OWNER}", "-F", f"repo={REPO}",
        ]
        if cursor:
            args += ["-F", f"cursor={cursor}"]
        page = json.loads(gh(args))["data"]["repository"]["issues"]
        for node in page["nodes"]:
            labels = {label["name"] for label in node["labels"]["nodes"]}
            issues[node["number"]] = {
                "number": node["number"],
                "title": node["title"],
                "url": node["url"],
                "labels": labels,
                "parent": (node["parent"] or {}).get("number"),
                "children": [c["number"] for c in node["subIssues"]["nodes"]],
                "open_children": [
                    c["number"] for c in node["subIssues"]["nodes"] if c["state"] == "OPEN"
                ],
                "depends_on": parse_depends_on(node["body"] or ""),
                "is_epic": "kord-epic" in labels,
            }
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return issues


def parse_depends_on(body: str) -> list[int]:
    """Issue numbers this issue declares a dependency on.

    Only lines that BEGIN with `Depends on:` count -- see DEPENDS_PREFIX. kord writes the
    line three ways across the current board (a bare first line, a bullet, and a
    comma-separated list), all of which this handles; prose mentioning the word does not
    count, which is the whole point.
    """
    found: list[int] = []
    for line in body.splitlines():
        match = DEPENDS_PREFIX.match(line)
        if not match:
            continue
        for ref in ISSUE_REF.findall(line[match.end():]):
            number = int(ref)
            if number not in found:
                found.append(number)
    return found


def sort_key(number: int, board: dict[int, dict]) -> tuple[int, int]:
    """Rank ascending, unranked last, issue number as the tiebreak.

    The tiebreak keeps the walk total and reproducible: two runs against an unchanged board
    must give the same answer, or the tool has reintroduced the judgement call it removes.
    """
    rank = board.get(number, {}).get("rank")
    return (rank if rank is not None else sys.maxsize, number)


def roots(issues: dict[int, dict]) -> list[int]:
    return [
        n for n, i in issues.items()
        if i["parent"] is None and i["labels"] & TRACKED_LABELS
    ]


def open_blockers(issue: dict, issues: dict[int, dict]) -> list[int]:
    """The dependencies of this issue that are still open.

    `issues` holds only OPEN issues, so a declared dependency absent from it is closed and
    hence satisfied. This is the hot path -- the walk calls it for every leaf -- so it stays
    pure lookup with no network access.
    """
    return [d for d in issue["depends_on"] if d in issues]


def dangling_refs(issue: dict, issues: dict[int, dict]) -> list[int]:
    """Declared dependencies that match no issue at all, open or closed.

    Such a reference reads as satisfied to open_blockers (it is not in the open set), which
    is precisely how a typo'd number becomes "ready". Only `check` needs this, because it
    costs one `gh` lookup per distinct unknown number.
    """
    return [
        d for d in issue["depends_on"]
        if d not in issues and not issue_exists(d)
    ]


_exists_cache: dict[int, bool] = {}


def issue_exists(number: int) -> bool:
    """Whether a closed-or-open issue with this number exists. Cached; one `gh` call each."""
    if number not in _exists_cache:
        try:
            gh(["issue", "view", str(number), "--repo", f"{OWNER}/{REPO}", "--json", "number"])
            _exists_cache[number] = True
        except GhError:
            _exists_cache[number] = False
    return _exists_cache[number]


def walk(issues: dict[int, dict], board: dict[int, dict]) -> tuple[dict | None, list[dict]]:
    """The first ready leaf, and every blocked leaf passed over on the way to it.

    Depth-first through the ranked roots. A leaf is an issue with no OPEN children; it is
    ready when every issue it declares a dependency on is closed. The blocked list is
    returned rather than discarded so `next` can say why the obvious answer was not chosen.
    """
    blocked: list[dict] = []
    chosen: dict | None = None

    def visit(number: int, trail: list[int]) -> dict | None:
        issue = issues.get(number)
        if issue is None:
            return None
        path = trail + [number]
        if issue["open_children"]:
            for child in sorted(issue["open_children"], key=lambda c: sort_key(c, board)):
                found = visit(child, path)
                if found:
                    return found
            return None
        blockers = open_blockers(issue, issues)
        entry = {
            "number": number,
            "title": issue["title"],
            "url": issue["url"],
            "path": path,
            "rank": board.get(path[0], {}).get("rank"),
            "blocked_by": blockers,
        }
        if blockers:
            blocked.append(entry)
            return None
        return entry

    for root in sorted(roots(issues), key=lambda r: sort_key(r, board)):
        chosen = visit(root, [])
        if chosen:
            break
    return chosen, blocked


def describe_path(path: list[int], issues: dict[int, dict]) -> str:
    return " > ".join(f"#{n} {issues[n]['title']}" for n in path if n in issues)


def cmd_next(args) -> int:
    issues = fetch_issues()
    board = fetch_board()
    chosen, blocked = walk(issues, board)

    if args.format == "json":
        print(json.dumps({"next": chosen, "blocked": blocked}, indent=2))
        return 0 if chosen else 1

    if not chosen:
        print("Nothing is ready to start.")
        if blocked:
            print("\nEverything reachable is blocked:")
            for entry in blocked:
                deps = ", ".join(f"#{d}" for d in entry["blocked_by"])
                print(f"  #{entry['number']} {entry['title']}  <- blocked by {deps}")
        return 1

    print(f"Next: #{chosen['number']}  {chosen['title']}")
    print(f"      {chosen['url']}")
    if len(chosen["path"]) > 1:
        print(f"      under {describe_path(chosen['path'][:-1], issues)}")
    print(f"      rank {chosen['rank']}")

    if blocked:
        print("\nPassed over (higher up the order, but blocked):")
        for entry in blocked:
            deps = ", ".join(f"#{d}" for d in entry["blocked_by"])
            print(f"  #{entry['number']} {entry['title']}  <- blocked by {deps}")
    return 0


def cmd_list(args) -> int:
    issues = fetch_issues()
    board = fetch_board()

    def render(number: int, depth: int) -> None:
        issue = issues.get(number)
        if issue is None:
            return
        rank = board.get(number, {}).get("rank")
        prefix = "  " * depth
        marker = f"[{rank:>3}] " if rank is not None else "      "
        blockers = open_blockers(issue, issues)
        suffix = ""
        if blockers:
            suffix = "  <- blocked by " + ", ".join(f"#{d}" for d in blockers)
        elif not issue["open_children"]:
            suffix = "  <- ready"
        print(f"{marker}{prefix}#{number} {issue['title']}{suffix}")
        for child in sorted(issue["open_children"], key=lambda c: sort_key(c, board)):
            render(child, depth + 1)

    for root in sorted(roots(issues), key=lambda r: sort_key(r, board)):
        render(root, 0)
    return 0


def find_problems(issues: dict[int, dict], board: dict[int, dict]) -> list[str]:
    """The ways this mechanism rots, checked rather than assumed.

    Pure over its two inputs so the tests exercise THIS function rather than a
    reimplementation of it. A drift guard whose tests restate its logic cannot fail when the
    logic is wrong -- that exact fault has already been fixed once in this repo (8864357).
    """
    problems: list[str] = []

    root_numbers = roots(issues)

    # 1. An open root-level issue with no rank. The order is incomplete and `next` would
    #    silently sort it last.
    for number in sorted(root_numbers):
        if number not in board:
            continue
        if board[number]["rank"] is None:
            problems.append(
                f"#{number} ({issues[number]['title']}) is root-level with no {RANK_FIELD}; "
                "it has no position in the order"
            )

    # 2. Two roots sharing a rank. The order stops being total and the tiebreak becomes
    #    the issue number, which is arrival order, not priority.
    seen: dict[int, list[int]] = {}
    for number in root_numbers:
        rank = board.get(number, {}).get("rank")
        if rank is not None:
            seen.setdefault(rank, []).append(number)
    for rank, numbers in sorted(seen.items()):
        if len(numbers) > 1:
            joined = ", ".join(f"#{n}" for n in sorted(numbers))
            problems.append(f"{RANK_FIELD} {rank} is shared by {joined}; the order is ambiguous")

    # 3. A tracked issue that never reached the board. kord-feature-create does not add
    #    project items (only kord-epic-create does), so a root-level feature is invisible
    #    to a board-stored rank until someone adds it by hand. Loud, not silent.
    for number, issue in sorted(issues.items()):
        if issue["labels"] & TRACKED_LABELS and number not in board:
            problems.append(
                f"#{number} ({issue['title']}) is labelled "
                f"{'/'.join(sorted(issue['labels'] & TRACKED_LABELS))} but is not on the board, "
                "so it cannot be ranked"
            )

    # 4. A dependency naming an issue that does not exist. Reads as satisfied because the
    #    number is not in the OPEN set, which is exactly how a typo becomes "ready".
    for number, issue in sorted(issues.items()):
        for target in dangling_refs(issue, issues):
            problems.append(
                f"#{number} declares `Depends on: #{target}`, but #{target} does not exist"
            )

    return problems


def cmd_check(args) -> int:
    issues = fetch_issues()
    board = fetch_board()
    problems = find_problems(issues, board)

    if args.format == "json":
        print(json.dumps({"problems": problems}, indent=2))
        return 1 if problems else 0

    root_numbers = roots(issues)
    ranked = sum(1 for n in root_numbers if board.get(n, {}).get("rank") is not None)
    print(f"Root-level issues: {len(root_numbers)}  ranked: {ranked}")
    print()
    if problems:
        print(f"FAILED: {len(problems)} problem(s)")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("All checks passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    for name, handler, help_text in [
        ("next", cmd_next, "report the next ready issue to implement"),
        ("list", cmd_list, "show the whole ordered tree"),
        ("check", cmd_check, "report drift in the order; non-zero exit on any problem"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--format", choices=["text", "json"], default="text")
        p.set_defaults(handler=handler)

    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except GhError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
