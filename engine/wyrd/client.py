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
import pathlib
import sys

from wyrd import overrides, render, state, verbs
from wyrd.catalog import TOOLS
from wyrd.overrides import OverrideError
from wyrd.resolution import ProposalError
from wyrd.state import StateError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wyrd")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    subparsers = parser.add_subparsers(dest="verb", required=True)

    describe_parser = subparsers.add_parser("describe", help="List available verbs.")
    describe_parser.add_argument("--name", help="Show only this verb's catalog entry.")
    describe_parser.add_argument(
        "--overridable",
        action="store_true",
        help="Report the closed overridable set instead of the verb catalog.",
    )
    describe_parser.add_argument(
        "--setting", help="Path to a setting.yaml whose overrides:, if any, filter the catalog."
    )
    describe_parser.add_argument(
        "--chronicle",
        help="Path to a chronicle houserules.yaml, layered on top of --setting.",
    )

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

    if "oracle-prompt" in TOOLS:
        oracle_prompt_parser = subparsers.add_parser(
            "oracle-prompt", help=TOOLS["oracle-prompt"]["description"]
        )
        oracle_prompt_parser.add_argument("--family", required=True)
        oracle_prompt_parser.add_argument("--seed", type=int, default=None)

    if "oracle-answer" in TOOLS:
        oracle_answer_parser = subparsers.add_parser(
            "oracle-answer", help=TOOLS["oracle-answer"]["description"]
        )
        oracle_answer_parser.add_argument("--band", required=True)
        oracle_answer_parser.add_argument("--seed", type=int, default=None)

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

    if "award-advance" in TOOLS:
        award_parser = subparsers.add_parser(
            "award-advance", help=TOOLS["award-advance"]["description"]
        )
        award_parser.add_argument("--trigger", required=True)
        award_parser.add_argument("--awarded", action="append", default=[])
        award_parser.add_argument("--advances-unspent", type=int, default=0)

    if "begin-session" in TOOLS:
        session_parser = subparsers.add_parser(
            "begin-session", help=TOOLS["begin-session"]["description"]
        )
        session_parser.add_argument("--awarded", action="append", default=[])
        session_parser.add_argument("--advances-unspent", type=int, default=0)

    if "spend-advance" in TOOLS:
        spend_parser = subparsers.add_parser(
            "spend-advance", help=TOOLS["spend-advance"]["description"]
        )
        spend_parser.add_argument("--spend", required=True)
        spend_parser.add_argument("--view-json", required=True)
        spend_parser.add_argument("--career-json", required=True)
        spend_parser.add_argument("--careers-json", default=None)
        spend_parser.add_argument("--ancestry-json", default=None)
        spend_parser.add_argument("--skill", default=None)
        spend_parser.add_argument("--target", default=None)

    if "spend-coin" in TOOLS:
        coin_parser = subparsers.add_parser("spend-coin", help=TOOLS["spend-coin"]["description"])
        coin_parser.add_argument("--gear-id", required=True)
        coin_parser.add_argument("--coin", type=int, required=True)
        coin_parser.add_argument("--catalog-json", required=True)

    if "martial-weapon-sighting" in TOOLS:
        sighting_parser = subparsers.add_parser(
            "martial-weapon-sighting", help=TOOLS["martial-weapon-sighting"]["description"]
        )
        sighting_parser.add_argument("--standing", type=int, required=True)
        sighting_parser.add_argument("--already-applied", action="store_true")

    if "adjust-standing" in TOOLS:
        adjust_parser = subparsers.add_parser(
            "adjust-standing", help=TOOLS["adjust-standing"]["description"]
        )
        adjust_parser.add_argument("--standing", type=int, required=True)
        adjust_parser.add_argument("--delta", type=int, required=True)

    if "track" in TOOLS:
        track_parser = subparsers.add_parser("track", help=TOOLS["track"]["description"])
        track_parser.add_argument("--value", type=int, required=True)
        track_parser.add_argument("--mechanism", required=True)
        track_parser.add_argument("--delta", type=int, required=True)
        track_parser.add_argument(
            "--setting", help="Path to a setting.yaml whose overrides:, if any, apply."
        )
        track_parser.add_argument(
            "--chronicle", help="Path to a chronicle houserules.yaml, layered on top of --setting."
        )

    if "find-noun" in TOOLS:
        find_noun_parser = subparsers.add_parser(
            "find-noun", help=TOOLS["find-noun"]["description"]
        )
        find_noun_parser.add_argument("--setting", required=True)
        find_noun_parser.add_argument("--name", required=True)
        find_noun_parser.add_argument(
            "--setting-dir", default=".", help="Root of the setting repository (default: cwd)."
        )

    if "find-rule" in TOOLS:
        find_rule_parser = subparsers.add_parser(
            "find-rule", help=TOOLS["find-rule"]["description"]
        )
        find_rule_parser.add_argument("--setting", required=True)
        find_rule_parser.add_argument("--term", required=True)
        find_rule_parser.add_argument(
            "--setting-dir", default=".", help="Root of the setting repository (default: cwd)."
        )

    if "find-table" in TOOLS:
        find_table_parser = subparsers.add_parser(
            "find-table", help=TOOLS["find-table"]["description"]
        )
        find_table_parser.add_argument("--setting", required=True)
        find_table_parser.add_argument("--dice", default=None, choices=("d6", "d10", "d66", "d100"))
        find_table_parser.add_argument("--about", default=None)
        find_table_parser.add_argument(
            "--setting-dir", default=".", help="Root of the setting repository (default: cwd)."
        )

    if "session-context" in TOOLS:
        session_context_parser = subparsers.add_parser(
            "session-context", help=TOOLS["session-context"]["description"]
        )
        session_context_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "get" in TOOLS:
        get_parser = subparsers.add_parser("get", help=TOOLS["get"]["description"])
        get_parser.add_argument("id")
        get_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "find" in TOOLS:
        find_parser = subparsers.add_parser("find", help=TOOLS["find"]["description"])
        find_parser.add_argument("--type", required=True)
        find_parser.add_argument("--status", default=None)
        find_parser.add_argument("--tag", default=None)
        find_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "party" in TOOLS:
        party_parser = subparsers.add_parser("party", help=TOOLS["party"]["description"])
        party_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "threads" in TOOLS:
        threads_parser = subparsers.add_parser("threads", help=TOOLS["threads"]["description"])
        threads_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "threats" in TOOLS:
        threats_parser = subparsers.add_parser("threats", help=TOOLS["threats"]["description"])
        threats_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "log" in TOOLS:
        log_parser = subparsers.add_parser("log", help=TOOLS["log"]["description"])
        log_group = log_parser.add_mutually_exclusive_group(required=True)
        log_group.add_argument("--last", type=int, default=None)
        log_group.add_argument("--since", default=None)
        log_parser.add_argument("--chronicle-name", required=True)
        log_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "save" in TOOLS:
        save_parser = subparsers.add_parser("save", help=TOOLS["save"]["description"])
        save_parser.add_argument("--state-json", required=True)
        save_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "load" in TOOLS:
        load_parser = subparsers.add_parser("load", help=TOOLS["load"]["description"])
        load_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "validate" in TOOLS:
        validate_parser = subparsers.add_parser("validate", help=TOOLS["validate"]["description"])
        validate_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "recap" in TOOLS:
        recap_parser = subparsers.add_parser("recap", help=TOOLS["recap"]["description"])
        recap_parser.add_argument("--where", default=None)
        recap_parser.add_argument("--changes", action="append", default=None)
        recap_parser.add_argument("--body-mind", default=None)
        recap_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "advance-time" in TOOLS:
        advance_time_parser = subparsers.add_parser(
            "advance-time", help=TOOLS["advance-time"]["description"]
        )
        advance_time_parser.add_argument("days", type=int)
        advance_time_parser.add_argument("--seed", type=int, default=None)
        advance_time_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

    if "threat-check" in TOOLS:
        threat_check_parser = subparsers.add_parser(
            "threat-check", help=TOOLS["threat-check"]["description"]
        )
        threat_check_parser.add_argument("id")
        threat_check_parser.add_argument("--seed", type=int, default=None)
        threat_check_parser.add_argument(
            "--chronicle-dir", default=".", help="Root of the chronicle (default: cwd)."
        )

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
        propose_parser.add_argument("--dread-witnessed", action="store_true")
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


