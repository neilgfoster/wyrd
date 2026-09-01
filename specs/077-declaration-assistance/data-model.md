# Phase 1 data model: Declaration and assistance bonuses

No chronicle state. Two new lookup shapes, plus an extension of #222's opposed-test result.

## Declaration category (input)

One of a closed set of five strings: `"specific"`, `"specific_leveraging"`, `"brief"`,
`"against_nature"`, `"removes_risk"`. Any other string is rejected (FR-002).

| Category | Bonus |
|---|---|
| `specific` | +10 |
| `specific_leveraging` | +20 |
| `brief` | 0 |
| `against_nature` | −20 |
| `removes_risk` | no roll — automatic success |

## Assistance input

`helper_skill: int` (0-100) and `can_attempt: bool` (default `True`). Output: an int bonus,
`min(helper_skill // 10, 10)` if `can_attempt` else `0`.

## Opposed test result (extended from #222)

All fields from `specs/076-opposed-test-resolution/data-model.md` remain, plus:

| Field | Type | Description |
|---|---|---|
| `declaration` | string \| null | The category supplied, or `null` if none |
| `helper_skill` | int \| null | The helper skill supplied, or `null` if none |
| `no_roll` | bool | `true` only for `declaration == "removes_risk"` |

When `no_roll` is `true`: `roll`, `effective_pct`, `degrees` are all `null`, `wyrd` is `"none"`,
and `success` is `true`.

When `no_roll` is `false` (the default, including when neither modifier is supplied): all
fields behave exactly as #222 already specified, computed against `skill + declaration_bonus +
assistance_bonus` rather than raw `skill` — this is the only change to the existing formula's
*input*, not its shape.

Validation:
- Calling with neither `declaration` nor `helper_skill` produces a result identical to #222's
  pre-existing three-argument call (SC-003) — `declaration` and `helper_skill` both `null` in
  the output, `no_roll: false`.
- An unrecognized `declaration` value raises before any roll is attempted (FR-002).
