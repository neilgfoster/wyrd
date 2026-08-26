# ADR 0017 — Assistance scales with the helper's skill; a group rolls once; long work accumulates

**Date:** 2026-08-25
**Status:** Accepted

## Context

**Assistance, group tests and extended tasks returned zero matches across every design document.**
The core roll, the difficulty ladder, the declaration bonuses, the Wyrd die and the opposed test
([ADR 0016](0016-opposed-tests-need-a-successful-actor.md)) were all specified. The shapes that sit
between them were not.

That gap costs more here than in a table game. The player runs one character and the GM runs the
whole rest of the party ([`16-session.md`](../design/16-session.md)), so almost every non-trivial action
has companions in it. The most-used part of the system after the core roll did not exist, and in
its absence each session invented it again — the fault class the design programme exists to close.

Three questions, each with an arithmetic failure mode invisible in prose.

**How much is a helper worth?** Too little and the rule is dead text. Too much and one companion
silently moves the test a rung down a ladder the GM chose deliberately.

**How many dice does a group throw?** Five characters rolling five times contradicts *only roll
when it is dramatic*, and spends five lines of prose on one beat. Sessions happen on a phone.

**Does long work accumulate?** Degrees are `tens(skill) − tens(roll)`, so the expected gain per
attempt is around one at average skill — which makes any tidy-looking target a long queue of rolls.

## Decision

### Assistance is one helper, worth a tenth of their own skill

The bonus is `helper_skill // 10`, to a ceiling of **+10**. The helper must be able to do the task,
must contribute something specific, and does not roll. **Further hands do not add.**

The divisor is not a preference. Computed across every rung of the ladder and every realistic skill
([`check_assistance.py`](../../specs/011-assistance-and-group-tests/check_assistance.py)), two tests
reject the alternatives:

- **No realistic helper may be worth a whole rung.** The smallest gap in the ladder is 10, so a
  bonus that reaches 10 at a skill a companion actually has rewrites the difficulty.
- **The cap must not bind at realistic skills.** A ceiling reached at 40% or 50% turns a scaled
  bonus back into a flat one in every case that matters — the decision undone by its own guardrail,
  and nothing about it would look wrong.

Only a divisor of 10 survives both. It gives +3 for a 30% helper and +6 for a 65% one: a real lift
of about 6 percentage points, and nowhere near a rung.

### A group test is one roll, at the skill the fiction points to

Where the thing must simply get done, the **most capable** member is tested. Where everyone must
get through, the **least capable** is — a party is as quiet as its noisiest member. Assistance
applies either way. A member with no relevant skill is tested at the untrained 10%.

### An extended task accumulates degrees toward a target

One test per interval named by the fiction. A success adds its degrees, **minimum 1**. A failed
interval is spent and gains nothing. Targets are **2, 4 and 6** degrees.

The minimum-1 rule is load-bearing rather than a rounding convenience: without it, a success whose
roll lands in the same tens as the skill advances the work by nothing while still consuming an
interval. At 25% skill that is **24% of all successes** — a character who keeps succeeding and never
finishes.

**The Wyrd die is read every interval, from that interval's own natural roll.** An interval is an
ordinary test; nothing here is an exception to the natural-roll rule.

## Consequences

**Help from the incompetent is worthless, and visibly so.** A 30% companion is worth +3. The rule
does not pretend that willingness substitutes for skill.

**The party's presence is fiction, not arithmetic.** Extra companions may move the difficulty the
GM sets — which is a judgement about the situation — but never the number. This is what stops a
Hard test at 45% becoming 55% because four people turned up.

**A group's weakest member becomes a decision.** In a test everyone must get through, the untrained
companion is the one tested. Leaving them behind is available, and is usually the interesting
choice rather than the optimal one.

**Long work is expensive at low skill, and says so.** A great labour is about six intervals at 45%
and nearly eighteen at 25%. The rule states this plainly instead of letting a character grind.

**Every added shape keeps the three axes independent.** All of them modify the *skill*
([ADR 0001](0001-resolution.md)); none touches the roll.

## A finding this record does not resolve

Assistance applies to attacks, because attacks are opposed tests. Whether companions may assist an
attack at all, and whether the telling-blow margin should read an assisted actor's degrees, is
**combat's** to settle (#44) — as is the telling-blow threshold ADR 0016 left open.

## Alternatives rejected

**A flat bonus per helper, at a fixed size.** Simplest rule that survives a party of five, and it
was the recommendation. Rejected by the operator in favour of scaling, on the grounds that a
master's hand should be worth more than a novice's — which a flat bonus cannot express at all.

**A diminishing stack: +10, +5, +2 for successive helpers.** Rewards bringing the party to bear
without running away. It needs an ordering rule and arithmetic at every assisted roll, and it
reintroduces the thing no-stacking exists to prevent, merely more slowly.

**Everyone rolls in a group test.** The honest simulation, and it guarantees that in a party of
five somebody fails every time — which converts *only roll when it is dramatic* into a lottery, and
costs five beats of prose for one action.

**The party rolls as a unit, at some pooled or averaged skill.** A second measure of a quantity the
skill already expresses, and averaging hides exactly the member the fiction is usually about.

**No extended tasks at all: one test, whose degrees read as how long it took and what it cost.**
This was the recommendation — it keeps a long task to a single beat and needs no new machinery.
Rejected by the operator: research, repairs and long journeys are wanted as sequences with
complications arriving on the way, and a single test cannot produce a middle. The cost is accepted
and bounded by the interval rule — *if an interval is not worth a beat of prose, it is not worth a
roll* — which is what keeps the mechanic from becoming a chore.