def _load_resolved(
    setting_path: str | None, chronicle_path: str | None
) -> overrides.ResolvedConfig | None:
    """Resolve `--setting`/`--chronicle` into a `ResolvedConfig`, or `None` if neither is given.

    Reads each file's `overrides:` block through `state.parse_yaml` -- the engine's own
    restricted reader (docs/design/27-tooling.md section 2: no third-party YAML dependency),
    never `tools/`'s authoring-time linter, per the layering `state.py` already documents.
    """
    layers: list[tuple[str, dict]] = [("engine", {})]
    if setting_path:
        data = state.parse_yaml(pathlib.Path(setting_path).read_text(encoding="utf-8"))
        layers.append(("setting", data.get("overrides") or {}))
    if chronicle_path:
        data = state.parse_yaml(pathlib.Path(chronicle_path).read_text(encoding="utf-8"))
        layers.append(("chronicle", data.get("overrides") or data or {}))
    if len(layers) == 1:
        return None
    return overrides.resolve(layers)


def _run_describe(args: argparse.Namespace) -> dict:
    if args.overridable:
        return {"verb": "describe", "overridable": overrides.describe_overridable()}

    resolved = _load_resolved(args.setting, args.chronicle)
    tools = TOOLS if resolved is None else overrides.filter_tools(TOOLS, resolved)

    if args.name is not None:
        entry = tools.get(args.name)
        if entry is None:
            return {"error": {"verb": "describe", "reason": f"no such verb: {args.name}"}}
        return entry
    return {"verb": "describe", "tools": list(tools.values())}


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


