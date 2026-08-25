# ADR 0016 — An opposed test needs a successful actor, and a failure has no degrees

**Date:** 2026-08-25
**Status:** Accepted

## Context

Opposed tests carried the whole weight of combat — "attacks are opposed tests"
([`03-rules.md`](../03-rules.md) §2) — on one sentence:

> **Opposed tests:** both roll; the higher degree of success wins; ties to the defender. The acting
> side reads the Wyrd die.

It reads complete. It leaves two questions unanswered, and both have consequences large enough to
change what the game feels like.

**What if the acting side fails?** "The higher degree of success wins" still compares. A missed
attack whose degrees happened to exceed the defender's would win, and do damage.

**What are the degrees of a failed roll?** Degrees are `tens(skill) − tens(roll)`
([`03-rules.md`](../03-rules.md) §1), which is negative on a failure. Subtracting a negative
*inflates* the margin — and the margin is what the telling blow reads.

The second is the dangerous one, because nothing in the prose hints at it. Computed
([`check_opposed.py`](../../specs/010-opposed-tests/check_opposed.py)), it makes **roughly three
quarters of successful attacks telling blows** across every realistic skill pairing. A telling blow
doubles damage. The rule as written would have made doubled damage the ordinary result of hitting
someone, and no amount of reading would have revealed it.

## Decision

**The acting side must succeed, and a failed roll has no degrees.**

1. The acting side rolls first and must succeed. On a failure the action fails; there is no
   comparison, and the resisting side need not roll.
2. Degrees exist only on a success. A failed roll contributes **zero**, not a negative.
3. If the resisting side also succeeds, the higher degrees win; ties go to the resisting side.
4. The margin is the difference in degrees.
5. Only the acting side reads the Wyrd die.

The **acting side** is whoever is trying to change the situation. Where neither is — two people
racing for one thing — it is not an opposed test.

## Consequences

**Telling blows roughly halve**, from about three quarters of successful attacks to a range that
rises with skill. That range is still probably wrong, and it is not this record's to fix — see
below.

**Most opposed tests need one roll, not two.** The acting side's failure short-circuits before the
resisting side rolls at all. At starting skills that is most of the time, which matters for the
twenty-minute session [`01-principles.md`](../01-principles.md) requires.

**Failing is unambiguous.** A missed attack cannot win by having rolled a worse failure than the
defender, which the original sentence permitted.

**One Wyrd die per test, whatever the dice count.** Preserved from the original rule and now stated
as a consequence of the actor/resister asymmetry rather than as a floating fact.

## A finding this record does not resolve

**The telling-blow threshold is probably too low.** Section 2 makes it a win by 3 or more degrees.
Under the corrected rule that is impossible at starting skills — degrees cannot reach 3 — and by
practised skill it is the **majority** of successful attacks:

| attacker vs defender | telling blows, as a share of hits |
|---|---|
| 25 v 25 | 0% |
| 30 v 30 | 27% |
| 40 v 40 | 42% |
| 55 v 40 | 52% |

Doubling damage on more than half of hits is unlikely to be the intent. The threshold belongs to
combat and is **Stage 5's** to set; this record only makes the margin honest enough to judge it by.

## Alternatives rejected

**Leave it: both roll, higher degrees wins, however either rolled.** The sentence as it stood. It
lets a failed action succeed, and it produces the three-quarters telling-blow rate above. Neither
fault is visible by reading, which is exactly why the rule survived this long.

**Count a failed defence as its negative degrees, but keep the actor's success requirement.** Fixes
the first fault and not the second. It is the reading a careful person arrives at from the original
text, and it is the one the numbers reject.

**Compare margins of success as percentages rather than degrees** — how far under the skill each
rolled. Finer-grained and it discards the degree scale the whole ruleset is built on
([ADR 0001](0001-resolution.md)), including the telling blow and the Aftermath modifiers. A second
measure of the same quantity, which is the drift class this repository is corrected for most often.

**Have the resisting side roll first.** Symmetric and slower: it spends a roll on a defence that is
irrelevant most of the time, since the actor fails more often than not at realistic skills.
