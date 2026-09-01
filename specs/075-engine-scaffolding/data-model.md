# Phase 1 data model: Engine scaffolding

This feature introduces no domain entities of its own (character, companion, etc. are later
features' concern — #209+). It defines only the minimal shapes needed to prove the two
load-bearing guarantees (deterministic dice, atomic persist-before-narrate state) end to end.

## Roll result

The structured object `verbs.roll` returns, and the shape `render.py` serializes to JSON.

| Field | Type | Description |
|---|---|---|
| `verb` | string | Always `"roll"` |
| `sides` | int | Number of sides on the die (100 for the standard case) |
| `result` | int | The rolled value, `1 <= result <= sides` |
| `seed` | int \| null | The seed used, if one was supplied; `null` for a genuinely random roll |

Validation:
- `sides` MUST be a positive integer (FR-004); `sides <= 0` is a structured error, not a roll.
- `result` is always in `[1, sides]` inclusive.

## Chronicle state (minimal, provisional)

The minimal on-disk shape this feature's `state.py` can round-trip, to demonstrate FR-005/006/007.
Later features (#209 The character model, etc.) will extend this shape; this feature is not
responsible for the eventual full schema, per the spec's Assumptions section.

| Field | Type | Description |
|---|---|---|
| `schema_version` | int | Format version of the state file, for future migrations |
| `last_roll` | object \| null | The most recent Roll result (above), or `null` if none yet |

State transitions: a `save(state)` call fully replaces the file's contents (no partial merge);
a `load()` call returns exactly what the last successful `save()` wrote. There is no other
lifecycle for this minimal shape — richer lifecycle rules belong to the entities later features
introduce.

Persistence invariant (FR-007): every `save()` call is atomic — write to a temp file in the same
directory, then `os.replace()` onto the target path. A reader never observes a partially-written
file.
