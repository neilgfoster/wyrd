"""Turn order, round structure, engagement and action economy: the scene-level state machine
around WHEN a combatant may act and WHO they are engaged with, not how a roll resolves (that
stays `resolution.py`'s own job).

docs/design/03-rules.md section 2 "Rounds and turn order" / "Surprise and ambush": whoever
started the exchange acts first; where neither side started it, the armed side acts first, or
the player's side if both/neither are armed (ADR 0018 -- the one rule here decided from outside
the fiction). A surprised side does not act in round 1 but still defends normally. An ambush
eases the ambushing side's round-1 attacks by +20, and nothing after.

"A turn is one action" / "Engagement" / "Ranged attacks" (specs/087-action-economy-engagement):
the engine records one fact about position -- two combatants are in close engagement, or they
are not. Closing costs the closing combatant their action. Breaking off always works and always
costs a parting blow from every opponent still engaged. A ranged attack from an engaged shooter
is Difficult; one at a target engaged with someone else is Challenging, and an Ill Omen on that
shot hits the ally instead.

"Getting away, and the pursuit" (specs/088-escape-and-pursuit): leaving the scene entirely is a
group test in the "everyone must get through" shape, at a difficulty set by how many pursuers
are able and willing to follow -- one is Challenging, each further pursuer one rung harder. A
success clears the scene; a failure resumes it exactly as it was.

"Crowds" (specs/089-the-crowd-rule): a crowd is tracked by body count, not per-body state. A
character or companion engaged with a crowd clears one qualifying body for free at the start of
their own turn -- no roll, no action spent. The crowd answers with exactly one attack a round
regardless of body count, eased +10 per body on its target beyond the first, capped at +20; its
parting blow is the same single, eased attack.

A combat scene is chronicle-scoped, not per-entity (specs/086-turn-order-round-structure/spec.md
Assumptions) -- it lives under a `combat` key in the same chronicle state `state.py` already
reads/writes atomically.

"The recurring wound" (docs/design/06-aftermath.md, specs/093-recurring-wound-combat-start):
every active recurring wound a combatant carries costs its named skill one Challenging step,
computed once at `start_combat` and fixed for that fight -- never reapplied mid-fight, never
carried between fights.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib

from wyrd import resolution, rules, state

#: docs/design/03-rules.md section 2 "Surprise and ambush": the ambush bonus, and the round it
#: stops applying after.
AMBUSH_BONUS = 20
AMBUSH_ROUNDS = 1


def determine_first_actor(started_by: str | None, armed: dict[str, bool], player_side: str) -> str:
    """docs/design/03-rules.md section 2 "Rounds and turn order": the exchange-starter, if one
    is named, wins outright. Otherwise (a mutual encounter): the sole armed side acts first; if
    both or neither side is armed, the designated player side acts first (ADR 0018). Pure --
    no persisted state, no randomness (docs/design/27-tooling.md: deterministic over inference).
    """
    if started_by is not None:
        return started_by
    armed_sides = [side for side, is_armed in armed.items() if is_armed]
    if len(armed_sides) == 1:
        return armed_sides[0]
    return player_side


def _recurring_wound_penalties(wounds: list[dict]) -> dict[str, int]:
    """docs/design/06-aftermath.md "The recurring wound": every active (`closed` is `None`)
    wound with `recurring: True` costs its `bears_on` skill one `CHALLENGING_MODIFIER` step;
    a character carrying more than one has each fire, stacking (summing) where two bear on the
    same skill (specs/093-recurring-wound-combat-start). Reuses the existing Challenging-
    difficulty constant rather than a new literal -- issue #254's own Definition of Done.
    """
    penalties: dict[str, int] = {}
    for wound in wounds:
        if not wound.get("recurring") or wound.get("closed") is not None:
            continue
        skill = wound.get("bears_on")
        if not skill:
            continue
        penalties[skill] = penalties.get(skill, 0) + CHALLENGING_MODIFIER
    return penalties


def start_combat(
    sides: dict[str, dict],
    started_by: str | None,
    player_side: str,
    *,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """Start a combat scene: validate `started_by`/`player_side` name real sides, compute the
    first actor, and persist the scene under chronicle state's `combat` key.

    `sides`: `{"<name>": {"armed": bool, "surprised": bool (default False),
    "ambush": bool (default False), "wounds": list[dict] (default [])}}`. `wounds` are the
    combatant's raw wound records (the same shape `character.active_wound_effects` reads);
    only active recurring wounds among them contribute -- see `_recurring_wound_penalties`.

    Raises `ValueError` if `started_by` or `player_side` names a side not in `sides`.
    """
    if started_by is not None and started_by not in sides:
        raise ValueError(f"no such side: {started_by}")
    if player_side not in sides:
        raise ValueError(f"no such side: {player_side}")

    armed = {name: bool(flags.get("armed", False)) for name, flags in sides.items()}
    first_actor = determine_first_actor(started_by, armed, player_side)

    normalized_sides = {
        name: {
            "armed": bool(flags.get("armed", False)),
            "surprised": bool(flags.get("surprised", False)),
            "ambush": bool(flags.get("ambush", False)),
        }
        for name, flags in sides.items()
    }
    wound_penalties = {
        name: penalties
        for name, flags in sides.items()
        if (penalties := _recurring_wound_penalties(flags.get("wounds") or []))
    }
    scene = {
        "sides": normalized_sides,
        "round": 1,
        "first_actor": first_actor,
        "engaged": [],
        "acted": [],
        "wound_penalties": wound_penalties,
    }

    current = state.load(state_path)
    current["combat"] = scene
    state.save(current, state_path)
    return scene


def _load_scene(state_path: pathlib.Path) -> dict:
    current = state.load(state_path)
    scene = current.get("combat")
    if scene is None:
        raise ValueError("no combat scene in progress -- call start_combat first")
    return scene


def advance_round(*, state_path: pathlib.Path = state.DEFAULT_STATE_PATH) -> dict:
    """Advance the current combat scene to its next round, clearing who has acted."""
    current = state.load(state_path)
    scene = current.get("combat")
    if scene is None:
        raise ValueError("no combat scene in progress -- call start_combat first")
    scene["round"] += 1
    scene["acted"] = []
    state.save(current, state_path)
    return scene


def can_act(side: str, *, state_path: pathlib.Path = state.DEFAULT_STATE_PATH) -> bool:
    """docs/design/03-rules.md section 2: a surprised side does not act in round 1 -- false only
    for a surprised side while the scene's round is still 1; true otherwise (and always true for
    a side that was never marked surprised)."""
    scene = _load_scene(state_path)
    if side not in scene["sides"]:
        raise ValueError(f"no such side: {side}")
    if scene["sides"][side]["surprised"] and scene["round"] == 1:
        return False
    return True


def attack_modifier(side: str, *, state_path: pathlib.Path = state.DEFAULT_STATE_PATH) -> int:
    """docs/design/03-rules.md section 2: an ambushing side's round-1 attacks carry +20, and
    nothing after."""
    scene = _load_scene(state_path)
    if side not in scene["sides"]:
        raise ValueError(f"no such side: {side}")
    if scene["sides"][side]["ambush"] and scene["round"] <= AMBUSH_ROUNDS:
        return AMBUSH_BONUS
    return 0


def _normalize(path: str | pathlib.Path) -> str:
    return str(pathlib.Path(path))


def has_acted(
    actor: str | pathlib.Path, *, state_path: pathlib.Path = state.DEFAULT_STATE_PATH
) -> bool:
    """Whether `actor` has already spent their action this round (docs/design/03-rules.md
    section 2: "A turn is one action"). Cleared by `advance_round`."""
    scene = _load_scene(state_path)
    return _normalize(actor) in scene["acted"]


def engaged_with(
    actor: str | pathlib.Path, *, state_path: pathlib.Path = state.DEFAULT_STATE_PATH
) -> list[str]:
    """Every combatant currently in close engagement with `actor` (docs/design/03-rules.md
    section 2 "Engagement": "two combatants are in close engagement, or they are not")."""
    scene = _load_scene(state_path)
    actor_norm = _normalize(actor)
    partners = []
    for pair in scene["engaged"]:
        if actor_norm == pair["a"]:
            partners.append(pair["b"])
        elif actor_norm == pair["b"]:
            partners.append(pair["a"])
    return partners


def is_engaged(
    actor: str | pathlib.Path, *, state_path: pathlib.Path = state.DEFAULT_STATE_PATH
) -> bool:
    return bool(engaged_with(actor, state_path=state_path))


def close(
    actor: str | pathlib.Path,
    opponent: str | pathlib.Path,
    *,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """docs/design/03-rules.md section 2: "Closing costs the closing combatant their action.
    They arrive; they do not also swing." Records the engagement pair and marks `actor` as
    having acted this round.

    Raises `ValueError` if `actor` has already acted this round -- closing is itself the one
    action a turn allows, never a free addition to whatever else the actor already did.
    """
    current = state.load(state_path)
    scene = current.get("combat")
    if scene is None:
        raise ValueError("no combat scene in progress -- call start_combat first")
    actor_norm, opponent_norm = _normalize(actor), _normalize(opponent)
    if actor_norm in scene["acted"]:
        raise ValueError(f"{actor} has already acted this round")
    scene["engaged"].append({"a": actor_norm, "b": opponent_norm})
    scene["acted"].append(actor_norm)
    state.save(current, state_path)
    return scene


def break_off(
    actor: str | pathlib.Path,
    opponent_attacks: dict[str, dict],
    *,
    seed: int | None = None,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """docs/design/03-rules.md section 2: "Breaking close engagement always works, and always
    costs a parting blow. Every opponent still engaged with the departing combatant attacks them
    as they go. There is no roll to leave."

    `opponent_attacks`: `{"<opponent path>": {"skill": str, "weapon_dice": str,
    "armour_dice": str}}` -- MUST name exactly the opponents currently engaged with `actor`
    (raises `ValueError` otherwise), since the engine has no other source for what gear each
    opponent's own parting blow uses.

    Removes every engagement pair involving `actor`, marks `actor` as having acted this round
    (breaking off is itself one of the five actions), and stages one `combat-attack` proposal
    per opponent -- via `resolution.propose_batch`, so all the parting blows land in one
    proposal -- each attacking `actor`. An actor with no current engagements stages nothing
    (a valid, non-error outcome): `resolution.propose_batch` requires at least one request, so
    that case returns a no-op result without calling it.
    """
    current = state.load(state_path)
    scene = current.get("combat")
    if scene is None:
        raise ValueError("no combat scene in progress -- call start_combat first")
    actor_norm = _normalize(actor)
    partners = engaged_with(actor_norm, state_path=state_path)
    if set(_normalize(p) for p in opponent_attacks) != set(partners):
        raise ValueError(
            f"opponent_attacks must name exactly the engaged opponents {partners}, "
            f"got {list(opponent_attacks)}"
        )

    scene["engaged"] = [
        pair for pair in scene["engaged"] if actor_norm not in (pair["a"], pair["b"])
    ]
    if actor_norm not in scene["acted"]:
        scene["acted"].append(actor_norm)
    state.save(current, state_path)

    if not partners:
        return {"proposal_id": None, "roll": None, "mutations": [], "steps": []}

    requests = [
        {
            "actor": opponent,
            "mechanic": "combat-attack",
            "target": actor_norm,
            "skill": gear["skill"],
            "weapon_dice": gear["weapon_dice"],
            "armour_dice": gear["armour_dice"],
        }
        for opponent, gear in opponent_attacks.items()
    ]
    return resolution.propose_batch(requests, seed=seed)


#: docs/design/03-rules.md section 2 "Breaking off, and getting away": the pursuit ladder --
#: one pursuer is Challenging, each further pursuer one rung harder. There is no rung below
#: Very Hard, so four or more pursuers all floor out there.
PURSUIT_DIFFICULTIES = ["challenging", "difficult", "hard", "very_hard"]


def escape_difficulty(pursuer_count: int) -> str | None:
    """Convert a pursuer count to the escape test's difficulty (docs/design/03-rules.md
    section 2's pursuit ladder). `None` means "no one able or willing to follow -- no test,
    you simply go"."""
    if pursuer_count < 0:
        raise ValueError(f"pursuer_count must not be negative, got {pursuer_count}")
    if pursuer_count == 0:
        return None
    return PURSUIT_DIFFICULTIES[min(pursuer_count - 1, len(PURSUIT_DIFFICULTIES) - 1)]


