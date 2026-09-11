# Contract: `engine/wyrd/state.py` chronicle-schema additions

This is a library module, not a network/CLI surface — the "contract" is the public function
signatures and their guarantees. All additions extend the existing module in place (no new file).

## `default_chronicle_state(name, engine_repo, engine_version, setting_repo, setting_version) -> dict`

Returns a fresh chronicle state per data-model.md's **Fresh chronicle** transition:
`created_under` equals `version` for both `engine` and `setting`; `sessions: 0`;
`danger_rating` and `calendar`/`era`/`migrations`/`intent`/`pending` at their documented defaults.

## `validate_chronicle(state: dict, previous_migrations: list | None = None) -> dict`

Validates `state` against data-model.md's rules 1–4, filling any absent optional field with its
documented default (rule 5), and returns the (possibly filled-in) mapping. Raises `StateError`,
naming the specific field/rule violated, on any failure. `previous_migrations`, when given, is
compared against `state["migrations"]`'s leading entries per rule 4.

**Guarantee**: called with a state that came from `load_chronicle()` immediately followed by an
in-place mutation (e.g. `append_migration`), `validate_chronicle` never raises for a field this
feature itself did not touch.

## `append_migration(state: dict, entry: dict) -> dict`

Returns a new state with `entry` appended to `state["migrations"]`. Does not mutate the `state`
argument's `migrations` list in place — callers get a fresh list back, so a caller holding a
reference to the old list is unaffected. Raises `StateError` if `entry["class"]` is not one of
the four allowed values (this is also checked again by `validate_chronicle`, so a caller that
skips `append_migration` and builds the list by hand is still caught at save time).

## `load_chronicle(path: pathlib.Path = DEFAULT_CHRONICLE_PATH) -> dict`

Reads `path` via the existing `load()`, applies `validate_chronicle()` (filling defaults, raising
on any missing required field or migration violation), and returns the validated mapping. If
`path` does not exist, returns `default_chronicle_state()`'s shape is **not** assumed here — unlike
`load()`, `load_chronicle()` requires the caller to have already created the file via
`save_chronicle(default_chronicle_state(...), path)`, since a fresh chronicle's identity (`name`,
`engine_repo`, etc.) cannot be invented by the loader. A missing file raises `StateError` naming
the path.

## `save_chronicle(state: dict, path: pathlib.Path = DEFAULT_CHRONICLE_PATH) -> None`

Validates `state` via `validate_chronicle()` (comparing against the file's currently-saved
`migrations`, read via a fresh `load()` of `path` if it exists, per FR-003/FR-004), then writes
via the existing atomic `save()`. Raises `StateError` without writing anything if validation
fails — a rejected write never touches the file on disk.
