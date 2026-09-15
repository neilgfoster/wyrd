"""The Archival memory tier: `log/<chronicle-name>.jsonl`, read by `wyrd log` (#402).

docs/design/02-architecture.md: "Archival -- log/. Rarely read; exists so the history is
recoverable and auditable. wyrd log --last N or wyrd log --since <beat> reads it, in beat
order." `loadtier.py` deliberately leaves this tier unread ("reachable by ordinary file access
... deliberately never surfaced by either query" -- its own docstring), since neither of its
two queries needs it; this module is the minimal reader/writer that verb actually needs.

One record per resolved beat, JSON Lines, each shaped exactly like `session.narrate_beat`'s own
return value (`{"beat_id", "mode", "resolved_at"}`) -- reusing that shape rather than inventing a
second, competing one (specs/153-chronicle-cli-verbs/research.md). Entries are appended in
resolution order, which is already beat order, so no separate sort is needed on read.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import json
import pathlib

from wyrd import state

_LOG_DIRNAME = "log"


def _log_path(chronicle_dir: pathlib.Path, chronicle_name: str) -> pathlib.Path:
    return pathlib.Path(chronicle_dir) / _LOG_DIRNAME / f"{chronicle_name}.jsonl"


def append_beat(chronicle_dir: pathlib.Path, chronicle_name: str, record: dict) -> None:
    """Append one beat-resolution `record` to this chronicle's live log file, atomically.

    `record` is expected to be shaped like `session.narrate_beat`'s return value, but this
    function does not itself validate that shape -- it is a plain append, matching `log/`'s own
    "rarely read, exists so history is auditable" role rather than a second schema enforcer.
    """
    path = _log_path(chronicle_dir, chronicle_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    updated = existing + json.dumps(record) + "\n"
    state.write_text_atomic(updated, path)


def read_log(
    chronicle_dir: pathlib.Path,
    chronicle_name: str,
    *,
    last: int | None = None,
    since: str | None = None,
) -> list[dict]:
    """Read this chronicle's live log file, filtered by exactly one of `last`/`since`.

    `last=N` returns the N most recent entries, in beat order. `since=<beat_id>` returns every
    entry from the first one whose `beat_id == <beat_id>` onward, inclusive; a `beat_id` never
    logged returns an empty list, not an error -- the tier is a query over what actually
    happened, not a manifest that could name something absent. Exactly one of `last`/`since`
    must be given; raises `ValueError` otherwise (the CLI verb's own mutual-exclusion, enforced
    here too so this function is safe to call directly).

    A missing log file (no beat yet resolved) returns an empty list rather than raising.
    """
    if (last is None) == (since is None):
        raise ValueError("read_log requires exactly one of 'last' or 'since'")

    path = _log_path(chronicle_dir, chronicle_name)
    if not path.exists():
        return []

    entries = [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]

    if last is not None:
        return entries[-last:] if last > 0 else []

    for index, entry in enumerate(entries):
        if entry.get("beat_id") == since:
            return entries[index:]
    return []
