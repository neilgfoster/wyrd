# Data Model: Optional intensity tiers for a system of power

## System of power (existing entity, unchanged fields)

| Field | Required | Type | Notes |
|---|---|---|---|
| `id` | yes | kebab-case string | unchanged |
| `name` | yes | string | unchanged |
| `skill` | yes | string | unchanged |
| `strain_cost` | yes | positive integer | unchanged — this feature does not touch its required/default semantics |
| `requires_training` | yes | boolean | unchanged |
| `resolve_cost` | no | positive integer | unchanged |
| `ill_omen_taint` | no, default `1` | positive integer | unchanged |
| `description` | no | string | unchanged |
| `intensity_tiers` | **no, new** | list of Intensity Tier | this feature's addition |

## Intensity Tier (new entity)

One entry in a system of power's `intensity_tiers` list.

| Field | Required | Type | Validation rule |
|---|---|---|---|
| `label` | yes | non-empty string | free text — a setting's own vocabulary (e.g. minor/moderate/major); rejected if missing or empty |
| `difficulty` | yes | string | must be one of the six recognised difficulty-ladder rungs (`easy`, `average`, `challenging`, `difficult`, `hard`, `very hard`), case as declared in `03-rules.md`'s table; rejected otherwise |
| `cost_multiplier` | yes | number (int or float) | must be `> 0`; rejected if zero or negative |
| `ill_omen_taint_bonus` | yes | integer | must be `>= 0`; rejected if negative |

### Relationships

- `intensity_tiers` belongs to exactly one system of power (list field, not a separate top-level
  collection — no cross-system sharing of a tier).
- A tier does not reference `strain_cost`/`resolve_cost`/`ill_omen_taint` directly; it modifies
  them at resolution time via the two derived values below. There is no stored "effective cost"
  field — it is always computed from the base field and the chosen tier.

### Derived values at resolution (not stored, computed per invocation)

Given a system of power with base fields `strain_cost` (`resolve_cost`, `ill_omen_taint`) and an
invocation declared at tier `T` (or no tier, for a system with none declared or an invocation not
framed at any tier):

- `effective_strain_cost = strain_cost * T.cost_multiplier` (or `strain_cost` unmodified with no
  tier)
- `effective_resolve_cost = resolve_cost * T.cost_multiplier` if `resolve_cost` is declared,
  else not applicable (nothing to scale)
- `effective_ill_omen_taint = ill_omen_taint + T.ill_omen_taint_bonus` (or `ill_omen_taint`
  unmodified, or the schema default of `1` if `ill_omen_taint` itself is undeclared, with no
  tier)

### State transitions

None — a system of power's `intensity_tiers` declaration is static setting data, not something
that changes over the course of a chronicle (per `docs/design/22-evolution.md`, rule changes are
forward-only and are an authoring-time edit, not a runtime state transition this feature tracks).

### Validation summary (feeds `tools/check_power_systems.py`)

For each entry in `intensity_tiers` (list may be absent or empty — both mean "no tiers", per
spec Edge Cases):

1. `label` missing or not a non-empty string → reject, naming the system of power and the tier's
   list position.
2. `difficulty` not one of the six recognised rungs → reject, naming the tier and the invalid
   value.
3. `cost_multiplier` missing, not a number, or `<= 0` → reject, naming the tier.
4. `ill_omen_taint_bonus` missing, not an integer, or `< 0` → reject, naming the tier.

A system of power with `intensity_tiers` entirely absent skips all four checks — identical to
today's behaviour (FR-003, FR-006).
