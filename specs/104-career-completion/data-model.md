# Phase 1 Data Model: Career completion grants Stamina and a Mark

## The character view, widened

#277 defined a four-field view that a spend reads and returns. This feature adds three fields.
Every one of them is optional on input with a documented default, so a caller written against
#277 keeps working and simply never earns a payout it did not ask for.

| Field | Type | Default | Meaning |
|---|---|---|---|
| `career` | string | — | the career-instance the character currently occupies |
| `career_history` | list of entries | `[]` | careers left, and whether each instance completed |
| `skills` | map name → int | — | percentages |
| `advances_unspent` | int | `0` | the balance |
| `stamina_max` | int | `6` (`creation.STARTING_STAMINA`) | maximum Stamina, bounded at 10 |
| `marks` | list of entries | `[]` | one entry per completed career-instance, oldest first |
| `career_completed` | bool | `False` | has *this* instance already paid out |

`stamina_max` and `marks` map onto `stamina.max` and `marks` in `docs/design/22-state.md`'s
character frontmatter, which already exist. `career_completed` is new state the frontmatter does
not carry yet; persisting it is the caller's, and this feature does not touch the entity writer.

### Mark entry

```json
{"career": "guard"}
```

One key. The Mark's fictional content — the "one small benefit" §6 describes — is the GM's, the
same way a career change's fictional reason is. Duplicates are meaningful: two entries naming
`guard` mean the character completed Guard twice.

### Career-history entry (unchanged shape, changed source)

```json
{"career": "guard", "completed": true}
```

`completed` is now the departing instance's `career_completed` flag, not a fresh
`career_complete(skills, career)` computation. See research.md R3.

## Constants

| Constant | Value | Home | Source |
|---|---|---|---|
| `STAMINA_MAX_CEILING` | 10 | `advancement.py` | `tools/check_advancement.py`'s `stamina_ceiling()` |
| `STARTING_STAMINA` | 6 | `creation.py` (existing) | `specs/008-character-creation/check_creation.py` |

Both are asserted equal to the scripts' computed values in tests, never restated.

## The completion predicate

`career.career_complete(skills, career)` — true when the career grants at least one skill and
every granted skill is held at or above its cap. Ancestry is not consulted: an ancestry widens
what a character may *spend on*, never what a career *grants*.

## Payout transition

Inside `spend_advance`, after a `raise` or an `open` succeeds and before the result is returned:

```
was_complete  = view["career_completed"]
now_complete  = career.career_complete(new_skills, career)

if now_complete and not was_complete:
    marks       = [*view["marks"], {"career": career["id"]}]
    stamina_max = min(view["stamina_max"] + 1, STAMINA_MAX_CEILING)
    career_completed = True
```

Notes on the transition:

- It is evaluated for `raise` and `open` only. `change_career` cannot complete the career it is
  leaving, and the career it enters starts unpaid with the skills the character walked in with —
  a character entering a career they already satisfy the cap of is handled below.
- `min(...)` is what makes the ceiling a ceiling: at 10 the Mark is still appended, the Stamina is
  not.
- A refused spend never reaches this block, so FR-009 holds by construction.

### Entering a career already at cap

A `change_career` into a career every one of whose granted skills the character already holds at
cap arrives complete but unpaid, and there is no further spend inside it to trigger the payout.
This is deliberate: a career-instance nobody advanced in was never *completed*, it was walked
into. `career_completed` is set to `False` on entry and the instance pays only if a spend inside
it moves it from not-complete to complete — which, for such a career, never happens.

## Verb surface

No new verb. `spend-advance` carries the widened view through `verbs.spend_advance` and
`client._run_spend_advance` unchanged — both pass `--view-json` opaquely. Only the catalog
`description` changes, to say that a spend completing a career pays out.
