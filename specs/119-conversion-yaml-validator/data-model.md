# Data Model: conversion.yaml

Schema source: `docs/design/24-authoring-a-setting.md`, "Conversion rules" section.

| Field | Type | Required | Validation |
|---|---|---|---|
| `from` | mapping | yes | present; no further shape checked (free-text `system`/`edition`) |
| `version` | int | yes | positive integer |
| `skills` | mapping | no | if present, `method` in {direct, scale, table} when given; `map` mapping of string→string when given |
| `difficulty` | mapping | no | if present, `map` mapping of string→int when given |
| `damage` | mapping | no | if present, `method` free-text; `wounds_to_stamina` free-text; any `damage_type` value found is checked against the closed four |
| `armour` | mapping | no | if present, `method` in {direct, scale, table} when given; `map` mapping when given |
| `danger` | mapping | no | if present, `derive_from`/`formula` free-text strings when given |
| `rename` | mapping | no | mapping of string→string |
| `arcs` | mapping | no | mapping of string→string (structure mapping is free-text on both sides) |
| `drop` | list | no | list of strings |
| `drop_note` | string | no | string |
| `manual` | list | no | list of strings |

Closed vocabularies:
- `skills.method` / `armour.method`: `direct`, `scale`, `table`
- `damage_type` (wherever it appears): `slashing`, `piercing`, `blunt`, `searing` (docs/adr/0022)

Unrecognised top-level fields, or unrecognised keys within a known section's mapping, are
rejected — same closed-schema contract as `check_gear.py`.
