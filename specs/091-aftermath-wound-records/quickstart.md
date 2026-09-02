# Quickstart: The Aftermath table and wound records

## Prerequisites

- `engine/` installed per the repo's existing dev setup (stdlib-only, no install step beyond the
  repo checkout).

## Validate the roll and table

```bash
cd engine
python3 -c "
from wyrd import resolution

steps = []
resolution._stage_aftermath(
    steps, entity='pc', points_below_zero=3, depends_on_step=0,
    seed_cursor=resolution._SeedCursor(seed=1), bears_on_skill='melee',
)
print(steps[-1])
"
```

Expected: one step with `mechanic: aftermath`, a `roll.table` of `aftermath`, a `roll.key` naming
one of the 8 published rows, and (for a wound-producing row) one mutation appending a wound record
that validates against `character.validate_wound`.

## Validate the boundaries and table structure

```bash
cd engine
python3 -m pytest ../tests/test_resolution.py -k aftermath -q
```

Expected: all boundary and wound-shape assertions pass (User Stories 1–3 of spec.md).

## Validate the computed odds

```bash
python3 tools/check_aftermath_odds.py
```

Expected: exits 0, asserting the unweighted 71% lasting-mark / 23% death figures
`docs/design/06-aftermath.md` itself publishes, computed across drops of 1–12 points below zero —
not eyeballed (SC-003, CLAUDE.md's deterministic-over-inference rule).
