# Phase 1 data model: session-context resolves the player character from pc.yaml

No new schema. This feature only changes *which files* one existing function reads; the shape
below already exists in `docs/design/25-entities.md` and `engine/wyrd/entity.py`.

## Player character (`pc.yaml`)

| Field | Type | Notes |
|---|---|---|
| `id` | str | Same common-schema field every entity carries; used as the dict key in the effective entity set. |
| `type` | `"character"` | Common-schema field; `_is_player_character` (loadtier.py) checks this. |
| `role` | `"player"` | One of the closed role vocabulary (`entity._ROLES`); `_is_player_character` checks this. |
| *(everything else)* | — | Whatever `create-character`'s return value populates (skills, Stamina, Fate, career_history, Drives, etc. — specs/156's data-model.md) — opaque to this feature; passed through unchanged. |

**Location**: `<chronicle_dir>/pc.yaml`, a sibling of `chronicle.yaml`, `setting/`, `overlay/`,
`entities/` — not itself under `entities/`.

**Cardinality**: At most one per chronicle (one player character), consistent with
`wyrd-chronicle-template`'s layout and `always_tier`'s existing single-player-character
assumption.

**Validation**: Identical to any other entity file — `entity.load`'s call to `validate()`
(common schema + per-type rules). A `pc.yaml` that fails validation raises `state.StateError`
naming the file, the same as an invalid `entities/*.md` file would.

## Effective entity set (`verbs.load_effective_entities`'s return value)

Unchanged shape (`dict[str, dict]`, keyed by entity id, frontmatter-only values) — this feature
adds one more source contributing entries to that same dict, not a new shape:

```
{setting entities resolved against overlay} + {entities/*.md} + {pc.yaml, if present}
```

`pc.yaml`'s entry is added last (after the existing `entities/*.md` merge), and simply
`dict[id] = frontmatter` — no different from how `entities/*.md` files are merged in today. If
`pc.yaml`'s `id` happens to collide with an existing entity's id, `pc.yaml`'s frontmatter wins
(last-write-wins on that key) — an id collision is a chronicle-authoring error the same way a
collision between an `entities/*.md` file and an overlaid setting entity already can be, and is
not this feature's concern to arbitrate specially.

## No state transitions, no new relationships

`pc.yaml` is loaded read-only by this feature; nothing here writes it, mutates it, or changes its
own schema.
