# ADR 0001 — Percentile resolution, with the units digit as the Wyrd die

**Status:** accepted 2026-08-21

## Context

Wyrd needs outcomes with **two independent axes**: did you succeed, and *what else happened*.
A bane must be able to land on a success and a boon on a failure — those are the two most
valuable results and the hardest to produce.

Independence is the requirement. Any scheme where the side effect is derived from *how well*
you rolled cannot produce them.

## Decision

> **Roll `d100`, succeed at or under `skill%`.**
> **Success Levels** (tens digit of skill minus tens digit of roll) give magnitude.
> **The units digit of the natural roll** is the Wyrd die.

One roll, three axes, no extra dice.

The units digit is uniform *within* both the success set and the failure set — exactly so at
any skill that is a multiple of ten, never more than two points off otherwise. That is
better independence than any scheme using separate dice achieved.

**The natural roll rule:** the Wyrd die is read from the dice as they first fell, never
modified and never rerolled. Modifiers apply to the skill, never the roll, which is what
keeps this true as the rest of the system evolves. It also prevents reroll laundering —
Fortune buys the result, never the world's reaction to the first attempt.

## Rejected

**Margin.** Reading the side effect from degree of success collapses both axes into one: a
large success can never carry a bane.

**A summed side die.** `3d6` with one die a different colour, all three summed. Still
correlated, and worst exactly where it matters — on a hard task a success *cannot* carry a
bane, because if the total cleared a high target the coloured die cannot have been low.

**A bell curve at all.** `3d6 + skill` was tried at two target numbers. At 20 a starting
character succeeded 16% of the time where a flat die gave 35%; at 17 the top broke instead —
at high skill a character literally could not fail. A bell curve compresses both tails, so it
delivers playable novices *or* fallible veterans, never both. Percentile is flat and does
both.

**Digit reversal.** A roll of 37 reversed is 73 — tempting as a free second value, but
systematically anti-correlated. `reversed ≤ 04` requires a low tens and units 0, so the
original is always low and therefore a success. Measured, a Fair Omen fell on 0–3% of
successes against 7–12% of failures.

**The d100's own doubles.** 11, 22, … 00 at 10%. On roll-under a low double is a good roll
and a high double a bad one, so reading direction from the doubled value is anti-correlated
in the same way.

## Consequences

- Skill values are percentages; difficulty is a flat modifier to skill.
- Source material that is already percentile can be read as printed
  ([ADR 0002](0002-source-system-compatibility.md)).
- Side-effect frequency is 20% at the default band, widening to 40% via house rules if play
  proves it sparse. The safer direction to be wrong in.
- The success mechanic is now swappable without touching the side-effect axis, since the two
  share no dice. Worth preserving.
