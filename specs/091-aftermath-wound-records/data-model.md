# Phase 1 Data Model: The Aftermath table and wound records

## Aftermath roll result (in-memory, staged step)

Not a new persisted entity — a `steps` entry in `resolution.py`'s existing proposal shape, the
same shape `_stage_critical` already produces:

| Field | Holds |
|---|---|
| `step_id` | this step's index in the proposal's `steps` list |
| `mechanic` | `"aftermath"` |
| `roll.roll` | the raw `d100` result |
| `roll.modifier` | `5 × points_below_zero` |
| `roll.total` | `roll + modifier` |
| `roll.table` | `"aftermath"` |
| `roll.key` | the resolved row's key (one of the 8 in `AFTERMATH_TABLE`) |
| `mutations` | zero or one wound-append mutation, per row |
| `depends_on` | `[depends_on_step]`, following `_stage_critical`'s existing convention |

## Wound record (existing shape, reused unchanged)

Already defined by `character.py`/`docs/design/22-state.md`; this feature only produces
instances, it adds no new field:

| Field | This feature's usage |
|---|---|
| `id` | `f"aftermath-{step_id}"` |
| `from` | `{"table": "aftermath", "beat": step_id}` |
| `effect` | row-specific: absent (`lasting-wound`, `left-for-dead`, `new-enemy`), `{"dread": 1}` (`disfigured`), `{"skill": -10}` (`recurring-wound`) |
| `recurring` | `True` only for `recurring-wound`; otherwise absent/`False` |
| `bears_on` | present only when `effect` includes `skill` (the `recurring-wound` row) |
| `closed` | never set by this feature (a fresh wound is always open) |

## The `AFTERMATH_TABLE` row table

A `list[tuple[int, int, str, dict | None]]`, the exact shape `CRITICAL_*_TABLE` already uses:
`(low, high, key, effect)`. The open-ended `death` row is handled the same way
`_critical_band`'s fallthrough handles a mortal result — no explicit upper bound; any total above
the last closed row's high resolves to `death`.

| low | high | key | effect |
|---|---|---|---|
| 6 | 30 | `out-of-action` | `None` |
| 31 | 52 | `lasting-wound` | `{}` (wound record, no mechanical effect) |
| 53 | 66 | `left-for-dead` | `{}` |
| 67 | 78 | `new-enemy` | `{}` |
| 79 | 88 | `taken` | `None` (no wound record) |
| 89 | 98 | `disfigured` | `{"dread": 1}` |
| 99 | 110 | `recurring-wound` | `{"skill": -10}` (plus `recurring: True`, `bears_on`) |
| 111 | — | `death` | `None` (no wound record) |

`effect: None` means "no wound record produced"; `effect: {}` means "a wound record is produced,
carrying no mechanical `effect` field" — these are the two distinct no-effect cases the spec's
User Story 2 distinguishes (`out-of-action`/`taken`/`death` produce nothing; `lasting-wound` etc.
produce a wound record whose own `effect` may still be empty).
