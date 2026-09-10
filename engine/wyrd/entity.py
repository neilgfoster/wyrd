"""Entity file format: common schema, the ten types, containment and connections.

docs/design/25-entities.md: every fact Wyrd knows about a world is a markdown file with YAML
frontmatter. `engine/wyrd/state.py` already implements the file-level split (frontmatter/body)
and atomic I/O via `parse_entity`/`dump_entity`/`save_entity`/`load_entity` -- this module reuses
those directly and adds the layer `state.py` deliberately leaves out: common-schema and per-type
validation, containment resolution (the `parent` tree, acyclic, children by reverse lookup),
connection-graph loading (free, directional, conditional, may loop, `hidden` preserved), and --
docs/design/25-entities.md's "chronicle overlay" section -- resolving a setting entity plus its
chronicle's overlay into the effective entity the rest of the engine operates on.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import pathlib

from wyrd import state

ENTITY_TYPES = (
    "character",
    "place",
    "organisation",
    "arc",
    "beat",
    "creature",
    "item",
    "tracker",
    "thread",
    "lore",
)

RECURSIVE_TYPES = ("place", "organisation", "arc")

STATUSES = ("stub", "drafted", "complete")

_ROLES = ("nemesis", "ally", "companion", "bystander", "authority", "quarry")
_DISPOSITIONS = ("ally", "wary", "hostile", "hunting", "unaware")
_PLACE_SCALES = ("world", "region", "settlement", "district", "building", "room")
_ORG_SCALES = ("institution", "order", "chapter", "cell")
_TRACKER_KINDS = ("clock", "meter", "state")

# Required common-schema fields, per docs/design/25-entities.md.
_REQUIRED_COMMON_FIELDS = ("id", "type", "name", "setting", "status")

# Type-specific enum fields: field name -> the closed set of values it may take.
_TYPE_ENUM_FIELDS: dict[str, dict[str, tuple[str, ...]]] = {
    "character": {"role": _ROLES, "disposition": _DISPOSITIONS},
    "place": {"scale": _PLACE_SCALES},
    "organisation": {"scale": _ORG_SCALES},
    "tracker": {"kind": _TRACKER_KINDS},
}

_CONNECTION_REQUIRED_FIELDS = ("to",)
_CONNECTION_OPTIONAL_FIELDS = ("via", "cost", "requires", "hidden")

# docs/design/18-arcs-and-beats.md "Conversion is lazy": each sources[] entry records provenance.
# `pages` is only required once an entity has moved past `stub` -- a stub records where it came
# from, a converted beat additionally records what pages it was drawn from.
_SOURCE_REQUIRED_FIELDS = ("work", "licence", "path")
_SOURCE_OPTIONAL_FIELDS = ("pages",)

# The two legal forward moves through STATUSES; anything else (staying put, skipping a state,
# moving backward) is rejected by legal_transition().
_LEGAL_TRANSITIONS = {("stub", "drafted"), ("drafted", "complete")}

# Fields whose value (or whose items) may be `[[wikilink]]`-wrapped references to another
# entity's id, checked by unresolved_references().
_REFERENCE_FIELDS = ("parent", "links", "allegiances", "cast", "members", "based_at")

# An overlay file's own bookkeeping fields -- never part of the effective entity produced by
# resolve_entity(): `id` there names the overlay file itself, not the entity it resolves to, and
# `overlay_of` is purely the join key to the setting entity.
_OVERLAY_BOOKKEEPING_FIELDS = ("id", "overlay_of")


def resolve_wikilink(value: str) -> str:
    """Strip a "[[id]]" wrapper to the bare id; returns `value` unchanged if not wrapped."""
    if isinstance(value, str) and value.startswith("[[") and value.endswith("]]"):
        return value[2:-2]
    return value


def _validate_connection(connection: dict) -> str | None:
    if not isinstance(connection, dict):
        return "connection entry is not a mapping"
    for field in _CONNECTION_REQUIRED_FIELDS:
        if not connection.get(field):
            return f"connection missing required field '{field}'"
    for field in connection:
        if field not in _CONNECTION_REQUIRED_FIELDS and field not in _CONNECTION_OPTIONAL_FIELDS:
            return f"connection has unexpected field '{field}'"
    return None


def validate(frontmatter: dict) -> dict:
    """Check an entity's frontmatter against the common schema and its type's additional fields.

    Returns {"valid": True} or {"valid": False, "error": "<which field, missing or invalid>"}.
    Never raises for a malformed but well-typed mapping; raises only on structurally invalid
    input (e.g. frontmatter is not a dict).
    """
    if not isinstance(frontmatter, dict):
        raise TypeError("frontmatter must be a mapping")

    for field in _REQUIRED_COMMON_FIELDS:
        if not frontmatter.get(field):
            return {"valid": False, "error": f"missing required field '{field}'"}

    entity_type = frontmatter["type"]
    if entity_type not in ENTITY_TYPES:
        return {"valid": False, "error": f"unknown type '{entity_type}'"}

    status = frontmatter["status"]
    if status not in STATUSES:
        return {"valid": False, "error": f"invalid status '{status}'"}

    for field, allowed in _TYPE_ENUM_FIELDS.get(entity_type, {}).items():
        value = frontmatter.get(field)
        if value is not None and value not in allowed:
            return {"valid": False, "error": f"invalid {field} '{value}' for type '{entity_type}'"}

    if entity_type == "place":
        for connection in frontmatter.get("connections", []) or []:
            problem = _validate_connection(connection)
            if problem:
                return {"valid": False, "error": problem}

    return {"valid": True}


def validate_source(source: dict, *, status: str) -> dict:
    """Check one `sources[]` entry against its field schema.

    Requires `work`, `licence`, and `path`; requires `pages` too once `status` is `"drafted"` or
    `"complete"` -- a stub records where it came from, a converted beat additionally records what
    pages it was drawn from. Rejects any field outside `{work, pages, licence, path}`. Returns
    `{"valid": True}` or `{"valid": False, "error": "..."}` naming the specific field.
    """
    if not isinstance(source, dict):
        return {"valid": False, "error": "source entry is not a mapping"}

    required = _SOURCE_REQUIRED_FIELDS
    if status in ("drafted", "complete"):
        required += ("pages",)

    for field in required:
        if not source.get(field):
            return {"valid": False, "error": f"source missing required field '{field}'"}

    for field in source:
        if field not in _SOURCE_REQUIRED_FIELDS and field not in _SOURCE_OPTIONAL_FIELDS:
            return {"valid": False, "error": f"source has unexpected field '{field}'"}

    return {"valid": True}


def check_stub_sufficiency(frontmatter: dict, body: str = "") -> dict:
    """Check that a `status: stub` entity carries enough to be selected, per 18-arcs-and-beats.md.

    A summary, tags, and a sourced path -- "enough to be selected and nothing more." The summary
    is the entity's body text (18-arcs-and-beats.md's stub example carries it below the
    frontmatter, not as a frontmatter field), so `body` is passed separately -- matching
    `state.load_entity`'s `(frontmatter, body)` shape rather than folding it into `frontmatter`.
    Entities whose status is not `stub` are exempt: this is a selectability guarantee for stubs
    specifically, not a general completeness check (that is `validate()`'s job).

    Returns `{"valid": True}` or `{"valid": False, "error": "..."}` naming the first unmet
    requirement, checked in the order summary -> tags -> sources[].path.
    """
    if frontmatter.get("status") != "stub":
        return {"valid": True}

    if not body.strip():
        return {"valid": False, "error": "stub missing required summary body text"}

    if not frontmatter.get("tags"):
        return {"valid": False, "error": "stub missing required field 'tags'"}

    sources = frontmatter.get("sources") or []
    if not any(isinstance(entry, dict) and entry.get("path") for entry in sources):
        return {"valid": False, "error": "stub missing a sources[] entry with a 'path'"}

    return {"valid": True}


def legal_transition(from_status: str, to_status: str) -> dict:
    """Check whether moving an entity from `from_status` to `to_status` is a legal transition.

    Only `stub` -> `drafted` and `drafted` -> `complete` are legal. Returns `{"valid": True}` or
    `{"valid": False, "error": "..."}` distinguishing "skips a state" (moving forward past an
    intermediate status), "moves backward" (moving to an earlier status), and "not a transition"
    (an unrecognised status, or `from_status == to_status`).
    """
    if (from_status, to_status) in _LEGAL_TRANSITIONS:
        return {"valid": True}

    if from_status not in STATUSES or to_status not in STATUSES:
        return {"valid": False, "error": f"'{from_status}' -> '{to_status}' is not a transition"}

    from_index = STATUSES.index(from_status)
    to_index = STATUSES.index(to_status)

    if to_index == from_index:
        return {"valid": False, "error": f"'{from_status}' -> '{to_status}' is not a transition"}
    if to_index < from_index:
        return {"valid": False, "error": f"'{from_status}' -> '{to_status}' moves backward"}
    return {"valid": False, "error": f"'{from_status}' -> '{to_status}' skips a state"}


def status_counts(entities: dict[str, dict]) -> dict:
    """Report the stub/drafted/complete mix over `entities`, for `doctor`-style reporting.

    Returns `{status: {"count": int, "proportion": float}}` for each of `STATUSES`. An empty
    `entities` reports zero counts and zero proportions rather than raising.
    """
    total = len(entities)
    counts = dict.fromkeys(STATUSES, 0)
    for frontmatter in entities.values():
        status = frontmatter.get("status")
        if status in counts:
            counts[status] += 1

    return {
        status: {
            "count": count,
            "proportion": (count / total) if total else 0.0,
        }
        for status, count in counts.items()
    }


def load(path: pathlib.Path) -> dict:
    """Read one entity file (via `state.load_entity`), validate it, and return its frontmatter.

    Raises `state.StateError` naming the file and the specific problem if either the file-level
    parse or `validate()` fails.
    """
    path = pathlib.Path(path)
    frontmatter, _body = state.load_entity(path)
    result = validate(frontmatter)
    if not result["valid"]:
        raise state.StateError(f"{path}: {result['error']}")
    return frontmatter


def children_of(entity_id: str, entities: dict[str, dict]) -> list[str]:
    """Every id in `entities` whose (resolved) `parent` is `entity_id`, via reverse lookup."""
    children = []
    for candidate_id, frontmatter in entities.items():
        parent = frontmatter.get("parent")
        if parent is not None and resolve_wikilink(parent) == entity_id:
            children.append(candidate_id)
    return children


def check_containment(entities: dict[str, dict]) -> dict:
    """Walk every entity's `parent` chain in `entities` (id -> frontmatter).

    Returns {"valid": True} or {"valid": False, "cycle": [<ids in the cycle>]} for the first
    cycle found. A missing/None parent is a root and never contributes to a cycle.
    """
    for start_id in entities:
        visited: list[str] = []
        current = start_id
        seen = set()
        while current is not None and current in entities:
            if current in seen:
                cycle_start = visited.index(current)
                return {"valid": False, "cycle": visited[cycle_start:] + [current]}
            seen.add(current)
            visited.append(current)
            parent = entities[current].get("parent")
            current = resolve_wikilink(parent) if parent is not None else None
    return {"valid": True}


def unresolved_references(entities: dict[str, dict]) -> list[dict]:
    """Every wikilink-style reference in `entities` whose target id is absent from `entities`.

    Covers `parent`, `links`, `connections[].to`, `allegiances`, `cast`, `members`, `based_at`.
    Returns a list of {"entity": <id>, "field": <field path>, "target": <unresolved id>}.
    """
    problems: list[dict] = []

    def _check(entity_id: str, field: str, value) -> None:
        target = resolve_wikilink(value)
        if isinstance(target, str) and target and target not in entities:
            problems.append({"entity": entity_id, "field": field, "target": target})

    for entity_id, frontmatter in entities.items():
        for field in _REFERENCE_FIELDS:
            value = frontmatter.get(field)
            if value is None:
                continue
            if isinstance(value, list):
                for item in value:
                    _check(entity_id, field, item)
            else:
                _check(entity_id, field, value)

        for i, connection in enumerate(frontmatter.get("connections", []) or []):
            if isinstance(connection, dict) and connection.get("to"):
                _check(entity_id, f"connections[{i}].to", connection["to"])

    return problems


def resolve_entity(
    entity_id: str,
    setting_entities: dict[str, dict],
    overlays: dict[str, dict],
    setting_bodies: dict[str, str] | None = None,
    overlay_bodies: dict[str, str] | None = None,
) -> tuple[dict, str]:
    """Resolve `setting entity + overlay = effective entity`, per 25-entities.md.

    `setting_entities` and `overlays` are both keyed by the *setting* entity id -- `overlays`
    keyed by each overlay's `overlay_of`, not the overlay file's own `id` (an overlay may name
    itself anything; it is the join key that matters). `setting_bodies`/`overlay_bodies` are the
    corresponding entity-file bodies, keyed the same way; omit either mapping if bodies are not
    tracked by the caller (an absent body behaves as empty everywhere below).

    Returns `(frontmatter, body)`, matching `state.load_entity`'s shape.

    With no overlay for `entity_id`, returns a shallow copy of the setting entity's frontmatter
    (never the same dict object, so a caller cannot mutate the stored setting entity through the
    result) and its body unchanged.

    With an overlay, every field present in the overlay (other than the bookkeeping fields `id`
    and `overlay_of`) overrides the setting entity's value for that field -- including introducing
    a field the setting entity never had (promotion); every field absent from the overlay falls
    through unchanged. The overlay body replaces the setting body if non-empty, else the setting
    body is used. The merged frontmatter is validated with `validate()`; a failure raises
    `state.StateError` naming `entity_id`.

    Raises `state.StateError` if `entity_id` is not in `setting_entities` -- naming the dangling
    overlay's target when some overlay claims that id (an overlay referencing a setting entity
    that does not exist), or simply the unknown id otherwise.
    """
    overlay = overlays.get(entity_id)

    if entity_id not in setting_entities:
        if overlay is not None:
            raise state.StateError(
                f"overlay '{overlay.get('id', entity_id)}': overlay_of '{entity_id}' "
                "does not name a known setting entity"
            )
        raise state.StateError(f"'{entity_id}' is not a known setting entity")

    setting_frontmatter = setting_entities[entity_id]
    setting_body = (setting_bodies or {}).get(entity_id, "")

    if overlay is None:
        return dict(setting_frontmatter), setting_body

    overlay_fields = {
        field: value for field, value in overlay.items() if field not in _OVERLAY_BOOKKEEPING_FIELDS
    }
    frontmatter = {**setting_frontmatter, **overlay_fields}
    overlay_body = (overlay_bodies or {}).get(entity_id, "")
    body = overlay_body if overlay_body else setting_body

    result = validate(frontmatter)
    if not result["valid"]:
        raise state.StateError(f"'{entity_id}' (overlay resolved): {result['error']}")

    return frontmatter, body


def load_set(paths) -> dict[str, dict]:
    """Load and validate every entity file in `paths`, keyed by id.

    Raises `state.StateError` on the first file-level or schema failure, naming the file. Does
    not itself call `check_containment`/`unresolved_references` -- those are separate calls so a
    caller can choose whether to treat either as fatal.
    """
    entities: dict[str, dict] = {}
    for path in paths:
        frontmatter = load(path)
        entities[frontmatter["id"]] = frontmatter
    return entities
