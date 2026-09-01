# CLI contract: `create-character` verb

## `describe --name create-character`

```json
{
  "name": "create-character",
  "description": "Run the 8-step character-creation procedure: validate an advance allocation (per #231) and, on success, produce a complete player-character entity with the fixed starting values from docs/design/11-character-creation.md section 2.",
  "annotations": {"readOnlyHint": false, "destructiveHint": true, "idempotentHint": true, "openWorldHint": false},
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {"type": "string"},
      "name": {"type": "string"},
      "career_json": {"type": "string"},
      "ancestry_json": {"type": "string"},
      "actions_json": {"type": "string"},
      "loyalty": {"type": "string"},
      "mortality": {"type": "string", "enum": ["low", "standard", "high"]},
      "drives_json": {"type": "string", "default": "[]"},
      "misfortune": {"type": "string", "default": null},
      "fault_line": {"type": "string"}
    },
    "required": ["path", "name", "career_json", "actions_json", "loyalty", "mortality", "fault_line"]
  }
}
```

```bash
python3 -m wyrd.client create-character \
  --path aria.md --name "Aria Nightingale" \
  --career-json '{"skills": {"stealth": 55, "swordplay": 45}, "entry_point": true}' \
  --actions-json '[{"action":"open","skill":"stealth"},{"action":"open","skill":"swordplay"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"swordplay"},{"action":"raise","skill":"swordplay"}]' \
  --loyalty "the-old-guard" --mortality standard \
  --drives-json '["find the truth"]' --fault-line "She trusts no one because the guild sold her out once."
```

```json
{
  "verb": "create-character",
  "valid": true,
  "path": "aria.md",
  "frontmatter": {"...": "the full produced entity, per data-model.md"}
}
```

A rejected allocation produces no file:

```json
{"verb": "create-character", "valid": false, "error": "allocation must spend exactly 8 advances, got 7"}
```

## Exit codes

- `0` — both accepted and rejected allocations (matching #231's precedent — a rejection is a
  legitimate structured result)
- Non-zero — a missing required argument, or malformed JSON (matching #231's precedent for
  genuinely malformed caller input)
