# CLI contract: `validate-allocation` verb

## `describe --name validate-allocation`

```json
{
  "name": "validate-allocation",
  "description": "Validate an 8-advance allocation against a career (optionally widened by an ancestry), per docs/design/11-character-creation.md section 3. Does not generate an allocation -- a character is chosen, not rolled (ADR 0014).",
  "annotations": {"readOnlyHint": true, "destructiveHint": false, "idempotentHint": true, "openWorldHint": false},
  "inputSchema": {
    "type": "object",
    "properties": {
      "career_json": {"type": "string"},
      "ancestry_json": {"type": "string"},
      "actions_json": {"type": "string"}
    },
    "required": ["career_json", "actions_json"]
  }
}
```

```bash
python3 -m wyrd.client validate-allocation \
  --career-json '{"skills": {"stealth": 55, "swordplay": 45}, "entry_point": true}' \
  --actions-json '[{"action":"open","skill":"stealth"},{"action":"open","skill":"swordplay"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"stealth"},{"action":"raise","skill":"swordplay"},{"action":"raise","skill":"swordplay"}]'
```

```json
{
  "verb": "validate-allocation",
  "valid": true,
  "skills": {"stealth": 45, "swordplay": 35}
}
```

A rejected allocation:

```json
{
  "verb": "validate-allocation",
  "valid": false,
  "error": "allocation must spend exactly 8 advances, got 7"
}
```

## Exit codes

- `0` — both accepted and rejected allocations (a rejection is a legitimate structured result,
  not a caller-input crash, matching #221-#229's precedent)
- Non-zero — a missing required argument, or malformed JSON in `--career-json`/`--actions-json`
