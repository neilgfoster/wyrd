# Playtest findings

Hand-run playtests of the Wyrd ruleset with **no engine**: dice rolled by script, arithmetic
by hand, state maintained by hand against [`../design/06-state.md`](../design/06-state.md).
The point is to find out whether Wyrd is enjoyable to play over text before building tooling
for it.

Chronicles live in their own repositories
([`../design/12-settings-and-parallel-play.md`](../design/12-settings-and-parallel-play.md)).

## Session 1 — three resolution mechanics in two rolls

The first playtest corrected the dice **three times**, and every correction came from play
rather than argument.

1. **`3d6 + skill` against a target of 20 was unplayable.** The defence — that `3d6` and
   `d20` share a mean — was true and irrelevant. What matters is the probability at the range
   actually rolled, and a starting character sat in the far tail: a test that should have
   succeeded 35% of the time succeeded 16%. Two attempts well within competence came in at
   9% and 16%, and both failed.
2. **Lowering the target to 17 fixed the bottom by breaking the top.** At high skill a
   character could no longer fail at all. A bell curve compresses both tails, so it can
   deliver playable novices *or* fallible veterans, never both.
3. **The error in both was making the side-effect dice part of the total.** Separating them
   resolved it — and percentile then made the separate dice unnecessary altogether, since the
   units digit of the roll is already independent.

Settled: `d100` roll-under, units digit as the Wyrd die
([ADR 0001](../design/adr/0001-d100-resolution.md)).

## What worked

The independent side-effect axis earned its place on the second roll of the campaign. The
failure and the complication were *separate facts*: a character did not merely fail to
convince someone, they also took a specific action that changed his position. That is the
texture the mechanic exists to produce, and it survived all three retunes.

## Still untested

Combat, the tracks, a Fate spend, party tension reaching a threshold, session length in
practice, and whether a 20% side-effect frequency is too sparse.
