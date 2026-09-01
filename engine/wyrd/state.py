"""Chronicle state: atomic save/load, no third-party YAML dependency.

docs/design/01-principles.md principle 2: persist before narrate. A write must complete --
old or new state fully intact -- before any narration step runs, and a crash mid-write must
never leave a partially-written, unparseable file (docs/design/27-tooling.md sections 1-2).

This feature's state shape is deliberately minimal (specs/075-engine-scaffolding/data-model.md):
`schema_version` and `last_roll`. Later features extend the schema; this module's read/write
contract does not change to accommodate that -- it just carries whatever mapping it is given.

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

_SCHEMA_VERSION = 1


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
    return text


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


def _atomic_write_text(text: str, path: pathlib.Path) -> None:
    """Write `text` to `path`, atomically -- shared by `save` and `save_entity` (FR-007)."""
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
    _atomic_write_text(dump_yaml(state), path)


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
    _atomic_write_text(dump_entity(frontmatter, body), path)


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
