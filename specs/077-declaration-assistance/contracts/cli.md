# CLI contract: declaration/assistance lookups and the extended `opposed-test` verb

Two new catalog entries plus an extended `opposed-test` (all in the same `TOOLS` catalog #221
established).

## `describe --name declaration-bonus`

```json
{
  "name": "declaration-bonus",
  "description": "Look up the fixed point value for a declaration category (specific, specific_leveraging, brief, against_nature, removes_risk). Never derives a bonus from length -- the caller judges the category from the actual declared action.",
  "annotations": {"readOnlyHint": true, "destructiveHint": false, "idempotentHint": true, "openWorldHint": false},
  "inputSchema": {
    "type": "object",
    "properties": {"category": {"type": "string", "enum": ["specific", "specific_leveraging", "brief", "against_nature", "removes_risk"]}},
    "required": ["category"]
  }
}
```

```bash
python3 -m wyrd.client declaration-bonus --category specific_leveraging
# {"verb": "declaration-bonus", "category": "specific_leveraging", "bonus": 20, "no_roll": false}

python3 -m wyrd.client declaration-bonus --category removes_risk
# {"verb": "declaration-bonus", "category": "removes_risk", "bonus": null, "no_roll": true}

python3 -m wyrd.client declaration-bonus --category bogus
# {"error": {"verb": "declaration-bonus", "reason": "no such category: bogus"}}
```

## `describe --name assistance-bonus`

```json
{
  "name": "assistance-bonus",
  "description": "Look up a helper's assistance bonus: a tenth of their own skill, rounded down, capped at +10. Zero if they could not attempt the task alone.",
  "annotations": {"readOnlyHint": true, "destructiveHint": false, "idempotentHint": true, "openWorldHint": false},
  "inputSchema": {
    "type": "object",
    "properties": {
      "helper_skill": {"type": "integer", "minimum": 0, "maximum": 100},
      "can_attempt": {"type": "boolean", "default": true}
    },
    "required": ["helper_skill"]
  }
}
```

```bash
python3 -m wyrd.client assistance-bonus --helper-skill 45
# {"verb": "assistance-bonus", "helper_skill": 45, "can_attempt": true, "bonus": 4}

python3 -m wyrd.client assistance-bonus --helper-skill 100 --can-attempt false
# {"verb": "assistance-bonus", "helper_skill": 100, "can_attempt": false, "bonus": 0}
```

## `opposed-test` (extended)

New optional flags: `--declaration <category>`, `--helper-skill <int>`, `--helper-cannot-attempt`
(a store-true flag; its absence means `can_attempt=True`).

```bash
python3 -m wyrd.client opposed-test --skill 50 --opponent 50 --declaration specific --helper-skill 45 --seed 1
```

```json
{
  "verb": "opposed-test",
  "skill": 50,
  "opponent": 50,
  "declaration": "specific",
  "helper_skill": 45,
  "effective_pct": 64,
  "roll": 18,
  "success": true,
  "degrees": 4,
  "wyrd": "none",
  "no_roll": false,
  "seed": 1
}
```

`--declaration removes_risk` short-circuits to no roll:

```bash
python3 -m wyrd.client opposed-test --skill 50 --opponent 50 --declaration removes_risk
```

```json
{
  "verb": "opposed-test",
  "skill": 50,
  "opponent": 50,
  "declaration": "removes_risk",
  "helper_skill": null,
  "effective_pct": null,
  "roll": null,
  "success": true,
  "degrees": null,
  "wyrd": "none",
  "no_roll": true,
  "seed": null
}
```

Called with neither flag, output is byte-identical to #222's existing contract (with
`declaration: null`, `helper_skill: null`, `no_roll: false` added).

## Exit codes

- `0` — all cases above, including an unrecognized `--category` (structured error, per
  `declaration-bonus`'s example) — matching #221/#222's precedent of a structured error over a
  crash for caller-input validation
- Non-zero — a missing required argument (argparse's own behavior, unchanged)
