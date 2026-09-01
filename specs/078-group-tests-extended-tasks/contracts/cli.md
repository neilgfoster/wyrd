# CLI contract: `group-test` and `extended-task-interval` verbs

Two new catalog entries in the same `TOOLS` catalog #221 established.

## `describe --name group-test`

```json
{
  "name": "group-test",
  "description": "Resolve a group test: select the most- or least-capable member's skill (untrained 10% for a member with none relevant), then resolve one opposed test against it. A group rolls once, never once per member.",
  "annotations": {"readOnlyHint": true, "destructiveHint": false, "idempotentHint": false, "openWorldHint": false},
  "inputSchema": {
    "type": "object",
    "properties": {
      "member_skills": {"type": "array", "items": {"type": ["integer", "null"]}},
      "mode": {"type": "string", "enum": ["most_capable", "least_capable"]},
      "opponent": {"type": "integer"},
      "seed": {"type": "integer"}
    },
    "required": ["member_skills", "mode", "opponent"]
  }
}
```

```bash
python3 -m wyrd.client group-test --member-skills 70,45,30 --mode most_capable --opponent 50 --seed 1
```

```json
{
  "verb": "group-test",
  "member_skills": [70, 45, 30],
  "mode": "most_capable",
  "selected_skill": 70,
  "opponent": 50,
  "effective_pct": 95,
  "roll": 18,
  "success": true,
  "degrees": 7,
  "wyrd": "none",
  "no_roll": false,
  "declaration": null,
  "helper_skill": null,
  "seed": 1
}
```

An empty `--member-skills` or an unrecognized `--mode` is a structured error:

```json
{"error": {"verb": "group-test", "reason": "member_skills must not be empty"}}
```

## `describe --name extended-task-interval`

```json
{
  "name": "extended-task-interval",
  "description": "Resolve one interval of an extended task: one opposed test, adding max(1, degrees) to progress on success, nothing on failure. Reports whether the task is now done. Does not persist progress -- the caller carries it into the next interval.",
  "annotations": {"readOnlyHint": true, "destructiveHint": false, "idempotentHint": false, "openWorldHint": false},
  "inputSchema": {
    "type": "object",
    "properties": {
      "skill": {"type": "integer"},
      "opponent": {"type": "integer"},
      "progress": {"type": "integer", "minimum": 0},
      "target": {"type": "integer", "minimum": 1},
      "seed": {"type": "integer"}
    },
    "required": ["skill", "opponent", "progress", "target"]
  }
}
```

```bash
python3 -m wyrd.client extended-task-interval --skill 45 --opponent 50 --progress 2 --target 4 --seed 1
```

```json
{
  "verb": "extended-task-interval",
  "skill": 45,
  "opponent": 50,
  "effective_pct": 45,
  "roll": 18,
  "success": true,
  "degrees": 2,
  "wyrd": "none",
  "no_roll": false,
  "declaration": null,
  "helper_skill": null,
  "progress": 4,
  "target": 4,
  "gained": 2,
  "done": true,
  "seed": 1
}
```

## Exit codes

- `0` — all cases above, including structured errors for empty `member_skills` or an
  unrecognized `mode` (matches #221-#223's precedent of a structured error over a crash for
  caller-input validation)
- Non-zero — a missing required argument (argparse's own behavior, unchanged)
