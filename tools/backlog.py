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
Python 3.11+, standard library only (doc/design/20-tooling.md).
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


def effective_blockers(path: list[int], issues: dict[int, dict]) -> list[int]:
    """Every currently-open issue that this issue, or any ancestor on `path`, depends on.

    A leaf is not ready merely because it carries no `Depends on:` of its own -- CLAUDE.md's
    own rule ("a rank orders what you choose between, it never authorises work whose
    prerequisites are open") applies to an ancestor epic's declared dependency too. #90
    ("Implement the engine") declares `Depends on: #1`; before this, a leaf under #90 with no
    dependency of its own read as ready even while #1 was open, and #31 was picked up as a
    result. Order-preserving and deduplicated across the whole path so the same blocker is
    not repeated.
    """
    blockers: list[int] = []
    for number in path:
        issue = issues.get(number)
        if issue is None:
            continue
        for blocker in open_blockers(issue, issues):
            if blocker not in blockers:
                blockers.append(blocker)
    return blockers


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
    """The first ready leaf, and every blocked or spent issue passed over on the way to it.

    Depth-first through the ranked roots. A leaf is an issue with no OPEN children; it is
    ready when every issue it declares a dependency on is closed. The blocked list is
    returned rather than discarded so `next` can say why the obvious answer was not chosen --
    and, since a spent epic occupies a rank position too, it is reported through the same
    list rather than a disconnected side channel `next` might not weigh against its answer.

    An epic is never *implementation* work. An epic with no open children is a *spent* epic,
    and is one of two distinct things depending on whether it ever had children at all:

    - **children non-empty, all closed** ("close"): finished. Closing it is never gated by
      its own `Depends on:` -- that dependency was about permission to do the work, and the
      work is already done. Handing an epic out as implementation work is how a completed
      stage gets silently reopened as a task: found when Stage 2's children closed and `next`
      offered the stage itself.
    - **children empty** ("decompose"): never broken down. Decomposing it *is* gated by its
      own `Depends on:` -- an epic that explicitly defers its own decomposition (`Implement
      the engine`, `Depends on: #1`) must not be offered for decomposition while that holds.

    Both are recorded in `blocked` with an `action` field (`"close"` / `"decompose"`, vs.
    `"blocked"` for an ordinary not-ready leaf) so `cmd_next` can recognize that resolving one
    of these may unblock a higher-ranked root than any ready leaf found elsewhere -- CLAUDE.md:
    a rank orders what you choose between, and an un-actioned spent epic at a higher rank is
    exactly the kind of prerequisite that should outrank a lower-ranked ready leaf.
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
        blockers = effective_blockers(path, issues)
        entry = {
            "number": number,
            "title": issue["title"],
            "url": issue["url"],
            "path": path,
            "rank": board.get(path[0], {}).get("rank"),
            "blocked_by": blockers,
        }
        if issue["is_epic"]:
            # Never the answer, at any rank -- but recorded, not discarded: see the
            # "close" vs "decompose" split in the docstring above.
            entry["action"] = "close" if issue["children"] else "decompose"
            blocked.append(entry)
            return None
        entry["action"] = "blocked"
        if blockers:
            blocked.append(entry)
            return None
        return entry

    for root in sorted(roots(issues), key=lambda r: sort_key(r, board)):
        chosen = visit(root, [])
        if chosen:
            break
    return chosen, blocked


def spent_epics(issues: dict[int, dict], board: dict[int, dict]) -> list[dict]:
    """Every open epic with no open children, ranked ones first.

    Each is either finished and wanting closure, or never decomposed and hiding work that
    cannot be reached. Both stall the backlog silently: an undecomposed epic is skipped by
    the walk forever, and a finished one used to be offered as the next thing to build.

    A full scan rather than a by-product of the walk, which stops at its first answer.
    """
    found = [
        {
            "number": n,
            "title": i["title"],
            "url": i["url"],
            "rank": board.get(n, {}).get("rank"),
            "root": i["parent"] is None,
        }
        for n, i in issues.items()
        if i["is_epic"] and not i["open_children"]
    ]
    return sorted(found, key=lambda e: (e["rank"] is None, e["rank"] or 0, e["number"]))


def describe_path(path: list[int], issues: dict[int, dict]) -> str:
    return " > ".join(f"#{n} {issues[n]['title']}" for n in path if n in issues)


def lifecycle_action_outranking(chosen: dict | None, blocked: list[dict]) -> dict | None:
    """The highest-priority actionable close/decompose entry, if it outranks `chosen`.

    "Actionable" means a `"close"` entry (never gated -- the work behind it is already done,
    so its own `Depends on:` is irrelevant to the bookkeeping of closing it) or a
    `"decompose"` entry with no blockers of its own. "Outranks" means its rank is at or above
    `chosen`'s (lower number = higher priority), or nothing was chosen at all -- #90 sitting
    at rank 20 with zero children, above a ready leaf found only at rank 30 under a different
    root, is exactly the case this exists to catch: CLAUDE.md's "a rank orders what you choose
    between" applies to a spent epic's un-actioned position too, not only to real leaves.
    """
    candidates = [
        e for e in blocked
        if e["action"] in ("close", "decompose")
        and (e["action"] == "close" or not e["blocked_by"])
    ]
    if not candidates:
        return None
    best = min(candidates, key=lambda e: (e["rank"] is None, e["rank"] or 0, e["number"]))
    if chosen is None:
        return best
    if best["rank"] is None:
        return None
    if chosen["rank"] is None or best["rank"] <= chosen["rank"]:
        return best
    return None


def format_passed_over(entry: dict) -> str:
    if entry["action"] == "close":
        return f"  #{entry['number']} {entry['title']}  <- finished; close it"
    if entry["action"] == "decompose":
        if entry["blocked_by"]:
            deps = ", ".join(f"#{d}" for d in entry["blocked_by"])
            return f"  #{entry['number']} {entry['title']}  <- no children yet, and blocked by {deps}"
        return f"  #{entry['number']} {entry['title']}  <- no children yet; decompose it"
    deps = ", ".join(f"#{d}" for d in entry["blocked_by"])
    return f"  #{entry['number']} {entry['title']}  <- blocked by {deps}"


def cmd_next(args) -> int:
    issues = fetch_issues()
    board = fetch_board()
    chosen, blocked = walk(issues, board)
    spent = spent_epics(issues, board)
    preferred = lifecycle_action_outranking(chosen, blocked)
    rest = [e for e in blocked if e is not preferred]

    if args.format == "json":
        print(json.dumps(
            {
                "next": preferred or chosen,
                "superseded_leaf": chosen if (preferred and chosen) else None,
                "blocked": rest,
                "spent_epics": spent,
            },
            indent=2,
        ))
        return 0 if (preferred or chosen) else 1

    if preferred:
        verb = "Close" if preferred["action"] == "close" else "Decompose"
        why = (
            "it has finished (every child is closed)"
            if preferred["action"] == "close"
            else "nothing has been broken out under it yet"
        )
        print(f"Next: {verb} #{preferred['number']}  {preferred['title']}")
        print(f"      {preferred['url']}")
        if len(preferred["path"]) > 1:
            print(f"      under {describe_path(preferred['path'][:-1], issues)}")
        print(f"      rank {preferred['rank']} -- {why}, outranking any ready leaf found")
        if chosen:
            print(
                f"\n(The best ready leaf otherwise was #{chosen['number']} {chosen['title']}, "
                f"rank {chosen['rank']} -- lower priority than the action above.)"
            )
        if rest:
            print("\nAlso passed over:")
            for entry in rest:
                print(format_passed_over(entry))
        report_spent(spent)
        return 0

    if not chosen:
        print("Nothing is ready to start.")
        if blocked:
            print("\nEverything reachable is blocked:")
            for entry in blocked:
                print(format_passed_over(entry))
        report_spent(spent)
        return 1

    print(f"Next: #{chosen['number']}  {chosen['title']}")
    print(f"      {chosen['url']}")
    if len(chosen["path"]) > 1:
        print(f"      under {describe_path(chosen['path'][:-1], issues)}")
    print(f"      rank {chosen['rank']}")

    if rest:
        print("\nPassed over (higher up the order, but blocked):")
        for entry in rest:
            print(format_passed_over(entry))

    report_spent(spent)
    return 0


def report_spent(spent: list[dict]) -> None:
    """Epics with nothing open inside them. Finished, or never decomposed."""
    if not spent:
        return
    print(f"\n{len(spent)} epic(s) with no open children — close them, or decompose them:")
    for entry in spent:
        rank = f"rank {entry['rank']}" if entry["rank"] is not None else "unranked"
        print(f"  #{entry['number']} {entry['title']}  ({rank})")


def render_notes(issue: dict, blockers: list[int]) -> list[str]:
    """The status notes `list` prints for one issue -- pure, so both can be true at once.

    Before this, an epic's "no open children" note replaced its "blocked by" note entirely
    (an `elif`), so a childless epic that was also blocked silently stopped reporting the
    block the moment it lost its last child -- exactly what happened to #90 ("Implement the
    engine", `Depends on: #1`) when #31 was removed as its child: it went from showing
    `blocked by #1` to showing only `no open children; close or decompose`, even though it was
    still both. Both notes are independent facts about the issue and both are reported.
    """
    notes: list[str] = []
    if blockers:
        notes.append("blocked by " + ", ".join(f"#{d}" for d in blockers))
    if issue["is_epic"] and not issue["open_children"]:
        notes.append("no open children; close or decompose")
    elif not blockers and not issue["open_children"]:
        notes.append("ready")
    return notes


def cmd_list(args) -> int:
    issues = fetch_issues()
    board = fetch_board()

    def render(number: int, depth: int, path: list[int]) -> None:
        issue = issues.get(number)
        if issue is None:
            return
        path = path + [number]
        rank = board.get(number, {}).get("rank")
        prefix = "  " * depth
        marker = f"[{rank:>3}] " if rank is not None else "      "
        blockers = effective_blockers(path, issues)
        notes = render_notes(issue, blockers)
        suffix = "  <- " + "; ".join(notes) if notes else ""
        print(f"{marker}{prefix}#{number} {issue['title']}{suffix}")
        for child in sorted(issue["open_children"], key=lambda c: sort_key(c, board)):
            render(child, depth + 1, path)

    for root in sorted(roots(issues), key=lambda r: sort_key(r, board)):
        render(root, 0, [])
    return 0


def find_problems(issues: dict[int, dict], board: dict[int, dict]) -> list[str]:
    """The ways this mechanism rots, checked rather than assumed.

    Pure over its two inputs so the tests exercise THIS function rather than a
    reimplementation of it. A drift guard whose tests restate its logic cannot fail when the
    logic is wrong -- that exact fault has already been fixed once in this repo (8864357).
    """
    problems: list[str] = []

    root_numbers = set(roots(issues))

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

    # 4. A ranked item that is NOT root-level. Ranks belong to roots only; a child that was
    #    once a root keeps its Rank when it is re-parented, and the stale value then shows up
    #    in `list` as though the child were ordered. Found exactly that way after the design
    #    programme restructure moved #26 under a stage.
    for number, issue in sorted(issues.items()):
        if number in root_numbers:
            continue
        rank = board.get(number, {}).get("rank")
        if rank is not None:
            problems.append(
                f"#{number} ({issue['title']}) has {RANK_FIELD} {rank} but is not root-level "
                f"(parent #{issue['parent']}); only roots carry a rank"
            )

    # 5. A dependency naming an issue that does not exist. Reads as satisfied because the
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
