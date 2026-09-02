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

A combat scene is chronicle-scoped, not per-entity (specs/086-turn-order-round-structure/spec.md
Assumptions) -- it lives under a `combat` key in the same chronicle state `state.py` already
reads/writes atomically.

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
    "ambush": bool (default False)}}`.

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
    scene = {
        "sides": normalized_sides,
        "round": 1,
        "first_actor": first_actor,
        "engaged": [],
        "acted": [],
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
    seed: int | None = None,
    state_path: pathlib.Path = state.DEFAULT_STATE_PATH,
) -> dict:
    """Resolve a ranged `combat-attack`, applying whichever of the two named difficulty rows
    (`ranged_attack_difficulty`) applies, through `resolution.propose`'s own `declaration_bonus`
    channel. If the target is engaged with an ally (not the shooter) and the resulting roll's
    own Wyrd die reads Ill Omen, the shot is redirected: the original proposal is discarded and
    a fresh one, identical except for its target, is raised against the ally instead
    (docs/design/03-rules.md: "an Ill Omen on the shot means the ally is hit instead").
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
            declaration_bonus=modifier,
            seed=redirect_seed,
        )
    return result
