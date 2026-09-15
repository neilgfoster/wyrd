"""The operations behind each catalog entry.

Each function here wires `rules.py`'s pure logic to `state.py`'s persistence, so the state
write happens as part of resolving the verb -- before the result is returned for narration
(docs/design/01-principles.md principle 2). Python 3.11+, standard library only.
"""

from __future__ import annotations

import json
import pathlib

from wyrd import advance_time as advance_time_module
from wyrd import (
    advancement,
    career,
    character,
    corpus_excerpt,
    corpus_find,
    creation,
    economy,
    loadtier,
    overrides,
    resolution,
    rules,
    state,
)
from wyrd import downtime as downtime_module
from wyrd import log as log_module
from wyrd import rally as rally_module
from wyrd import threat as threat_module


def roll(
    sides: int = 100,
    seed: int | None = None,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """Resolve the `roll` verb: roll, persist, then return the structured result.

    Raises `ValueError` for an invalid `sides` (propagated from `rules.roll_d100`,
    unchanged) -- `client.py` is responsible for turning that into the structured
    `{"error": ...}` shape at the CLI boundary; this function stays a plain Python API.
    """
    result = rules.roll_d100(sides=sides, seed=seed)
    current = state.load(state_path)
    current["last_roll"] = {"verb": "roll", "sides": sides, "result": result, "seed": seed}
    state.save(current, state_path)
    return {
        "verb": "roll",
        "sides": sides,
        "result": result,
        "seed": seed,
        "state_written": True,
    }


def opposed_test(
    skill: int,
    opponent: int,
    seed: int | None = None,
    declaration: str | None = None,
    helper_skill: int | None = None,
    helper_can_attempt: bool = True,
) -> dict:
    """Resolve the `opposed-test` verb.

    A thin wrapper over `rules.opposed_test` -- no state read or write, unlike `roll`.
    Nothing yet depends on a stored opposed-test result, so none is persisted
    (specs/076-opposed-test-resolution/research.md's "No state I/O" decision).
    """
    return rules.opposed_test(
        skill=skill,
        opponent=opponent,
        seed=seed,
        declaration=declaration,
        helper_skill=helper_skill,
        helper_can_attempt=helper_can_attempt,
    )


def declaration_bonus(category: str) -> dict:
    """Resolve the `declaration-bonus` verb."""
    bonus = rules.declaration_bonus(category)
    return {
        "verb": "declaration-bonus",
        "category": category,
        "bonus": bonus,
        "no_roll": bonus is None,
    }


def oracle_prompt(family: str, seed: int | None = None) -> dict:
    """Resolve the `oracle-prompt` verb: roll, then look up the row -- read-only.

    docs/design/15-oracle-prompts.md: no state is written by generating a prompt; the
    caller (GM) applies the returned content to whatever structure it fills. Unlike
    `roll()`, this never touches `state.py`.
    """
    natural_roll = rules.roll_d100(seed=seed)
    effect, description = rules.oracle_prompt(family, natural_roll)
    return {
        "verb": "oracle-prompt",
        "family": family,
        "roll": natural_roll,
        "effect": effect,
        "description": description,
        "seed": seed,
    }


def oracle_answer(band: str, seed: int | None = None) -> dict:
    """Resolve the `oracle-answer` verb: roll, then look up the row -- read-only.

    docs/design/14-oracle-answers.md: no state is written by resolving an oracle-bound
    question; the caller (GM) records the question, band, roll and outcome to the beat log
    itself. Unlike `roll()`, this never touches `state.py`.
    """
    natural_roll = rules.roll_d100(seed=seed)
    outcome, wyrd = rules.oracle_answer(band, natural_roll)
    return {
        "verb": "oracle-answer",
        "band": band,
        "roll": natural_roll,
        "outcome": outcome,
        "wyrd": wyrd,
        "seed": seed,
    }


def assistance_bonus(helper_skill: int, can_attempt: bool = True) -> dict:
    """Resolve the `assistance-bonus` verb."""
    return {
        "verb": "assistance-bonus",
        "helper_skill": helper_skill,
        "can_attempt": can_attempt,
        "bonus": rules.assistance_bonus(helper_skill, can_attempt),
    }


def group_test(
    member_skills: list[int | None],
    mode: str,
    opponent: int,
    seed: int | None = None,
    **opposed_test_kwargs,
) -> dict:
    """Resolve the `group-test` verb.

    A thin wrapper over `rules.group_test` -- no state read or write, matching
    `opposed_test`'s own no-state-I/O precedent.
    """
    return rules.group_test(
        member_skills=member_skills,
        mode=mode,
        opponent=opponent,
        seed=seed,
        **opposed_test_kwargs,
    )


def resolve_extended_interval(
    skill: int,
    opponent: int,
    progress: int,
    target: int,
    seed: int | None = None,
    **opposed_test_kwargs,
) -> dict:
    """Resolve the `extended-task-interval` verb.

    A thin wrapper over `rules.resolve_extended_interval`. Does not persist `progress` --
    the caller carries the returned value into the next interval's call.
    """
    return rules.resolve_extended_interval(
        skill=skill,
        opponent=opponent,
        progress=progress,
        target=target,
        seed=seed,
        **opposed_test_kwargs,
    )


def character_save(path: pathlib.Path, frontmatter: dict, body: str = "") -> dict:
    """Resolve the `character-save` verb."""
    character.save(frontmatter, body, path)
    return {"verb": "character-save", "path": str(path), "saved": True}


def character_load(path: pathlib.Path) -> dict:
    """Resolve the `character-load` verb."""
    frontmatter, body = character.load(path)
    return {
        "verb": "character-load",
        "path": str(path),
        "frontmatter": frontmatter,
        "body": body,
    }


def skill_scale() -> dict:
    """Resolve the `skill-scale` verb."""
    return {
        "verb": "skill-scale",
        "open_value": rules.SKILL_OPEN_VALUE,
        "advance_step": rules.SKILL_ADVANCE_STEP,
        "untrained": rules.UNTRAINED_SKILL,
    }


def validate_allocation(
    actions: list[dict], career_data: dict, ancestry: dict | None = None
) -> dict:
    """Resolve the `validate-allocation` verb."""
    result = career.validate_allocation(actions, career_data, ancestry)
    return {"verb": "validate-allocation", **result}


def award_advance(trigger: str, awarded: list[str], advances_unspent: int) -> dict:
    """Resolve the `award-advance` verb."""
    record = {"triggers": list(awarded), "advances_unspent": advances_unspent}
    return {"verb": "award-advance", **advancement.award_advance(trigger, record)}


def begin_session(awarded: list[str], advances_unspent: int) -> dict:
    """Resolve the `begin-session` verb."""
    record = {"triggers": list(awarded), "advances_unspent": advances_unspent}
    return {"verb": "begin-session", **advancement.begin_session(record)}


def spend_advance(
    spend: str,
    view: dict,
    career_data: dict,
    careers: list[dict] | None = None,
    ancestry: dict | None = None,
    skill: str | None = None,
    target: str | None = None,
) -> dict:
    """Resolve the `spend-advance` verb."""
    result = advancement.spend_advance(
        spend, view, career_data, careers=careers, ancestry=ancestry, skill=skill, target=target
    )
    return {"verb": "spend-advance", **result}


def spend_coin(gear_id: str, coin: int, catalog: list[dict]) -> dict:
    """Resolve the `spend-coin` verb."""
    result = economy.spend_coin(gear_id, coin, catalog)
    return {"verb": "spend-coin", **result}


def martial_weapon_sighting(standing: int, already_applied: bool = False) -> dict:
    """Resolve the `martial-weapon-sighting` verb."""
    result = economy.martial_weapon_sighting(standing, already_applied)
    return {"verb": "martial-weapon-sighting", **result}


def adjust_standing(standing: int, delta: int) -> dict:
    """Resolve the `adjust-standing` verb."""
    result = economy.adjust_standing(standing, delta)
    return {"verb": "adjust-standing", **result}


def gain_allegiance(allegiance_id: str, allegiances: list[str]) -> dict:
    """Resolve the `gain-allegiance` verb."""
    result = economy.gain_allegiance(allegiance_id, allegiances)
    return {"verb": "gain-allegiance", **result}


def lose_allegiance(allegiance_id: str, allegiances: list[str]) -> dict:
    """Resolve the `lose-allegiance` verb."""
    result = economy.lose_allegiance(allegiance_id, allegiances)
    return {"verb": "lose-allegiance", **result}


def gain_holding(holding_id: str, holdings: list[str]) -> dict:
    """Resolve the `gain-holding` verb."""
    result = economy.gain_holding(holding_id, holdings)
    return {"verb": "gain-holding", **result}


def lose_holding(holding_id: str, holdings: list[str]) -> dict:
    """Resolve the `lose-holding` verb."""
    result = economy.lose_holding(holding_id, holdings)
    return {"verb": "lose-holding", **result}


def roll_standing(standing: int, roll: int) -> dict:
    """Resolve the `roll-standing` verb."""
    result = economy.roll_standing(standing, roll)
    return {"verb": "roll-standing", **result}


def create_character(
    path: pathlib.Path,
    name: str,
    career_data: dict,
    actions: list[dict],
    loyalty: str,
    mortality: str,
    fault_line: str,
    ancestry: dict | None = None,
    drives: list | None = None,
    misfortune=None,
) -> dict:
    """Resolve the `create-character` verb."""
    result = creation.create_character(
        path=path,
        name=name,
        career=career_data,
        actions=actions,
        loyalty=loyalty,
        mortality=mortality,
        fault_line=fault_line,
        ancestry=ancestry,
        drives=drives,
        misfortune=misfortune,
    )
    return {"verb": "create-character", **result}


def propose(
    actor: pathlib.Path,
    mechanic: str,
    skill: str | None = None,
    target: pathlib.Path | None = None,
    difficulty: str = "average",
    declaration_bonus: int = 0,
    tier: str | None = None,
    power: dict | None = None,
    weapon_dice: str | None = None,
    armour_dice: str | None = None,
    damage_type: str | None = None,
    dread_witnessed: bool = False,
    seed: int | None = None,
) -> dict:
    """Resolve the `propose` verb. `power` (docs/design/09-systems-of-power.md) carries a
    caller-resolved system-of-power declaration; it is read only by the `system-of-power`
    mechanic."""
    result = resolution.propose(
        actor=actor,
        mechanic=mechanic,
        skill=skill,
        target=target,
        difficulty=difficulty,
        declaration_bonus=declaration_bonus,
        tier=tier,
        power=power,
        weapon_dice=weapon_dice,
        armour_dice=armour_dice,
        damage_type=damage_type,
        dread_witnessed=dread_witnessed,
        seed=seed,
    )
    return {"verb": "propose", **result}


def commit(proposal_id: str) -> dict:
    """Resolve the `commit` verb."""
    result = resolution.commit(proposal_id)
    return {"verb": "commit", **result}


def discard(proposal_id: str) -> dict:
    """Resolve the `discard` verb."""
    result = resolution.discard(proposal_id)
    return {"verb": "discard", **result}


def reroll(proposal_id: str, step: int, resource: str, seed: int | None = None) -> dict:
    """Resolve the `reroll` verb."""
    result = resolution.reroll(proposal_id, step=step, resource=resource, seed=seed)
    return {"verb": "reroll", **result}


def track(
    value: int,
    mechanism: str,
    delta: int,
    resolved: overrides.ResolvedConfig | None = None,
) -> dict:
    """Resolve the `track` verb: apply `delta` to a trackable mechanism's current `value`.

    `mechanism` is always the engine's own internal identifier (docs/design/24-authoring-a-
    setting.md: "Internal identifiers never change") -- a disabled mechanism cannot be tracked
    at all (a structured error, never a silent no-op, per docs/design/27-tooling.md section 4),
    and a renamed one is reported under its setting's word without this input ever accepting
    that word.
    """
    if mechanism not in overrides.TRACKABLE_MECHANISMS:
        return {
            "error": {
                "verb": "track",
                "reason": f"{mechanism!r} is not a trackable mechanism",
            }
        }
    if resolved is not None and not resolved.is_enabled(mechanism):
        return {
            "error": {
                "verb": "track",
                "reason": f"{mechanism!r} is disabled by the active setting",
            }
        }
    label = resolved.label(mechanism) if resolved is not None else mechanism
    return {
        "verb": "track",
        "mechanism": mechanism,
        "label": label,
        "value": value + delta,
        "delta": delta,
    }


def _load_setting_index(setting_dir: pathlib.Path, name: str):
    """One of a setting's `index/*.json` files, or its empty-shaped default if absent."""
    path = setting_dir / "index" / f"{name}.json"
    if not path.exists():
        return {} if name in ("nouns", "terms") else []
    return json.loads(path.read_text(encoding="utf-8"))


def _with_excerpts(
    results: list[dict], documents_index: list[dict], setting: str, setting_dir: pathlib.Path
) -> list[dict]:
    """Extend every `doc`/`offset`-bearing result with its resolved excerpt (#397, FR-006).

    A result carrying no `offset` (there is none for this shape) is left unchanged. A result
    whose excerpt cannot be resolved still appears, with `excerpt: None` -- the coordinate
    lookup and the excerpt resolution are independent (contracts/find-verb.md)."""
    extended = []
    for result in results:
        if "offset" not in result:
            extended.append(result)
            continue
        excerpt = corpus_excerpt.read_excerpt(
            documents_index, setting, setting_dir, result["doc"], result["offset"]
        )
        extended.append({**result, "excerpt": excerpt})
    return extended


def find_noun(setting: str, name: str, setting_dir: pathlib.Path) -> dict:
    """Resolve the `find-noun` verb (#397): every occurrence of `name`, each carrying its
    resolved excerpt."""
    nouns_index = _load_setting_index(setting_dir, "nouns")
    documents_index = _load_setting_index(setting_dir, "documents")
    results = corpus_find.find_noun(nouns_index, setting, name)
    return {
        "verb": "find-noun",
        "results": _with_excerpts(results, documents_index, setting, setting_dir),
    }


def find_rule(setting: str, term: str, setting_dir: pathlib.Path) -> dict:
    """Resolve the `find-rule` verb (#397): every posting for `term`, each carrying its
    resolved excerpt."""
    terms_index = _load_setting_index(setting_dir, "terms")
    documents_index = _load_setting_index(setting_dir, "documents")
    results = corpus_find.find_rule(terms_index, setting, term)
    return {
        "verb": "find-rule",
        "results": _with_excerpts(results, documents_index, setting, setting_dir),
    }


def find_table(
    setting: str,
    setting_dir: pathlib.Path,
    dice: str | None = None,
    about: str | None = None,
) -> dict:
    """Resolve the `find-table` verb (#397): matching table records, each carrying its resolved
    excerpt where the record has an offset."""
    tables_index = _load_setting_index(setting_dir, "tables")
    documents_index = _load_setting_index(setting_dir, "documents")
    results = corpus_find.find_table(tables_index, setting, dice=dice, about=about)
    return {
        "verb": "find-table",
        "results": _with_excerpts(results, documents_index, setting, setting_dir),
    }


# --- Chronicle-level verbs (#402) --------------------------------------------------------
#
# docs/design/02-architecture.md's Memory tiers: session-context/get/find/party/threads/
# threats read the chronicle's effective entity set; log reads the Archival tier; save/load/
# validate/recap wrap wyrd.state/wyrd.loadtier; advance-time/threat-check wrap
# wyrd.advance_time/wyrd.threat. Each is a thin wrapper over an existing pure function
# (specs/153-chronicle-cli-verbs/research.md) -- no new mechanic is invented here.


def load_effective_entities(chronicle_dir: pathlib.Path) -> dict[str, dict]:
    """The chronicle's full effective entity set, keyed by id (docs/design/22-state.md):
    every `setting/*.md` entity resolved against its `overlay/*.md` counterpart, plus every
    `entities/*.md` file the chronicle invented directly.

    Reuses `wyrd.resolution._load_chronicle_entities` -- the same effective-entity-set
    assembly `commit`'s own passive validation already performs -- rather than a second copy
    of the same glob-and-resolve logic (specs/153-chronicle-cli-verbs/research.md).
    """
    chronicle_dir = pathlib.Path(chronicle_dir)
    return resolution._load_chronicle_entities(chronicle_dir / "chronicle.yaml")


def find_entities(
    entities: dict[str, dict], *, type: str, status: str | None = None, tag: str | None = None
) -> dict[str, dict]:
    """`find --type T [--status S] [--tag G]` (docs/design/02-architecture.md): every entity in
    `entities` matching every filter given. Omitted filters are not applied."""
    results = {}
    for entity_id, frontmatter in entities.items():
        if frontmatter.get("type") != type:
            continue
        if status is not None and frontmatter.get("status") != status:
            continue
        if tag is not None and tag not in (frontmatter.get("tags") or []):
            continue
        results[entity_id] = frontmatter
    return results


def companions_with_party(entities: dict[str, dict]) -> dict[str, dict]:
    """`party`'s own predicate: `role: companion` + `status: with-party`

    (docs/design/02-architecture.md; not a literal `find` call -- `find`'s public flags don't
    expose `role`, per spec.md's Clarifications)."""
    return {
        entity_id: fm
        for entity_id, fm in entities.items()
        if fm.get("role") == "companion" and fm.get("status") == "with-party"
    }


def open_threads_by_heat(entities: dict[str, dict]) -> list[dict]:
    """`threads`: the full `status: open` thread set, ordered by `heat` descending
    (docs/design/02-architecture.md) -- broader than `session-context`'s `heat >= 3` slice."""
    open_threads = [
        fm for fm in entities.values() if fm.get("type") == "thread" and fm.get("status") == "open"
    ]
    open_threads.sort(key=lambda fm: (-(fm.get("heat") or 0), fm["id"]))
    return open_threads


def session_context(chronicle_dir: pathlib.Path) -> dict:
    """`session-context`: the Always-loaded tier in one call (docs/design/02-architecture.md) --
    player character, with-party companions, `heat >= 3` threads, the recap, and the contract."""
    chronicle_dir = pathlib.Path(chronicle_dir)
    entities = load_effective_entities(chronicle_dir)
    tier = loadtier.always_tier(entities)

    recap_path = chronicle_dir / "recap.md"
    recap = recap_path.read_text(encoding="utf-8") if recap_path.exists() else ""

    contract_path = chronicle_dir / "engine" / "contract.md"
    contract = contract_path.read_text(encoding="utf-8") if contract_path.exists() else ""

    return {
        "verb": "session-context",
        "player_character": tier["player_character"],
        "companions": tier["companions"],
        "threads": tier["threads"],
        "recap": recap,
        "contract": contract,
    }


def get(entity_id: str, chronicle_dir: pathlib.Path) -> dict:
    """`get <id>`: one entity resolved to its effective form; raises `state.StateError` (via
    `load_effective_entities`'s underlying `entity.resolve_entity`) if `entity_id` does not
    resolve in either the setting, the overlay, or the chronicle's own entities."""
    entities = load_effective_entities(chronicle_dir)
    if entity_id not in entities:
        raise state.StateError(f"'{entity_id}' is not a known entity in this chronicle")
    return {"verb": "get", "id": entity_id, "entity": entities[entity_id]}


def find(
    chronicle_dir: pathlib.Path, *, type: str, status: str | None = None, tag: str | None = None
) -> dict:
    """`find --type T [--status S] [--tag G]`: every entity matching every filter given."""
    entities = load_effective_entities(chronicle_dir)
    results = find_entities(entities, type=type, status=status, tag=tag)
    return {
        "verb": "find",
        "filters": {"type": type, "status": status, "tag": tag},
        "results": results,
    }


def party(chronicle_dir: pathlib.Path) -> dict:
    """`party`: `role: companion` + `status: with-party` -- a named query."""
    entities = load_effective_entities(chronicle_dir)
    return {"verb": "party", "results": companions_with_party(entities)}


def threads(chronicle_dir: pathlib.Path) -> dict:
    """`threads`: the full `status: open` set, ordered by `heat` descending -- a named query."""
    entities = load_effective_entities(chronicle_dir)
    return {"verb": "threads", "results": open_threads_by_heat(entities)}


def threats(chronicle_dir: pathlib.Path) -> dict:
    """`threats`: entities carrying an active threat block -- a named query."""
    entities = load_effective_entities(chronicle_dir)
    active = threat_module.active_threats(list(entities.values()))
    return {"verb": "threats", "results": {fm["id"]: fm for fm in active}}


def log(
    chronicle_dir: pathlib.Path,
    chronicle_name: str,
    *,
    last: int | None = None,
    since: str | None = None,
) -> dict:
    """`log --last N | --since <beat>`: the Archival tier, in beat order (docs/design/
    02-architecture.md). Exactly one of `last`/`since` must be given."""
    if (last is None) == (since is None):
        raise ValueError("log requires exactly one of --last or --since")
    entries = log_module.read_log(chronicle_dir, chronicle_name, last=last, since=since)
    return {"verb": "log", "entries": entries}


def save(chronicle_state: dict, chronicle_dir: pathlib.Path) -> dict:
    """`save`: validate and write chronicle state to `chronicle.yaml`, atomically."""
    path = pathlib.Path(chronicle_dir) / "chronicle.yaml"
    state.save_chronicle(chronicle_state, path)
    return {"verb": "save", "path": str(path)}


def load(chronicle_dir: pathlib.Path) -> dict:
    """`load`: read and validate `chronicle.yaml`."""
    path = pathlib.Path(chronicle_dir) / "chronicle.yaml"
    return {"verb": "load", "state": state.load_chronicle(path)}


def validate(chronicle_dir: pathlib.Path) -> dict:
    """`validate`: schema-validate `chronicle.yaml`, reporting the violation rather than
    raising."""
    path = pathlib.Path(chronicle_dir) / "chronicle.yaml"
    try:
        state.load_chronicle(path)
    except state.StateError as exc:
        return {"verb": "validate", "valid": False, "error": str(exc)}
    return {"verb": "validate", "valid": True, "error": None}


def recap(
    chronicle_dir: pathlib.Path,
    *,
    where: str | None = None,
    changes: list[str] | None = None,
    body_mind: str | None = None,
) -> dict:
    """`recap`: regenerate `recap.md` from current chronicle state."""
    chronicle_dir = pathlib.Path(chronicle_dir)
    entities = load_effective_entities(chronicle_dir)
    chronicle_state = state.load_chronicle(chronicle_dir / "chronicle.yaml")
    text = loadtier.generate_recap(
        entities, chronicle_state, where=where, changes=changes, body_mind=body_mind
    )
    path = chronicle_dir / "recap.md"
    state.write_text_atomic(text, path)
    return {"verb": "recap", "path": str(path), "text": text}


def advance_time(chronicle_dir: pathlib.Path, days: int, *, seed: int | None = None) -> dict:
    """`advance-time <days>`: advance the calendar and resolve threat activation/expected-value
    events across the span."""
    if days < 0:
        raise ValueError(f"days must be non-negative, got {days!r}")
    chronicle_dir = pathlib.Path(chronicle_dir)
    chronicle_state = state.load_chronicle(chronicle_dir / "chronicle.yaml")
    entities = load_effective_entities(chronicle_dir)
    active = threat_module.active_threats(list(entities.values()))
    result = advance_time_module.advance_time(chronicle_state["calendar"], active, days, seed=seed)
    new_state = {**chronicle_state, "calendar": result["calendar"]}
    state.save_chronicle(new_state, chronicle_dir / "chronicle.yaml")
    return {
        "verb": "advance-time",
        "calendar": result["calendar"],
        "activations": result["activations"],
    }


def threat_check(chronicle_dir: pathlib.Path, threat_id: str, *, seed: int | None = None) -> dict:
    """`threat-check`: one threat's activation roll, on demand."""
    entities = load_effective_entities(chronicle_dir)
    if threat_id not in entities:
        raise state.StateError(f"'{threat_id}' is not a known entity in this chronicle")
    threat_block = entities[threat_id].get("threat") or {}
    imminence = threat_block.get("imminence", 0)
    wyrd_roll = rules.roll_d100(seed=seed)
    activated = threat_module.check_activation(imminence, wyrd_roll)
    return {"verb": "threat-check", "id": threat_id, "activated": activated, "roll": wyrd_roll}


def downtime(
    action: str,
    *,
    destination: str | None = None,
    standing: int | None = None,
    coin: int | None = None,
    trade: str | None = None,
    wound_id: str | None = None,
    wounds: list[dict] | None = None,
    stamina_max: int | None = None,
) -> dict:
    """Resolve the `downtime` verb: dispatch on `action` to `downtime.py`'s `apply_upkeep`,
    `apply_mend` or `apply_rest`, merging `{"verb": "downtime", "action": action}` into whichever
    result it returns. Raises ValueError for an unknown `action` or a missing required parameter
    for the chosen one -- this wrapper adds no arithmetic of its own (contracts/cli-verbs.md)."""
    if action == "upkeep":
        if destination is None or standing is None or coin is None:
            raise ValueError("downtime --action upkeep requires destination, standing and coin")
        result = downtime_module.apply_upkeep(destination, standing, coin, trade=trade)
    elif action == "mend":
        if wound_id is None or wounds is None:
            raise ValueError("downtime --action mend requires wound_id and wounds")
        result = downtime_module.apply_mend(wound_id, wounds)
    elif action == "rest":
        if stamina_max is None:
            raise ValueError("downtime --action rest requires stamina_max")
        result = {"stamina": downtime_module.apply_rest(stamina_max)}
    else:
        raise ValueError(f"unknown downtime action: {action!r}")
    return {"verb": "downtime", "action": action, **result}


def rally(
    strain: int,
    stamina: int,
    stamina_max: int,
    advancement_record: dict,
    *,
    trigger: str | None = None,
    pending: dict | None = None,
) -> dict:
    """Resolve the `rally` verb: `rally.py`'s `apply_rally`, always called with `commit=None`
    (research.md -- committing is the calling skill's own git step, not this verb's)."""
    result = rally_module.apply_rally(
        strain,
        stamina,
        stamina_max,
        advancement_record,
        trigger=trigger,
        pending=pending,
        commit=None,
    )
    return {"verb": "rally", **result}
