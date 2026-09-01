# Phase 1 data model: Core opposed-test resolution

No chronicle state is read or written by this feature (spec.md's Key Entities, research.md's "No
state I/O" decision). The only shape is the function's own return value.

## Opposed test result

| Field | Type | Description |
|---|---|---|
| `verb` | string | Always `"opposed-test"` |
| `skill` | int | The acting side's skill, as given |
| `opponent` | int | The opposing skill/baseline, as given |
| `effective_pct` | int | `clip(50 + (skill - opponent), 5, 95)` |
| `roll` | int | The natural, unmodified d100 roll |
| `success` | bool | `roll <= effective_pct` |
| `degrees` | int \| null | `tens(effective_pct) - tens(roll)` if `success`, else `null` — never a comparison performed on failure |
| `wyrd` | string | One of `"ill_omen"` (roll's units digit is 0), `"fair_omen"` (units digit is 9), or `"none"` (units digit 1-8) |
| `seed` | int \| null | The seed used, if one was supplied |

Validation:
- `effective_pct` is always in `[5, 95]` inclusive, regardless of how extreme `skill - opponent`
  is (FR-002).
- `degrees` is present (non-null) if and only if `success` is `true` (FR-004, FR-005).
- `wyrd` is computed identically regardless of `success` (FR-007) — the same units-digit lookup
  runs before the success/failure branch, not inside either one.

No state transitions — this is a pure computation, not a chronicle mutation.