def _run_oracle_prompt(args: argparse.Namespace) -> dict:
    try:
        return verbs.oracle_prompt(args.family, seed=args.seed)
    except ValueError as exc:
        return {"error": {"verb": "oracle-prompt", "reason": str(exc)}}


def _run_oracle_answer(args: argparse.Namespace) -> dict:
    try:
        return verbs.oracle_answer(args.band, seed=args.seed)
    except ValueError as exc:
        return {"error": {"verb": "oracle-answer", "reason": str(exc)}}


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


def _run_award_advance(args: argparse.Namespace) -> dict:
    return verbs.award_advance(
        trigger=args.trigger,
        awarded=args.awarded,
        advances_unspent=args.advances_unspent,
    )


def _run_begin_session(args: argparse.Namespace) -> dict:
    return verbs.begin_session(
        awarded=args.awarded,
        advances_unspent=args.advances_unspent,
    )


def _run_spend_advance(args: argparse.Namespace) -> dict:
    return verbs.spend_advance(
        spend=args.spend,
        view=json.loads(args.view_json),
        career_data=json.loads(args.career_json),
        careers=json.loads(args.careers_json) if args.careers_json is not None else None,
        ancestry=json.loads(args.ancestry_json) if args.ancestry_json is not None else None,
        skill=args.skill,
        target=args.target,
    )


def _run_spend_coin(args: argparse.Namespace) -> dict:
    return verbs.spend_coin(
        gear_id=args.gear_id,
        coin=args.coin,
        catalog=json.loads(args.catalog_json),
    )


def _run_martial_weapon_sighting(args: argparse.Namespace) -> dict:
    return verbs.martial_weapon_sighting(
        standing=args.standing,
        already_applied=args.already_applied,
    )


def _run_adjust_standing(args: argparse.Namespace) -> dict:
    return verbs.adjust_standing(
        standing=args.standing,
        delta=args.delta,
    )


def _run_track(args: argparse.Namespace) -> dict:
    resolved = _load_resolved(args.setting, args.chronicle)
    return verbs.track(
        value=args.value,
        mechanism=args.mechanism,
        delta=args.delta,
        resolved=resolved,
    )


def _run_find_noun(args: argparse.Namespace) -> dict:
    return verbs.find_noun(
        setting=args.setting, name=args.name, setting_dir=pathlib.Path(args.setting_dir)
    )


def _run_find_rule(args: argparse.Namespace) -> dict:
    return verbs.find_rule(
        setting=args.setting, term=args.term, setting_dir=pathlib.Path(args.setting_dir)
    )


def _run_find_table(args: argparse.Namespace) -> dict:
    return verbs.find_table(
        setting=args.setting,
        setting_dir=pathlib.Path(args.setting_dir),
        dice=args.dice,
        about=args.about,
    )


def _run_session_context(args: argparse.Namespace) -> dict:
    return verbs.session_context(pathlib.Path(args.chronicle_dir))


def _run_get(args: argparse.Namespace) -> dict:
    try:
        return verbs.get(args.id, pathlib.Path(args.chronicle_dir))
    except StateError as exc:
        return {"error": {"verb": "get", "reason": str(exc)}}


def _run_find(args: argparse.Namespace) -> dict:
    return verbs.find(
        pathlib.Path(args.chronicle_dir), type=args.type, status=args.status, tag=args.tag
    )


def _run_party(args: argparse.Namespace) -> dict:
    return verbs.party(pathlib.Path(args.chronicle_dir))


def _run_threads(args: argparse.Namespace) -> dict:
    return verbs.threads(pathlib.Path(args.chronicle_dir))


