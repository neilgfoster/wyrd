# Contract: `wyrd.entity`

This is a library, not a network service — its "contract" is the public function surface
`engine/wyrd/entity.py` exposes, matching the shape `character.py`/`party.py` already use (plain
functions over plain dicts, no classes, standard library only).

```python
ENTITY_TYPES = (
    "character", "place", "organisation", "arc", "beat",
    "creature", "item", "tracker", "thread", "lore",
)
RECURSIVE_TYPES = ("place", "organisation", "arc")
STATUSES = ("stub", "drafted", "complete")

def validate(frontmatter: dict) -> dict:
    """Check an entity's frontmatter against the common schema and its type's additional fields.

    Returns {"valid": True} or {"valid": False, "error": "<which field, missing or invalid>"}.
    Never raises for a malformed but well-typed mapping; raises only on structurally invalid
    input (e.g. frontmatter is not a dict). Delegates to state.parse_entity's frontmatter for
    file-level parsing -- this function operates on the already-parsed mapping.
    """

def load(path) -> dict:
    """Read one entity file (via state.load_entity), validate it, and return its frontmatter.

    Raises state.StateError naming the file and the specific problem if either the file-level
    parse or validate() fails.
    """

def resolve_wikilink(value: str) -> str:
    """Strip a "[[id]]" wrapper to the bare id; returns the value unchanged if not wrapped."""

def children_of(entity_id: str, entities: dict[str, dict]) -> list[str]:
    """Every id in `entities` whose (resolved) `parent` is `entity_id`, via reverse lookup."""

def check_containment(entities: dict[str, dict]) -> dict:
    """Walk every entity's `parent` chain in `entities` (id -> frontmatter).

    Returns {"valid": True} or {"valid": False, "cycle": [<ids in the cycle>]} for the first
    cycle found. A missing/None parent is a root and never contributes to a cycle.
    """

def unresolved_references(entities: dict[str, dict]) -> list[dict]:
    """Every wikilink-style reference (parent, links, connections.to, allegiances, cast,
    members, based_at, ...) in `entities` whose target id is absent from `entities`.

    Returns a list of {"entity": <id>, "field": <field path>, "target": <unresolved id>}.
    """

def load_set(paths) -> dict[str, dict]:
    """Load and validate every entity file in `paths`, keyed by id.

    Raises state.StateError on the first file-level or schema failure, naming the file. Does
    not itself call check_containment/unresolved_references -- those are separate calls so a
    caller can choose whether to treat either as fatal.
    """
```

No HTTP/CLI surface is added by this feature; `engine/wyrd/client.py`'s verb catalog is untouched
unless a future feature exposes entity operations as an MCP tool.
