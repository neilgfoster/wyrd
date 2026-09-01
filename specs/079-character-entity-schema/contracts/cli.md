# CLI contract: character entity verbs and skill-scale lookup

## `describe --name character-save` / `character-load`

```json
{
  "name": "character-save",
  "description": "Save a player-character entity to a file, validating wound rules before writing.",
  "annotations": {"readOnlyHint": false, "destructiveHint": true, "idempotentHint": true, "openWorldHint": false},
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": {"type": "string"},
      "frontmatter": {"type": "object"},
      "body": {"type": "string", "default": ""}
    },
    "required": ["path", "frontmatter"]
  }
}
```

```bash
python3 -m wyrd.client character-load --path pc.md
```

```json
{
  "verb": "character-load",
  "path": "pc.md",
  "frontmatter": {"id": "...", "skills": {...}, "wounds": [...], "...": "..."},
  "body": "The character's own prose, if any."
}
```

A wound violating any of the three load-error rules is a structured error:

```json
{"error": {"verb": "character-load", "reason": "wound 'the-knee': effect 'skill' requires bears_on"}}
```

## `describe --name skill-scale`

```json
{
  "name": "skill-scale",
  "description": "Report the skill-scale constants: the value a skill opens at, and the amount it rises per advance.",
  "annotations": {"readOnlyHint": true, "destructiveHint": false, "idempotentHint": true, "openWorldHint": false},
  "inputSchema": {"type": "object", "properties": {}, "required": []}
}
```

```bash
python3 -m wyrd.client skill-scale
# {"verb": "skill-scale", "open_value": 25, "advance_step": 5, "untrained": 10}
```

## Exit codes

- `0` — all cases above, including a structured wound-validation error (matches #221-#224's
  precedent)
- Non-zero — a missing required argument, or a file-not-found/parse failure on `character-load`
  (an unexpected I/O failure, not a caller-input validation case, per #221's `StateError`
  precedent)
