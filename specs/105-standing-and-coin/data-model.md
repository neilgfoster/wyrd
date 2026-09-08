# Data Model: Standing and coin as one material position

## Character state additions

`docs/design/22-state.md`'s player-character frontmatter gains one field:

```yaml
coin: 0
```

`reputation: {score: 0, label: null}` already exists and is reused as Standing — no new field,
no rename.

`engine/wyrd/character.py`'s `PLAYER_CHARACTER_FIELDS` gains `"coin"`.

## Verbs

### `spend-coin`

Spends coin against a `gear.yaml` entry's price.

Input: `gear_id: str`, `coin: int` (current total), `catalog: list[dict]` (loaded gear entries).

Output:
- success: `{"verb": "spend-coin", "success": true, "coin": <new total>, "item": <gear entry>}`
- unknown id: `{"verb": "spend-coin", "success": false, "reason": "unknown gear id: <id>"}`
- insufficient coin: `{"verb": "spend-coin", "success": false, "reason": "insufficient coin: costs <price>, have <coin>"}`

Coin is never negative; a refusal leaves the caller's `coin` value to re-save unchanged.

### `martial-weapon-sighting`

Applies the martial-weapon Standing cost, once per open sighting.

Input: `standing: int` (current `reputation.score`), `already_applied: bool` (true when this
sighting has already been charged this scene — the caller/session log tracks which sighting is
which, per spec.md's Assumptions; the engine does not detect scenes).

Output: `{"verb": "martial-weapon-sighting", "standing": <new or unchanged>, "applied": <bool>}`

When `already_applied` is true, `standing` is returned unchanged and `applied` is `false`.
Otherwise Standing falls by 1 and `applied` is `true`.

### `adjust-standing`

A general scene-consequence Standing delta, no floor or ceiling.

Input: `standing: int` (current), `delta: int` (may be positive, negative, or zero).

Output: `{"verb": "adjust-standing", "standing": standing + delta}`
