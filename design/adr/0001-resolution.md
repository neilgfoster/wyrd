# ADR 0001 — Percentile resolution, with the units digit as the Wyrd die

**Status:** accepted 2026-08-21

## Context

Wyrd needs outcomes on **two independent axes**: whether the action succeeded, and *what else
happened*. An **Ill Omen** must be able to land on a success and a **Fair Omen** on a failure
— those are the two most valuable results and the hardest to produce.

Independence is the whole requirement. Any scheme deriving the second axis from *how well*
the first went cannot produce them.

## Decision

> **Roll `d100`. Succeed at or under `skill%`.**
> **Degrees of success** — tens digit of the skill minus tens digit of the roll — give
> magnitude.
> **The units digit of the natural roll** is the **Wyrd die**.

One roll, three axes, no extra dice.

The units digit is uniform *within* both the success set and the failure set: exactly uniform
at any skill that is a multiple of ten, and never more than two points off otherwise. That is
better independence than any scheme using a separate die achieved here.

**The natural roll rule.** The Wyrd die is read from the dice as they first fell — never
modified, never rerolled. Difficulty modifies the **skill**, never the roll, which is what
keeps this property true as the rest of the engine changes. It also closes reroll laundering:
Fortune buys the result, never the world's reaction to the first attempt.

## Alternatives rejected

**Margin.** Deriving the Wyrd die from degrees of success collapses two axes into one. A
large success can then never carry an Ill Omen — losing exactly the result the axis exists
for.

**A summed side die.** A separate die of a different colour, added to the total alongside the
others. Still correlated, and worst where it matters: against a hard difficulty a success
*cannot* carry an Ill Omen, because a total high enough to succeed forecloses a low die.

**A bell curve.** Tried at two thresholds. At the first, a starting character succeeded 16%
of the time at tasks a flat die gave 35%; at the second, the top broke instead and a highly
skilled character could not fail at all. A bell curve compresses both tails, so it yields
playable novices *or* fallible veterans, never both. A flat distribution gives both, which
matters because [`../01-principles.md`](../01-principles.md) leaves the power curve to the
setting: a bell curve would decide it for every setting at once.

**Digit reversal.** Reading the roll backwards looks like a free second value and is
systematically anti-correlated: a low reversed value requires a low roll, which is a success.
Measured, a Fair Omen fell on 0–3% of successes against 7–12% of failures.

**The roll's own doubles.** Matching digits occur at 10%, but on roll-under a low double is a
good roll and a high double a bad one, so direction read from the doubled value is
anti-correlated in the same way.

## Consequences

- Skills are percentages; difficulty is a flat modifier to the skill.
- Material already expressed in percentages can be read as printed
  ([ADR 0002](0002-source-material.md)).
- Wyrd-die frequency is 20% at the default band — units `0` and `9` — widening to 40% via
  `houserules.yaml` if play shows it sparse. The safer direction to be wrong in.
- Taint can bend the die without touching competence, because the two are read separately
  ([`../03-rules.md`](../03-rules.md)).
- The success mechanic is now swappable without disturbing the second axis, since they share
  no dice. Worth preserving deliberately.
