# ADR 0046: Reroll resources stack unbounded on one roll, deliberately

**Status:** Accepted
**Date:** 2026-08-27

## Context

Three separate mechanics each grant a reroll after a failed test, and nothing in
`03-rules.md` stated a limit on using more than one against the same original roll:

- **The Bargain** (§4) — 1 Taint, once no Fortune is left, for a plain reroll.
- **Resolve** (§4) — 1 point, for a +20-boosted reroll.
- **Fortune** (§3) — 1 point each, for a plain reroll, with no stated per-test cap on how many
  Fortune points may be spent.

Played straight, nothing stops a player from chaining all three: fail, take the Bargain, fail
again, spend both Resolve points, fail again, spend every remaining Fortune point — one original
roll, up to seven total attempts.

#153's playtest ran seven independent trials of this exact stack at a fixed 30% effective skill.
Six of seven succeeded — a real, material shift from the 30% single-roll base rate — but the
seventh exhausted every resource (Bargain, both Resolve, all three Fortune) and still failed, so
the stack is not an automatic win. It is, however, a lot of narrative real estate and resource
spend for one roll, with no stated pacing guidance — a GM running this at the table with no
stated limit either has to invent a pacing cap on the spot, or let a single dramatic beat absorb
up to seven rolls.

## Decision

**Stacking is unbounded and deliberate.** Fortune, Resolve and the Bargain may all be spent
against the same original failed roll, with no engine-imposed cap on how many a character uses in
sequence. `03-rules.md` §3 and §4 both state this explicitly now, rather than leaving it as an
unexamined silence.

## Why

- **It is a real, earned story beat, not a loophole.** A character throwing everything they have
  — Taint, Resolve, every point of Fortune — at one make-or-break moment is exactly the kind of
  scene this ruleset should be able to produce. Capping it would remove a genuine dramatic
  possibility for no stated benefit beyond table-pacing convenience.
- **It is not a guaranteed win, verified by actual play, not assumed.** #153's own seven trials —
  real seeded rolls, every attempt disclosed — showed one of seven still failed after the full
  stack was exhausted. The character pays everything and can still lose; that is what keeps the
  stack a dramatic gamble rather than a mechanical certainty.
- **The cost is already steep and self-limiting.** Spending the full stack costs 1 Taint, both
  Resolve points, and every Fortune point a character has — Fortune only renews daily, Resolve
  only at a Rally or downtime, and Taint never comes back down for free. A character cannot do
  this repeatedly in the same session without running out of exactly the resources the ruleset
  already uses to price desperation. No second cap is needed on top of the ones these three
  mechanics already carry individually.
- **A cap would cost more than it buys.** The only stated problem is table-time pacing ("several
  minutes of resolution across up to seven rolls"), which a GM can already manage narratively
  (narrating the stack's rolls briskly, or asking the player to declare the whole stack before
  rolling) without an engine rule forcing a specific number.

## Alternatives rejected

- **Cap the number of reroll-granting resources usable per original failed roll** (e.g. one
  Bargain, Resolve, or Fortune spend per test, not several in sequence). Workable, and would
  remove the pacing concern outright, but rejected: it removes a genuine, resource-costly,
  narratively-earned story beat (a character spending everything at once) for a pacing concern a
  GM can already manage without a new rule, and #153's own trials showed the stack is not
  actually broken (6/7 succeeded, not 7/7) — the finding was about table pacing, not balance.
- **Some other pacing mechanism** (e.g. a declared-in-advance-only rule, an escalating cost per
  additional resource spent on the same roll). Considered and set aside for the same reason as the
  flat cap: the playtest evidence does not show a balance problem severe enough to justify a new
  rule, only a pacing one a GM already has the tools to manage.

## Consequences

- `03-rules.md` §3 and §4 both state the stacking rule explicitly, cross-referencing each other
  and this ADR.
- No change to how Fortune, Resolve, or the Bargain each work individually — ADR 0041/0042/0043
  govern each of them unchanged; this ADR only states that they compose.
- No verification script is added — #153's own seven-trial playtest record
  (`docs/design/30-playtest-transcript.md` §12) already serves as the evidence this decision
  relies on, and re-deriving it would duplicate work already done and disclosed in full.
