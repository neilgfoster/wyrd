# Data Model: Chronicle overlay resolution

Source: `docs/design/25-entities.md` ("The chronicle overlay" section), building on #305's
`engine/wyrd/entity.py` common schema.

## Overlay file

An overlay file is a regular entity file (markdown + YAML frontmatter, read via
`state.load_entity`) with a restricted, non-validated frontmatter shape:

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | str | yes | the overlay file's own id — informational; the effective entity's `id` comes from the setting entity, not this field |
| `overlay_of` | str | yes | the setting entity id this overlay modifies — the join key |
| *(any other field)* | any | no | any field name valid for the setting entity's `type` — replaces the setting value wholesale when present |

An overlay's frontmatter is **not** run through `entity.validate()` — it may legitimately omit
`type`, `name`, `setting`, `status`, since it carries only a delta (research.md).

## Effective entity

The result of resolving a setting entity against its (optional) overlay:

- **Frontmatter**: `{**setting_frontmatter, **overlay_fields}`, where `overlay_fields` excludes
  `id` and `overlay_of` themselves (those are overlay-only bookkeeping fields, not part of the
  effective entity), and the result's `id` is always the setting entity's `id`.
- **Body**: the overlay's body if non-empty, else the setting entity's body.
- Never persisted as a file — computed in memory each time `resolve_entity`/`load_setting` is
  called.

The effective entity's frontmatter is validated with the existing `entity.validate()` (#305)
before being returned; a failure is surfaced as `state.StateError`, matching `entity.load`'s
existing error style, so a merge that produces something schema-invalid (e.g. an unrecognized
`role`) is caught the same way a malformed setting file already is.

## Resolution inputs

| Input | Type | Notes |
|---|---|---|
| `setting_entities` | `dict[str, dict]` | id → frontmatter, as returned by `entity.load_set` over `chronicle/setting/` |
| `overlays` | `dict[str, dict]` | keyed by `overlay_of` (not the overlay file's own `id`) → overlay frontmatter, loaded from `chronicle/overlay/` |
| `bodies` | per-entity | each id's setting body and (if present) overlay body, needed for FR-007 |

## Errors

| Condition | Reported as |
|---|---|
| Overlay's `overlay_of` not in `setting_entities` | `state.StateError` naming the overlay file and the missing target id (FR-008) |
| Merged frontmatter fails `entity.validate()` | `state.StateError` naming the entity id and the validation failure (FR-009), same shape `entity.load` already raises |
| No overlay exists for a given setting entity id | Not an error — resolves to the setting entity unchanged (FR-004) |
