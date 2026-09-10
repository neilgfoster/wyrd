# Data Model: Setting Overrides Mechanism

## Overridable set entry

The closed set `describe --overridable` reports. Not persisted -- computed from
`overrides.OVERRIDABLE`, a static mapping in code.

| Field | Type | Notes |
|---|---|---|
| `name` | string | The engine's own identifier for the mechanism (e.g. `taint`). Never changes. |
| `kinds` | list of string | Which of `disable`/`rename`/`tables`/`extend` are legal against this mechanism. |
| `depends_on` | list of string | Other mechanisms this one depends on -- reserved for the contradiction check as the dependency graph grows; empty for every entry seeded by this feature. |

## Override block

The shape of one layer's `overrides:` mapping (a setting's `setting.yaml`, or a chronicle's
`houserules.yaml`). All four keys are optional.

| Key | Type | Meaning |
|---|---|---|
| `disable` | list of mechanism name | Mechanisms switched off entirely at this layer. |
| `rename` | mapping of mechanism name → string | Presentation-only relabeling; the value is never a mechanism name, it is the word rendered to a person. |
| `tables` | mapping of mechanism name → path | Wholesale replacement of a table, by the engine's own name for it. |
| `extend` | mapping of mechanism name → path | An additional file whose rows are appended, never replacing the engine's own. |

Validated by `overrides.validate_block()`: every key must be one of the four; every named
mechanism must be in the closed set and support the kind it's named under; a mechanism may not be
named under `disable` and any other key in the same block (the contradiction case).

## Resolved configuration

The single output of `overrides.resolve()`, applying engine defaults → setting overrides →
chronicle houserules in order.

| Field | Type | Notes |
|---|---|---|
| `disabled` | frozenset of mechanism name | Union of every layer's `disable` list. Once a mechanism is here, no later layer may name it under any key (narrowing-only). |
| `renames` | mapping of mechanism name → string | Last layer to rename a mechanism wins. |
| `tables` | mapping of mechanism name → path | Last layer to retune a mechanism's table wins. |
| `extends` | mapping of mechanism name → list of path | Every layer's extension path for a mechanism, in layer order -- accumulates rather than replacing (see research.md). |

Two derived operations:

- `label(mechanism)` — the word to render: the rename if one applies, else the mechanism's own
  name. Never affects what is stored.
- `is_enabled(mechanism)` — whether a mechanism may still be acted on at all.

## Filtered catalog entry

`overrides.filter_tools()`'s output shape, applied to `catalog.TOOLS`. A tool entry unrelated to
any mechanism (no `mechanisms` key) passes through untouched. A tool entry that names
`mechanisms` (e.g. `track`, listing `["taint", "trauma"]`) is:

- **dropped entirely** if every mechanism it names is disabled;
- **narrowed** (its `mechanisms` list, and any `inputSchema.properties.mechanism.enum`, reduced
  to the still-enabled subset) if only some are disabled;
- **untouched** if none are disabled.

## Relationships

```
ResolvedConfig
   ├── built from  →  [ ("engine", {}), ("setting", overrides_block), ("chronicle", houserules_block) ]
   ├── validated against  →  OVERRIDABLE (the closed set)
   └── consumed by  →  filter_tools(TOOLS, resolved)  →  what `describe` reports
                     →  verbs.track(..., resolved=resolved)  →  disable/rename enforcement at the verb boundary
```
