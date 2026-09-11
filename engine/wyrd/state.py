"""Chronicle state: atomic save/load, no third-party YAML dependency.

docs/design/01-principles.md principle 2: persist before narrate. A write must complete --
old or new state fully intact -- before any narration step runs, and a crash mid-write must
never leave a partially-written, unparseable file (docs/design/27-tooling.md sections 1-2).

The original minimal scaffold (specs/075-engine-scaffolding/data-model.md) carried only
`schema_version` and `last_roll`; this module's read/write contract does not change to
accommodate a larger schema -- it just carries whatever mapping it is given. The full
chronicle.yaml schema (docs/design/22-state.md, specs/122-chronicle-yaml-schema) -- engine/
setting version pins, calendar/era/sessions/danger_rating, an append-only migrations log, the
bootstrap intent block, and an opaque `pending` marker -- is layered on top via
`default_chronicle_state`/`validate_chronicle`/`load_chronicle`/`save_chronicle`/
`append_migration` below, still using the same generic `save`/`load`.

The reader below is a restricted YAML subset -- nested mappings, scalars, `null` -- sufficient
for this shape. It follows the same restricted-subset approach as tools/check_bestiary.py's
reader (docs/design/02-architecture.md: "parsed by a small internal reader"), written separately
here rather than imported from tools/, since engine/ is the shipped engine and tools/ is
repository-maintenance scripts -- the two must not depend on each other.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import os
import pathlib
import re
import tempfile

DEFAULT_STATE_PATH = pathlib.Path("chronicle_state.yaml")
DEFAULT_CHRONICLE_PATH = pathlib.Path("chronicle.yaml")

_SCHEMA_VERSION = 1

_MIGRATION_CLASSES = frozenset({"additive", "tuning", "structural", "behavioural"})

#: docs/design/23-chronicle-bootstrap.md: "How lethal? Sets starting Fate, and whether the
#: Aftermath table's death rows are closed" -- the same vocabulary `creation.MORTALITY_FATE`
#: and `resolution.MORTALITY_LEVELS` already use. Declared independently here rather than
#: imported (state.py -> creation.py would cycle via character.py), matching resolution.py's
#: own existing independent declaration of the same three-value set (#369).
_LETHALITY_LEVELS = frozenset({"low", "standard", "high"})

_INTENT_DEFAULTS = {
    "about": None,
    "avoid": [],
    "session_length": 20,
    "lethality": "standard",
    "world_acts_offstage": True,
}

_CHRONICLE_REQUIRED_FIELDS = (
    "schema_version",
    "name",
    "engine",
    "setting",
    "calendar",
    "sessions",
    "danger_rating",
)


class StateError(Exception):
    """A state file exists but could not be read as valid chronicle state."""


def _dump_scalar(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return str(value)


def _dump_block(data, indent: int, lines: list[str]) -> None:
    pad = " " * indent
    if isinstance(data, dict):
        if not data:
            lines.append(f"{pad}{{}}")
            return
        for key, value in data.items():
            if isinstance(value, (dict, list)) and value:
                lines.append(f"{pad}{key}:")
                _dump_block(value, indent + 2, lines)
            elif isinstance(value, dict):
                lines.append(f"{pad}{key}: {{}}")
            elif isinstance(value, list):
                lines.append(f"{pad}{key}: []")
            else:
                lines.append(f"{pad}{key}: {_dump_scalar(value)}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item:
                # First key inline after "- ", remaining keys indented two further -- the
                # conventional list-of-mappings style, matching what the reader below expects
                # (tools/check_bestiary.py's reader already relies on this same shape).
                item_lines: list[str] = []
                _dump_block(item, indent + 2, item_lines)
                first, *rest = item_lines
                lines.append(f"{pad}- {first[indent + 2 :]}")
                lines.extend(rest)
            else:
                lines.append(f"{pad}- {_dump_scalar(item)}")
    else:
        lines.append(f"{pad}{_dump_scalar(data)}")


def dump_yaml(data: dict) -> str:
    """Serialize a mapping to this feature's restricted YAML subset."""
    lines: list[str] = []
    _dump_block(data, 0, lines)
    return "\n".join(lines) + "\n"


def _scalar(text: str):
    text = text.strip()
    if text in ("true", "false"):
        return text == "true"
    if text in ("null", "~", ""):
        return None
    if re.fullmatch(r"[+-]?\d+", text):
        return int(text)
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    if text.startswith("[") and text.endswith("]"):
        return _flow_list(text[1:-1])
    if text.startswith("{") and text.endswith("}"):
        return _flow_mapping(text[1:-1])
    return text


