# Quickstart: Related settings — shared worlds and kindred tone

## Prerequisites

- Python 3.11+, standard library only.
- A checkout of this repository with `settings.yaml` present.

## Declare a same-world relation

Add an entry to the new `relations:` list in `settings.yaml`:

```yaml
relations:
  - a: wh40k-darkheresy
    b: wh40k-onlywar
    kind: same-world
```

## Declare a kindred-tone relation

```yaml
relations:
  - a: some-grim-setting
    b: some-other-grim-setting
    kind: kindred-tone
```

## Validate the catalogue

```bash
python3 tools/check_settings_catalogue.py
```

Expected outcomes:

- Exits 0, reporting no problems, when every relation names two distinct existing settings and no
  pair is declared under both `kind` values.
- Exits non-zero and names the specific problem for: an unknown setting id in `a`/`b`; `a == b`;
  the same unordered pair declared twice (with the same or different `kind`); the same pair
  declared as both `same-world` and `kindred-tone`.

`--format json` (existing flag) includes the relation-validation findings alongside the existing
fleet-drift findings.

## Record a borrowed entity's provenance

When a setting author copies an entity (character, creature, location, adventure, threat) from a
related setting, the resulting entity — in the *destination* setting's own data — carries:

```yaml
borrowed:
  from_setting: wh40k-darkheresy
  from_entity: inquisitor-varn
  relation: same-world
  on: 2026-09-12
```

This mirrors the existing `converted: {rules, on}` stamp used for entities converted from a
published source (`docs/design/24-authoring-a-setting.md`) — an entity carries one or the other,
never both. `relation:` must match a `relations:` entry that actually exists between the two
settings at the time of borrowing (validated the same way conversion's `from`/`version` fields are
validated for a converted entity, once a setting defines the concrete entity schema this stamp
attaches to — out of scope for this feature per its own Assumptions).

## What this feature does not include

- No tooling that performs an actual borrow (copying and reskinning an entity's file from one
  setting repository into another) — this feature specifies the declaration and provenance schema
  only, per the issue's own "out of scope: the actual conversion of any specific content."
- No change to any specific setting repository's content — `settings.yaml` and
  `docs/design/24-authoring-a-setting.md` live in this (public, engine) repository; the settings
  themselves, and any entity that ends up stamped `borrowed:`, live in their own `wyrd-setting-*`
  repositories.
