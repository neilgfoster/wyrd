# Data Model: The tracks that actually grow

## Character state additions

None. `docs/design/22-state.md`'s player-character frontmatter already declares `allegiances: []`,
`holdings: []` and `reputation: {score: 0, label: null}` — this feature adds verbs over those
existing fields, not new ones. `engine/wyrd/character.py`'s `PLAYER_CHARACTER_FIELDS` is
unchanged.

## Verbs

### `gain-allegiance`

Adds an allegiance id to a character's `allegiances` list, idempotently.

Input: `allegiance_id: str`, `allegiances: list[str]` (current list).

Output: `{"verb": "gain-allegiance", "success": true, "allegiances": <new list>}` — the id present
exactly once, whether or not it was already there. Order of existing entries is preserved; a
newly-added id is appended.

### `lose-allegiance`

Removes an allegiance id from a character's `allegiances` list.

Input: `allegiance_id: str`, `allegiances: list[str]` (current list).

Output:
- success: `{"verb": "lose-allegiance", "success": true, "allegiances": <list without the id>}`
- not held: `{"verb": "lose-allegiance", "success": false, "reason": "allegiance not held: <id>", "allegiances": <unchanged>}`

### `gain-holding`

Adds a holding id to a character's `holdings` list, idempotently. Same shape as
`gain-allegiance`, over `holdings` instead of `allegiances`.

Input: `holding_id: str`, `holdings: list[str]` (current list).

Output: `{"verb": "gain-holding", "success": true, "holdings": <new list>}`.

### `lose-holding`

Removes a holding id from a character's `holdings` list. Same shape as `lose-allegiance`, over
`holdings` instead of `allegiances`.

Input: `holding_id: str`, `holdings: list[str]` (current list).

Output:
- success: `{"verb": "lose-holding", "success": true, "holdings": <list without the id>}`
- not held: `{"verb": "lose-holding", "success": false, "reason": "holding not held: <id>", "holdings": <unchanged>}`

### `roll-standing`

Bands an already-rolled d100 value against a character's Standing (`reputation.score`) into one
of three outcomes. The engine does not roll the die itself (matching `roll()`'s own split of
randomness from banding).

Input: `standing: int` (current `reputation.score`), `roll: int` (1-100, already rolled).

Band widths, for a given `standing`:

```
favourable   = min(45, 5 + 5 * max(standing, 0))
unfavourable = min(45, 5 + 5 * max(-standing, 0))
neutral      = 100 - favourable - unfavourable
```

Rows `1..favourable` land "recognised favourably"; the next `neutral` rows land "not
recognised"; the remaining `unfavourable` rows land "recognised unfavourably". At `standing == 0`
this is 5/90/5 — recognition is rare and, when it happens, has no lean. Because favourable and
unfavourable are capped at 45 independently rather than jointly, neutral never falls below 50 in
practice (it would only reach the 45+45=90 floor if a single roll could be simultaneously
favourable-capped and unfavourable-capped, which a signed `standing` never is).
`check_reputation_roll.py` asserts these three widths sum to exactly 100 and cover 1-100 with no
gaps or overlaps, for a swept range of `standing` values, the same way `check_oracle_answers.py`
already asserts the oracle table's widths.

Output: `{"verb": "roll-standing", "outcome": "favourable" | "neutral" | "unfavourable"}`.
`roll_standing` never reads or writes any skill percentage, difficulty value, or other input to
`resolution.py`'s opposed-test path (FR-006).