def _flow_list(inner: str) -> list:
    """Parse a flow-style sequence of scalars, e.g. `[taint, trauma]`. No nested flow
    collections -- an override block's `disable:` list is the only user of this shape, and it
    is always a flat list of names."""
    inner = inner.strip()
    if not inner:
        return []
    return [_scalar(item) for item in inner.split(",")]


def _flow_mapping(inner: str) -> dict:
    """Parse a flow-style mapping of scalar keys to scalar values, e.g. `{taint: shadow}`. No
    nested flow collections -- see `_flow_list`."""
    inner = inner.strip()
    if not inner:
        return {}
    mapping: dict = {}
    for item in inner.split(","):
        key, _, val = item.partition(":")
        mapping[key.strip()] = _scalar(val)
    return mapping


def _parse_block(lines: list[tuple[int, int, str]], start: int, indent: int):
    """Parse one block (a mapping or a list) at the given indentation.

    A list item may be a scalar (`- value`) or a mapping whose first key sits inline after
    the dash and whose remaining keys are indented two further (`- id: x\\n    effect: ...`)
    -- the same shape tools/check_bestiary.py's reader already relies on.
    """
    i = start
    items: list = []
    mapping: dict = {}
    while i < len(lines):
        lineno, ind, text = lines[i]
        if ind < indent:
            break
        if ind > indent:
            raise StateError(f"line {lineno}: unexpected indentation")
        if items and not text.startswith("- "):
            # A mapping sitting at its parent key's own indentation ends where a sequence's
            # sibling key would begin -- without this a following key would be read as part
            # of the list.
            break
        if text == "{}":
            i += 1
            continue
        if text.startswith("- "):
            rest = text[2:].strip()
            if ":" in rest and not rest.startswith(('"', "'")):
                key, _, val = rest.partition(":")
                sub_lines = [(lineno, indent + 2, f"{key.strip()}:{val}")]
                j = i + 1
                while j < len(lines) and lines[j][1] > indent:
                    sub_lines.append(lines[j])
                    j += 1
                value, _ = _parse_block(sub_lines, 0, indent + 2)
                items.append(value)
                i = j
                continue
            items.append(_scalar(rest))
            i += 1
            continue
        if ":" not in text:
            raise StateError(f"line {lineno}: expected 'key: value' or '- item'")
        key, _, val = text.partition(":")
        key = key.strip()
        val = val.strip()
        if val:
            if val == "{}":
                mapping[key] = {}
            elif val == "[]":
                mapping[key] = []
            else:
                mapping[key] = _scalar(val)
            i += 1
            continue
        j = i + 1
        if j < len(lines) and lines[j][1] > indent:
            value, j = _parse_block(lines, j, lines[j][1])
            mapping[key] = value
        elif j < len(lines) and lines[j][1] == indent and lines[j][2].startswith("- "):
            # A sequence may share its parent key's own indentation rather than being
            # indented under it -- both are legal YAML.
            value, j = _parse_block(lines, j, indent)
            mapping[key] = value
        else:
            mapping[key] = None
        i = j
    if items and mapping:
        raise StateError("a block is either a list or a mapping, never both")
    return (items if items else mapping), i


def parse_yaml(text: str) -> dict:
    """Parse this feature's restricted YAML subset back into a mapping."""
    raw_lines = text.splitlines()
    lines: list[tuple[int, int, str]] = []
    for lineno, line in enumerate(raw_lines, 1):
        if not line.strip():
            continue
        lines.append((lineno, len(line) - len(line.lstrip()), line.strip()))
    if not lines:
        return {}
    try:
        value, _ = _parse_block(lines, 0, lines[0][1])
    except StateError:
        raise
    except Exception as exc:  # pragma: no cover - defensive, see FR-008
        raise StateError(f"could not parse state: {exc}") from exc
    return value


def default_state() -> dict:
    """The empty chronicle state shape a fresh chronicle (or a missing file) starts from."""
    return {"schema_version": _SCHEMA_VERSION, "last_roll": None}


