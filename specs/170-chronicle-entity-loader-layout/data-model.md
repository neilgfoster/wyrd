# Data Model: Chronicle Entity Loader Layout

This feature introduces no new entity type and no schema change. It corrects how existing entity
files are *located* on disk — not what an entity's fields mean, not the frontmatter schema
(docs/design/25-entities.md), and not the resolution rules (setting + overlay -> effective
entity, docs/design/22-state.md).

## Affected structural elements

- **Chronicle root**: unchanged — `_find_chronicle_root` (engine/wyrd/resolution.py) already
  finds it correctly by walking up for a directory holding `entities/`, `overlay/`, and
  `setting/`. Not touched by this feature.
- **Entity type subdirectory** (new structural element this feature must recognise): a directory
  named for one of `entity.ENTITY_TYPES` (engine/wyrd/entity.py), nested one level under
  `setting/entities/`, `overlay/`, or `entities/`, holding that type's entity files. Per
  spec.md's Assumptions, an entity type folder name is taken as-is — this feature adds no new
  validation of what counts as a legal type name.
- **Entity file**: unchanged shape (frontmatter + optional body, `---`-delimited, per
  `state.parse_entity`). Only its *expected location* changes.

## On-disk layout (before / after)

| Directory | Before (assumed) | After (this feature) |
|---|---|---|
| `setting/` | `setting/*.md` (flat) | `setting/entities/<type>/*.yaml` (new), plus `setting/*.md` (kept, FR-004) |
| `overlay/` | `overlay/*.md` (flat) | `overlay/<type>/*.yaml` (new), plus `overlay/*.md` (kept, FR-004) |
| `entities/` | `entities/*.md` (flat) | `entities/<type>/*.yaml` (new), plus `entities/*.md` (kept, FR-004) |

Note the asymmetry: `setting/`'s nested entities live under `setting/entities/<type>/`, one level
deeper than `overlay/<type>/` and `entities/<type>/` — matching the confirmed on-disk reality
(`setting/entities/faction/...`) rather than a hypothetical `setting/<type>/...` shape that isn't
observed anywhere.
