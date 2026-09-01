"""The `wyrd` CLI entry point: argparse dispatch built from catalog.TOOLS.

docs/design/27-tooling.md section 3: `describe` and dispatch read the same `TOOLS` catalog,
so they cannot drift. Structured JSON is the default output; `--format text` is for a
person at a terminal. Errors are structured (`{"error": {...}}`), never a bare traceback,
for a caller-input validation failure (specs/075-engine-scaffolding/contracts/cli.md).

Python 3.11+, standard library only.
"""

from __future__ import annotations

import argparse
import sys

from wyrd import render, state, verbs
from wyrd.catalog import TOOLS


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wyrd")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    subparsers = parser.add_subparsers(dest="verb", required=True)

    describe_parser = subparsers.add_parser("describe", help="List available verbs.")
    describe_parser.add_argument("--name", help="Show only this verb's catalog entry.")

    # Built from the catalog rather than a second, hand-maintained list of verb names --
    # today there is exactly one (roll), but adding a verb means adding a catalog entry,
    # not touching this dispatch loop.
    if "roll" in TOOLS:
        roll_parser = subparsers.add_parser("roll", help=TOOLS["roll"]["description"])
        roll_parser.add_argument("--sides", type=int, default=100)
        roll_parser.add_argument("--seed", type=int, default=None)

    return parser


def _run_describe(args: argparse.Namespace) -> dict:
    if args.name is not None:
        entry = TOOLS.get(args.name)
        if entry is None:
            return {"error": {"verb": "describe", "reason": f"no such verb: {args.name}"}}
        return entry
    return {"verb": "describe", "tools": list(TOOLS.values())}


def _run_roll(args: argparse.Namespace) -> dict:
    try:
        return verbs.roll(sides=args.sides, seed=args.seed, state_path=state.DEFAULT_STATE_PATH)
    except ValueError as exc:
        return {"error": {"verb": "roll", "reason": str(exc)}}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.verb == "describe":
        result = _run_describe(args)
    elif args.verb == "roll":
        result = _run_roll(args)
    else:  # pragma: no cover - argparse's `required=True` already prevents this
        parser.error(f"unknown verb: {args.verb}")
        return 2

    rendered = render.to_text(result) if args.format == "text" else render.to_json(result)
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