def write_text_atomic(text: str, path: pathlib.Path) -> None:
    """Write `text` to `path`, atomically -- shared by `save`, `save_entity` and `save_chronicle`
    (FR-007), and exposed publicly (specs/123-chronicle-load-tiers) for `recap.md`'s regeneration
    to reuse rather than duplicating a fourth atomic-write implementation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent) or ".", prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)
        raise


def save(state: dict, path: pathlib.Path = DEFAULT_STATE_PATH) -> None:
    """Write `state` to `path`, atomically.

    Writes to a temp file in the same directory, then `os.replace()`s it onto `path`. A
    reader of `path` never observes a partially-written file: it is either the previous
    fully-valid state, or this fully-valid state (FR-007).
    """
    path = pathlib.Path(path)
    write_text_atomic(dump_yaml(state), path)


_FRONTMATTER_DELIMITER = "---"


def parse_entity(text: str) -> tuple[dict, str]:
    """Split an entity file into its YAML frontmatter and its markdown body.

    docs/design/25-entities.md: "a markdown file with YAML frontmatter. The frontmatter is
    the schema, the body is the prose." Only the first two `---`-only lines delimit the
    frontmatter block; any further `---` line belongs to the body untouched (e.g. a
    horizontal rule in prose).
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != _FRONTMATTER_DELIMITER:
        raise StateError("entity file must open with a '---' frontmatter delimiter")
    for i in range(1, len(lines)):
        if lines[i].strip() == _FRONTMATTER_DELIMITER:
            frontmatter_text = "".join(lines[1:i])
            body = "".join(lines[i + 1 :])
            return parse_yaml(frontmatter_text), body
    raise StateError("entity file is missing its closing '---' frontmatter delimiter")


def dump_entity(frontmatter: dict, body: str = "") -> str:
    """Serialize a frontmatter mapping and a body back into an entity file."""
    return f"{_FRONTMATTER_DELIMITER}\n{dump_yaml(frontmatter)}{_FRONTMATTER_DELIMITER}\n{body}"


def save_entity(frontmatter: dict, body: str, path: pathlib.Path) -> None:
    """Write an entity file (frontmatter + body) to `path`, atomically."""
    path = pathlib.Path(path)
    write_text_atomic(dump_entity(frontmatter, body), path)


def load_entity(path: pathlib.Path) -> tuple[dict, str]:
    """Read an entity file from `path`, returning its (frontmatter, body).

    Raises `StateError` naming the file if it does not exist or fails to parse -- there is
    no "default empty entity" the way `load()` has a default chronicle state, since an
    entity file is expected to already exist before something asks to load it.
    """
    path = pathlib.Path(path)
    if not path.exists():
        raise StateError(f"{path}: no such entity file")
    text = path.read_text(encoding="utf-8")
    try:
        return parse_entity(text)
    except StateError as exc:
        raise StateError(f"{path}: {exc}") from exc


def load(path: pathlib.Path = DEFAULT_STATE_PATH) -> dict:
    """Read chronicle state from `path`.

    If `path` does not exist yet, returns the default empty state rather than failing --
    the first-ever save has nothing to load beforehand. If `path` exists but fails to
    parse, raises `StateError` naming the file and the failure (FR-008) rather than
    silently discarding or guessing at the data.
    """
    path = pathlib.Path(path)
    if not path.exists():
        return default_state()
    text = path.read_text(encoding="utf-8")
    try:
        return parse_yaml(text)
    except StateError as exc:
        raise StateError(f"{path}: {exc}") from exc


def default_chronicle_state(
    *,
    name: str,
    engine_repo: str,
    engine_version: str,
    setting_repo: str,
    setting_version: str,
) -> dict:
    """The full chronicle.yaml shape a fresh chronicle starts from (docs/design/22-state.md).

    `created_under` starts equal to `version` for both engine and setting -- a chronicle
    begins under whatever it begins under (FR-002).
    """
    return {
        "schema_version": _SCHEMA_VERSION,
        "name": name,
        "engine": {
            "repo": engine_repo,
            "version": engine_version,
            "created_under": engine_version,
        },
        "setting": {
            "repo": setting_repo,
            "version": setting_version,
            "created_under": setting_version,
        },
        "calendar": {"year": 0, "month": None, "day": 0},
        "era": None,
        "eras": [],
        "era_crossings": [],
        "sessions": 0,
        "danger_rating": 2,
        "migrations": [],
        "intent": dict(_INTENT_DEFAULTS),
        "pending": None,
    }


