"""The base propose/commit/discard resolution mechanism, with cascading resolution.

docs/design/31-action-resolution.md "Propose, then commit" (ADR 0050): `propose` resolves a
roll (or a whole chain of them, see "Cascading resolution" below) against an actor's own state,
stages any implied mutation, and writes nothing; `commit` applies exactly the staged mutations
atomically; `discard` writes nothing. Both `commit` and `discard` invalidate the proposal id so
it can never resolve twice.

**Cascading resolution** (specs/083-cascading-resolution, extending #235's single-step case):
a resolved step spawns a further step inside the same proposal whenever the mechanic's own rule
calls for one. Two trigger shapes, both wired up for exactly the two instances
docs/design/31-action-resolution.md's own worked examples need (spec.md Assumptions):

- A mutation crossing a threshold: `taint` crossing a multiple of 3 stages a `transformation`
  step (docs/design/07-transformations.md).
- A roll's own outcome calling for a further roll: a landed `combat-attack` stages
  `weapon-damage` + `armour`, whose combined Stamina mutation is itself threshold-checked,
  staging a `critical` step (`critical-slashing` only, docs/design/05-criticals.md) on a
  crossing below zero.

Partial reroll and Omen carryover are separate, later features (#237, #238) that build on the
`depends_on` edges this module records but does not yet consume.

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

#: docs/design/07-transformations.md "The thresholds": every multiple of 3, starting at 3.
TAINT_THRESHOLD_SPACING = 3

#: docs/design/07-transformations.md "The table": row (1-6, the d6 result) -> severity.
TRANSFORMATION_SEVERITIES = [1, 1, 2, 2, 3, 4]

#: docs/design/05-criticals.md "critical-slashing": (low, high, key, effect-or-None). The 21+
#: ("slashing-mortal") row is handled separately -- it stages no wound-record mutation
#: (ADR 0023: a critical never kills during the fight).
CRITICAL_SLASHING_TABLE = [
    (2, 5, "slashing-glancing", None),
    (6, 9, "slashing-scored", {"dread": 1}),
    (10, 13, "slashing-opened", {"skill": -5}),
    (14, 17, "slashing-hamstrung", {"skill": -10}),
    (18, 20, "slashing-maimed", {"stamina_max": -1, "dread": 1}),
]


class ProposalError(Exception):
    """Raised when `commit`/`discard` is called against an id that is not an open proposal."""


class _SeedCursor:
    """A deterministic seed sequence for a whole cascade (research.md's Decision): the first
    internal roll uses the caller's own `seed`, each subsequent one increments it by 1. `None`
    stays `None` throughout -- unseeded real play never becomes accidentally reproducible."""

    def __init__(self, seed: int | None):
        self._seed = seed

    def next(self) -> int | None:
        if self._seed is None:
            return None
        current = self._seed
        self._seed += 1
        return current


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


def _get_nested(state: dict, field: str):
    """Read a possibly dotted field path (e.g. `stamina.current`), defaulting to `0` at any
    missing step -- the same default `_apply_mutation`'s `+`/`-` already use."""
    value: object = state
    for part in field.split("."):
        if not isinstance(value, dict):
            return 0
        value = value.get(part, 0)
    return value


def _apply_mutation(state: dict, mutation: dict) -> None:
    """Apply one mutation to an in-memory state dict -- used both by `commit` (against a
    freshly-loaded entity) and, during `propose`, against a scratch copy already held in memory
    so a cascade can see the running effect of its own earlier steps without ever writing to
    disk (docs/design/31-action-resolution.md: "propose... writes nothing")."""
    parts = mutation["field"].split(".")
    container = state
    for part in parts[:-1]:
        container = container.setdefault(part, {})
    key = parts[-1]
    op = mutation["op"]
    if op == "set":
        container[key] = mutation["value"]
    elif op == "+":
        container[key] = container.get(key, 0) + mutation["value"]
    elif op == "-":
        container[key] = container.get(key, 0) - mutation["value"]
    elif op == "append":
        container.setdefault(key, []).append(mutation["value"])
    else:
        raise ValueError(f"no such mutation op: {op}")


def _crossed_threshold(before: int, after: int, spacing: int) -> int | None:
    """The highest multiple of `spacing` that `before -> after` crosses from below, or `None`
    if none was crossed (docs/design/07-transformations.md "Crossing a threshold")."""
    if after <= before:
        return None
    highest = (after // spacing) * spacing
    if highest == 0 or not (before < highest <= after):
        return None
    return highest


def _resolve_test(
    *,
    actor: str,
    mechanic: str,
    skill_value: int,
    difficulty: str,
    declaration_bonus: int,
    seed: int | None,
) -> dict:
    """The shared single-roll resolution every ordinary/Exposure mechanic composes with:
    `effective_pct` from skill + difficulty + declaration, a `d100` roll, degrees on success
    only, the Wyrd die read independently (docs/design/03-rules.md section 1)."""
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


#: The single-step mechanic vocabulary (docs/design/31-action-resolution.md's `mechanic`
#: parameter): mechanic name -> (resolve, mutate). `combat-attack` is handled separately below
#: (its own outcome-triggered cascade, not a simple resolve/mutate pair); `transformation`,
#: `weapon-damage`, `armour` and `critical` are internal step mechanics a cascade stages itself,
#: never named directly by a caller.
_MECHANICS: dict[str, tuple[Callable[..., dict], Callable[..., list[dict]]]] = {
    "ordinary-test": (_resolve_ordinary_test, _mutate_ordinary_test),
    "exposure": (_resolve_exposure, _mutate_exposure),
}

_PUBLIC_MECHANICS = frozenset({*_MECHANICS.keys(), "combat-attack"})

_proposal_ids = itertools.count(1)

#: Process-local proposal store (docs/design/31-action-resolution.md: "an unpersisted,
#: in-memory ... record"). Never written to disk -- the engine has no backend/daemon
#: (CLAUDE.md, docs/design/27-tooling.md).
_open_proposals: dict[str, dict] = {}


def _roll_dice(spec: str, seed_cursor: _SeedCursor) -> tuple[list[int], int]:
    """Roll an `NdM` spec (e.g. `1d8`), one die at a time through the seed cursor. Returns the
    individual rolls and their total."""
    count_text, sides_text = spec.lower().split("d")
    count, sides = int(count_text), int(sides_text)
    if count < 1 or sides < 1:
        raise ValueError(f"invalid dice spec: {spec!r}")
    rolls = [rules.roll_d100(sides=sides, seed=seed_cursor.next()) for _ in range(count)]
    return rolls, sum(rolls)


def _critical_slashing_band(total: int) -> tuple[str, dict | None]:
    for low, high, key, effect in CRITICAL_SLASHING_TABLE:
        if low <= total <= high:
            return key, effect
    return "slashing-mortal", None


def _stage_critical(
    steps: list[dict],
    entity: str,
    points_below_zero: int,
    depends_on_step: int,
    seed_cursor: _SeedCursor,
    bears_on_skill: str,
) -> None:
    """docs/design/05-criticals.md: `1d6 + points below zero` against `critical-slashing`,
    staging a wound-record mutation (or nothing further for a mortal result -- ADR 0023, and
    FR-009: Aftermath is deliberately deferred, never cascaded here)."""
    d6 = rules.roll_d100(sides=6, seed=seed_cursor.next())
    total = d6 + points_below_zero
    key, effect = _critical_slashing_band(total)
    mortal = key == "slashing-mortal"
    step_id = len(steps)
    mutations: list[dict] = []
    if not mortal and effect is not None:
        wound = {"id": f"critical-{step_id}", "effect": dict(effect), "closed": None}
        if "skill" in effect:
            wound["bears_on"] = bears_on_skill
        mutations.append(
            {
                "entity": entity,
                "field": "wounds",
                "op": "append",
                "value": wound,
                "produced_by_step": step_id,
            }
        )
    steps.append(
        {
            "step_id": step_id,
            "mechanic": "critical",
            "roll": {
                "roll": d6,
                "modifier": points_below_zero,
                "total": total,
                "table": "critical-slashing",
                "key": key,
                "mortal": mortal,
            },
            "mutations": mutations,
            "depends_on": [depends_on_step],
        }
    )


def _stage_transformation_chain(
    steps: list[dict],
    entity: str,
    state: dict,
    threshold: int,
    depends_on_step: int,
    seed_cursor: _SeedCursor,
) -> None:
    """docs/design/07-transformations.md: roll `1d6` against the six-row table, unique per
    character within this cascade; consume Taint equal to severity, gain the same in Dread; on
    the character's first-ever Transformation, also set the hidden threshold once. If Taint is
    still at or over `threshold` afterward, re-roll (a different row) and repeat -- bounded by
    the table's own 6 rows (FR-008, tools/check_transformation.py's termination proof)."""
    taken_rows: set[int] = set()
    while True:
        while True:
            row = rules.roll_d100(sides=6, seed=seed_cursor.next())
            if row not in taken_rows:
                break
            # A duplicate is re-rolled (docs/design/07-transformations.md "unique per
            # character"); the table has 6 rows, so this inner loop cannot spin past 6 draws.
        taken_rows.add(row)
        severity = TRANSFORMATION_SEVERITIES[row - 1]
        step_id = len(steps)
        is_first_ever = state.get("hidden_threshold") is None
        mutations = [
            {
                "entity": entity,
                "field": "taint",
                "op": "-",
                "value": severity,
                "produced_by_step": step_id,
            },
            {
                "entity": entity,
                "field": "dread",
                "op": "+",
                "value": severity,
                "produced_by_step": step_id,
            },
        ]
        if is_first_ever:
            hidden_threshold = rules.roll_d100(sides=6, seed=seed_cursor.next()) + 2
            mutations.append(
                {
                    "entity": entity,
                    "field": "hidden_threshold",
                    "op": "set",
                    "value": hidden_threshold,
                    "produced_by_step": step_id,
                }
            )
        steps.append(
            {
                "step_id": step_id,
                "mechanic": "transformation",
                "roll": {"roll": row, "row": row, "severity": severity},
                "mutations": mutations,
                "depends_on": [depends_on_step],
            }
        )
        for mutation in mutations:
            _apply_mutation(state, mutation)
        if _get_nested(state, "taint") < threshold:
            return
        depends_on_step = step_id


def _cascade_from_mutation(
    steps: list[dict],
    mutation: dict,
    state_by_entity: dict[str, dict],
    seed_cursor: _SeedCursor,
) -> None:
    """The threshold-crossing trigger (FR-002): after a mutation is staged, check its field
    against the one rule this feature registers -- `taint` crossing a multiple of 3. Applies the
    mutation to the in-memory scratch state first, so `before`/`after` (and any further cascade)
    reflect it, without writing to disk."""
    field = mutation["field"]
    entity = mutation["entity"]
    state = state_by_entity.get(entity)
    if state is None or field != "taint":
        return
    before = _get_nested(state, field)
    _apply_mutation(state, mutation)
    after = _get_nested(state, field)
    threshold = _crossed_threshold(before, after, TAINT_THRESHOLD_SPACING)
    if threshold is not None:
        _stage_transformation_chain(
            steps, entity, state, threshold, mutation["produced_by_step"], seed_cursor
        )


def _stage_combat_attack(
    steps: list[dict],
    *,
    actor: str,
    actor_state: dict,
    target: str,
    target_state: dict,
    skill: str | None,
    weapon_dice: str | None,
    armour_dice: str | None,
    seed_cursor: _SeedCursor,
) -> None:
    """The combat resolution chain (docs/design/31-action-resolution.md "The combat resolution
    chain"): an opposed test on the acting side only; a landed blow stages weapon-damage and
    armour, doubling damage first if telling (`degrees >= 6`); the two combine into the target's
    Stamina mutation, itself threshold-checked for a crossing below 0, staging `critical`."""
    if skill is None:
        raise ValueError("combat-attack requires a skill")
    if weapon_dice is None or armour_dice is None:
        raise ValueError("combat-attack requires weapon_dice and armour_dice")

    attacker_value = actor_state.get("skills", {}).get(skill, rules.UNTRAINED_SKILL)
    defender_value = target_state.get("skills", {}).get(skill, rules.UNTRAINED_SKILL)
    opposed = rules.opposed_test(attacker_value, defender_value, seed=seed_cursor.next())
    landed = bool(opposed["success"])
    telling = bool(landed and opposed["degrees"] is not None and opposed["degrees"] >= 6)
    roll_data = {
        "actor": actor,
        "target": target,
        "mechanic": "combat-attack",
        "skill": skill,
        "roll": opposed["roll"],
        "effective_pct": opposed["effective_pct"],
        "degrees": opposed["degrees"],
        "wyrd_die": opposed["wyrd"],
        "outcome": "success" if landed else "fail",
        "landed": landed,
        "telling": telling,
    }
    steps.append(
        {
            "step_id": 0,
            "mechanic": "combat-attack",
            "roll": roll_data,
            "mutations": [],
            "depends_on": [],
        }
    )
    if not landed:
        return

    damage_rolls, damage_total = _roll_dice(weapon_dice, seed_cursor)
    if telling:
        damage_total *= 2
    weapon_step_id = len(steps)
    steps.append(
        {
            "step_id": weapon_step_id,
            "mechanic": "weapon-damage",
            "roll": {
                "dice": weapon_dice,
                "rolls": damage_rolls,
                "total": damage_total,
                "doubled": telling,
            },
            "mutations": [],
            "depends_on": [0],
        }
    )

    armour_rolls, armour_total = _roll_dice(armour_dice, seed_cursor)
    armour_step_id = len(steps)
    net_damage = max(1, damage_total - armour_total)
    stamina_before = _get_nested(target_state, "stamina.current")
    stamina_mutation = {
        "entity": target,
        "field": "stamina.current",
        "op": "-",
        "value": net_damage,
        "produced_by_step": armour_step_id,
    }
    steps.append(
        {
            "step_id": armour_step_id,
            "mechanic": "armour",
            "roll": {
                "dice": armour_dice,
                "rolls": armour_rolls,
                "total": armour_total,
                "net_damage": net_damage,
            },
            "mutations": [stamina_mutation],
            "depends_on": [0],
        }
    )
    _apply_mutation(target_state, stamina_mutation)
    stamina_after = _get_nested(target_state, "stamina.current")
    if stamina_before >= 0 and stamina_after < 0:
        _stage_critical(
            steps, target, -stamina_after, armour_step_id, seed_cursor, bears_on_skill=skill
        )


def propose(
    actor: str | pathlib.Path,
    mechanic: str,
    skill: str | None = None,
    target: str | pathlib.Path | None = None,
    difficulty: str = "average",
    declaration_bonus: int = 0,
    *,
    tier: str | None = None,
    weapon_dice: str | None = None,
    armour_dice: str | None = None,
    seed: int | None = None,
) -> dict:
    """Resolve `mechanic` against `actor`'s own state, cascading into further steps whenever the
    mechanic's own rule calls for one (module docstring). Writes nothing -- state on disk is
    unchanged by this call, verifiably (spec.md User Story 2). Returns `{"proposal_id", "roll",
    "mutations", "steps"}` -- `roll`/`mutations` keep #235's exact shape (`roll` is `steps[0]`'s
    own roll data; `mutations` is every step's mutations, concatenated in step order) for
    backward compatibility; `steps` is the full cascade. Raises `ValueError` for an unknown
    mechanic/difficulty/Exposure tier, or a missing `combat-attack` argument; propagates
    `character.load`'s own error for a missing actor or target entity.
    """
    if mechanic not in _PUBLIC_MECHANICS:
        raise ValueError(f"no such mechanic: {mechanic}")

    actor_path = pathlib.Path(actor)
    actor_state, _ = character.load(actor_path)
    target_path = pathlib.Path(target) if target is not None else None
    target_state: dict | None = None
    if target_path is not None:
        target_state, _ = character.load(target_path)

    seed_cursor = _SeedCursor(seed)
    steps: list[dict] = []

    if mechanic == "combat-attack":
        if target_state is None:
            raise ValueError("combat-attack requires a target")
        _stage_combat_attack(
            steps,
            actor=str(actor_path),
            actor_state=actor_state,
            target=str(target_path),
            target_state=target_state,
            skill=skill,
            weapon_dice=weapon_dice,
            armour_dice=armour_dice,
            seed_cursor=seed_cursor,
        )
    else:
        resolve_fn, mutate_fn = _MECHANICS[mechanic]
        roll_data = resolve_fn(
            actor=str(actor_path),
            actor_state=actor_state,
            skill=skill,
            difficulty=difficulty,
            declaration_bonus=declaration_bonus,
            tier=tier,
            target_state=target_state,
            seed=seed_cursor.next(),
        )
        mutations = mutate_fn(roll_data, actor_state=actor_state, target_state=target_state)
        for mutation in mutations:
            mutation["produced_by_step"] = 0
        steps.append(
            {
                "step_id": 0,
                "mechanic": mechanic,
                "roll": roll_data,
                "mutations": mutations,
                "depends_on": [],
            }
        )
        state_by_entity = {str(actor_path): actor_state}
        if target_path is not None:
            state_by_entity[str(target_path)] = target_state
        for mutation in list(mutations):
            _cascade_from_mutation(steps, mutation, state_by_entity, seed_cursor)

    all_mutations = [mutation for step in steps for mutation in step["mutations"]]
    proposal_id = f"p-{next(_proposal_ids)}"
    _open_proposals[proposal_id] = {"steps": steps, "mutations": all_mutations, "open": True}
    return {
        "proposal_id": proposal_id,
        "roll": steps[0]["roll"],
        "mutations": all_mutations,
        "steps": steps,
    }


def _pop_open_proposal(proposal_id: str) -> dict:
    proposal = _open_proposals.get(proposal_id)
    if proposal is None or not proposal["open"]:
        raise ProposalError(f"no open proposal: {proposal_id}")
    proposal["open"] = False
    return proposal


def commit(proposal_id: str) -> dict:
    """Apply exactly `proposal_id`'s staged mutations to state, atomically per entity, and
    invalidate it.

    A cascade can stage mutations against more than one entity (e.g. a combat chain's Stamina/
    wound mutations land on the target, not the attacker) -- mutations are grouped by their own
    `entity` path and each entity is loaded, mutated, and saved once, via the existing atomic
    per-file write (`state.py`'s `save_entity`). Atomicity is per entity file, the same guarantee
    `state.py` has always provided; this module makes no claim of a single atomic write spanning
    more than one entity file.

    Raises `ProposalError` if `proposal_id` does not resolve to a currently-open proposal
    (already committed, already discarded, or never issued) -- never a silent no-op
    (spec.md User Story 3).
    """
    proposal = _pop_open_proposal(proposal_id)
    mutations = proposal["mutations"]
    mutations_by_entity: dict[str, list[dict]] = {}
    for mutation in mutations:
        mutations_by_entity.setdefault(mutation["entity"], []).append(mutation)
    for entity_path_text, entity_mutations in mutations_by_entity.items():
        entity_path = pathlib.Path(entity_path_text)
        frontmatter, body = character.load(entity_path)
        for mutation in entity_mutations:
            _apply_mutation(frontmatter, mutation)
        character.save(frontmatter, body, entity_path)
    return {"proposal_id": proposal_id, "mutations": mutations}


def discard(proposal_id: str) -> dict:
    """Invalidate `proposal_id` without writing anything.

    Raises `ProposalError` if `proposal_id` does not resolve to a currently-open proposal.
    """
    _pop_open_proposal(proposal_id)
    return {"proposal_id": proposal_id}
