# Phase 1 data model: Character entity schema and validator

## Entity file

| Part | Type | Description |
|---|---|---|
| `frontmatter` | dict | The YAML block between the two `---` delimiters |
| `body` | string | Raw markdown text after the closing `---`, preserved unchanged |

## Player-character frontmatter (docs/design/22-state.md)

All fields are carried through unvalidated except `wounds` (see below) — this feature does not
range-check `taint`/`trauma`/`stamina`/etc. against game-rule bounds, only the structural rules
`docs/design/22-state.md` states as load errors.

| Field | Type |
|---|---|
| `id`, `type`, `role` | string |
| `loyalty`, `career` | string (opaque, possibly a wikilink) |
| `career_history` | list |
| `skills` | dict[str, int] |
| `stamina`, `fate` | dict `{current, max}` |
| `fortune`, `resolve` | dict `{current}` |
| `taint`, `trauma`, `strain`, `dread`, `advances_unspent` | int |
| `pending_omen` | `null \| "+10" \| "-10"` |
| `hidden_threshold`, `fault_line`, `misfortune` | value or `null` |
| `transformations`, `afflictions`, `drives`, `holdings`, `allegiances`, `marks` | list |
| `reputation` | dict `{score, label}` |
| `wounds` | list of Wound (below) |

## Wound

| Field | Type | Rule |
|---|---|---|
| `id` | string | unique on the character |
| `from` | dict | provenance, e.g. `{table, beat}` |
| `effect` | dict, exactly one key | key MUST be one of `stamina_max`, `skill`, `dread` (FR-003) |
| `bears_on` | string, optional | REQUIRED if `effect`'s key is `skill` (FR-004); absent otherwise |
| `recurring` | bool | if `true`, `closed` MUST be `null` (FR-005) |
| `closed` | int or `null` | the beat the wound stopped biting, or `null` while still active |
| `description` | string | prose |

Validation order: closed effect-key set → `bears_on` requirement → `recurring`/`closed`
exclusivity. Each violation raises `StateError` naming the wound's `id` and the specific rule.

## Active wound effect (computed, not stored)

| Field | Type | Description |
|---|---|---|
| `wound_id` | string | which wound this effect comes from |
| `effect` | dict | the wound's `effect`, unchanged |
| `bears_on` | string or absent | carried through if present |

Computed by filtering `wounds` to `closed is None`, in the order given (no stated ordering
requirement beyond source order).