def _run_threats(args: argparse.Namespace) -> dict:
    return verbs.threats(pathlib.Path(args.chronicle_dir))


def _run_log(args: argparse.Namespace) -> dict:
    try:
        return verbs.log(
            pathlib.Path(args.chronicle_dir),
            args.chronicle_name,
            last=args.last,
            since=args.since,
        )
    except ValueError as exc:
        return {"error": {"verb": "log", "reason": str(exc)}}


def _run_save(args: argparse.Namespace) -> dict:
    try:
        chronicle_state = json.loads(args.state_json)
        return verbs.save(chronicle_state, pathlib.Path(args.chronicle_dir))
    except (StateError, json.JSONDecodeError) as exc:
        return {"error": {"verb": "save", "reason": str(exc)}}


def _run_load(args: argparse.Namespace) -> dict:
    try:
        return verbs.load(pathlib.Path(args.chronicle_dir))
    except StateError as exc:
        return {"error": {"verb": "load", "reason": str(exc)}}


def _run_validate(args: argparse.Namespace) -> dict:
    return verbs.validate(pathlib.Path(args.chronicle_dir))


def _run_recap(args: argparse.Namespace) -> dict:
    try:
        return verbs.recap(
            pathlib.Path(args.chronicle_dir),
            where=args.where,
            changes=args.changes,
            body_mind=args.body_mind,
        )
    except StateError as exc:
        return {"error": {"verb": "recap", "reason": str(exc)}}


def _run_advance_time(args: argparse.Namespace) -> dict:
    try:
        return verbs.advance_time(pathlib.Path(args.chronicle_dir), args.days, seed=args.seed)
    except (ValueError, StateError) as exc:
        return {"error": {"verb": "advance-time", "reason": str(exc)}}


def _run_threat_check(args: argparse.Namespace) -> dict:
    try:
        return verbs.threat_check(pathlib.Path(args.chronicle_dir), args.id, seed=args.seed)
    except StateError as exc:
        return {"error": {"verb": "threat-check", "reason": str(exc)}}


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
            dread_witnessed=args.dread_witnessed,
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
        try:
            result = _run_describe(args)
        except OverrideError as exc:
            result = {"error": {"verb": "describe", "reason": str(exc)}}
    elif args.verb == "roll":
        result = _run_roll(args)
    elif args.verb == "opposed-test":
        result = _run_opposed_test(args)
    elif args.verb == "declaration-bonus":
        result = _run_declaration_bonus(args)
    elif args.verb == "oracle-prompt":
        result = _run_oracle_prompt(args)
    elif args.verb == "oracle-answer":
        result = _run_oracle_answer(args)
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
    elif args.verb == "award-advance":
        result = _run_award_advance(args)
    elif args.verb == "begin-session":
        result = _run_begin_session(args)
    elif args.verb == "spend-advance":
        result = _run_spend_advance(args)
    elif args.verb == "spend-coin":
        result = _run_spend_coin(args)
    elif args.verb == "martial-weapon-sighting":
        result = _run_martial_weapon_sighting(args)
    elif args.verb == "adjust-standing":
        result = _run_adjust_standing(args)
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
    elif args.verb == "track":
        try:
            result = _run_track(args)
        except OverrideError as exc:
            result = {"error": {"verb": "track", "reason": str(exc)}}
    elif args.verb == "find-noun":
        result = _run_find_noun(args)
    elif args.verb == "find-rule":
        result = _run_find_rule(args)
    elif args.verb == "find-table":
        result = _run_find_table(args)
    elif args.verb == "session-context":
        result = _run_session_context(args)
    elif args.verb == "get":
        result = _run_get(args)
    elif args.verb == "find":
        result = _run_find(args)
    elif args.verb == "party":
        result = _run_party(args)
    elif args.verb == "threads":
        result = _run_threads(args)
    elif args.verb == "threats":
        result = _run_threats(args)
    elif args.verb == "log":
        result = _run_log(args)
    elif args.verb == "save":
        result = _run_save(args)
    elif args.verb == "load":
        result = _run_load(args)
    elif args.verb == "validate":
        result = _run_validate(args)
    elif args.verb == "recap":
        result = _run_recap(args)
    elif args.verb == "advance-time":
        result = _run_advance_time(args)
    elif args.verb == "threat-check":
        result = _run_threat_check(args)
    else:  # pragma: no cover - argparse's `required=True` already prevents this
        parser.error(f"unknown verb: {args.verb}")
        return 2

    rendered = render.to_text(result) if args.format == "text" else render.to_json(result)
    print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
