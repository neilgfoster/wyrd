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

**It survives untouched, because it is already decoupled.** The `2d6` Wyrd dice contribute
nothing to the success calculation — that was the whole point of the third design. They do
not know or care what resolves success. Swapping `d20 + skill vs 20` for `d100 roll-under`
changes nothing about them: same 16.7% trigger, same five outcomes, same corruption gating.

That decoupling was adopted to fix an independence bug. It turns out to have made the
success mechanic **swappable**, which is a stronger property than it was designed for and is
worth noting as a general principle: keeping the axes separate keeps them replaceable.

An alternative worth recording and rejecting: a d100 is two d10s, so **doubles are already
visible** (11, 22, … 00) at 10%. Tempting to use them as the trigger and drop the `2d6`.
Rejected because on a roll-under system a low double is a *good* roll and a high double a
*bad* one, so reading direction from the doubled value makes the side effect systematically
anti-correlated with success — the same class of bug as reading it from the margin. WFRP 4e
and Zweihander do exactly this (doubles = critical on a success, fumble on a failure), which
is fine for a crit mechanic and wrong for an independent axis.

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

**Proposed: adopt d100 roll-under**, keeping the `2d6` Wyrd dice exactly as they are.

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
