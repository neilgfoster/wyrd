# CLI contract: `wyrd` entry point (this feature's slice)

Per `docs/design/27-tooling.md` section 3, the `TOOLS` catalog in `catalog.py` is the single
source of truth: `describe` and argparse dispatch both read it, so they cannot drift. This
feature's catalog has exactly one verb, `roll`; later features add their own catalog entries
without touching this contract.

## `describe`

```bash
python3 -m wyrd.client describe
python3 -m wyrd.client describe --name roll
```

Output (JSON): the whole `TOOLS` catalog, or (with `--name`) the single matching entry:

```json
{
  "name": "roll",
  "description": "Roll a die (default d100) through the deterministic dice tool. Use this whenever a rule calls for a random result — never narrate a roll without calling this first.",
  "annotations": {
    "readOnlyHint": false,
    "destructiveHint": false,
    "idempotentHint": false,
    "openWorldHint": false
  },
  "inputSchema": {
    "type": "object",
    "properties": {
      "sides": {"type": "integer", "minimum": 1, "default": 100},
      "seed": {"type": "integer"}
    },
    "required": []
  }
}
```

`--name` for a verb not in the catalog is a structured error, not a bare traceback:

```json
{"error": {"verb": "describe", "reason": "no such verb: bogus"}}
```

## `roll`

```bash
python3 -m wyrd.client roll [--sides N] [--seed N] [--format json|text]
```

Structured output (default, `--format json` implied):

```json
{
  "verb": "roll",
  "sides": 100,
  "result": 42,
  "seed": null,
  "state_written": true
}
```

`--format text` renders the same result as a short human-readable line (e.g. `d100: 42`), for a
person at a terminal rather than the GM narrating from JSON.

Errors (e.g. `--sides 0` or `--sides -5`) are structured, not a bare traceback:

```json
{"error": {"verb": "roll", "reason": "sides must be a positive integer, got 0"}}
```

## Exit codes

- `0` — verb completed successfully (including a structured `{"error": ...}` result reported via
  stdout for a caller-facing validation failure such as bad `--sides`, per `27-tooling.md`
  section 3's "structured, actionable" errors rather than a process crash)
- Non-zero — genuinely unexpected failure (e.g. state file unreadable/corrupt on disk, per
  FR-008) that isn't a normal caller-input validation case
