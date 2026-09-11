# Data Model: Threats aspect & activation

## `threat` block

Attached to the frontmatter of any entity (`character`, `organisation`, or `place`,
docs/design/19-campaign.md). This feature treats it as a plain `dict` with the following fields —
no schema-validating class is introduced; validation (if any) belongs to `entity.py`'s existing
common/type-specific schema layer, which this feature does not modify.

| Field | Type | Required | Notes |
|---|---|---|---|
| `imminence` | `int` | yes | `0` means inactive (excluded from the active set); `> 0` means live. Promotion (FR-006) rejects `<= 0`. |
| `clues` | `list[str]` | no | ordered discovery path; not read by this feature's functions. |
| `effects` | `dict[str, Any]` | no | range-keyed table (`"1"`, `"3-6"`, `"7"`, ...), rolled on activation. Keys parsed the same way `journey._parse_range` already does. |
| `ambient` | `list[str]` | no | standing costs while within reach; not read by this feature's functions (routed by the caller, per journey.py's existing convention). |
| `counters` | `list[str]` | no | not read by this feature's functions. |
| `weakness` | `str` | no | not read by this feature's functions. |
| `connection` | `str` | no | not read by this feature's functions. |
| `known_to_player` | `"none" \| "rumoured" \| "partial" \| "understood"` | no | not read by this feature's functions. |

## Function signatures (pure, no I/O)

- `active_threats(entities: list[dict]) -> list[dict]`
  Returns the subset of `entities` carrying a `threat` block with `imminence > 0` (FR-001,
  FR-002). Each returned item is the *entity* dict (not just its `threat` block), matching
  `journey.legs_for`'s convention of returning caller-shaped records.

- `check_activation(imminence: int, wyrd_roll: int) -> bool`
  `wyrd_roll <= imminence * 10` and `imminence > 0` (FR-003). Mirrors
  `journey.roll_hazard`'s activation half exactly.

- `resolve_effects(effects: dict, table_roll: int) -> dict`
  Matches `table_roll` against `effects`' range-keyed entries (FR-004); returns
  `{"matched": <entry>}` or `{"matched": None}` for an unmatched roll or an empty table — mirrors
  `journey.roll_hazard`'s existing no-op-on-no-match convention.

- `promote(entity: dict, threat: dict, objective: str) -> dict`
  Returns a new dict: `entity` with `threat` and `objective` attached, every other field
  unchanged (FR-005). Raises `ValueError` if `entity` already carries a `threat` block, or if
  `threat["imminence"]` is not `> 0` (FR-006) — matching `entity.py`'s existing convention of
  raising `ValueError` for a rejected write rather than returning a sentinel.

## State transitions

- **Seeded/inherited**: an entity is created (elsewhere, out of scope) already carrying a
  `threat` block with `imminence > 0` — no transition through this module.
- **Promoted**: `promote()` moves an entity from "no `threat` block" to "carries one" — the only
  transition this feature performs directly.
- **Faded**: an external caller (out of scope — `advance-time` or GM action) reduces `imminence`
  to `0`. This feature's contract is only that `active_threats` immediately excludes it once that
  happens (FR-007) — no explicit "fade" function is needed since imminence is a plain field the
  caller can set directly.
