"""The base propose/commit/discard resolution mechanism.

docs/design/31-action-resolution.md "Propose, then commit" (ADR 0050): `propose` resolves one
roll against an actor's own state, stages any implied mutation, and writes nothing; `commit`
applies exactly the staged mutations atomically; `discard` writes nothing. Both `commit` and
`discard` invalidate the proposal id so it can never resolve twice.

Single-step resolution only (specs/082-propose-commit-core) -- cascading resolution, partial
reroll, and Omen carryover are separate, later features (#236, #237, #238) that build on the
`depends_on` shape this module does not yet need.

An actor/target is identified by its entity file path, the same identifier
`character.load`/`character.save` already use -- there is no separate actor-id registry in this
engine (docs/design/22-state.md: one file per entity).

Python 3.11+, standard library only.
"""

from __future__ import annotations

import itertools
import pathlib
from collections.abc import Callable

from wyrd import character, rules

#: docs/design/03-rules.md section 1's difficulty ladder -- modifies the skill, never the roll.
DIFFICULTY_BONUSES = {
    "easy": 20,
    "average": 0,
    "challenging": -10,
    "difficult": -20,
    "hard": -30,
    "very_hard": -40,
}

#: docs/design/03-rules.md section 4: minor/moderate/major Exposure tiers. Fault Line bias
#: (running with the grain, one tier worse) is an already-decided input from the caller, the
#: same way `declaration_bonus` is already-decided (spec.md Assumptions) -- this module does
#: not compute Fault Line alignment itself.
EXPOSURE_TIERS = {"minor": 1, "moderate": 2, "major": 3}


class ProposalError(Exception):
    """Raised when `commit`/`discard` is called against an id that is not an open proposal."""


def _tens(value: int) -> int:
    return value // 10


def _wyrd_die(natural_roll: int) -> str:
    """Read the Wyrd die from the units digit of the natural roll (mirrors `rules._wyrd_die`;
    duplicated locally rather than imported, since the leading underscore marks it as
    module-internal to `rules.py`)."""
    units = natural_roll % 10
    if units == 0:
        return "ill_omen"
    if units == 9:
        return "fair_omen"
    return "none"


def _resolve_test(
    *,
    actor: str,
    mechanic: str,
    skill_value: int,
    difficulty: str,
    declaration_bonus: int,
    seed: int | None,
) -> dict:
    """The shared single-roll resolution every mechanic below composes with: `effective_pct`
    from skill + difficulty + declaration, a `d100` roll, degrees on success only, the Wyrd die
    read independently (docs/design/03-rules.md section 1)."""
    if difficulty not in DIFFICULTY_BONUSES:
        raise ValueError(f"no such difficulty: {difficulty}")
    effective_pct = max(
        5, min(95, skill_value + DIFFICULTY_BONUSES[difficulty] + declaration_bonus)
    )
    roll = rules.roll_d100(sides=100, seed=seed)
    wyrd_die = _wyrd_die(roll)
    outcome = "success" if roll <= effective_pct else "fail"
    degrees = _tens(effective_pct) - _tens(roll) if outcome == "success" else None
    return {
        "actor": actor,
        "mechanic": mechanic,
        "roll": roll,
        "effective_pct": effective_pct,
        "degrees": degrees,
        "wyrd_die": wyrd_die,
        "outcome": outcome,
    }


def _resolve_ordinary_test(
    *,
    actor: str,
    actor_state: dict,
    skill: str,
    difficulty: str,
    declaration_bonus: int,
    seed: int | None,
    **_ignored,
) -> dict:
    if skill is None:
        raise ValueError("ordinary-test requires a skill")
    skill_value = actor_state.get("skills", {}).get(skill, rules.UNTRAINED_SKILL)
    roll_data = _resolve_test(
        actor=actor,
        mechanic="ordinary-test",
        skill_value=skill_value,
        difficulty=difficulty,
        declaration_bonus=declaration_bonus,
        seed=seed,
    )
    roll_data["skill"] = skill
    return roll_data


def _mutate_ordinary_test(roll_data: dict, **_ignored) -> list[dict]:
    # No consequence is bound to a bare ordinary test -- an outcome with no implied mutation is
    # a common, valid result (docs/design/31-action-resolution.md "What propose returns").
    return []


def _resolve_exposure(
    *,
    actor: str,
    actor_state: dict,
    skill: str,
    difficulty: str,
    declaration_bonus: int,
    tier: str,
    seed: int | None,
    **_ignored,
) -> dict:
    if skill is None:
        raise ValueError("exposure requires a skill")
    if tier not in EXPOSURE_TIERS:
        raise ValueError(f"no such Exposure tier: {tier}")
    skill_value = actor_state.get("skills", {}).get(skill, rules.UNTRAINED_SKILL)
    roll_data = _resolve_test(
        actor=actor,
        mechanic="exposure",
        skill_value=skill_value,
        difficulty=difficulty,
        declaration_bonus=declaration_bonus,
        seed=seed,
    )
    roll_data["skill"] = skill
    roll_data["tier"] = tier
    return roll_data


