# Phase 0 Research: Cascading resolution

## Decision: internal rolls within one `propose` call use a deterministic seed sequence

**Rationale**: A cascade can involve several dice within one `propose` call (attack roll, weapon
dice, armour dice, critical d6; Exposure roll, one or more Transformation d6, a hidden-threshold
d6). `rules.roll_d100` already accepts an explicit `seed`. This feature threads a single caller-
supplied base `seed` through the whole cascade by incrementing it by 1 before each subsequent
internal roll (first roll uses `seed`, the next uses `seed + 1`, and so on, including each die of
a multi-die `NdM` spec) — fully deterministic and reproducible from one caller-visible seed,
without needing a stateful RNG object threaded through every mechanic function.

**Alternatives considered**: passing a `random.Random` instance through every mechanic call
(rejected — every other function in this module takes a plain `int | None` seed, matching
`rules.roll_d100`'s own signature; threading an RNG object would be the only function in the
module to do so). Hashing the step id into the seed (rejected — unnecessarily indirect; a plain
increment is simpler to reason about and to disclose in a worked example).

## Worked example: the combat chain (SC-001)

Freshly computed (not asserted) with `python3`, reproducing the shape of
`docs/design/31-action-resolution.md`'s own combat-chain worked example (that document's own
numbers come from real hand-rolled dice in a playtest transcript, not a disclosed engine seed, so
this feature computes its own seeded scenario rather than claiming to reproduce numbers that were
never seed-disclosed in the first place):

Attacker `swordplay: 60`, target `swordplay: 0` (opposed via `rules.opposed_test`, `eff. 95`
after the ±50 clip), target Stamina `5`, weapon `1d8`, armour `1d3`, base seed `2`:

```
attack roll (seed 2):        8   -> succeeds against eff. 95, degrees 9 (telling, >= 6)
weapon-damage roll (seed 3): 4   -> doubled to 8 (telling)
armour roll (seed 4):        1
net damage: max(1, 8 - 1) = 7
Stamina: 5 - 7 = -2 (crosses below 0, 2 points below zero)
critical-slashing roll (seed 5): 5, + 2 below zero = 7 -> band 6-9, `slashing-scored`,
    wound record { dread: +1 }
```

## Worked example: the Taint-threshold-into-Transformation chain (SC-002)

Actor Taint `1`, major (3) Exposure tier (already-decided, matching #235's own
already-decided-tier convention), skill `eff. 35`, base seed `5`:

```
Exposure roll (seed 5): 80  -> fails against eff. 35, Taint +3 -> 4 (crosses threshold 3)
transformation roll (seed 6): 5 -> row 5, severity 3
    Taint: 4 - 3 = 1 (clears the threshold, no further re-roll needed)
    Dread: + 3
first Transformation -> hidden_threshold roll (seed 7): 3, + 2 = 5 -> set once
```

## Worked example: a multi-reroll Transformation cascade (SC-003)

Same actor/tier, base seed `7` (a different scenario, chosen because neither of the two worked
examples above needs more than one Transformation re-roll, and SC-003 requires demonstrating the
re-roll loop explicitly):

```
Exposure roll (seed 7): 42  -> fails against eff. 35, Taint +3 -> 4
transformation roll (seed 8): 2 -> row 2, severity 1
    Taint: 4 - 1 = 3 (still at the threshold -- re-roll)
    first Transformation -> hidden_threshold roll (seed 9): 4, + 2 = 6 -> set once
transformation roll (seed 10): 5 -> row 5, severity 3
    Taint: 3 - 3 = 0 (clears the threshold)
```

Two distinct rows (2 and 5) are drawn — the unique-per-character rule is satisfied without
needing to demonstrate the duplicate-skip path itself (a third scenario would be needed to force
an actual duplicate draw; not required by any Success Criterion, so not constructed here).

## Decision: `critical-slashing` only

**Rationale**: spec.md's Assumptions already state this; `docs/design/05-criticals.md`'s other
three tables (`critical-piercing`/`critical-blunt`/`critical-searing`) share the same die/modifier
shape and would be additive, not a redesign, when a future feature needs them.

**Alternatives considered**: implementing all four tables now (rejected — no worked example or
acceptance criterion in this feature exercises anything but slashing; guessing at how a weapon's
damage type is supplied by the caller, absent any gear-lookup integration, would be speculative).
