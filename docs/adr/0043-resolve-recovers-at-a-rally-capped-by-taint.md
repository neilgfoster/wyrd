# ADR 0043 — Resolve recovers at a Rally, capped at Taint plus 3

**Date:** 2026-08-27
**Status:** Accepted

## Context

`03-rules.md` §4 states Resolve is "spendable, renewable" and defines the Spent state as "Resolve
fallen to equal Taint," but named no trigger that ever raises Resolve above 0. Character creation
sets it to 0, and nothing else in `docs/design/` or `docs/adr/` ever adds to it. #149's playtest
(part of the playtest epic, #134) hit this directly: it could not exercise Resolve or the Spent
state at all, because the mechanic as written has no path to a positive value — read literally,
Resolve can never be spent, and Spent could only ever be true at Taint 0 (before anything has
happened), backwards from what the state represents. Raised as #157. #151's playtest confirmed
the same gap recurs independently for any system of power declaring a `resolve_cost`.

Two workable gain mechanisms were identified when #157 was raised: Resolve rises alongside Taint
whenever Taint is gained, or Resolve recovers at a Rally/downtime the way Strain and Stamina
already do. The operator chose the Rally/downtime shape, capped by Taint, in conversation before
this record was written.

**A naive version of that shape does not work, and was caught before shipping.** If Resolve's
cap were exactly the character's current Taint, a fully-rested character's Resolve sits exactly
*at* Taint — which is the Spent condition itself, not headroom above it. Every character would be
Spent (or on the exact boundary of it) immediately after every downtime, with no positive amount
ever actually spendable without going below Taint into undefined territory. The cap needed real
headroom above Taint to make "spendable" and "Spent, reachable through ordinary play" both true
at once — the two properties #157's own Definition of Done named as required.

## Decision

**Resolve recovers +1 at a Rally, and back up to its cap at a downtime — the same rate ADR 0020
fixed for Stamina and Strain, reused rather than inventing a third recovery number.** Resolve's
cap is **the character's current Taint plus 3** — one threshold-interval of headroom, the same
spacing that already governs Transformation thresholds (§4), so a fully-rested character always
has real Resolve to spend down before reaching Taint.

**Spending 1 Resolve buys a +20 bonus to an immediate reroll** of the failed test — distinct from
Fortune's plain reroll (§3): Fortune buys a fresh roll at the same odds, Resolve buys a better
one, and costs the resource that measures how much fight is left rather than the one that
measures luck.

**At Taint 0, the character can never be Spent, however tired** — kept as its own stated rule,
not derived from the cap formula. The formula alone would give a Taint-0 character 3 Resolve to
spend, which could reach Spent at 0 too; the explicit exception is what the original text already
asserted, and it is preserved rather than left to arithmetic that would quietly contradict it.

## Why

**It reuses an existing rate rather than inventing one.** ADR 0020 already fixed Stamina and
Strain's recovery at "1 per Rally, full at downtime," specifically to avoid a second number doing
one job. Resolve joins that same cadence instead of adding a third.

**The Taint-plus-3 cap keeps the pairing genuinely a counterweight, not a coincidence.** Resolve
rises and falls with Taint (it always caps at Taint's own value plus a fixed margin), so a
character who has accrued more Taint has proportionally more Resolve to draw on when rested — and
the margin (3, not some other number) reuses the interval Transformations already use, rather
than inventing a fresh constant with no other job in the ruleset.

**The reroll-plus-bonus spend keeps Resolve distinct from Fortune, deliberately.** Both resources
can now be described as "spend to get a better result after a roll," which risks the same
overlap Luck and Fortune had before ADR 0041 merged them. The distinction here is real rather
than cosmetic: Fortune's reroll carries no bonus (a second try at the same odds); Resolve's does
(+20, a meaningfully better try) — different resources for a genuinely different kind of push,
not two labels on one mechanic.

## Alternatives rejected

**Resolve's cap exactly equal to Taint, with no margin.** The first draft of this decision.
Rejected because it makes "spendable" and "Spent, reachable through ordinary play" contradict
each other: a fully-rested character sits exactly on the Spent boundary, unable to spend anything
without going below Taint. Caught before merge by working through what a full rest actually
produces, not assumed correct because the formula read cleanly in prose.

**Resolve rises alongside Taint whenever Taint is gained**, rather than recovering at a
Rally/downtime. Considered directly against the chosen shape. Rejected in favour of reusing an
existing recovery cadence (Rally/downtime) rather than inventing a formula tied to Taint's own
gain events, which would need its own derivation and its own check script to prove out, for a
result the Rally/downtime shape already gives more simply.

**Resolve's spend granting a plain reroll**, the same shape as Fortune's. Rejected because it
would recreate the functional overlap Luck and Fortune had before ADR 0041 — two resources doing
the identical job with no stated reason to reach for one over the other.

## Consequences

- `docs/design/03-rules.md` §4 states Resolve's gain trigger, spend amount and bonus, and cap
  formula explicitly — the three things #157 found entirely absent.
- The Spent state is now reachable through ordinary play at any Taint above 0, by spending
  Resolve down from its post-recovery cap to Taint's own value — a constant 3 points of real
  headroom at every Taint level, the same margin whether Taint is 1 or 20.
- `docs/design/30-playtest-transcript.md`'s condition-tracks playtest (#149) and systems-of-power
  playtest (#151) both found this gap; a follow-up playtest exercising the corrected mechanic is
  not required by this ADR, but the next condition-tracks-adjacent pass should confirm it plays
  as described.
- No new dice mechanic, no new track, no power-specific consequence chain — Resolve's recovery
  reuses ADR 0020's rate, and its cap reuses the Transformation threshold's own spacing, per
  CLAUDE.md's own preference for reuse over invention.
