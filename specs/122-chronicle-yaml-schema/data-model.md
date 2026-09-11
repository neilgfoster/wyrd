# Data Model: Chronicle.yaml schema, load/save and versioning

Source of truth for field shape: docs/design/22-state.md § `chronicle.yaml`. This document names
which fields are required vs. optional-with-default, and validation rules, for this feature's
implementation.

## Chronicle state

| Field | Type | Required | Default if absent | Notes |
|---|---|---|---|---|
| `schema_version` | int | yes | — | must equal this feature's `_SCHEMA_VERSION` |
| `name` | string | yes | — | the chronicle id |
| `engine` | mapping | yes | — | see **Version pin** below |
| `setting` | mapping | yes | — | see **Version pin** below |
| `calendar` | mapping `{year, month, day}` | yes | — | `month`/`day` may individually be `null` |
| `era` | string \| null | no | `null` | |
| `sessions` | int | yes | — | non-negative (FR-010) |
| `danger_rating` | int | yes | — | non-negative (FR-010) |
| `migrations` | list of **Migration entry** | no | `[]` | append-only (FR-003/FR-004) |
| `intent` | mapping | no | see **Intent** below | |
| `pending` | mapping \| null | no | `null` | opaque to this feature (FR-006) |

### Version pin (`engine`, `setting`)

| Field | Type | Required | Notes |
|---|---|---|---|
| `repo` | string | yes | |
| `version` | string | yes | what it runs under now |
| `created_under` | string | yes | what the chronicle began under; independent of `version` (FR-002) |

### Migration entry

| Field | Type | Required | Notes |
|---|---|---|---|
| `from` | mapping | yes | partial version pin, e.g. `{engine: 0.1.0}` |
| `to` | mapping | yes | partial version pin |
| `class` | string | yes | one of `additive`, `tuning`, `structural`, `behavioural` (FR-005) |
| `applied` | string | yes | date |
| `note` | string | yes | human-readable, what changed and why it applied forward only |

**Invariant**: once a chronicle state has been loaded and its `migrations` list saved again, every
entry present in the loaded list must still be present, unchanged, at the same list position, in
the saved list (FR-003/FR-004). Enforced by `validate_chronicle()` comparing the new list's
leading entries against the previously-loaded list, given as an optional argument.

### Intent

| Field | Type | Required | Default if absent |
|---|---|---|---|
| `about` | string \| null | no | `null` |
| `avoid` | list of string | no | `[]` |
| `session_length` | int | no | `20` |
| `lethality` | string | no | `"standard"` |
| `world_acts_offstage` | bool | no | `true` |

## State transitions

- **Fresh chronicle** → `default_chronicle_state(name, engine_repo, engine_version,
  setting_repo, setting_version)` produces a state with `created_under` equal to `version` for
  both engine and setting, `migrations: []`, `sessions: 0`, `pending: null`, and `intent` at its
  documented defaults.
- **Version bump** → the caller updates `engine.version` and/or `setting.version` (leaving
  `created_under` untouched) and calls `append_migration(state, entry)`, which appends `entry` to
  `migrations` without touching any existing entry.
- **Session interrupted** → the caller sets `pending` to whatever mapping it needs (opaque to
  this feature); **session resumes cleanly** → the caller sets `pending` back to `null`. Neither
  transition is validated for meaning by this feature (FR-006).

## Validation rules (`validate_chronicle`)

1. Every required field above is present (FR-008) — raises `StateError` naming the specific
   missing field.
2. `sessions >= 0` and `danger_rating >= 0` (FR-010).
3. Every `migrations[i].class` is one of the four allowed values (FR-005).
4. If a previously-loaded `migrations` list is supplied for comparison, the new list's first
   `len(previous)` entries equal `previous` exactly, in the same order (FR-003/FR-004) —
   otherwise raises `StateError` naming the altered/reordered entry's position.
5. Absent optional fields are not errors — the loader fills their defaults per the table above
   before returning (FR-009).
