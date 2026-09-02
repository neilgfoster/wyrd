# Phase 0 Research: Partial reroll

No `NEEDS CLARIFICATION` markers — `docs/design/31-action-resolution.md` and #235/#236's already
-landed `resolution.py` answer every open question this feature needs.

## Decision: `propose_batch` is added, and `propose` becomes a single-request call to it

**Rationale**: `docs/design/31-action-resolution.md`'s own "independent branch survives a
reroll" worked example requires two unrelated top-level steps in one proposal — a capability
neither #235 nor #236 provides (both only ever staged one top-level mechanic call per proposal).
`propose_batch(requests, seed=...)` is the natural, minimal addition; `propose`'s existing
signature is preserved exactly by delegating to `propose_batch` with a single-element list.

**Alternatives considered**: adding reroll-batching as a special case only inside `reroll` itself
(rejected — the worked example this feature must reproduce is itself a *batch* proposal, not
something `reroll` invents; `propose_batch` is needed regardless of `reroll`).

## Decision: each top-level step records its own originating request as `inputs`

**Rationale**: `reroll` needs to redo exactly what originally produced the step it's rerolling —
same actor, mechanic, skill, target, difficulty, tier, dice — under the resource's modifier. The
simplest correct source of truth is the literal request dict `propose_batch`/`propose` already
built; storing it on the step avoids re-deriving or guessing it from the step's own roll data.

**Alternatives considered**: reconstructing the original request from the step's `roll` dict
(rejected — the roll dict is a *result*, not always sufficient to redo the call; `declaration_bonus`
and `difficulty`, for instance, are consumed into `effective_pct` and not separately recoverable
from it).

## Decision: only a top-level request is directly rerollable

**Rationale**: spec.md's Assumptions state this; every use of "reroll" in `docs/design/03-rules.md`
§§3-4 is the player's own test, never an internal cascade step. A step with no `inputs` (the
cascade-produced ones: `transformation`/`weapon-damage`/`armour`/`critical`) raises rather than
guessing what it would even mean to "redo" it under a modifier that was never defined for it.

**Alternatives considered**: making every step reconstructible and rerollable (rejected — no
worked example or acceptance criterion needs it, and `weapon-damage`/`armour` rolls have no
`effective_pct`/declaration-bonus concept for Resolve's `+20` to even apply to).

## Worked example: an independent branch survives a reroll (SC-001)

Senna Vask, Taint `0`, `bargaining: 35`, `stealth: 45`. Two unrelated minor Exposure sources,
proposed together — freshly computed with `python3` (not asserted), base seed `20260854`
(reused from `docs/design/31-action-resolution.md`'s own worked example, since it happens to
reproduce that document's own two rolls exactly, unlike this feature's later scenarios where a
fresh seed is used because the document's own numbers come from real hand-rolled dice):

```
step 0 (bargaining, eff. 35): roll 91 -- fails, Taint +1 staged
step 1 (stealth, eff. 45):    roll 38 -- succeeds, degrees 1, nothing staged
```

Spending **the Bargain** against step 0, reroll seed `5` (a fresh, disclosed seed for the reroll
itself -- not part of the original batch's own seed sequence, since `reroll` starts its own
`_SeedCursor`):

```
reroll of step 0 (eff. 35, unmodified -- Bargain is a plain reroll): roll 80 -- still fails
    mutations: Taint +1 (from the roll) + Taint +1 (the Bargain's own cost) = Taint +2 total
step 1: completely untouched -- same roll 38, eff. 45, degrees 1, no mutation
```

Committing applies Taint `+2` (both on step 0) and nothing from step 1 -- exactly the shape
`docs/design/31-action-resolution.md`'s own worked example describes.

## Worked example: a reroll discards a stale cascade and stages a fresh one (SC-002)

Senna Vask, Taint `1`, `bargaining: 35`, major (3) Exposure tier, base seed `5` (#236's own
research.md scenario, reused as the starting proposal):

```
step 0 (exposure, eff. 35): roll 80 -- fails, Taint +3 -> 4 (crosses threshold 3)
step 1 (transformation, depends_on [0]): row 5, severity 3 -- Taint 4-3=1, Dread +3,
    hidden_threshold set to 5
```

Spending **Fortune** against step 0, reroll seed `6`:

```
reroll of step 0 (eff. 35, unmodified -- Fortune is a plain reroll): roll 74 -- still fails,
    Taint +3 -> 4 (crosses the same threshold again)
    mutations: Taint +3 (roll) + fortune.current -1 (cost)
new step 1 (transformation, depends_on [0], a FRESH id continuing after the highest kept id):
    row 3, severity 2 (a different row than the original's row 5) -- Taint 4-2=2,
    Dread +2, hidden_threshold set to 4 (a fresh 1d6+2 roll, since hidden_threshold was still
    unset going into this reroll -- the original step 1's own set never actually committed)
```

The original step 1 (row 5, severity 3, hidden_threshold 5) is gone entirely from the revised
proposal -- replaced by the fresh cascade, never left alongside it.

## Worked example: each resource's modifier (SC-003)

Senna Vask, Taint `0`, `bargaining: 35`, minor Exposure tier, original propose seed `5` (roll 42,
fails, `eff. 35`). Rerolling the same step under each resource, reroll seed `1` for `resolve` (to
show a genuinely different roll under the modifier):

```
resolve  (seed 1): roll 18 against eff. 55 (35 + 20)      -- succeeds; resolve.current -1 staged
fortune  (seed 1): roll 18 against eff. 35 (unmodified)   -- succeeds too; fortune.current -1 staged
bargain  (seed 1): roll 18 against eff. 35 (unmodified)   -- succeeds too; taint +1 (cost) staged
```

(Roll 18 succeeds against every one of these effective percentages, so none of the three stages
an Exposure-implied Taint mutation here — only each resource's own cost. This still verifies
what SC-003 requires: the correct `effective_pct` per resource, and the correct cost mutation per
resource, independent of whether the roll happens to land inside or outside that percentage.)
