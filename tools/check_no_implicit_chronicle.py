#!/usr/bin/env python3
"""Check that no engine/wyrd/*.py module holds an implicit, unjustified chronicle-scoped global.

docs/design/21-parallel-chronicles.md, "Isolation is the whole problem": "There is no 'current
chronicle' global, so the wrong one cannot be edited by accident" -- every verb in this codebase
already takes an explicit chronicle path/state by convention (#303). This check turns that
convention into an enforced invariant, catching a future module-level mutable container that
could leak data or a decision from one chronicle into a call meant for another, before it ships.

A **candidate** is a module-level assignment (top of the file, not nested in a function or
class) whose value is an *empty, mutable* container -- `{}`, `[]`, `set()`, or the equivalent
no-argument `dict()`/`list()`/`set()` call -- found via `ast` parsing rather than a text/regex
scan, so it cannot be fooled by a string literal or an indented assignment inside a function
body that merely looks similar (research.md). A populated constant (`_STOP_WORDS =
frozenset({...})`) is never a candidate: it is read-only reference data fixed at import time,
not accumulating state.

A candidate is **justified**, and not flagged, when the contiguous `#`-prefixed comment lines
immediately above it contain the case-insensitive substring `"process-local"` -- the exact
phrase this codebase's one existing exception, `resolution._open_proposals`, already uses
("Process-local proposal store... Never written to disk", docs/design/31-action-resolution.md).
This check operationalises that existing precedent's own language rather than inventing a new
justification vocabulary.

Usage:
    python3 tools/check_no_implicit_chronicle.py
    python3 tools/check_no_implicit_chronicle.py --format json

Python 3.11+, standard library only (docs/design/27-tooling.md). Reads the filesystem, nothing
else. Run on demand -- this repo has no CI to run it automatically.
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys

ENGINE_DIR = "engine/wyrd"
_JUSTIFICATION_MARKER = "process-local"


def _is_mutable_empty(node: ast.AST) -> bool:
    """`True` for an empty `{}`/`[]`/`set()` literal, or a no-argument `dict()`/`list()`/
    `set()` call."""
    if isinstance(node, ast.Dict) and not node.keys:
        return True
    if isinstance(node, (ast.List, ast.Set)) and not node.elts:
        return True
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"dict", "list", "set"}
        and not node.args
        and not node.keywords
    ):
        return True
    return False


def _is_justified(lines: list[str], assignment_lineno: int) -> bool:
    """Whether the contiguous `#`-prefixed lines immediately above `assignment_lineno`
    (1-indexed) contain `_JUSTIFICATION_MARKER`."""
    i = assignment_lineno - 2  # 0-indexed line directly above the assignment
    comment_lines = []
    while i >= 0 and lines[i].strip().startswith("#"):
        comment_lines.append(lines[i])
        i -= 1
    return any(_JUSTIFICATION_MARKER in line.lower() for line in comment_lines)


def find_problems(root: pathlib.Path) -> list[str]:
    """Every unjustified module-level mutable-container candidate under `<root>/engine/wyrd/`,
    formatted as `"<path>:<line>: ..."` strings (FR-001, FR-002, FR-003)."""
    problems = []
    engine_dir = root / ENGINE_DIR
    if not engine_dir.is_dir():
        return problems

    for path in sorted(engine_dir.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines()
        tree = ast.parse(source, filename=str(path))

        for node in tree.body:
            if isinstance(node, ast.Assign):
                targets, value = node.targets, node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets, value = [node.target], node.value
            else:
                continue

            if not _is_mutable_empty(value):
                continue

            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                if _is_justified(lines, node.lineno):
                    continue
                rel = path.relative_to(root).as_posix()
                problems.append(
                    f"{rel}:{node.lineno}: module-level mutable '{target.id}' has no "
                    f"'{_JUSTIFICATION_MARKER}' justification comment"
                )

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--root", default=".", help="repository root (default: cwd)")
    args = parser.parse_args(argv)

    root = pathlib.Path(args.root).resolve()
    problems = find_problems(root)

    if args.format == "json":
        print(json.dumps({"problems": problems}, indent=2))
        return 1 if problems else 0

    if not problems:
        print(f"{ENGINE_DIR}: no unjustified chronicle-scoped globals found")
        return 0

    for problem in problems:
        print(problem)
    print(f"tools/check_no_implicit_chronicle.py: {len(problems)} problem(s) found")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
