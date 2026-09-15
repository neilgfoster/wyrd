# Phase 1 data model: Wyrd bootstrap skill

No new schema is introduced. Every shape below already exists in the engine
(`engine/wyrd/state.py`, `engine/wyrd/creation.py`) or in docs/design/25-entities.md; this records
which fields this skill reads and writes on each.

## Bootstrap intent record (`chronicle.yaml.json`)

Written by `wyrd-chronicle-template/bootstrap`. Read once, then deleted by this skill.

| Field | Type | Read by this skill for |
|---|---|---|
| `name` | str | chronicle identity, passed to `default_chronicle_state` |
| `engine.repo`, `engine.version` | str | chronicle identity |
| `setting.repo`, `setting.version` | str | chronicle identity, and which `setting/*.yaml` files to read for career/Loyalty/Drive/Misfortune data |
| `intent.about` | str | opening-situation selection |
| `intent.avoid` | list[str] | opening-situation selection (must not open on excluded content) |
| `intent.session_length` | int | carried through unchanged into `chronicle.yaml`'s `intent` |
| `intent.lethality` | `low`\|`standard`\|`high`* | passed to `create-character --mortality`; *bootstrap's own prompt uses `low`/`standard`/`grim` — reconciled against `creation.MORTALITY_FATE`'s `low`/`standard`/`high` vocabulary during implementation, not assumed here |
| `intent.world_acts_offstage` | bool | carried through into `chronicle.yaml`'s `intent` |
| `pending_seed` | bool | existence check only — its being `true` is what confirms this skill has not yet run |

## Player character (`pc.yaml`)

Produced entirely by `create-character`'s returned frontmatter (`engine/wyrd/creation.py`). This
skill supplies the inputs `create-character` (`engine/wyrd/client.py`) requires and writes back
exactly what it returns:

| Input this skill gathers from the player | Passed as |
|---|---|
| chosen entry career | `--career-json` (looked up from `setting/careers.yaml`) |
| chosen ancestry, if the setting declares one | `--ancestry-json` |
| the 8-advance spend (which skills opened/raised) | `--actions-json` |
| chosen Loyalty | `--loyalty` |
| `intent.lethality` | `--mortality` |
| chosen Drive(s) | `--drives-json` |
| chosen Misfortune | `--misfortune` |
| the written Fault Line sentence | `--fault-line` |
| character name | `--name` |

Everything `pc.yaml` ends up containing (skills, Stamina, Fate, career_history, and so on) comes
from `create-character`'s own return value — never recomputed (spec FR-004).

## Opening situation

An `arc` and/or `beat` entity (docs/design/25-entities.md), written directly by this skill —
either newly created under `entities/`, or an existing `setting/` entity referenced as-is when one
already fits (no overlay needed just to *reference* a stub scene). No new fields beyond the
existing entity schema.

## Seeded Threat

Either:
- an **overlay** (`overlay/<id>.md`, `overlay_of: <setting-id>`) promoting an existing
  `setting/` character/organisation/place by adding a `threat:` block, when a personal connection
  already ties the character to some existing entity (e.g. the entity implicated by the chosen
  Misfortune); or
- a **new entity** under `entities/` carrying its own `threat:` block from creation, when no
  existing entity fits (spec's Edge Cases section).

Either way, the `threat:` block itself is the existing schema from docs/design/25-entities.md /
docs/design/19-campaign.md:

| Field | Value this skill supplies |
|---|---|
| `imminence` | an integer from the Imminence table (docs/design/19-campaign.md) matching how central a threat this is meant to be at the start of a chronicle — a judgment call, not a computed value |
| `connection` | concrete text naming what ties this Threat to the player character (spec FR-006), typically drawn from the chosen Misfortune |
| `clues`, `effects`, `ambient` | authored per the setting's own content, following the same schema an existing seeded/inherited threat in that setting already uses |

## Chronicle state (`chronicle.yaml`)

Assembled from `state.default_chronicle_state(...)` plus the recorded `intent`, then written via
the `save` CLI verb (`engine/wyrd/client.py`'s `save` verb, backed by `state.save_chronicle`).
Every required field (`_CHRONICLE_REQUIRED_FIELDS` in `engine/wyrd/state.py`) is satisfied by
`default_chronicle_state`'s own shape; this skill only overrides `intent` with the values read
from `chronicle.yaml.json`.