def _mutate_exposure(roll_data: dict, **_ignored) -> list[dict]:
    # Resisting successfully avoids the tier entirely; failing gains the full tier value
    # (docs/design/31-action-resolution.md's own worked examples never exercise a reduction by
    # degrees of success -- see specs/082-propose-commit-core/research.md).
    if roll_data["outcome"] == "success":
        return []
    return [
        {
            "entity": roll_data["actor"],
            "field": "taint",
            "op": "+",
            "value": EXPOSURE_TIERS[roll_data["tier"]],
        }
    ]


#: The closed mechanic vocabulary (docs/design/31-action-resolution.md's `mechanic` parameter):
#: mechanic name -> (resolve, mutate). Adding a further mechanic later is additive -- a new
#: entry here, no change to `propose`/`commit`/`discard` themselves.
_MECHANICS: dict[str, tuple[Callable[..., dict], Callable[..., list[dict]]]] = {
    "ordinary-test": (_resolve_ordinary_test, _mutate_ordinary_test),
    "exposure": (_resolve_exposure, _mutate_exposure),
}

_proposal_ids = itertools.count(1)

#: Process-local proposal store (docs/design/31-action-resolution.md: "an unpersisted,
#: in-memory ... record"). Never written to disk -- the engine has no backend/daemon
#: (CLAUDE.md, docs/design/27-tooling.md).
_open_proposals: dict[str, dict] = {}


def propose(
    actor: str | pathlib.Path,
    mechanic: str,
    skill: str | None = None,
    target: str | pathlib.Path | None = None,
    difficulty: str = "average",
    declaration_bonus: int = 0,
    *,
    tier: str | None = None,
    seed: int | None = None,
) -> dict:
    """Resolve one roll against `actor`'s own state and stage any implied mutation.

    `actor`/`target` are entity file paths, per `character.load`/`character.save`'s own
    identifier. Writes nothing -- state on disk is unchanged by this call, verifiably (spec.md
    User Story 2). Returns `{"proposal_id", "roll", "mutations"}`. Raises `ValueError` for an
    unknown mechanic or difficulty; propagates `character.load`'s own error for a missing actor
    or target entity.
    """
    if mechanic not in _MECHANICS:
        raise ValueError(f"no such mechanic: {mechanic}")
    resolve_fn, mutate_fn = _MECHANICS[mechanic]

    actor_path = pathlib.Path(actor)
    actor_state, _ = character.load(actor_path)
    target_state = None
    if target is not None:
        target_state, _ = character.load(pathlib.Path(target))

    roll_data = resolve_fn(
        actor=str(actor_path),
        actor_state=actor_state,
        skill=skill,
        difficulty=difficulty,
        declaration_bonus=declaration_bonus,
        tier=tier,
        target_state=target_state,
        seed=seed,
    )
    mutations = mutate_fn(roll_data, actor_state=actor_state, target_state=target_state)

    proposal_id = f"p-{next(_proposal_ids)}"
    _open_proposals[proposal_id] = {
        "actor_path": actor_path,
        "roll": roll_data,
        "mutations": mutations,
        "open": True,
    }
    return {"proposal_id": proposal_id, "roll": roll_data, "mutations": mutations}


def _pop_open_proposal(proposal_id: str) -> dict:
    proposal = _open_proposals.get(proposal_id)
    if proposal is None or not proposal["open"]:
        raise ProposalError(f"no open proposal: {proposal_id}")
    proposal["open"] = False
    return proposal


def _apply_mutation(frontmatter: dict, mutation: dict) -> None:
    field = mutation["field"]
    if mutation["op"] == "set":
        frontmatter[field] = mutation["value"]
    elif mutation["op"] == "+":
        frontmatter[field] = frontmatter.get(field, 0) + mutation["value"]
    elif mutation["op"] == "-":
        frontmatter[field] = frontmatter.get(field, 0) - mutation["value"]
    else:
        raise ValueError(f"no such mutation op: {mutation['op']}")


def commit(proposal_id: str) -> dict:
    """Apply exactly `proposal_id`'s staged mutations to state, atomically, and invalidate it.

    Raises `ProposalError` if `proposal_id` does not resolve to a currently-open proposal
    (already committed, already discarded, or never issued) -- never a silent no-op
    (spec.md User Story 3).
    """
    proposal = _pop_open_proposal(proposal_id)
    mutations = proposal["mutations"]
    if mutations:
        # Single-actor, single-step: every mutation in this feature's scope targets the same
        # entity the proposal was raised against, so one load/save round-trip is atomic for
        # all of them (state.save_entity's own atomic write, character.save's thin wrapper
        # over it). A mutation naming a different entity is out of this feature's scope
        # (cascading resolution, #236, is where a multi-entity proposal would first appear).
        actor_path = proposal["actor_path"]
        frontmatter, body = character.load(actor_path)
        for mutation in mutations:
            _apply_mutation(frontmatter, mutation)
        character.save(frontmatter, body, actor_path)
    return {"proposal_id": proposal_id, "mutations": mutations}


def discard(proposal_id: str) -> dict:
    """Invalidate `proposal_id` without writing anything.

    Raises `ProposalError` if `proposal_id` does not resolve to a currently-open proposal.
    """
    _pop_open_proposal(proposal_id)
    return {"proposal_id": proposal_id}
