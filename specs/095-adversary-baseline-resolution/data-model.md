# Data Model: Adversary baseline skill resolution

No new entity or persisted shape. This feature adds one pure function reading two existing fields
of the adversary block #259 already defines and validates: `baseline` (int 0-100) and `skills`
(non-empty mapping of skill name -> int 0-100).

## `resolve_skill(block, skill) -> int`

| Input | Output |
|---|---|
| `skill` present in `block["skills"]` | that skill's own listed value |
| `skill` absent from `block["skills"]` | `block["baseline"]` |

No state transitions -- a pure lookup over an already-loaded block.
