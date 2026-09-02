"""The base propose/commit/discard resolution mechanism, with cascading resolution and partial
reroll.

docs/design/31-action-resolution.md "Propose, then commit" (ADR 0050): `propose`/`propose_batch`
resolve a roll (or a whole chain of them, see "Cascading resolution" below) against one or more
actors' own state, stage any implied mutation, and write nothing; `commit` applies exactly the
staged mutations atomically; `discard` writes nothing. Both `commit` and `discard` invalidate the
proposal id so it can never resolve twice.

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

**Partial reroll** (specs/084-partial-reroll, extending #236's `depends_on` edges):
`reroll(proposal_id, step, resource)` discards exactly the downstream set of one staged
top-level step -- itself and everything that transitively depends on it -- and freshly resolves
it under the spent resource's own modifier (Resolve `+20`, Fortune/Bargain plain), re-cascading
under the same rule `propose`/`propose_batch` already use. Everything outside the downstream set
is untouched. `reroll` never invalidates the proposal id; only `commit`/`discard` do.

**Omen carryover** (specs/085-omen-carryover): an Ill/Fair Omen read off one roll's own Wyrd die
applies to that same actor's own *next* roll, whatever mechanic it is. An actor's own persisted
`pending_omen` field (`None`/`+10`/`-10`) is read -- never consumed just by reading -- at the
start of a batch and applied to that actor's first request in it; within a batch, each of an
actor's own further requests checks whether an earlier one produced a still-pending Omen, applies
and spends it (a fresh Omen replaces rather than stacks with a still-pending one), and
`depends_on` the step that produced it -- the same edge cascading resolution and partial reroll
already use, which is what makes `reroll` correct here for free: rerolling an Omen-producing step
pulls its Omen-consuming step (even from a different top-level request) into the downstream set.

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

#: docs/design/03-rules.md sections 3-4: a reroll resource's own modifier to the rerolled roll's
#: effective%. Fortune and the Bargain are a plain reroll at the same odds; Resolve adds +20.
RESOURCE_MODIFIERS = {"resolve": 20, "fortune": 0, "bargain": 0}

#: The resource's own cost, staged as a mutation on the reroll itself (docs/design/31-action-
#: resolution.md "Partial reroll": "The resource's own cost is itself a staged mutation").
RESOURCE_COSTS = {
    "resolve": ("resolve.current", "-", 1),
    "fortune": ("fortune.current", "-", 1),
    "bargain": ("taint", "+", 1),
}


class ProposalError(Exception):
    """Raised when `commit`/`discard` is called against an id that is not an open proposal."""


class _SeedCursor:
    """A deterministic seed sequence for a whole cascade/reroll (research.md's Decision): the
    first internal roll uses the caller's own `seed`, each subsequent one increments it by 1.
    `None` stays `None` throughout -- unseeded real play never becomes accidentally
    reproducible."""

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
    freshly-loaded entity) and, during `propose`/`propose_batch`/`reroll`, against a scratch copy
    already held in memory so a cascade can see the running effect of its own earlier steps
    without ever writing to disk (docs/design/31-action-resolution.md: "propose... writes
    nothing")."""
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
            "inputs": None,
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
                "inputs": None,
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

    attack_step_id = len(steps)
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
            "step_id": attack_step_id,
            "mechanic": "combat-attack",
            "roll": roll_data,
            "mutations": [],
            "depends_on": [],
            "inputs": None,
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
            "depends_on": [attack_step_id],
            "inputs": None,
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
            "depends_on": [attack_step_id],
            "inputs": None,
        }
    )
    _apply_mutation(target_state, stamina_mutation)
    stamina_after = _get_nested(target_state, "stamina.current")
    if stamina_before >= 0 and stamina_after < 0:
        _stage_critical(
            steps, target, -stamina_after, armour_step_id, seed_cursor, bears_on_skill=skill
        )


