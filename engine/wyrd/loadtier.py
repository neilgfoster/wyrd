"""Chronicle load-tier resolution (always / on-demand / archival) and recap.md generation.

docs/design/22-state.md § Load policy: a three-tier scheme chosen entirely by query over the
entity set, never by a manifest, so the tier can't drift out of date. `entity.py` already gives
the loadable entity set (`load_set`) and per-entity resolution (`resolve_entity`); this module
adds what neither `entity.py` nor `session.py` provide -- the always-tier query itself (player
character, with-party companions, hot threads), on-demand fetch/search over the rest, and
`recap.md` regeneration. `session.py`'s `run_close` already leaves recap regeneration as an
injected zero-argument step, deliberately, pending this layer (see its own docstring) -- this
module is what a caller now wires into that step.

`log/` (the archival tier) needs no function here: it is reachable by ordinary file access and
deliberately never surfaced by either query below (docs/design/22-state.md).

Where and when the player character is, what changed this session, and the character's body/mind
state in one sentence are GM narrative judgment or diegetic renderings the engine does not
generate on its own (no field tracks "current location", and mapping raw taint/trauma to prose
would leak the exact numbers docs/design/13-diegesis.md forbids showing, and bake in a tone the
engine never owns) -- `generate_recap` takes these as caller-supplied text rather than inventing
them (specs/123-chronicle-load-tiers/research.md).

Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib
from collections.abc import Callable

from wyrd import state

_RECAP_PLACEHOLDER = "Not recorded."
_HOT_THREAD_COUNT = 3


def _is_player_character(frontmatter: dict) -> bool:
    return frontmatter.get("type") == "character" and frontmatter.get("role") == "player"


def _is_with_party_companion(frontmatter: dict) -> bool:
    return (
        frontmatter.get("type") == "character"
        and frontmatter.get("role") == "companion"
        and frontmatter.get("status") == "with-party"
    )


def _is_hot_thread(frontmatter: dict) -> bool:
    return frontmatter.get("type") == "thread" and (frontmatter.get("heat") or 0) >= 3


def always_tier(entities: dict[str, dict]) -> dict:
    """The always-loaded subset of `entities`, computed fresh -- no manifest.

    Returns `{"player_character": dict | None, "companions": dict[str, dict], "threads":
    dict[str, dict]}` (docs/design/22-state.md § Load policy). `chronicle.yaml` and `recap.md`
    are not represented here -- they are the two fixed per-chronicle files a caller always loads
    alongside this result, not entities to query (specs/123-chronicle-load-tiers/research.md).

    Raises `ValueError` if more than one entity carries `role: player` -- that is a data error
    this function is not positioned to arbitrate silently.
    """
    player_ids = [entity_id for entity_id, fm in entities.items() if _is_player_character(fm)]
    if len(player_ids) > 1:
        raise ValueError(f"more than one player character: {player_ids}")

    return {
        "player_character": entities[player_ids[0]] if player_ids else None,
        "companions": {
            entity_id: fm for entity_id, fm in entities.items() if _is_with_party_companion(fm)
        },
        "threads": {entity_id: fm for entity_id, fm in entities.items() if _is_hot_thread(fm)},
    }


def lookup(entity_id: str, entities: dict[str, dict]) -> dict | None:
    """An on-demand fetch by id -- the full frontmatter, or `None` if `entity_id` is absent."""
    return entities.get(entity_id)


def search(term: str, entities: dict[str, dict], bodies: dict[str, str] | None = None) -> list[str]:
    """On-demand search: ids (in `entities`' own order) whose frontmatter or body matches `term`.

    Case-insensitive substring match against every frontmatter value (stringified) and, when
    `bodies` supplies one for that id, the entity's body text. An empty `term` matches nothing --
    it is not treated as "everything".
    """
    if not term:
        return []
    needle = term.lower()
    matches = []
    for entity_id, frontmatter in entities.items():
        haystack = " ".join(str(value) for value in frontmatter.values())
        if bodies and entity_id in bodies:
            haystack += " " + bodies[entity_id]
        if needle in haystack.lower():
            matches.append(entity_id)
    return matches


def _hottest_open_threads(entities: dict[str, dict], count: int = _HOT_THREAD_COUNT) -> list[dict]:
    open_threads = [
        fm for fm in entities.values() if fm.get("type") == "thread" and fm.get("status") == "open"
    ]
    open_threads.sort(key=lambda fm: (-fm.get("heat", 0), fm["id"]))
    return open_threads[:count]


def generate_recap(
    entities: dict[str, dict],
    chronicle: dict,
    *,
    where: str | None = None,
    changes: list[str] | None = None,
    body_mind: str | None = None,
) -> str:
    """Regenerate `recap.md`'s text (docs/design/22-state.md § `recap.md`), ~200 words.

    `where`, `changes` and `body_mind` are caller-supplied (module docstring: this is GM/
    narrative content, not derived from raw tracked fields) -- each falls back to a short
    placeholder when omitted, so the document stays well-formed rather than failing outright.
    The three hottest threads and who's-present are computed directly from `entities`.

    `chronicle` names which chronicle and setting this recap belongs to (docs/design/21-parallel-
    chronicles.md: "a session loads exactly one chronicle and one setting, and says which in the
    recap") -- `name` and `setting.repo`, each independently falling back to the same placeholder
    convention when absent (#363). It is otherwise reserved for calendar/session context a future
    caller may add to the "where and when" line.
    """
    chronicle_name = chronicle.get("name") or _RECAP_PLACEHOLDER
    setting_name = (chronicle.get("setting") or {}).get("repo") or _RECAP_PLACEHOLDER

    tier = always_tier(entities)
    companion_names = [fm.get("name", entity_id) for entity_id, fm in tier["companions"].items()]
    hottest = _hottest_open_threads(entities)
    thread_lines = [f"- {fm.get('name', fm['id'])} (heat {fm.get('heat', 0)})" for fm in hottest]

    lines = [
        "# Recap",
        "",
        "## Chronicle",
        f"{chronicle_name} in {setting_name}",
        "",
        "## Where and when",
        where or _RECAP_PLACEHOLDER,
        "",
        "## Hottest threads",
        *(thread_lines or [_RECAP_PLACEHOLDER]),
        "",
        "## What changed",
        "; ".join(changes) if changes else _RECAP_PLACEHOLDER,
        "",
        "## Body and mind",
        body_mind or _RECAP_PLACEHOLDER,
        "",
        "## Who's present",
        ", ".join(companion_names) if companion_names else "no one",
        "",
    ]
    return "\n".join(lines)


def recap_close_step(
    entities: dict[str, dict],
    chronicle: dict,
    recap_path: pathlib.Path,
    **recap_kwargs,
) -> Callable[[], None]:
    """A zero-argument callable suitable for `session.run_close`'s `steps` list.

    Regenerates `recap.md` (via `generate_recap`) and writes it atomically to `recap_path`
    (via `state.write_text_atomic`) when called -- this is the "recap regeneration" step
    `session.run_close`'s own docstring names as depending on this layer, which now exists.
    `recap_kwargs` is forwarded to `generate_recap` (`where`, `changes`, `body_mind`).
    """

    def step() -> None:
        text = generate_recap(entities, chronicle, **recap_kwargs)
        state.write_text_atomic(text, recap_path)

    return step
