# ADR 0001 — Percentile resolution

**Status:** proposed
**Date:** 2026-08-21

## Context

Wyrd currently resolves as `d20 + skill vs 20` (Warlock's mechanic) with a separate `2d6`
pair — the Wyrd dice — carrying the side-effect axis. Two earlier schemes were rejected in
[`../../reference/dice-design.md`](../../reference/dice-design.md).

The question raised: what would move to **d100 roll-under** cost, and could the
multi-dimensional outcome survive it?

## The short answer on multi-dimensionality

**It survives, and gets cheaper and cleaner.** The `2d6` Wyrd dice contribute
nothing to the success calculation — that was the whole point of the third design. They do
not know or care what resolves success. Swapping `d20 + skill vs 20` for `d100 roll-under`
changes nothing about them: same 16.7% trigger, same five outcomes, same corruption gating.

That decoupling was adopted to fix an independence bug. It turns out to have made the
success mechanic **swappable**, which is a stronger property than it was designed for and is
worth noting as a general principle: keeping the axes separate keeps them replaceable.

### Better: the units digit *is* the Wyrd die

Under d100 the `2d6` become unnecessary. **The units digit of the roll is already an
independent d10.**

Success is decided by the whole value against the threshold. The units digit is uniform
*within* both the success set and the failure set — **exactly uniform at any skill that is a
multiple of 10**, and never more than 2 percentage points off otherwise:

| Skill | units 0–9 among successes | among failures |
|---|---|---|
| 30% | 10 10 10 10 10 10 10 10 10 10 | 10 10 10 10 10 10 10 10 10 10 |
| 45% | 11 11 11 11 11 9 9 9 9 9 | 9 9 9 9 9 11 11 11 11 11 |
| 75% | 11 11 11 11 11 9 9 9 9 9 | 8 8 8 8 8 12 12 12 12 12 |

That is *better independence than the `2d6` scheme achieves* — the 2d6 design still carried
residual skew (a hard-won success took a bane 0.5% of the time against a failure's 6.9%).
Here the worst case is a 2-point deviation.

So one roll yields three axes with no extra dice at all:

| Axis | Read from |
|---|---|
| Success / failure | the whole roll vs `skill%` |
| Magnitude | Success Levels — tens digit of skill minus tens digit of roll |
| What else happened | **the units digit** |

Proposed bands, with the natural 10% granularity:

| Units | Result |
|---|---|
| 0 | **Chaos Star** |
| 9 | **Comet** |
| 1–8 | nothing |

20% frequency, close to the `2d6` scheme's 16.7%, and **widening is a one-line house rule**:
`0–1` / `8–9` gives 40% with banes and boons added. Corruption gating gets natural
granularity too — the Chaos Star range widens from `0` to `0–1` to `0–2` as corruption rises.

It reads cleanly in text: *"Stealth 35, rolled 37 — failure by 0 degrees, and the 7 means
nothing else went wrong."*

### Rejected: reversing the digits

Tempting — a roll of 37 reversed is 73, so it looks like a free second value. It is not
independent. `reversed ≤ 04` requires units 0 and a low tens, so the original is in
{00,10,20,30,40} — all low, all successes. `reversed ≥ 95` requires units 9 and a high tens,
so the original is in {59,69,79,89,99} — all failures. Measured:

| | Chaos Star | Comet |
|---|---|---|
| on a success | 7–12% | **0–3%** |
| on a failure | 0–3% | 7–12% |

Systematically **anti-correlated**, and at skill 45+ a success cannot produce a Comet at all.
The extremes of the reversed value map straight back onto the extremes of the original —
the same class of bug as reading the side effect from the margin.

(Worth noting the reversed d100 *does* have a real use in WFRP: it is how 4e determines hit
location. Wyrd has no hit locations — criticals are by damage type — so the digit is free.)

### Also rejected: the d100's own doubles

A d100 shows doubles (11, 22, … 00) at 10%. On roll-under, a low double is a *good* roll and
a high double a *bad* one, so reading direction from the doubled value is anti-correlated in
the same way. WFRP 4e and Zweihander use exactly this (doubles = critical on a success,
fumble on a failure), which is right for a crit mechanic and wrong for an independent axis.

## Migration is exact

Warlock's skill ladder maps to percentages with **no probability drift at all**:

> **`skill% = (skill + 1) × 5`**

| Skill | `d20 + skill vs 20` | `skill%` |
|---|---|---|
| 4 | 25% | 25% |
| 6 | 35% | 35% |
| 10 | 55% | 55% |
| 12 *(career cap)* | 65% | 65% |
| 14 | 75% | 75% |

Difficulty maps as cleanly: Warlock's −2 / −4 become **−10 / −20**, which lands exactly on
WFRP's own difficulty ladder (Easy +20, Average +0, Challenging −10, Difficult −20, Hard
−30, Very Hard −40). We inherit a tested six-band ladder in place of Warlock's two.

## What d100 adds

**1. The library.** This is the decisive argument. Every WFRP edition (1e–4e), Zweihander,
and the entire 40k line — Dark Heresy, Rogue Trader, Deathwatch, Black Crusade, Only War —
is d100. That is roughly 700 PDFs of careers, NPCs, stat blocks, creatures, gear and
adventures that become **directly usable rather than requiring conversion**. The corpus
currently being OCR'd is d100 material. Under Warlock's scale, every one of those stat
blocks needs translating by hand or by model; under d100 they are read as printed.

For the 40k setting this is close to decisive on its own: Dark Heresy's careers and gear are
the obvious source and they are percentile-native.

**2. A magnitude axis for free.** `d100` yields **Success Levels** naturally — the tens digit
of the skill minus the tens digit of the roll. That is a genuine third dimension (did you
succeed · by how much · what else happened) at no dice cost, where `d20` gives nothing
comparable. Useful for opposed tests, for scaling damage, and for the "succeed at a cost"
texture Wyrd wants.

**3. Granularity that suits a decade.** Advancement in 1–5% steps gives a long chronicle
somewhere to go without the numbers inflating. Warlock's 4–12 ladder has nine rungs total.

**4. It reads well in text.** "Stealth 35, rolled 28 — success, 1 degree" is at least as
legible as `d20 + skill vs 20`, and roll-under needs no addition at all.

## What it costs

- **Warlock's own material needs converting** — careers, skill caps, tables. One book, and
  the mapping above is mechanical. Everything else in the library gets *easier*.
- **Opposed tests change shape** — from "higher total wins" to comparing Success Levels.
  This is a genuine behavioural change, not a representation change.
- **Some of Warlock's charm is its lightness.** `d100` is marginally more system. Though
  roll-under is arguably simpler than add-and-compare.
- Career caps of 10–12 become 55–65%, which is squarely WFRP-shaped and probably correct for
  a game where veterans stay fallible.

## Decision

**Proposed: adopt d100 roll-under**, and **retire the `2d6` Wyrd dice** — the units digit of
the roll replaces them, with better independence and no extra dice.

Classification per [`../09-evolution.md`](../09-evolution.md): **Structural** for basic
tests (representation changes, outcomes identical), **Behavioural** for opposed tests
(they genuinely resolve differently). Both require confirmation.

**Decide before implementation, not after.** No engine exists yet, so this costs nothing
today and a migration tomorrow. The playtest chronicle would need converting — four skill
values and a stamina track — which is minutes of work now.

## Open

- Do we adopt WFRP's **characteristics + skill advances** model wholesale, or keep Warlock's
  flat single-value skills expressed as percentages? The latter is simpler and preserves
  Wyrd's lightness; the former buys even closer library compatibility. **Leaning flat**, on
  the grounds that stat blocks are read for their numbers, not their derivation.
- Does Success Level replace or supplement the Wyrd dice for "how well"? They answer
  different questions — SL is magnitude, the Wyrd die is *what else* — so probably
  supplement, but this wants playtesting rather than argument.