def _normalize_request(raw_request: dict) -> dict:
    """`propose`/`propose_batch`'s own kwargs, normalized to plain strings/None so a request can
    be stored verbatim on its step as `inputs` (what `reroll` later needs to redo it) and
    compared/reused without re-parsing paths."""
    target = raw_request.get("target")
    return {
        "actor": str(pathlib.Path(raw_request["actor"])),
        "mechanic": raw_request["mechanic"],
        "skill": raw_request.get("skill"),
        "target": str(pathlib.Path(target)) if target is not None else None,
        "difficulty": raw_request.get("difficulty", "average"),
        "declaration_bonus": raw_request.get("declaration_bonus", 0),
        "tier": raw_request.get("tier"),
        "weapon_dice": raw_request.get("weapon_dice"),
        "armour_dice": raw_request.get("armour_dice"),
    }


def _read_wyrd_omen(wyrd_die: str | None) -> int | None:
    """docs/design/03-rules.md section 1 / 31-action-resolution.md "Omen carryover": the units
    digit read as `fair_omen` (+10) or `ill_omen` (-10); any other reading produces no Omen."""
    if wyrd_die == "fair_omen":
        return 10
    if wyrd_die == "ill_omen":
        return -10
    return None


def _stage_request(
    steps: list[dict],
    request: dict,
    state_cache: dict[str, dict],
    seed_cursor: _SeedCursor,
    *,
    declaration_bonus_delta: int = 0,
    extra_depends_on: list[int] | None = None,
) -> None:
    """Stage one top-level request (a `propose_batch` entry, or a `reroll`'s fresh
    re-resolution) into `steps`, tagging its own first step with `inputs=request` so it can later
    be rerolled. `declaration_bonus_delta` is the combined reroll-resource and/or pending-Omen
    modifier already added together by the caller (0 for neither). `extra_depends_on` records the
    step this one's own roll consumed a pending Omen from, if any (docs/design/31-action-
    resolution.md "Omen carryover": "a step that consumes another step's Omen depends on it")."""
    if request["mechanic"] not in _PUBLIC_MECHANICS:
        raise ValueError(f"no such mechanic: {request['mechanic']}")

    def load_state(path_text: str) -> dict:
        if path_text not in state_cache:
            frontmatter, _ = character.load(pathlib.Path(path_text))
            state_cache[path_text] = frontmatter
        return state_cache[path_text]

    actor_state = load_state(request["actor"])
    target_state = load_state(request["target"]) if request["target"] is not None else None

    base_id = len(steps)
    if request["mechanic"] == "combat-attack":
        if target_state is None:
            raise ValueError("combat-attack requires a target")
        boosted_state = actor_state
        if declaration_bonus_delta and request["skill"] is not None:
            boosted_state = dict(actor_state)
            boosted_state["skills"] = dict(actor_state.get("skills", {}))
            boosted_state["skills"][request["skill"]] = (
                actor_state.get("skills", {}).get(request["skill"], rules.UNTRAINED_SKILL)
                + declaration_bonus_delta
            )
        _stage_combat_attack(
            steps,
            actor=request["actor"],
            actor_state=boosted_state,
            target=request["target"],
            target_state=target_state,
            skill=request["skill"],
            weapon_dice=request["weapon_dice"],
            armour_dice=request["armour_dice"],
            seed_cursor=seed_cursor,
        )
    else:
        resolve_fn, mutate_fn = _MECHANICS[request["mechanic"]]
        roll_data = resolve_fn(
            actor=request["actor"],
            actor_state=actor_state,
            skill=request["skill"],
            difficulty=request["difficulty"],
            declaration_bonus=request["declaration_bonus"] + declaration_bonus_delta,
            tier=request["tier"],
            target_state=target_state,
            seed=seed_cursor.next(),
        )
        mutations = mutate_fn(roll_data, actor_state=actor_state, target_state=target_state)
        for mutation in mutations:
            mutation["produced_by_step"] = base_id
        steps.append(
            {
                "step_id": base_id,
                "mechanic": request["mechanic"],
                "roll": roll_data,
                "mutations": mutations,
                "depends_on": [],
                "inputs": None,
            }
        )
        state_by_entity = {request["actor"]: actor_state}
        if request["target"] is not None:
            state_by_entity[request["target"]] = target_state
        for mutation in list(mutations):
            _cascade_from_mutation(steps, mutation, state_by_entity, seed_cursor)

    steps[base_id]["inputs"] = request
    steps[base_id]["depends_on"] = list(extra_depends_on or [])


