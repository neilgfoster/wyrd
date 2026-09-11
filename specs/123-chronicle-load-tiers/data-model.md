# Data model: Chronicle load-tier resolution and recap.md

No new entity type or persisted field is introduced. This feature reads existing entity schema
(docs/design/25-entities.md, docs/design/22-state.md) and produces two in-memory shapes plus one
generated file.

## Always-tier result

Not a stored object — the return value of `loadtier.always_tier(entities)`, recomputed on every
call from `entities: dict[str, dict]` (the shape `entity.load_set` already produces).

| Field | Type | Source |
|---|---|---|
| `player_character` | `dict \| None` | the one entity with `type: character`, `role: player` |
| `companions` | `dict[str, dict]` | entities with `type: character`, `role: companion`, `status: with-party`, keyed by id |
| `threads` | `dict[str, dict]` | entities with `type: thread`, `heat >= 3`, keyed by id |

`chronicle.yaml` and `recap.md` are not represented here — they are the two fixed per-chronicle
files a caller always loads alongside this result (see research.md).

## recap.md

A generated markdown/plain-text file, not frontmatter, produced by
`loadtier.generate_recap(entities, chronicle, *, where=None, changes=None, body_mind=None)`.

| Section | Computed how |
|---|---|
| Where and when | caller-supplied `where` string (GM narrative judgment; no tracked field — research.md) |
| Three hottest threads | the three highest-`heat` entities among `type: thread`, `status: open`, ordered by `heat` descending then `id` for a stable tie-break; fewer than three named if fewer exist |
| What changed | caller-supplied `changes` (list of short strings, joined) |
| Body/mind state | caller-supplied `body_mind` one-sentence string (diegetic; never raw `taint`/`trauma`/`resolve`) |
| Who's present | the with-party companions' names, from the same always-tier query |

Falls back to a short placeholder ("Not recorded.") for any of `where`/`changes`/`body_mind` the
caller omits, so the document is always well-formed and near the ~200-word budget rather than
failing outright.

## Existing schema fix required

`engine/wyrd/entity.py`'s `_ROLES` gains `"player"` (currently
`nemesis, ally, companion, bystander, authority, quarry`) — without it, `validate()`/`load`/
`load_set` reject any real player-character file, which the always-tier query depends on being
loadable (research.md).
