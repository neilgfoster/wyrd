# Phase 1 data model: Character creation procedure

## Creation input

| Field | Type | Description |
|---|---|---|
| `path` | str | where to save the produced entity |
| `name` | str | the character's name |
| `career` | dict | per #231's Career shape |
| `ancestry` | dict \| None | per #231's Ancestry shape |
| `actions` | list[dict] | the 8-advance allocation, per #231 |
| `loyalty` | str | opaque identifier |
| `mortality` | `"low"` \| `"standard"` \| `"high"` | |
| `drives` | list | caller-supplied, carried through unjudged |
| `misfortune` | any | caller-supplied |
| `fault_line` | str | the Fault Line sentence |
| `body` | str | optional prose body for the entity file (default `""`) |

## Creation result

On success: `{"valid": True, "path": ..., "frontmatter": {...}}` — the saved entity's full
frontmatter, so a caller can inspect what was written without a separate load call.

On failure (allocation rejected): `{"valid": False, "error": "..."}` — #231's own rejection
reason, verbatim. No file is written.

## Produced character frontmatter (fixed values)

| Field | Value |
|---|---|
| `name` | as supplied |
| `type` | `"character"` |
| `role` | `"player"` |
| `loyalty` | as supplied |
| `career` | as supplied |
| `career_history` | `[]` |
| `skills` | from `validate_allocation`'s result |
| `stamina` | `{current: 6, max: 6}` |
| `fate` | `{current: N, max: N}`, `N` from the mortality table |
| `fortune` | `{current: N}` |
| `resolve` | `{current: 0}` |
| `taint`, `trauma`, `strain`, `dread`, `advances_unspent` | `0` |
| `pending_omen`, `hidden_threshold`, `fault_line`* | `null`, `null`, as supplied |
| `transformations`, `afflictions`, `wounds`, `holdings`, `allegiances`, `marks` | `[]` |
| `reputation` | `{score: 0, label: null}` |
| `drives`, `misfortune` | as supplied |

\* `fault_line` is the one field docs/design/22-state.md lists as starting `null` in general but
that this procedure's own step 8 always sets from the caller's sentence, per spec.md FR-006.