def _stage_requests(
    steps: list[dict],
    ordered_requests: list[dict],
    state_cache: dict[str, dict],
    seed_cursor: _SeedCursor,
    *,
    resource_deltas: dict[int, int] | None = None,
) -> None:
    """Stage `ordered_requests` (already in the chronological order they must resolve in) into
    `steps`, threading each actor's own pending-Omen token across their requests -- the shared
    core `propose_batch` and `reroll` (for a downstream set spanning more than one top-level
    request) both use, so the two can never diverge (docs/design/31-action-resolution.md "Omen
    carryover").

    For each actor, `token` starts at that actor's own currently-persisted `pending_omen`
    (docs/design/31-action-resolution.md: "propose reads this field at the start of ... a batch"),
    read but not yet consumed. Each of that actor's own requests, processed in order: applies the
    current token (if any) as this request's `declaration_bonus_delta`, recording a `depends_on`
    edge to whichever step produced it (only if that step exists within *this* call -- a token
    that came from persisted state has no in-call producer to depend on); then reads its own
    fresh roll's Wyrd die -- a fresh Omen always *replaces* the token, whether or not the old one
    was just consumed by this same request ("a further Omen ... replaces ... rather than
    stacking"); with no fresh Omen, a token that was just consumed clears to `None`.

    `resource_deltas` (only used by `reroll`) adds an extra modifier to specific requests by
    their index in `ordered_requests`, on top of whatever Omen modifier that request already
    carries -- both compose into the same `declaration_bonus_delta` channel.

    At the end, for every actor whose final token differs from what was persisted going in, one
    `pending_omen` `set` mutation is appended to the last step that changed it -- committed
    atomically with everything else; a discarded proposal leaves the persisted field untouched,
    since nothing here ever writes to disk (module docstring)."""
    resource_deltas = resource_deltas or {}
    omen_by_actor: dict[str, dict] = {}

    def get_omen(actor_path: str) -> dict:
        if actor_path not in omen_by_actor:
            if actor_path not in state_cache:
                frontmatter, _ = character.load(pathlib.Path(actor_path))
                state_cache[actor_path] = frontmatter
            original = state_cache[actor_path].get("pending_omen")
            omen_by_actor[actor_path] = {
                "token": original,
                "producing_step": None,
                "original": original,
                "last_change_step": None,
            }
        return omen_by_actor[actor_path]

    for index, request in enumerate(ordered_requests):
        omen = get_omen(request["actor"])
        omen_modifier = omen["token"] or 0
        extra_depends_on = (
            [omen["producing_step"]] if omen_modifier and omen["producing_step"] is not None else []
        )
        base_id = len(steps)
        _stage_request(
            steps,
            request,
            state_cache,
            seed_cursor,
            declaration_bonus_delta=omen_modifier + resource_deltas.get(index, 0),
            extra_depends_on=extra_depends_on,
        )
        top_step = steps[base_id]
        consumed = bool(omen_modifier)
        fresh_omen = _read_wyrd_omen(top_step["roll"].get("wyrd_die"))
        if fresh_omen is not None:
            omen["token"] = fresh_omen
            omen["producing_step"] = base_id
            omen["last_change_step"] = base_id
        elif consumed:
            omen["token"] = None
            omen["producing_step"] = None
            omen["last_change_step"] = base_id

    for actor_path, omen in omen_by_actor.items():
        if omen["token"] != omen["original"]:
            change_step = next(s for s in steps if s["step_id"] == omen["last_change_step"])
            change_step["mutations"].append(
                {
                    "entity": actor_path,
                    "field": "pending_omen",
                    "op": "set",
                    "value": omen["token"],
                    "produced_by_step": omen["last_change_step"],
                }
            )


