# Data Model: Mortal blows, Fate, and death

No new persisted entity or file shape is introduced. This feature extends the in-memory step/
mutation shapes `resolution.py` already defines.

## Aftermath step (extended)

The `aftermath` step `_stage_aftermath` produces (`docs/design/06-aftermath.md` "Reading a
result") gains two new possible states of its recorded `key`/`row`, both already anticipated by
the design doc's own worked example (`"fate_spent": false`):

| Field | Type | Notes |
|---|---|---|
| `roll.key` | `str` | unchanged shape; may now be forced to `death` (mortal critical) or re-read off `death` onto the worst non-death row (Fate spend / `mortality: low`) |
| `roll.forced_mortal` | `bool` | new — `True` when this step's row was forced to `death` by a mortal critical rather than reached by the roll itself |
| `roll.fate_spent` | `bool` | already named in the design doc's worked example; `True` only when a *Fate spend* closed this result — never set for a `mortality: low` closure |
| `roll.closed_by` | `str \| None` | new — `"fate"`, `"mortality"`, or `None` (result stands as rolled/forced); disambiguates a `mortality: low` closure from a Fate spend without overloading `fate_spent` |

## Fate (existing field, new consumer)

`fate.current`/`fate.max` (`character.py`'s `PLAYER_CHARACTER_FIELDS`) is read and decremented by
`close_death_row`. No shape change — this feature is a new consumer of an existing field, not a
new field.

| Field | Type | Notes |
|---|---|---|
| `fate.current` | `int` | decremented by exactly 1 on an accepted Fate spend; unchanged on a `mortality: low` closure (there is nothing to spend) or a rejected spend |

## Companion status (existing field, new consumer)

`status` on a `character` entity with `role: companion` (`docs/design/22-state.md`) is set by this
feature's companion-status helper. No new value is introduced to its vocabulary.

| Value | When set |
|---|---|
| `dead` | the companion's Aftermath result stands as `death` (not closed by Fate spend or `mortality: low`) |
| `away` | the companion's Aftermath result is `taken` (held) |
| *(unchanged)* | any other row — this feature never touches `status` for a non-`death`/`taken` result |

## New function signatures (behavioural contract, not a data shape)

```text
_stage_aftermath(steps, entity, points_below_zero, depends_on_step, seed_cursor,
                  bears_on_skill, *, mortal: bool = False, mortality: str = "standard") -> None
    # mortal=True forces roll.key to "death" regardless of the rolled total.
    # mortality="low" then re-reads a "death" key (forced or rolled) onto the worst
    # non-death row, setting roll.closed_by = "mortality".
    # Both closures are staged inline -- no second call, no player input required.

close_death_row(steps, step_id, entity, *, spender_state: dict,
                 companion_state: dict | None = None) -> list[dict]
    # step_id must reference an existing `aftermath` step whose roll.key == "death" and
    # roll.closed_by is None -- otherwise raises ValueError (spec.md FR-002/FR-004).
    # Rewrites that step's roll.key to the worst non-death row, sets
    # roll.closed_by = "fate" and roll.fate_spent = True, decrements spender_state's
    # fate.current by 1, and (when companion_state is not None) sets its status per the
    # table above. Returns the list of mutations applied, for the caller to persist.
```
