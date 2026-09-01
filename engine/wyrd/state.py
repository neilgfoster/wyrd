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
            else:
                scalar = "{}" if isinstance(value, (dict, list)) else _dump_scalar(value)
                lines.append(f"{pad}{key}: {scalar}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append(f"{pad}-")
                _dump_block(item, indent + 2, lines)
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
    i = start
    mapping: dict = {}
    while i < len(lines):
        lineno, ind, text = lines[i]
        if ind < indent:
            break
        if ind > indent:
            raise StateError(f"line {lineno}: unexpected indentation")
        if text == "{}":
            i += 1
            continue
        if ":" not in text:
            raise StateError(f"line {lineno}: expected 'key: value'")
        key, _, val = text.partition(":")
        key = key.strip()
        val = val.strip()
        if val:
            mapping[key] = None if val == "{}" else _scalar(val)
            i += 1
            continue
        j = i + 1
        if j < len(lines) and lines[j][1] > indent:
            value, j = _parse_block(lines, j, lines[j][1])
            mapping[key] = value
        else:
            mapping[key] = None
        i = j
    return mapping, i


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


def save(state: dict, path: pathlib.Path = DEFAULT_STATE_PATH) -> None:
    """Write `state` to `path`, atomically.

    Writes to a temp file in the same directory, then `os.replace()`s it onto `path`. A
    reader of `path` never observes a partially-written file: it is either the previous
    fully-valid state, or this fully-valid state (FR-007).
    """
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = dump_yaml(state)
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
