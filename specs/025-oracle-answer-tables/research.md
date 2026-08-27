# Research: Oracle answer tables

## Decision: the roll is `d100`, reusing the resolution die

**Rationale**: The ruleset already commits to `d100` as its one resolution mechanic
(`docs/design/03-rules.md` §1). Reusing it for the oracle keeps the engine to one die vocabulary
instead of introducing a second (a d6, d12, d20 as other table families do for their own reasons —
`docs/design/04-tables.md`'s index). A hundred-sided space also gives enough resolution to place five
likelihood bands and an "exceptional" degree at each without cramping any of them into single-digit
ranges.

**Alternatives considered**: A dedicated small die (`1d10`, `1d6`) — rejected, because
percentile odds are what "likelihood band" means to a GM in practice (30% chance, 70% chance), and
translating that into a d6/d10 range just reintroduces percentile thinking one conversion step
removed.

## Decision: likelihood bands are five, fixed, and symmetric around 50%

**Rationale**: Five named bands — mirroring the shape (not the values) of the existing difficulty
table in `docs/design/03-rules.md` §1 — give the GM a bounded, auditable set of odds rather than a
free numeric slider, matching this repo's existing pattern for GM-declared modifiers. Each band's
Yes-threshold `T` (the roll, 1–100, at or under which the base answer is Yes) is:

| Band | T (Yes at or under) |
|---|---|
| Near Certain | 90 |
| Likely | 70 |
| Even | 50 |
| Unlikely | 30 |
| Near Impossible | 10 |

**Alternatives considered**: A 3-band or 7-band set — rejected. Three bands (Likely/Even/Unlikely)
collapse extremes the GM sometimes needs ("nearly certain but not impossible"); seven crowds the
table with distinctions no GM judgment call can reliably tell apart at the table.

## Decision: every band carries the same four-row shape, computed not asserted

**Rationale**: Within every band, four rows in this fixed order over the `1d100` roll:

1. **Exceptional Yes** — rolls 1–5
2. **Yes** — rolls 6–T
3. **No** — rolls (T+1)–95
4. **Exceptional No** — rolls 96–100

This holds for every `T` in the table above because 5 ≤ T ≤ 90 always, so the two five-point
exceptional bands never overlap the boundary. The four widths are `5, T−5, 95−T, 5`, which sum to
100 for any `T` — verified by `tools/check_oracle_answers.py`, not
asserted. Resulting outcome probabilities:

| Band | Exceptional Yes | Yes | No | Exceptional No | Total Yes | Total No |
|---|---|---|---|---|---|---|
| Near Certain (T=90) | 5% | 85% | 5% | 5% | 90% | 10% |
| Likely (T=70) | 5% | 65% | 25% | 5% | 70% | 30% |
| Even (T=50) | 5% | 45% | 45% | 5% | 50% | 50% |
| Unlikely (T=30) | 5% | 25% | 65% | 5% | 30% | 70% |
| Near Impossible (T=10) | 5% | 5% | 85% | 5% | 10% | 90% |

**Alternatives considered**: A plain Yes/No table with no exceptional degree — rejected by
FR-006 (the issue asks for "yes/no with degrees"), and because a flat coin flip at every band gives
the GM no way to signal "yes, dramatically so" the way a telling blow does elsewhere in the
ruleset.

## Decision: the oracle reuses the Wyrd die exactly, no second complication mechanism

**Rationale**: The oracle roll *is* a `d100` roll, so `docs/design/03-rules.md` §1's Wyrd die
already applies to it unmodified — units digit 0 is Ill Omen, 9 is Fair Omen, otherwise nothing.
Answer-table rows encode the yes/no axis; the Wyrd die stays the sole "what else happened" channel
across the whole ruleset, satisfying FR-008 with no new mechanism at all rather than one that has to
be justified against the existing one.

**Alternatives considered**: A dedicated oracle complication table (as some GM-emulator designs
use) — rejected. It would duplicate the Wyrd die's job under a different name, which is exactly the
kind of shadow mechanic `docs/design/04-tables.md`'s "declared by the family" clause exists to prevent
when no real difference justifies a second die.

## Decision: an oracle roll is obligatory for a question the fiction has not settled and that future play could contradict

**Rationale**: `docs/adr/0005-deterministic-over-inference.md` frames the risk as an LLM GM
inventing a fluent answer that is later invented differently. That risk exists precisely for
questions whose answer could be asked again — a fact about the world, not a one-off flourish of
description. The obligation is stated as: any yes/no (or degreed) *factual* question about the
fiction that isn't already established, and whose answer might matter again, must be rolled. Purely
cosmetic description — the colour of a curtain nobody will ask about twice — stays an ordinary GM
decision.

**Alternatives considered**: Making every unscripted GM decision oracle-bound — rejected, and
explicitly out of scope per the issue: "the part that does the real work" is drawing this
boundary, not maximizing how much goes through the table.

## Decision: an oracle roll records to the beat log with the same provenance shape as any other roll

**Rationale**: `docs/design/22-state.md`'s log-provenance example already fixes the shape every roll's
entry takes (`beat`, `verb`, `engine`, `setting`, plus roll-specific fields). The oracle reuses it
verbatim, adding its own fields: `table` (the key, `oracle-answer`), `question` (the GM's stated
question, verbatim), `band` (the likelihood band declared), and `outcome` (one of the four row
labels). The `roll` field is already covered by the shared shape, and `wyrd` reuses its existing
value vocabulary (`none`, `ill`, `fair`) from the resolution roll's own log entries.

**Alternatives considered**: A separate `oracles.log` file — rejected. `docs/design/04-tables.md`'s
own versioning section already states a table roll's provenance belongs in the ordinary log
(`beat`/`table`/version), and a second log for one family reopens the "two lists of the same thing
drift" fault class `CLAUDE.md` names for the backlog specifically, which applies here for the same
reason.
