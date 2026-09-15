# Data Model: Chronicle CLI Verbs

This feature introduces no new persisted schema. It reads and composes existing entities and
chronicle state (docs/design/22-state.md, 25-entities.md) and adds one new on-disk artifact
(the live log file) plus in-memory result shapes returned by each verb.

## Existing entities read (no changes)

- **Chronicle state** (`chronicle.yaml`) — read via `state.load_chronicle`; unchanged.
- **Entity** (`setting/**/*.md`, `overlay/**/*.md`, `entities/**/*.md`) — read via
  `entity.load_set` + `entity.resolve_entity`; unchanged. Relevant frontmatter fields this
  feature filters or composes on: `type`, `status`, `role`, `tags`, `heat`, `threat.imminence`.
- **Recap** (`recap.md`) — read/regenerated via `loadtier.generate_recap`/
  `recap_close_step`; unchanged.

## New on-disk artifact: the live log file

- **Path**: `log/<chronicle-name>.jsonl`, one JSON object per line.
- **Record shape**: `{"beat_id": str, "mode": "played" | "summarised", "resolved_at": float}`
  — identical to `session.narrate_beat`'s existing return value (research.md's log-format
  decision).
- **Write path**: appended, one record per resolved beat. Out of this feature's direct scope is
  wiring the append into the session loop's own `beat` step (that step already exists in
  `session.py`; this feature adds the log-writing function itself and the `log` read verb, and
  calls the write function at the same point `narrate_beat` is already invoked).
- **Read path**: `log --last N` returns the last N records in file order (== beat order);
  `log --since <beat>` returns every record from the first record whose `beat_id == <beat>`
  onward, inclusive.

## Verb result shapes (returned to the CLI caller, JSON-serialisable)

- **`session-context`**: `{"verb": "session-context", "player_character": dict | None,
  "companions": dict[str, dict], "threads": dict[str, dict], "recap": str, "contract": str}`.
- **`get`**: `{"verb": "get", "id": str, "entity": dict, "body": str}` on success; raises on an
  id that does not resolve (distinguishable from an empty result, per spec.md FR-002).
- **`find`**: `{"verb": "find", "filters": {"type": str, "status": str | None,
  "tag": str | None}, "results": dict[str, dict]}`.
- **`party`**: `{"verb": "party", "results": dict[str, dict]}`.
- **`threads`**: `{"verb": "threads", "results": list[dict]}` (ordered by `heat` descending).
- **`threats`**: `{"verb": "threats", "results": dict[str, dict]}`.
- **`log`**: `{"verb": "log", "entries": list[dict]}`.
- **`save`**: `{"verb": "save", "path": str}`.
- **`load`**: `{"verb": "load", "state": dict}`.
- **`validate`**: `{"verb": "validate", "valid": bool, "error": str | None}`.
- **`recap`**: `{"verb": "recap", "path": str, "text": str}`.
- **`advance-time`**: `{"verb": "advance-time", "calendar": dict, "activations": list[dict]}`
  — the direct shape `advance_time.advance_time` already returns, plus the `verb` tag.
- **`threat-check`**: `{"verb": "threat-check", "id": str, "activated": bool, "roll": int}`.

Every shape follows the existing `{"verb": <name>, ...}` convention `verbs.py`'s current
functions (`roll`, `find_noun`, etc.) already use, so no new output convention is introduced
(spec.md FR-012, Assumptions).
