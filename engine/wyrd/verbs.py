"""The operations behind each catalog entry.

Each function here wires `rules.py`'s pure logic to `state.py`'s persistence, so the state
write happens as part of resolving the verb -- before the result is returned for narration
(docs/design/01-principles.md principle 2). Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib

from wyrd import career, character, creation, resolution, rules, state


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
    weapon_dice: str | None = None,
    armour_dice: str | None = None,
    damage_type: str | None = None,
    seed: int | None = None,
) -> dict:
    """Resolve the `propose` verb."""
    result = resolution.propose(
        actor=actor,
        mechanic=mechanic,
        skill=skill,
        target=target,
        difficulty=difficulty,
        declaration_bonus=declaration_bonus,
        tier=tier,
        weapon_dice=weapon_dice,
        armour_dice=armour_dice,
        damage_type=damage_type,
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
