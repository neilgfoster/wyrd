# Quickstart: Mortal blows, Fate, and death

Validation scenarios proving this feature works end-to-end. Run from the repo root with the
existing test/check tooling — no new setup.

## Prerequisites

```bash
cd /root/source/neilgfoster/wyrd
python3 -m pytest -q tests/engine/test_resolution.py
```

## Scenario 1 — a mortal critical forces death

1. Stage a fight where a combatant's critical lands on the top, open-ended row of its damage
   table (`roll.mortal == True`, per `#251`'s `_stage_critical`).
2. Stage that combatant's Aftermath with `mortal=True`, using a seed whose natural `d100` roll
   would land on a low, survivable row (e.g. `out-of-action`).
3. **Expect**: the staged step's `roll.key == "death"`, `roll.forced_mortal == True`, and the
   underlying roll/total are still recorded as actually rolled.

```bash
python3 -m pytest -q tests/engine/test_resolution.py -k mortal_forces_death
```

## Scenario 2 — a spent Fate point re-reads death

1. Stage an Aftermath step that lands on `death` (rolled or forced).
2. Call `close_death_row` for that step with a spender character whose `fate.current >= 1`.
3. **Expect**: the step's `roll.key` becomes the current worst non-death row (read from the live
   table, not hardcoded), `roll.fate_spent == True`, `roll.closed_by == "fate"`, and the spender's
   `fate.current` decreased by exactly 1.
4. Call `close_death_row` again against the same step. **Expect**: `ValueError` — nothing left to
   buy.

```bash
python3 -m pytest -q tests/engine/test_resolution.py -k fate_spend
```

## Scenario 3 — a Fate spend on a companion requires the player present and able

1. Stage a companion's Aftermath result to `death`.
2. Call `close_death_row` passing the player character's state as `spender_state` and the
   companion's state as `companion_state`, under three conditions: player present & able; player
   present but incapacitated; player absent.
3. **Expect**: only the first condition succeeds; the other two raise/reject and leave the
   companion's result at `death` with `status` unset by this path.

```bash
python3 -m pytest -q tests/engine/test_resolution.py -k companion_fate_gate
```

## Scenario 4 — `mortality: low` closes death unconditionally

1. Stage an Aftermath step (rolled or mortal-forced) with `mortality="low"` and a combatant
   holding `fate.current == 0`.
2. **Expect**: the step's `roll.key` is the worst non-death row, `roll.closed_by == "mortality"`,
   `roll.fate_spent == False`, and `fate.current` is unchanged.

```bash
python3 -m pytest -q tests/engine/test_resolution.py -k mortality_low_closes
```

## Scenario 5 — companion status transitions

1. Resolve a companion's Aftermath result to a standing `death` (no closure available).
   **Expect**: the companion's `status` becomes `dead`.
2. Resolve a companion's Aftermath result to `taken`. **Expect**: `status` becomes `away`.
3. Resolve the player character's own result to a standing `death`. **Expect**: no `status`
   mutation is attempted for the player character (FR-011).

```bash
python3 -m pytest -q tests/engine/test_resolution.py -k companion_status
```

## Determinism check

```bash
python3 tools/check_death_row_determinism.py
```

Asserts both re-read directions (mortal-critical-to-death, Fate-spend-off-death) are fully
deterministic and idempotent across repeated resolutions of the same inputs (SC-002).

## Full suite

```bash
ruff check . && ruff format --check . && python3 -m pytest -q
```
