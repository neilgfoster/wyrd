# Data Model: Adversary block loading and validation

## Adversary block (the shape this feature produces)

Mirrors docs/design/12-the-adversary.md section 2 exactly:

```json
{
  "id": "the-hunter",
  "name": "A named antagonist",
  "baseline": 35,
  "stamina_max": 7,
  "armour": "modest",
  "skills": {"blade": 55, "tracking": 60},
  "damage": "1d6",
  "damage_type": "slashing",
  "ranged": false,
  "traits": [{"name": "Unhurried", "effect": {"difficulty": -10}}],
  "notes": null
}
```

- **Required**: `id` (kebab-case, stable/unique per file), `name`, `baseline` (int 0-100),
  `stamina_max` (int >= 1), `armour` (one of `none`/`light`/`modest`/`heavy`), `skills`
  (non-empty mapping of name -> int 0-100).
- **Optional**: `damage` (a dice-expression string, e.g. `1d6`, `1d6+2`), `damage_type` (one of
  `slashing`/`piercing`/`blunt`/`searing`), `ranged` (bool, defaults to `false`), `traits` (list
  of `{"name": str, "effect": {<one of the six trait-effect keys>: value}}`), `notes` (free
  text, read by no mechanism).
- `damage` and `damage_type` are constrained together: both present, or both absent. Never one
  without the other.
- Every field not in the required/optional sets above is rejected at load.

## Bestiary file (input)

```yaml
creatures:
  - id: the-hunter
    name: A named antagonist
    baseline: 35
    stamina_max: 7
    armour: modest
    skills:
      blade: 55
      tracking: 60
    damage: 1d6
    damage_type: slashing
    ranged: false
    traits:
      - name: Unhurried
        effect:
          difficulty: -10
```

Read via `state.parse_yaml`, which returns `{"creatures": [...]}` for this shape -- the top-level
mapping this feature scans for the requested id.

## Validation rules (mirrors `tools/check_bestiary.py`'s `check_entry`)

| Rule | Source |
|---|---|
| Every required field present | `REQUIRED_FIELDS` |
| No field outside required ∪ optional | `ALL_FIELDS` |
| `id` matches kebab-case | `ID_RE` |
| `baseline` is an int in 0-100 | `SKILL_MIN`/`SKILL_MAX` |
| `stamina_max` is an int >= 1 | `STAMINA_MIN` |
| `armour` is one of the four ranks | `ARMOUR_RANKS` |
| `skills` is a non-empty mapping of int 0-100 values | `SKILL_MIN`/`SKILL_MAX` |
| `damage` (if present) matches a dice expression | `DAMAGE_RE` |
| `damage_type` (if present) is one of the closed four | `DAMAGE_TYPES` |
| `damage` and `damage_type` travel together | new for this feature's load path |
| `ranged` (if present) is a bool | — |
| Each `traits[n]` has a `name` and a non-empty `effect` | — |
| Each `traits[n].effect` key is in the closed six-effect vocabulary | `TRAIT_EFFECTS` |

Every constant above is re-declared in `engine/wyrd/adversary.py` (research.md: "re-expressed as
engine code, not imported from tools/") with the same values `tools/check_bestiary.py` already
uses.

## State transitions

None. This feature is read-only: it loads and validates one entry from a file already on disk,
producing an in-memory mapping. It writes nothing back, and the loaded block is not persisted
anywhere new by this feature.
