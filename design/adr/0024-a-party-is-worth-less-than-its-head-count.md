# ADR 0024 — A party is worth less than its head count, on both sides of the ratio

**Date:** 2026-08-25
**Status:** Accepted

## Context

[`03-rules.md`](../03-rules.md) §7 has published the engine's only scaling equation since the
ruleset was written:

> `danger_effective = danger × (party_effective / written_for)`

`danger` was defined. `written_for` was defined. **`party_effective` was not defined anywhere.**
The nearest thing to a definition was one sentence in
[`11-corpus-index.md`](../11-corpus-index.md) — the player character counts as 1 and each companion
counts as "a fraction" — which never said which fraction. So the equation could not be evaluated at
all, and every claim resting on it rested on a term nobody could compute: that a chronicle stays
interesting for years without escalating the fiction, and that a corpus written for four-to-six
adventurers is usable by a table of one player.

`11-corpus-index.md` went further and quoted a *result* — a danger-3 arc written for four, run by
one character and two companions, "plays at roughly danger 2". That figure was never computed from
anything, because until now there was nothing to compute it from. It is the second uncomputed
figure this repository has published and the second to be wrong.

The decision was constrained three ways. It had to be a **pure function of party composition**,
because the engine evaluates it without asking anyone. It had to use **only data the engine already
holds** — companions carry presence, a bond and a competence or two, and no capability score
([`06-state.md`](../06-state.md)), so any weighting by a companion's own power would have meant
inventing a companion stat block the engine has spent five documents declining to have. And it had
to leave the **shape** of the formula and the **meaning** of `written_for` alone.

## Decision

**The k-th body is worth `1/k`.** A party of `p` bodies has an effective size of
`1 + 1/2 + 1/3 + … + 1/p`. The player character is one body; so is each companion at
`status: with-party`, and no other companion is.

**Both sides of the ratio are read through that same function.** `party_effective` is the effective
size of the party present; the denominator is the effective size of a party of `written_for` bodies.

**`danger_effective` is never rounded.** Each quantity built from it rounds at its own point of
use: round half up, and never below 1 where the written quantity was at least 1.

Three properties earn the curve, and all three are computed in
[`specs/016-party-effective/check_party.py`](../../specs/016-party-effective/check_party.py) rather
than asserted here:

- **It is order-independent.** A sum over bodies does not care which body was counted first, so no
  roster ordering has to be invented and two people counting the same party reach the same number.
- **It bounds the retinue.** Effective size grows like a logarithm. Twenty bodies buy 1.73 against
  content written for four — five times the head count, not quite double the danger. Gathering
  companions is therefore fiction the player earned, not a difficulty setting they found.
- **The identity case is exact.** Four bodies run content written for four at exactly its written
  danger, for every danger rating. This is only true because the same function is applied to both
  counts.

## Rejected

**A flat fraction per companion — a half each, or two-thirds.** Much simpler, and a half is the
only weighting under which the figure `11-corpus-index.md` already quoted comes out right, which is
some evidence it was what the original sentence meant. Rejected because it makes a retinue scale
linearly: ten companions would count as six bodies and content would harden in step, so the
cheapest way to flatten a long chronicle would be to collect people. A party of bodies is not a
party of players, and the tenth body plainly is not worth what the first was.

**Weighting a companion by their own capability.** The intuitive answer — companions differ, so
count them differently — and the one the original sentence's reasoning ("companions are GM-run and
less capable") points at. Rejected because the engine holds no number to weight by. Introducing one
would give companions the mechanical depth
[`04-session.md`](../04-session.md) and [`06-state.md`](../06-state.md) both deliberately withhold,
and it would put a judgement call inside an equation whose whole purpose is to be evaluated without
one.

**Leaving the denominator a raw head count** — the formula exactly as it was literally printed.
Nothing about `written_for` would have been reinterpreted, which is the conservative reading of the
scope. Rejected because it compares an effective size with a head count: content would permanently
run at a quarter to a half of its written danger, the identity case would be unreachable
(`party_effective` would need about thirty-one bodies to reach 4), and a table of four would never
in its life run an adventure the way it was written. That is not a ratio; it is a discount with a
ratio's notation.

**Rounding `danger_effective` to an integer, half up or down.** Tidier at the record — one integer,
carried everywhere. Rejected because `danger` is a multiplier and the multiplications come after:
precision discarded up front goes wrong first at the largest count in a piece of content, which is
generally the fight. Worked in
[`specs/016-party-effective/worked-scaling.md`](../../specs/016-party-effective/worked-scaling.md):
at three bodies against content written for four, a pre-rounded `danger_effective` puts six
cultists in the undercroft where the exact one puts five, while every smaller quantity in the same
arc agrees. Rounding down specifically was also the softer of the two and had a precedent in §3's
assistance bonus — but that rule rounds down because it *grants* something, and a magnitude to be
represented is not a bonus to be granted.

**Letting a setting override the curve.** Nearly every other number in this engine is a default a
setting may replace, so a reader will expect it here. Rejected because it does not compose:
with the same function on both sides of the ratio, an override on one side breaks the identity case
and an override on both cancels out. A setting's levers over difficulty are the companions it
grants and the `danger` its content carries.

## Consequences

- `03-rules.md` §7 can be evaluated. It no longer contains an undefined term, and a reader does not
  have to consult the corpus index to use the engine's only scaling equation.
- The two documents that describe scaling now describe the same thing, and
  `check_party.py` asserts every figure either of them publishes — so an edit that drifts fails
  loudly instead of reading as authoritative.
- A lone player character runs content written for four at 0.48. That is a hard chronicle by
  construction, and it is meant to be: the scaling is what makes the corpus playable by one player,
  not what makes it fair.
- Companions stay mechanically thin. Nothing in this decision needs a capability score, so the
  pressure to invent one is not created here.
- Applied forward only ([`09-evolution.md`](../09-evolution.md)). Content already prepared and
  played is not rescaled.
