# Playtest findings

Hand-run playtests of the Wyrd ruleset with **no engine**: dice rolled by script, arithmetic
by hand, state maintained manually against the schema in
[`../design/06-state.md`](../design/06-state.md). The point is to find out whether Wyrd is
enjoyable to play over text before building tooling for it.

The chronicles themselves live in their own private repositories
(see [`../design/12-settings-and-parallel-play.md`](../design/12-settings-and-parallel-play.md)):

- **Hemmelfurt** (Reikland) — `neilgfoster/wyrd-chronicle-hemmelfurt`

## Findings so far

**Session 1 — two rules errors found in the first two rolls.**

1. **`3d6 + skill vs 20` is unplayable for starting characters.** The equal-mean argument
   against `d20` was true and irrelevant; what matters is probability at the range actually
   rolled. A skill-6 test succeeded 16% of the time instead of 35%. Wendel attempted two
   things within his competence at 9% and 16%.
2. **`3d6 + skill vs 17` fixed the bottom by breaking the top.** At skill 14 a character
   cannot fail at all (0.0%), and at the career cap of 12 the failure rate is 1.9% against
   Warlock's 35%. A bell curve compresses both tails: playable novices *or* fallible
   veterans, not both.

**Resolution (settled 2026-08-21):** `d100` roll-under, with the **units digit of the natural
roll** as the Wyrd die — one roll, three independent axes, no extra dice. The `d20 + 2d6`
scheme above was itself superseded within the day. See
[`../reference/dice-design.md`](../reference/dice-design.md) and
[ADR 0001](../design/adr/0001-d100-resolution.md).

**What worked.** The independent side-effect axis earned its place immediately. On roll 2
the failure and the bane were separate facts: Brida didn't merely disbelieve him, she took a
specific action that changed his position. That is exactly the texture the mechanic exists
to produce, and it survived both retunes.

**Still untested:** combat, corruption, Fate spends, party tension reaching a threshold,
session length, and whether 16.7% side-effect frequency is too sparse.
