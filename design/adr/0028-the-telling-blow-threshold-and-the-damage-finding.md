# ADR 0028 — The telling blow moves to 6 degrees; the issue's damage-multiplier figure is corrected

**Date:** 2026-08-25
**Status:** Accepted

## Context

[ADR 0027](0027-combat-rolls-belong-to-the-player.md) converts combat's attack and defence to a
single player roll against `effective%`. Two numbers depended on the shape of the roll it replaced
and could not be carried over unexamined:

**The telling-blow threshold.** `03-rules.md` §2 doubles damage on a win by **3 or more degrees**.
That number was already flagged as probably wrong under the opposed test — [ADR 0016](0016-opposed-tests-need-a-successful-actor.md)
found telling blows reaching a *majority* of hits at practised skill (52% at 55 v 40) — and it is
fed a different input now: degrees are read against `effective%`, not a raw skill, and a
successful roll's degrees skew toward the high end of what the effective percentage allows,
because the roll that produced them was, by definition, at or under it.

**The damage-multiplier consequence.** Issue #69 (recording #44's own finding) states that a
player-rolled defence — replacing the requirement that the opponent's attack beat a static
defence — raises incoming damage by a factor of **1.4×-3.1×**, and requires this be faced
explicitly: accepted and offset, or corrected. `CLAUDE.md`'s "check the maths" applies to a figure
proposed in an issue exactly as much as to one proposed from intuition, so the figure is
independently reproduced rather than designed around unverified.

Both are computed in
[`specs/018-player-facing-combat/check_conversion.py`](../../specs/018-player-facing-combat/check_conversion.py),
exact arithmetic throughout, asserting agreement with the mapping table
[`specs/012-combat-sequencing/check_mapping.py`](../../specs/012-combat-sequencing/check_mapping.py)
already published.

## Decision

**The telling-blow threshold moves from 3 degrees to 6.** At threshold 6, telling blows stay a
minority of hits across the representative skill-gap span this repo already uses, from 0% at an
even match up to 43% at the largest realistic gaps — the same shape ADR 0016 asked for and did not
get to set, now met at the roll the mechanic actually produces:

| attacker vs defender | effective% | telling blows, share of hits |
|---|---|---|
| 40 v 40 | 50% | 0% |
| 55 v 40 | 65% | 13.8% |
| 60 v 30 | 80% | 36.2% |
| 100 v 50 | 95% | 41.1% |

**The issue's stated 1.4×-3.1× damage-multiplier figure does not reproduce, and is corrected.**
Computed expected damage per round, today's opposed-test structure against the converted
single-roll structure, across every pairing in the representative span where the attacker has the
advantage:

| attacker vs defender | multiplier |
|---|---|
| 35 v 30 | 1.44× |
| 55 v 40 | 1.04× |
| 50 v 30 | 1.23× |
| 60 v 30 | 1.17× |
| 70 v 35 | 0.98× |
| 60 v 20 | 1.32× |
| 80 v 40 | 1.02× |
| 100 v 50 | 0.83× |

The computed range is **0.83×-1.44×** — a modest increase at most pairings, and at the largest
skill gaps a *decrease*. The issue's figure conflated two different comparisons: it read the
opponent's improved chance to land a hit at all (no longer gated behind its own success) against
the player's, without accounting for the corrected telling-blow threshold pulling the other way —
fewer of those hits double. **No offset is required.** Starting Stamina is reaffirmed at 6
([ADR 0027](0027-combat-rolls-belong-to-the-player.md)) on the strength of this corrected figure,
not the issue's.

## Consequences

**`03-rules.md` §2's telling-blow line changes from "3 or more" to "6 or more".** Nothing else about
the rule's mechanism changes — win by enough degrees, the damage rolled doubles, then armour
subtracts.

**The issue's acceptance criterion "the design either accepts that or states what offsets it" is
met by neither branch as written** — the premise itself does not hold at the computed figure.
Stating the correction, with the computation that produced it, is what this record is for.

**A future correction to the effective% clip or the pairings this repo treats as representative
would need `check_conversion.py` re-run**, not the threshold or the multiplier re-guessed — both
are read off the same script that asserts its own agreement with the prior mapping table.

## Alternatives rejected

**Keep the telling-blow threshold at 3 and accept a majority-of-hits telling-blow rate.** Doubling
damage on more than half of hits was already rejected once, for the same reason, by ADR 0016 — it
is unlikely to be the intent twice.

**Accept the issue's 1.4×-3.1× figure and design an offset for it** — reducing starting Stamina,
raising armour, or similar. Rejected because the figure does not reproduce; designing a mitigation
for an unverified number would have left the engine correcting a problem that, at the computed
figure, is largely absent.

**Set the telling-blow threshold by a fixed percentage of hits (e.g. exactly 25%) rather than a
degree count.** Would require reading a probability at the table rather than comparing two numbers
already in front of the player — a departure from how every other threshold in this ruleset is
stated, for no gain the fixed-degree threshold does not already deliver.