def validate_chronicle(state: dict, previous_migrations: list | None = None) -> dict:
    """Validate a chronicle state against docs/design/22-state.md's schema.

    Fills any absent optional field with its documented default (FR-009) and returns the
    (possibly filled-in) mapping. Raises `StateError` naming the specific field/rule violated
    on any failure -- a required field missing (FR-008), a negative `sessions`/
    `danger_rating` (FR-010), an out-of-vocabulary migration `class` (FR-005), or an edit/
    reorder of an already-saved migration entry when `previous_migrations` is given
    (FR-003/FR-004).
    """
    for field in _CHRONICLE_REQUIRED_FIELDS:
        if field not in state:
            raise StateError(f"chronicle state is missing required field {field!r}")

    result = dict(state)
    result.setdefault("era", None)
    result.setdefault("pending", None)
    result["eras"] = list(result.get("eras") or [])
    result["era_crossings"] = list(result.get("era_crossings") or [])
    result["migrations"] = list(result.get("migrations") or [])
    result["intent"] = {**_INTENT_DEFAULTS, **(result.get("intent") or {})}

    if result["intent"]["lethality"] not in _LETHALITY_LEVELS:
        raise StateError(
            f"intent.lethality {result['intent']['lethality']!r} is not one of "
            f"{sorted(_LETHALITY_LEVELS)}"
        )

    if result["sessions"] < 0:
        raise StateError(f"sessions must be non-negative, got {result['sessions']!r}")
    if result["danger_rating"] < 0:
        raise StateError(f"danger_rating must be non-negative, got {result['danger_rating']!r}")

    for i, entry in enumerate(result["migrations"]):
        entry_class = entry.get("class")
        if entry_class not in _MIGRATION_CLASSES:
            raise StateError(
                f"migrations[{i}].class {entry_class!r} is not one of {sorted(_MIGRATION_CLASSES)}"
            )

    if previous_migrations:
        prefix = result["migrations"][: len(previous_migrations)]
        if prefix != previous_migrations:
            for i, (old, new) in enumerate(zip(previous_migrations, prefix, strict=False)):
                if old != new:
                    raise StateError(
                        f"migrations[{i}] was edited or reordered -- "
                        "an already-appended migration entry is immutable"
                    )
            raise StateError(
                "migrations list no longer contains every previously-saved entry, in order"
            )

    return result


def append_migration(state: dict, entry: dict) -> dict:
    """Return a new state with `entry` appended to `state["migrations"]`.

    Does not mutate `state`'s own `migrations` list in place -- a caller holding a reference
    to the old list is unaffected. Raises `StateError` if `entry["class"]` is not one of the
    four allowed values (also re-checked by `validate_chronicle` at save time).
    """
    if entry.get("class") not in _MIGRATION_CLASSES:
        raise StateError(
            f"migration class {entry.get('class')!r} is not one of {sorted(_MIGRATION_CLASSES)}"
        )
    new_state = dict(state)
    new_state["migrations"] = [*state.get("migrations", []), entry]
    return new_state


def load_chronicle(path: pathlib.Path = DEFAULT_CHRONICLE_PATH) -> dict:
    """Read chronicle.yaml from `path`, validating its schema.

    Unlike `load()`, a missing file raises `StateError` naming the path -- a fresh
    chronicle's identity (`name`, `engine`, `setting`) cannot be invented by the loader; the
    caller must first `save_chronicle(default_chronicle_state(...), path)`.
    """
    path = pathlib.Path(path)
    if not path.exists():
        raise StateError(f"{path}: no such chronicle file")
    text = path.read_text(encoding="utf-8")
    try:
        raw = parse_yaml(text)
    except StateError as exc:
        raise StateError(f"{path}: {exc}") from exc
    try:
        return validate_chronicle(raw)
    except StateError as exc:
        raise StateError(f"{path}: {exc}") from exc


def save_chronicle(state: dict, path: pathlib.Path = DEFAULT_CHRONICLE_PATH) -> None:
    """Validate and write chronicle state to `path`, atomically.

    Validates first, comparing against the file's currently-saved migrations if it already
    exists (FR-003/FR-004) -- a rejected write never touches the file on disk.
    """
    path = pathlib.Path(path)
    previous_migrations = None
    if path.exists():
        previous_migrations = parse_yaml(path.read_text(encoding="utf-8")).get("migrations")
    validated = validate_chronicle(state, previous_migrations=previous_migrations)
    write_text_atomic(dump_yaml(validated), path)