def escape_scene(
    party_skills: dict[str, int | None],
    pursuer_count: int,
    *,
    seed: int | None = None,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """docs/design/03-rules.md section 2: "Getting away from the scene is a group test, in the
    *everyone must get through* shape ... the party escapes as fast as its slowest member."
    Resolved via `rules.group_test` in `"least_capable"` mode -- the same mode the "everyone
    must get through" shape already names, never reimplemented here.

    `party_skills`: `{"<member path>": skill_or_None}`, the same shape `select_group_skill`
    already expects per member (`None` meaning "no relevant skill at all", substituted with the
    untrained rate, never excluded).

    On success, or on the no-test (zero-pursuer) case, the chronicle's `combat` scene is
    removed entirely -- the party has left. On failure, state is left untouched: "the fight
    resumes, and it resumes where the slowest member is," which is already where combat state
    already has them, so there is nothing further to change (spec.md FR-005).
    """
    if not party_skills:
        raise ValueError("party_skills must not be empty")
    slowest_member = min(
        party_skills,
        key=lambda member: (
            rules.UNTRAINED_SKILL if party_skills[member] is None else party_skills[member]
        ),
    )
    difficulty = escape_difficulty(pursuer_count)
    if difficulty is None:
        current = state.load(state_path)
        current.pop("combat", None)
        state.save(current, state_path)
        return {
            "escaped": True,
            "no_test": True,
            "difficulty": None,
            "roll": None,
            "slowest_member": slowest_member,
        }

    opponent = 50 - resolution.DIFFICULTY_BONUSES[difficulty]
    result = rules.group_test(list(party_skills.values()), "least_capable", opponent, seed=seed)
    escaped = bool(result["success"])
    if escaped:
        current = state.load(state_path)
        current.pop("combat", None)
        state.save(current, state_path)
    return {
        **result,
        "escaped": escaped,
        "no_test": False,
        "difficulty": difficulty,
        "slowest_member": slowest_member,
    }


#: docs/design/03-rules.md section 2 "Crowds": the three-part qualification lookup's own
#: thresholds -- max Stamina, and the skill gap that must be met or exceeded.
CROWD_MAX_STAMINA = 1
CROWD_SKILL_GAP = 20

#: the crowd's own attack ease: +10 per body on the target beyond the first, capped at +20
#: (reached at three bodies).
CROWD_EASE_PER_BODY = 10
CROWD_EASE_CAP = 20


def is_crowd_member(
    opponent_max_stamina: int,
    opponent_armoured: bool,
    character_skill: int,
    opponent_skill: int,
) -> bool:
    """docs/design/03-rules.md section 2 "Crowds": the three-part lookup. All three must hold:
    the opponent's maximum Stamina is 1, the opponent wears no armour, and the character's
    relevant skill is ahead of the opponent's by 20 or more."""
    if opponent_max_stamina != CROWD_MAX_STAMINA:
        return False
    if opponent_armoured:
        return False
    return character_skill - opponent_skill >= CROWD_SKILL_GAP


def crowd_ease(body_count: int) -> int:
    """docs/design/03-rules.md section 2: "+10 for each body on that character beyond the
    first, to a ceiling of +20" -- reached at three bodies."""
    if body_count < 1:
        raise ValueError(f"body_count must be at least 1, got {body_count}")
    return min((body_count - 1) * CROWD_EASE_PER_BODY, CROWD_EASE_CAP)


def register_crowd(
    crowd: str | pathlib.Path,
    body_count: int,
    *,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """Record `crowd`'s current body count in the combat scene, under a `crowds` dict keyed by
    the crowd's normalized path -- the state `clear_crowd_member`/`crowd_attack` read and
    decrement. `body_count` MUST be positive; a crowd with no bodies is not a crowd."""
    if body_count < 1:
        raise ValueError(f"body_count must be at least 1, got {body_count}")
    current = state.load(state_path)
    scene = current.get("combat")
    if scene is None:
        raise ValueError("no combat scene in progress -- call start_combat first")
    scene.setdefault("crowds", {})[_normalize(crowd)] = body_count
    state.save(current, state_path)
    return scene


def crowd_body_count(
    crowd: str | pathlib.Path, *, state_path: pathlib.Path = state.DEFAULT_STATE_PATH
) -> int:
    """The crowd's currently-remaining body count, or 0 if it was never registered or has been
    fully cleared."""
    scene = _load_scene(state_path)
    return scene.get("crowds", {}).get(_normalize(crowd), 0)


def clear_crowd_member(
    actor: str | pathlib.Path,
    crowd: str | pathlib.Path,
    *,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """docs/design/03-rules.md section 2: "At the start of their turn, a character in close
    engagement with a crowd clears one crowd member, without a roll and without spending their
    action." Decrements the crowd's body count by exactly one; never touches `acted` (unlike
    `close`/`break_off`, this is not the actor's one action for the turn).

    Raises `ValueError` if `actor` is not currently engaged with `crowd`, or if `crowd` has no
    bodies left to clear.
    """
    current = state.load(state_path)
    scene = current.get("combat")
    if scene is None:
        raise ValueError("no combat scene in progress -- call start_combat first")
    actor_norm, crowd_norm = _normalize(actor), _normalize(crowd)
    if crowd_norm not in engaged_with(actor_norm, state_path=state_path):
        raise ValueError(f"{actor} is not engaged with {crowd}")
    crowds = scene.setdefault("crowds", {})
    remaining = crowds.get(crowd_norm, 0)
    if remaining <= 0:
        raise ValueError(f"{crowd} has no bodies left to clear")
    crowds[crowd_norm] = remaining - 1
    state.save(current, state_path)
    return scene


def _crowd_attack_request(
    crowd_norm: str,
    target_norm: str,
    skill: str,
    weapon_dice: str,
    armour_dice: str,
    body_count: int,
    damage_type: str | None = None,
) -> dict:
    return {
        "actor": crowd_norm,
        "mechanic": "combat-attack",
        "target": target_norm,
        "skill": skill,
        "weapon_dice": weapon_dice,
        "armour_dice": armour_dice,
        "damage_type": damage_type,
        "declaration_bonus": crowd_ease(body_count),
    }


def crowd_attack(
    crowd: str | pathlib.Path,
    target: str | pathlib.Path,
    skill: str,
    weapon_dice: str,
    armour_dice: str,
    *,
    damage_type: str | None = None,
    seed: int | None = None,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """docs/design/03-rules.md section 2: "A crowd engaged with a character makes one attack on
    them each round," eased by `crowd_ease` of its own currently-registered body count against
    `target`. Exactly one `combat-attack` request via `resolution.propose_batch` -- never one
    per body, regardless of how many bodies the crowd has left. `damage_type`
    (docs/design/05-criticals.md) is forwarded unchanged to that request; unset defaults to
    `slashing` (specs/090-damage-type-criticals FR-001b)."""
    body_count = crowd_body_count(crowd, state_path=state_path)
    request = _crowd_attack_request(
        _normalize(crowd),
        _normalize(target),
        skill,
        weapon_dice,
        armour_dice,
        body_count,
        damage_type,
    )
    return resolution.propose_batch([request], seed=seed)


def crowd_parting_blow(
    crowd: str | pathlib.Path,
    actor: str | pathlib.Path,
    skill: str,
    weapon_dice: str,
    armour_dice: str,
    *,
    damage_type: str | None = None,
    seed: int | None = None,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """docs/design/03-rules.md section 2: "A crowd's parting blow is one attack on the same
    terms," not one per body -- the same eased single `combat-attack` request `crowd_attack`
    stages, with the crowd attacking the departing `actor` instead of its usual target. Used in
    place of `break_off` for a crowd specifically: `break_off`'s own contract stages one attack
    per engaged opponent with no ease channel, which would both roll once per crowd body and
    skip the ease this rule requires."""
    return crowd_attack(
        crowd,
        actor,
        skill,
        weapon_dice,
        armour_dice,
        damage_type=damage_type,
        seed=seed,
        state_path=state_path,
    )


#: docs/design/03-rules.md section 1's difficulty ladder, reused here for the two named
#: ranged-attack rows (section 2 "Ranged attacks").
DIFFICULT_MODIFIER = resolution.DIFFICULTY_BONUSES["difficult"]
CHALLENGING_MODIFIER = resolution.DIFFICULTY_BONUSES["challenging"]


def ranged_attack_difficulty(
    shooter: str | pathlib.Path,
    target: str | pathlib.Path,
    *,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> str:
    """docs/design/03-rules.md section 2 "Ranged attacks": the shooter's own engagement takes
    precedence over the target's (an engaged shooter is Difficult regardless of the target's own
    engagement); otherwise a target engaged with someone other than the shooter is Challenging;
    otherwise this feature has no fiction-only row to offer (spec.md Assumptions) and reports
    "average"."""
    if is_engaged(shooter, state_path=state_path):
        return "difficult"
    if [p for p in engaged_with(target, state_path=state_path) if p != _normalize(shooter)]:
        return "challenging"
    return "average"


def resolve_ranged_attack(
    shooter: str | pathlib.Path,
    target: str | pathlib.Path,
    skill: str,
    weapon_dice: str,
    armour_dice: str,
    *,
    damage_type: str | None = None,
    seed: int | None = None,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """Resolve a ranged `combat-attack`, applying whichever of the two named difficulty rows
    (`ranged_attack_difficulty`) applies, through `resolution.propose`'s own `declaration_bonus`
    channel. If the target is engaged with an ally (not the shooter) and the resulting roll's
    own Wyrd die reads Ill Omen, the shot is redirected: the original proposal is discarded and
    a fresh one, identical except for its target, is raised against the ally instead
    (docs/design/03-rules.md: "an Ill Omen on the shot means the ally is hit instead").
    `damage_type` (docs/design/05-criticals.md) is forwarded unchanged; unset defaults to
    `slashing` (specs/090-damage-type-criticals FR-001b).
    """
    difficulty = ranged_attack_difficulty(shooter, target, state_path=state_path)
    modifier = {"difficult": DIFFICULT_MODIFIER, "challenging": CHALLENGING_MODIFIER}.get(
        difficulty, 0
    )
    allies = [p for p in engaged_with(target, state_path=state_path) if p != _normalize(shooter)]

    result = resolution.propose(
        actor=shooter,
        mechanic="combat-attack",
        skill=skill,
        target=target,
        weapon_dice=weapon_dice,
        armour_dice=armour_dice,
        damage_type=damage_type,
        declaration_bonus=modifier,
        seed=seed,
    )
    if allies and result["roll"]["wyrd_die"] == "ill_omen":
        resolution.discard(result["proposal_id"])
        redirect_seed = None if seed is None else seed + 1
        result = resolution.propose(
            actor=shooter,
            mechanic="combat-attack",
            skill=skill,
            target=allies[0],
            weapon_dice=weapon_dice,
            armour_dice=armour_dice,
            damage_type=damage_type,
            declaration_bonus=modifier,
            seed=redirect_seed,
        )
    return result