def propose_batch(requests: list[dict], *, seed: int | None = None) -> dict:
    """Resolve several independent top-level requests into one proposal (docs/design/31-action-
    resolution.md "A worked example": "Two unrelated Exposure sources in the same scene, proposed
    together"). Each request takes the same keys as `propose`'s own kwargs (`actor`, `mechanic`,
    `skill`, `target`, `difficulty`, `declaration_bonus`, `tier`, `weapon_dice`, `armour_dice`).
    An actor/target appearing in more than one request shares one in-memory scratch state across
    them, so a later request in the batch sees any earlier request's own staged mutations when
    checking for a threshold crossing. Writes nothing. Returns `{"proposal_id", "roll",
    "mutations", "steps"}` -- `roll`/`mutations` cover the *first* request's own first step, for
    #235 single-request backward compatibility; `steps` is the full, possibly multi-request,
    cascade.
    """
    if not requests:
        raise ValueError("propose_batch requires at least one request")

    seed_cursor = _SeedCursor(seed)
    steps: list[dict] = []
    state_cache: dict[str, dict] = {}
    ordered_requests = [_normalize_request(raw_request) for raw_request in requests]
    _stage_requests(steps, ordered_requests, state_cache, seed_cursor)

    all_mutations = [mutation for step in steps for mutation in step["mutations"]]
    proposal_id = f"p-{next(_proposal_ids)}"
    _open_proposals[proposal_id] = {"steps": steps, "mutations": all_mutations, "open": True}
    return {
        "proposal_id": proposal_id,
        "roll": steps[0]["roll"],
        "mutations": all_mutations,
        "steps": steps,
    }


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

    A thin single-request wrapper over `propose_batch` -- see that function for proposing
    several independent requests together in one proposal.
    """
    return propose_batch(
        [
            {
                "actor": actor,
                "mechanic": mechanic,
                "skill": skill,
                "target": target,
                "difficulty": difficulty,
                "declaration_bonus": declaration_bonus,
                "tier": tier,
                "weapon_dice": weapon_dice,
                "armour_dice": armour_dice,
            }
        ],
        seed=seed,
    )


def _downstream_set(steps: list[dict], step_id: int) -> set[int]:
    """`step_id` itself, plus every step that transitively depends on it (docs/design/31-action-
    resolution.md "Partial reroll": "every step that step_id names, or anything that in turn
    depends on it, transitively")."""
    result = {step_id}
    changed = True
    while changed:
        changed = False
        for step in steps:
            if step["step_id"] in result:
                continue
            if any(dep in result for dep in step["depends_on"]):
                result.add(step["step_id"])
                changed = True
    return result


def _renumber_and_merge(
    kept_steps: list[dict], new_steps: list[dict], original_step_id: int
) -> list[dict]:
    """`new_steps` were built fresh, 0-based. Remap so the rerolled step keeps its own original
    id (the identifier the player/GM already referred to it by) and every further cascade step
    gets a fresh id after the highest one already in use -- never colliding with any kept step,
    including an independent step from elsewhere in the same batch."""
    max_existing_id = max([step["step_id"] for step in kept_steps] + [original_step_id])
    id_map = {0: original_step_id}
    next_id = max_existing_id + 1
    for old_id in range(1, len(new_steps)):
        id_map[old_id] = next_id
        next_id += 1
    for step in new_steps:
        step["step_id"] = id_map[step["step_id"]]
        step["depends_on"] = [id_map[dep] for dep in step["depends_on"]]
        for mutation in step["mutations"]:
            mutation["produced_by_step"] = id_map[mutation["produced_by_step"]]
    return kept_steps + new_steps


def reroll(proposal_id: str, step: int, resource: str, *, seed: int | None = None) -> dict:
    """Spend `resource` (`resolve`, `fortune`, or `bargain`) against staged `step`: compute its
    downstream set (itself and everything depending on it, transitively) from `depends_on`,
    discard exactly that set, and freshly resolve `step` under the resource's own modifier,
    re-cascading under the same rule `propose`/`propose_batch` use. Every step outside the
    downstream set is untouched -- an independent branch elsewhere in the same batch is never
    affected (docs/design/31-action-resolution.md "Partial reroll").

    The resource's own cost is staged as an extra mutation on the freshly-resolved `step`, not
    applied separately (Resolve/Fortune spent, or Taint gained for the Bargain).

    Does **not** invalidate `proposal_id` -- the proposal stays open, revised in place, until an
    explicit `commit`/`discard`.

    Raises `ProposalError` if `proposal_id` is not open; `ValueError` for an unknown `resource`,
    an unknown `step`, or a `step` that was not itself a top-level request (an internal cascade
    step such as `transformation`/`weapon-damage`/`armour`/`critical` has no `inputs` recorded
    and is not directly rerollable -- only the top-level roll a reroll resource is actually spent
    against ever is).
    """
    if resource not in RESOURCE_MODIFIERS:
        raise ValueError(f"no such reroll resource: {resource}")
    proposal = _open_proposals.get(proposal_id)
    if proposal is None or not proposal["open"]:
        raise ProposalError(f"no open proposal: {proposal_id}")

    steps = proposal["steps"]
    target_step = next((s for s in steps if s["step_id"] == step), None)
    if target_step is None:
        raise ValueError(f"no such step: {step}")
    request = target_step.get("inputs")
    if request is None:
        raise ValueError(f"step {step} is not a top-level request and cannot be rerolled")

    downstream = _downstream_set(steps, step)
    kept_steps = [s for s in steps if s["step_id"] not in downstream]

    # A step whose downstream membership came only from an Omen-consumption edge belongs to a
    # *different* top-level request than the rerolled one (docs/design/31-action-resolution.md
    # "Omen carryover" worked example: rerolling the Omen-producing step pulls the Omen-consuming
    # step's own request into the downstream set too). Every such request is re-run, in their
    # original chronological order -- `step`'s own request is always first, since nothing in the
    # downstream set can have a smaller step_id than `step` itself (a dependent always resolves
    # after what it depends on).
    downstream_steps_in_order = sorted(
        (s for s in steps if s["step_id"] in downstream), key=lambda s: s["step_id"]
    )
    requests_to_redo = [
        s["inputs"] for s in downstream_steps_in_order if s.get("inputs") is not None
    ]

    # Rebuild scratch state: fresh from disk (propose/reroll never write), then replay every
    # kept step's own mutations so the reroll's own cascade -- including its own Omen tracking,
    # which reads each actor's pending_omen from this same scratch state -- sees their cumulative
    # effect.
    state_cache: dict[str, dict] = {}

    def load_state(path_text: str) -> dict:
        if path_text not in state_cache:
            frontmatter, _ = character.load(pathlib.Path(path_text))
            state_cache[path_text] = frontmatter
        return state_cache[path_text]

    for kept_step in kept_steps:
        for mutation in kept_step["mutations"]:
            _apply_mutation(load_state(mutation["entity"]), mutation)
    for redo_request in requests_to_redo:
        load_state(redo_request["actor"])
        if redo_request["target"] is not None:
            load_state(redo_request["target"])

    seed_cursor = _SeedCursor(seed)
    new_steps: list[dict] = []
    _stage_requests(
        new_steps,
        requests_to_redo,
        state_cache,
        seed_cursor,
        resource_deltas={0: RESOURCE_MODIFIERS[resource]},
    )

    roller_entity = new_steps[0]["roll"]["actor"]
    cost_field, cost_op, cost_value = RESOURCE_COSTS[resource]
    new_steps[0]["mutations"].append(
        {
            "entity": roller_entity,
            "field": cost_field,
            "op": cost_op,
            "value": cost_value,
            "produced_by_step": new_steps[0]["step_id"],
        }
    )

    merged = _renumber_and_merge(kept_steps, new_steps, step)
    proposal["steps"] = merged
    proposal["mutations"] = [mutation for s in merged for mutation in s["mutations"]]
    return {
        "proposal_id": proposal_id,
        "roll": merged[0]["roll"],
        "mutations": proposal["mutations"],
        "steps": merged,
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

    A cascade (or a batch, or a reroll) can stage mutations against more than one entity (e.g. a
    combat chain's Stamina/wound mutations land on the target, not the attacker) -- mutations
    are grouped by their own `entity` path and each entity is loaded, mutated, and saved once,
    via the existing atomic per-file write (`state.py`'s `save_entity`). Atomicity is per entity
    file, the same guarantee `state.py` has always provided; this module makes no claim of a
    single atomic write spanning more than one entity file.

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
