# CLI contract: `opposed-test` verb (extends #221's catalog)

A new entry in the same `TOOLS` catalog #221 established (`engine/wyrd/catalog.py`) — `describe`
and dispatch both read it, so they cannot drift, per `docs/design/27-tooling.md` section 3.

## `describe --name opposed-test`

```json
{
  "name": "opposed-test",
  "description": "Resolve a single player-facing opposed test: one roll on the acting side only, against effective% derived from the skill gap. The opponent's dice are never consulted. Use this whenever a player character or companion is opposed by an NPC/opponent.",
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false,
    "idempotentHint": false,
    "openWorldHint": false
  },
  "inputSchema": {
    "type": "object",
    "properties": {
      "skill": {"type": "integer"},
      "opponent": {"type": "integer"},
      "seed": {"type": "integer"}
    },
    "required": ["skill", "opponent"]
  }
}
```

`readOnlyHint: true` here (unlike `roll`'s `false`) since this verb performs no state write at
all, per research.md's "No state I/O" decision.

## `opposed-test`

```bash
python3 -m wyrd.client opposed-test --skill 70 --opponent 30 [--seed N] [--format json|text]
```

Structured output (default):

```json
{
  "verb": "opposed-test",
  "skill": 70,
  "opponent": 30,
  "effective_pct": 90,
  "roll": 23,
  "success": true,
  "degrees": 7,
  "wyrd": "none",
  "seed": null
}
```

On failure, `degrees` is `null`:

```json
{
  "verb": "opposed-test",
  "skill": 40,
  "opponent": 60,
  "effective_pct": 30,
  "roll": 87,
  "success": false,
  "degrees": null,
  "wyrd": "fair_omen",
  "seed": null
}
```

`--format text` renders e.g. `opposed-test: success (degrees 7, wyrd: none)` or `opposed-test:
failure (wyrd: fair_omen)`.

`--skill`/`--opponent` are required; a missing one is argparse's own usage error (exit non-zero,
matching #221's precedent for a malformed invocation rather than a validated-but-wrong value).

## Exit codes

- `0` — verb completed successfully, in all cases above (there is no invalid-input case this
  verb rejects beyond argparse's own required-argument check — any integer skill/opponent pair
  is meaningful input, unlike `roll`'s `sides <= 0`)
- Non-zero — a genuinely unexpected failure, or a missing required argument (argparse's own
  behavior, unchanged from #221)
