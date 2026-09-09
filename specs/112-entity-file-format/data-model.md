# Data Model: Entity file format engine support

Source: `docs/design/25-entities.md`.

## Common schema (every entity, every type)

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | str | yes | unique in the repo, kebab-case, stable forever |
| `type` | str | yes | one of the ten closed types |
| `name` | str | yes | |
| `aliases` | list[str] | no | defaults to `[]` |
| `setting` | str | yes | the setting id this entity belongs to |
| `status` | str | yes | one of `stub` \| `drafted` \| `complete` |
| `tags` | list[str] | no | defaults to `[]` |
| `sources` | list[dict] | no | each `{work, pages, licence}`; defaults to `[]` |
| `parent` | str \| None | no | the sole containment field; a `[[wikilink]]`-resolved id |
| `links` | list[str] | no | free association; ids, defaults to `[]` |

## The ten types and their additional fields

| Type | Recursive | Additional fields |
|---|---|---|
| `character` | no | `role` (nemesis\|ally\|companion\|bystander\|authority\|quarry), `archetype`, `disposition` (ally\|wary\|hostile\|hunting\|unaware), `allegiances` (list of org ids), `based_at` (place id), `objective` (`wants`, `because`, `next_step`, `blocked_by`, `escalates_to`, `timeline`), `stats` (dict, as printed by source) |
| `place` | **yes** | `scale` (world\|region\|settlement\|district\|building\|room), `connections` (list, see below), `danger` (int) |
| `organisation` | **yes** | `scale` (institution\|order\|chapter\|cell), `objective` (dict), `members` (list of character ids), `reach` (str) |
| `arc` | **yes** | `scale` (free label: campaign\|adventure\|scenario\|situation, no structural meaning), `entry` (`requires_threads`, `requires_state`, `hooks`), `exit` (`emits_threads`, `changes`, `leads_to`), `place` (place id), `cast` (list of character ids) |
| `beat` | leaf | (no additional fields defined by #305's scope — beat *behaviour* is #299) |
| `creature` | no | stat-block fields — out of this feature's scope beyond common schema; consumed by `docs/design/12-the-adversary.md`'s existing adversary block |
| `item` | no | (no additional fields defined by #305's scope) |
| `tracker` | no | `kind` (clock\|meter\|state), `value` (int), `max` (int), `advances_on` (list[str]), `fires` (dict[int, str]) |
| `thread` | no | (no additional fields defined by #305's scope) |
| `lore` | no | (no additional fields defined by #305's scope) |

A type with "(no additional fields defined by #305's scope)" still validates fully against the
common schema; this feature does not invent fields the design document has not specified, per
`CLAUDE.md`'s "a new type is an engine change" discipline applied to fields as well.

## Connection (element of `place.connections`, or any entity's connection list)

| Field | Type | Required | Notes |
|---|---|---|---|
| `to` | str | yes | target entity id (`[[wikilink]]`-resolved) |
| `via` | str | no | free text describing the route |
| `cost` | str | no | free text |
| `requires` | str | no | free text condition, preserved verbatim, not evaluated |
| `hidden` | bool | no | defaults to `false`; preserved distinctly in loaded data |

Connections form a graph, not a tree: `to` may point back at an ancestor or at any other entity,
and this is valid (unlike `parent`, which must be acyclic).

## Validation rules

- **Required-field check**: `id`, `type`, `name`, `setting`, `status` must be present and
  non-empty; `type` must be one of the ten; `status` must be one of the three.
- **Type-specific field check**: each type's additional fields (above) are validated for shape
  where the design specifies an enum or a structural pattern (e.g. `character.disposition` must be
  one of the five listed values; `place.connections` must be a list of connection mappings).
  Fields not present are treated as unset, not an error, unless the design marks them required
  (none of the type-specific fields are required beyond the common schema).
- **Containment resolution**: build a lookup of `id -> parent_id` across the loaded set; children
  of a given id are every entity whose `parent` resolves to it. A `parent` chain that returns to
  its own starting id is rejected.
- **Connection loading**: connections are loaded as given, with no acyclicity check, and no
  evaluation of `requires`.
- **Wikilink resolution**: any field holding a `[[...]]`-wrapped reference (or a list of them) is
  stripped to its bare id; if that id is absent from the loaded set, this is reported as an
  unresolved reference rather than silently ignored.

## State transitions

`status` moves `stub -> drafted -> complete` in the ordinary case (an author fleshing out a stub),
but this feature does not enforce that direction — `docs/design/25-entities.md` does not specify
one, and forcing monotonicity here would be inventing a rule the design document does not state.
