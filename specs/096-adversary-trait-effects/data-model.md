# Data Model: Adversary trait effects

No new persisted entity. This feature adds pure computations over the adversary block and
`traits` list #259 already defines and validates.

## `effective_block(block) -> dict`

A new dict, never mutating `block`, with:

| Field | Computation |
|---|---|
| `stamina_max` | `block["stamina_max"] + sum(stamina_max trait effects)`, floored at `STAMINA_MIN` |
| `armour` | `block["armour"]` shifted along `ARMOUR_RANKS` by `sum(armour_rank trait effects)`, clamped at either end |
| `damage` | `block["damage"]`'s dice count adjusted by `sum(damage trait effects)`, floored at 1 die, die size and flat modifier unchanged -- only present if `block` itself declares `damage` |
| `damage_type` | the last active `damage_type` trait effect's value, if any; otherwise `block["damage_type"]` unchanged |

Every other field of `block` (`id`, `name`, `baseline`, `skills`, `ranged`, `traits`, `notes`) is
carried through unchanged.

## `shift_difficulty(base: str, rungs: int) -> str`

Steps `base` along `tuple(resolution.DIFFICULTY_BONUSES)` (`easy, average, challenging,
difficult, hard, very_hard`) by `rungs` positions, clamped to the ladder's ends. `rungs` is
typically `sum(difficulty trait effects)`, computed by the caller for whichever test class it has
decided a `difficulty` trait applies to (spec.md Assumptions).

## `wyrd_band_width(block) -> int`

`max(0, sum(wyrd trait effects))` over `block["traits"]`.

## `rules._wyrd_die(natural_roll, omen_width: int = 0) -> str`

| `omen_width` | Ill Omen band | Fair Omen band |
|---|---|---|
| 0 (default, unchanged) | units digit == 0 | units digit == 9 |
| `w` | units digit in `0..w` | units digit in `(9-w)..9` |

`rules.opposed_test` gains the same `omen_width: int = 0` parameter, passed straight through to
`_wyrd_die`.

## State transitions

None. Every function here is a pure computation; nothing is persisted or mutated.
