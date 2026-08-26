# ADR 0026 — Danger scales a skill in points, not in multiples

**Date:** 2026-08-25
**Status:** Accepted

## Context

[`03-rules.md`](../design/03-rules.md) §7 has said since the ruleset was written that content scales from a
danger rating, and that:

> enemy counts **and skill values** scale from the same number

The count half was settled by [ADR 0024](0024-a-party-is-worth-less-than-its-head-count.md), which
defined `party_effective`, read both sides of the ratio through the same curve, and fixed the
rounding at the point of use. **The skill half was never evaluable**, and the reason is arithmetic:
`danger_effective` is a multiplier, and a percentage multiplied by a multiplier is not a percentage.
A 45% opponent in a danger-3 encounter run at `danger_effective` 2.64 is not a 119% opponent.

So §7 published a claim about two quantities and delivered one, and the missing half read as
authoritative because the sentence naming it was correct English. Nothing about it looked wrong —
the fourth fault class in [`CLAUDE.md`](../../CLAUDE.md).

Once [ADR 0025](0025-an-adversary-is-a-thin-block.md) gave an opponent a schema, the gap became
load-bearing: an adversary block carries absolute percentages, and something has to say what happens
to them when the party is not the party the content was written for.

## Decision

**The skill half of §7 resolves to a points adjustment added to the opponent's percentage.**

> `adjustment = 15.5 × log₂(ratio)`, rounded to the nearest **5** and clipped to **±20**,
> where `ratio = party_effective / H(written_for)`.

The adjusted percentage floors at 0.

**The block itself never changes.** A bestiary entry means one thing whatever content refers to it;
scaling happens when content is prepared. Otherwise the same creature reads differently in two arcs
and neither reads as wrong.

Four properties, and none of the numbers in them was chosen before the arithmetic:

**Additive, in the engine's own units.** Every other modifier in this engine is additive on the
skill — the difficulty ladder in §1 is +20 to −40, assistance is a bounded bonus, declaration is +10
or +20. A multiplicative modifier would be the only one, and it would compound with all of them
unpredictably.

**Exactly +0 on the diagonal.** Content written for four, run by four bodies, meets opponents at
exactly their written percentages. That is the identity case ADR 0024 exists to protect, now holding
on both quantities §7 scales rather than on the count alone.

**The coefficient is fitted, not picked.** Across every party size and `written_for` from one to
six, the ratio runs `0.408` to `2.450` — exactly antisymmetric, because swapping the two inverts it.
Requiring the extreme of that computed range to land on the ladder's top rung yields
`20 / log₂(2.45) = 15.4705`, which the published `15.5` reproduces cell for cell. The range was
computed before the curve was fitted to it, and the printed figure is asserted against the printed
table in [`check_adversary.py`](../../specs/017-adversary-model/check_adversary.py) — a round number
in a design document means nothing here unless something checks it.

**The clip is symmetric at ±20**, not the ladder's asymmetric −40, because the adjustment must
negate when party and `written_for` swap. A −40 floor against a +20 ceiling breaks exactly that.

## Why not counts only

The leaner answer was to scale the count and leave percentages alone — and then §7's published
sentence would have been **wrong**, and corrected in place.

It is a real option. It keeps a stat block meaning exactly one thing at every difficulty, needs no
curve, and needs no ADR. It was rejected because it leaves the engine one lever where the design has
always claimed two, and the missing lever is the one that matters at the extremes: a party of six
walking into content written for one meets *more of the same*, endlessly, rather than anything
harder. A solo chronicle meant to stay interesting for years cannot have its only difficulty
control be a body count.

## Why not a separate tougher entry

Content could scale counts and, where it wants harder opposition, point at a different bestiary
entry — a veteran, a champion. Explicit, readable, no arithmetic.

Rejected: it pushes the work onto every setting author, multiplies entries by however many rungs a
setting wants, and gives the engine no answer at all for a party size nobody wrote an entry for.

## Why not multiply the percentage

Named for completeness, because it is what the published sentence literally implies and someone will
propose it again. `45 × 2.64` is 119, and `45 × 0.48` is 22. The first is off the top of the ladder
and the second is a different opponent. There is no clipping rule that rescues it, because the
identity case is the only point where multiplication and the engine's additive vocabulary agree.

## Consequences

- §7 is now evaluable in full, and the sentence it has always carried is true.
- One published table covers party and `written_for` from one to six; outside it the formula still
  applies and clips.
- An adversary block stays absolute, so a creature can be written once and used at any danger.
- The floor at 0 is reachable and does real work: an opponent already at the untrained 10, in
  content written for six, met by a lone character, takes the full −20 and would land at −10. A
  percentage is not a negative number, and §1 already says what a test at or below zero is — it is
  not attempted. No new rule was needed, but without computing it the design would have published a
  negative percentage.
- The curve is not overridable, for the same reason ADR 0024's is not: with the same function on
  both sides of the ratio, replacing it on one side breaks the identity case and replacing it on
  both cancels out.
