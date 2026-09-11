# Data model: End-to-end functional test suite

This feature adds no new persisted schema. It documents the existing entity shapes the sequence
reads and writes, so the test's assertions are traceable to something concrete.

## Player character (entity file, frontmatter)

Produced by `creation.create_character` (area 1) and mutated in place by every later area via
`character.load`/`character.save`.

| Field | Shape | Set/mutated by |
|---|---|---|
| `id` | str, filename stem by default | creation |
| `skills` | dict[str, int] | creation |
| `stamina` | `{"current": int, "max": int}` | creation; combat; downtime (`apply_rest`) |
| `fate` | `{"current": int, "max": int}` | creation |
| `wounds` | `list[dict]`, each `{"id", "effect", "closed", "bears_on"?}` | combat (`_stage_critical`); downtime (`apply_mend`) |
| `taint` / `trauma` / `strain` | int | resolution (`exposure`/`terror`/`system-of-power` mutations); rally |
| `reputation` | `{"score": int, "label": str \| None}` | economy (`adjust_standing`) |
| `coin` | int | economy (`spend_coin`) |
| `allegiances` | list | economy (`gain_allegiance`) |
| `advances_unspent` | int | rally (`apply_rally`'s award) |
| `hidden_threshold` / `transformations` | set on first taint-threshold crossing | resolution (exposure cascade) |

## Wound (nested in `wounds`)

`{"id": str, "effect": dict, "closed": None | <timestamp-shaped value>, "bears_on"?: str}`.
`effect` keys are restricted to `stamina_max`, `skill`, `dread` (`character.WOUND_EFFECT_KEYS`).
A `dread`/`stamina_max` wound closes on a single Mend; a `skill` wound steps down one rung before
closing on a second Mend; a `recurring: True` wound never closes.

## Adversary block (loaded from a bestiary fixture, not an entity file)

`{"id", "name", "baseline", "stamina_max", "armour", "skills", "damage"?, "damage_type"?,
"traits"?, "notes"?}` — validated and returned unchanged by `adversary.load`. To let an
adversary participate in `combat-attack`, its adjusted skill value is copied into a minimal
`type: creature` entity file (`character.save` accepts any dict; `validate_character` only
checks `wounds`).

## Proposal (in-memory, `resolution.propose`/`commit`/`discard`)

`{"proposal_id": str, "roll": dict, "mutations": list[dict], "steps": list[dict]}`. A mutation is
`{"entity": str(path), "field": str, "op": "+" | "set", "value": ..., "produced_by_step": int}`.
Never persisted until `commit(proposal_id)` is called; `commit`/`discard` invalidate the id.

## Chronicle pending state (`chronicle.py`)

`{"beat": ..., "awaiting": ..., "rolled": str | None}` — tracks at most one open proposal id per
actor; `record_rolled` raises if `rolled` is already set, `discard_at_rally` clears it and names
the proposal id (if any) to discard.

## Chronicle-level state (`state.py`)

`state.default_chronicle_state(name, engine_repo, engine_version, setting_repo,
setting_version)` returns the top-level `chronicle.yaml` shape; `save_chronicle`/`load_chronicle`
round-trip it to/from disk. Independent of the per-entity `state.save_entity`/`load_entity` path
every character file above uses.
