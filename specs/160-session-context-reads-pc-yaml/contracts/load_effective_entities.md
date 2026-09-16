# Contract: `verbs.load_effective_entities`

This feature adds no new CLI verb and no new public function — it changes the observable
contract of one existing internal function that four existing verbs already call.

## Before

```python
def load_effective_entities(chronicle_dir: pathlib.Path) -> dict[str, dict]:
    """Every setting/*.md entity resolved against overlay/*.md, plus every entities/*.md file."""
```

Never includes a chronicle's `pc.yaml`, even when one exists.

## After

```python
def load_effective_entities(chronicle_dir: pathlib.Path) -> dict[str, dict]:
    """Every setting/*.md entity resolved against overlay/*.md, plus every entities/*.md file,
    plus pc.yaml (the player character) if it exists at the chronicle root."""
```

Same signature, same return shape (`dict[str, dict]`, keyed by entity id). The only observable
change: when `<chronicle_dir>/pc.yaml` exists, its entity is now present in the returned dict.

## Callers affected (all four already use this function; none change their own signature)

| Verb | Effect of this change |
|---|---|
| `session_context` | `loadtier.always_tier(entities)`'s `_is_player_character` predicate now finds the `pc.yaml` entity, so `player_character` is populated instead of always `null`. |
| `get` | `get <pc-id>` now resolves, where it previously raised `state.StateError` (id not found). |
| `find --type character` | The player character's id now appears among matching results. |
| `party` | Unaffected in practice (the player character is never `role: companion`), but sees the same enlarged entity set as every other caller for consistency. |

## Failure modes

| Condition | Behavior |
|---|---|
| `pc.yaml` does not exist | Unchanged — no entry added, `player_character` stays `null`. |
| `pc.yaml` exists, valid | New entity present under its own `id`. |
| `pc.yaml` exists, fails schema validation | `state.StateError` raised, naming `pc.yaml` — same failure shape as an invalid `entities/*.md` file. |
| `pc.yaml` and an `entities/*.md` (or resolved setting/overlay) entity both declare `role: player` | `loadtier.always_tier` raises `ValueError` listing both ids — unchanged existing behavior, now reachable via this new source. |
