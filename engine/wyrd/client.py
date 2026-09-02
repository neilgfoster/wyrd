"""The `wyrd` CLI entry point: argparse dispatch built from catalog.TOOLS.

docs/design/27-tooling.md section 3: `describe` and dispatch read the same `TOOLS` catalog,
so they cannot drift. Structured JSON is the default output; `--format text` is for a
person at a terminal. Errors are structured (`{"error": {...}}`), never a bare traceback,
for a caller-input validation failure (specs/075-engine-scaffolding/contracts/cli.md).

Python 3.11+, standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys

from wyrd import render, state, verbs
from wyrd.catalog import TOOLS
from wyrd.resolution import ProposalError
from wyrd.state import StateError


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

    if "opposed-test" in TOOLS:
        opposed_parser = subparsers.add_parser(
            "opposed-test", help=TOOLS["opposed-test"]["description"]
        )
        opposed_parser.add_argument("--skill", type=int, required=True)
        opposed_parser.add_argument("--opponent", type=int, required=True)
        opposed_parser.add_argument("--seed", type=int, default=None)
        opposed_parser.add_argument("--declaration", default=None)
        opposed_parser.add_argument("--helper-skill", type=int, default=None)
        opposed_parser.add_argument(
            "--helper-cannot-attempt", dest="helper_can_attempt", action="store_false"
        )

    if "declaration-bonus" in TOOLS:
        declaration_parser = subparsers.add_parser(
            "declaration-bonus", help=TOOLS["declaration-bonus"]["description"]
        )
        declaration_parser.add_argument("--category", required=True)

    if "assistance-bonus" in TOOLS:
        assistance_parser = subparsers.add_parser(
            "assistance-bonus", help=TOOLS["assistance-bonus"]["description"]
        )
        assistance_parser.add_argument("--helper-skill", type=int, required=True)
        assistance_parser.add_argument("--can-attempt", type=_parse_bool, default=True)

    if "group-test" in TOOLS:
        group_parser = subparsers.add_parser("group-test", help=TOOLS["group-test"]["description"])
        group_parser.add_argument("--member-skills", type=_parse_member_skills, required=True)
        group_parser.add_argument("--mode", required=True)
        group_parser.add_argument("--opponent", type=int, required=True)
        group_parser.add_argument("--seed", type=int, default=None)

    if "extended-task-interval" in TOOLS:
        interval_parser = subparsers.add_parser(
            "extended-task-interval", help=TOOLS["extended-task-interval"]["description"]
        )
        interval_parser.add_argument("--skill", type=int, required=True)
        interval_parser.add_argument("--opponent", type=int, required=True)
        interval_parser.add_argument("--progress", type=int, required=True)
        interval_parser.add_argument("--target", type=int, required=True)
        interval_parser.add_argument("--seed", type=int, default=None)

    if "character-save" in TOOLS:
        save_parser = subparsers.add_parser(
            "character-save", help=TOOLS["character-save"]["description"]
        )
        save_parser.add_argument("--path", required=True)
        save_parser.add_argument("--frontmatter-json", required=True)
        save_parser.add_argument("--body", default="")

    if "character-load" in TOOLS:
        load_parser = subparsers.add_parser(
            "character-load", help=TOOLS["character-load"]["description"]
        )
        load_parser.add_argument("--path", required=True)

    if "skill-scale" in TOOLS:
        subparsers.add_parser("skill-scale", help=TOOLS["skill-scale"]["description"])

    if "validate-allocation" in TOOLS:
        allocation_parser = subparsers.add_parser(
            "validate-allocation", help=TOOLS["validate-allocation"]["description"]
        )
        allocation_parser.add_argument("--career-json", required=True)
        allocation_parser.add_argument("--ancestry-json", default=None)
        allocation_parser.add_argument("--actions-json", required=True)

    if "create-character" in TOOLS:
        creation_parser = subparsers.add_parser(
            "create-character", help=TOOLS["create-character"]["description"]
        )
        creation_parser.add_argument("--path", required=True)
        creation_parser.add_argument("--name", required=True)
        creation_parser.add_argument("--career-json", required=True)
        creation_parser.add_argument("--ancestry-json", default=None)
        creation_parser.add_argument("--actions-json", required=True)
        creation_parser.add_argument("--loyalty", required=True)
        creation_parser.add_argument("--mortality", required=True)
        creation_parser.add_argument("--drives-json", default="[]")
        creation_parser.add_argument("--misfortune", default=None)
        creation_parser.add_argument("--fault-line", required=True)

    if "propose" in TOOLS:
        propose_parser = subparsers.add_parser("propose", help=TOOLS["propose"]["description"])
        propose_parser.add_argument("--actor", required=True)
        propose_parser.add_argument(
            "--mechanic", required=True, choices=("ordinary-test", "exposure", "combat-attack")
        )
        propose_parser.add_argument("--skill", default=None)
        propose_parser.add_argument("--target", default=None)
        propose_parser.add_argument("--difficulty", default="average")
        propose_parser.add_argument("--declaration-bonus", type=int, default=0)
        propose_parser.add_argument(
            "--tier", default=None, choices=(None, "minor", "moderate", "major")
        )
        propose_parser.add_argument("--weapon-dice", default=None)
        propose_parser.add_argument("--armour-dice", default=None)
        propose_parser.add_argument(
            "--damage-type",
            default=None,
            choices=(None, "slashing", "piercing", "blunt", "searing"),
        )
        propose_parser.add_argument("--seed", type=int, default=None)

    if "commit" in TOOLS:
        commit_parser = subparsers.add_parser("commit", help=TOOLS["commit"]["description"])
        commit_parser.add_argument("proposal_id")

    if "discard" in TOOLS:
        discard_parser = subparsers.add_parser("discard", help=TOOLS["discard"]["description"])
        discard_parser.add_argument("proposal_id")

    if "reroll" in TOOLS:
        reroll_parser = subparsers.add_parser("reroll", help=TOOLS["reroll"]["description"])
        reroll_parser.add_argument("proposal_id")
        reroll_parser.add_argument("--step", type=int, required=True)
        reroll_parser.add_argument(
            "--resource", required=True, choices=("resolve", "fortune", "bargain")
        )
        reroll_parser.add_argument("--seed", type=int, default=None)

    return parser


def _parse_member_skills(text: str) -> list[int | None]:
    """Parse a comma-separated `--member-skills` list; an empty entry means untrained."""
    if text == "":
        return []
    return [int(item) if item != "" else None for item in text.split(",")]


def _parse_bool(text: str) -> bool:
    if text.lower() in ("true", "1", "yes"):
        return True
    if text.lower() in ("false", "0", "no"):
        return False
    raise argparse.ArgumentTypeError(f"expected a boolean, got {text!r}")


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


def _run_opposed_test(args: argparse.Namespace) -> dict:
    try:
        return verbs.opposed_test(
            skill=args.skill,
            opponent=args.opponent,
            seed=args.seed,
            declaration=args.declaration,
            helper_skill=args.helper_skill,
            helper_can_attempt=args.helper_can_attempt,
        )
    except ValueError as exc:
        return {"error": {"verb": "opposed-test", "reason": str(exc)}}


def _run_declaration_bonus(args: argparse.Namespace) -> dict:
    try:
        return verbs.declaration_bonus(args.category)
    except ValueError as exc:
        return {"error": {"verb": "declaration-bonus", "reason": str(exc)}}


def _run_assistance_bonus(args: argparse.Namespace) -> dict:
    return verbs.assistance_bonus(helper_skill=args.helper_skill, can_attempt=args.can_attempt)


def _run_group_test(args: argparse.Namespace) -> dict:
    try:
        return verbs.group_test(
            member_skills=args.member_skills,
            mode=args.mode,
            opponent=args.opponent,
            seed=args.seed,
        )
    except ValueError as exc:
        return {"error": {"verb": "group-test", "reason": str(exc)}}


def _run_extended_task_interval(args: argparse.Namespace) -> dict:
    return verbs.resolve_extended_interval(
        skill=args.skill,
        opponent=args.opponent,
        progress=args.progress,
        target=args.target,
        seed=args.seed,
    )


def _run_character_save(args: argparse.Namespace) -> dict:
    try:
        frontmatter = json.loads(args.frontmatter_json)
        return verbs.character_save(path=args.path, frontmatter=frontmatter, body=args.body)
    except (StateError, json.JSONDecodeError) as exc:
        return {"error": {"verb": "character-save", "reason": str(exc)}}


def _run_character_load(args: argparse.Namespace) -> dict:
    try:
        return verbs.character_load(path=args.path)
    except StateError as exc:
        return {"error": {"verb": "character-load", "reason": str(exc)}}


def _run_skill_scale(args: argparse.Namespace) -> dict:
    return verbs.skill_scale()


def _run_validate_allocation(args: argparse.Namespace) -> dict:
    # Malformed JSON is a genuine caller mistake distinct from a rejected-but-well-formed
    # allocation; per contracts/cli.md it propagates as an uncaught, non-zero-exit failure
    # rather than the structured {"error": ...} shape (that shape is reserved for a
    # well-formed allocation's own documented validation result).
    career_data = json.loads(args.career_json)
    ancestry = json.loads(args.ancestry_json) if args.ancestry_json is not None else None
    actions = json.loads(args.actions_json)
    return verbs.validate_allocation(actions, career_data, ancestry)


def _run_create_character(args: argparse.Namespace) -> dict:
    career_data = json.loads(args.career_json)
    ancestry = json.loads(args.ancestry_json) if args.ancestry_json is not None else None
    actions = json.loads(args.actions_json)
    drives = json.loads(args.drives_json)
    return verbs.create_character(
        path=args.path,
        name=args.name,
        career_data=career_data,
        actions=actions,
        loyalty=args.loyalty,
        mortality=args.mortality,
        fault_line=args.fault_line,
        ancestry=ancestry,
        drives=drives,
        misfortune=args.misfortune,
    )


def _run_propose(args: argparse.Namespace) -> dict:
    try:
        return verbs.propose(
            actor=args.actor,
            mechanic=args.mechanic,
            skill=args.skill,
            target=args.target,
            difficulty=args.difficulty,
            declaration_bonus=args.declaration_bonus,
            tier=args.tier,
            weapon_dice=args.weapon_dice,
            armour_dice=args.armour_dice,
            damage_type=args.damage_type,
            seed=args.seed,
        )
    except (ValueError, StateError) as exc:
        return {"error": {"verb": "propose", "reason": str(exc)}}


def _run_commit(args: argparse.Namespace) -> dict:
    try:
        return verbs.commit(args.proposal_id)
    except ProposalError as exc:
        return {"error": {"verb": "commit", "reason": str(exc)}}


def _run_discard(args: argparse.Namespace) -> dict:
    try:
        return verbs.discard(args.proposal_id)
    except ProposalError as exc:
        return {"error": {"verb": "discard", "reason": str(exc)}}


def _run_reroll(args: argparse.Namespace) -> dict:
    try:
        return verbs.reroll(
            args.proposal_id, step=args.step, resource=args.resource, seed=args.seed
        )
    except (ValueError, ProposalError) as exc:
        return {"error": {"verb": "reroll", "reason": str(exc)}}


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.verb == "describe":
        result = _run_describe(args)
    elif args.verb == "roll":
        result = _run_roll(args)
    elif args.verb == "opposed-test":
        result = _run_opposed_test(args)
    elif args.verb == "declaration-bonus":
        result = _run_declaration_bonus(args)
    elif args.verb == "assistance-bonus":
        result = _run_assistance_bonus(args)
    elif args.verb == "group-test":
        result = _run_group_test(args)
    elif args.verb == "extended-task-interval":
        result = _run_extended_task_interval(args)
    elif args.verb == "character-save":
        result = _run_character_save(args)
    elif args.verb == "character-load":
        result = _run_character_load(args)
    elif args.verb == "skill-scale":
        result = _run_skill_scale(args)
    elif args.verb == "validate-allocation":
        result = _run_validate_allocation(args)
    elif args.verb == "create-character":
        result = _run_create_character(args)
    elif args.verb == "propose":
        result = _run_propose(args)
    elif args.verb == "commit":
        result = _run_commit(args)
    elif args.verb == "discard":
        result = _run_discard(args)
    elif args.verb == "reroll":
        result = _run_reroll(args)
    else:  # pragma: no cover - argparse's `required=True` already prevents this
        parser.error(f"unknown verb: {args.verb}")
        return 2

    rendered = render.to_text(result) if args.format == "text" else render.to_json(result)
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
