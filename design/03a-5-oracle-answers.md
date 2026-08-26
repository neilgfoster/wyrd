# Oracle answers

The table the GM rolls to **settle a question the fiction has not answered yet**, instead of
inventing one. It is what [`02-architecture.md`](02-architecture.md) and
[`07-tooling.md`](07-tooling.md) have listed as `oracles` without defining, and it is the fifth
family [`03a-tables.md`](03a-tables.md) commits to.

It is a family of the kind [`03a-tables.md`](03a-tables.md) defines, and everything below is
declared within those conventions.

---

## What an oracle is, and why the GM's judgment isn't enough

[ADR 0005](adr/0005-deterministic-over-inference.md) names the failure mode this exists to close:
asked an unsettled question, an LLM GM invents a fluent answer, then invents a different fluent
answer to the same question next session, because nothing about the first answer was ever
recorded as a decision rather than as colour. An oracle is the GM rolling instead of deciding —
the roll is authoritative the same way a resolution roll is
([`01-principles.md`](01-principles.md) §1), and it is recorded, so the world's answer stays the
same the next time anyone asks.

**An oracle is not a substitute for ordinary narration.** Most of what a GM says at the table is
never a fact the fiction is committed to holding stable — the exact words a merchant uses, which
side of the street a building sits on, whether the rain lets up mid-scene. That stays an ordinary
GM decision, made and never revisited.

## When the GM must roll one

**A question is oracle-bound when both hold:**

1. **It is a yes/no (or more/less likely) question of fact about the world** — not a question of
   what the GM wants to happen, and not a request for description.
2. **The answer could plausibly be asked again**, by the player or by the GM's own later
   improvisation, in a way that would expose an inconsistency if answered differently the second
   time.

Concretely: "is the door locked", "did anyone see them leave", "is the letter still in the
strongbox", "does the guard captain believe the story" are all oracle-bound — each is a fact a
later scene could easily test again. "What does the tavern smell like", "what's the innkeeper's
name" are not — nothing in the fiction depends on either being asked twice with the same answer,
and naming them is itself the answer, not a coin flip about one.

A GM who is unsure falls back to the second test: *if I invented an answer here and a different
one three sessions later, would the fiction visibly contradict itself?* If yes, roll. If the
question would only ever surface once, decide it and move on.

**This is an obligation, not a suggestion.** An oracle nobody is obliged to consult constrains
nothing — it becomes a tool the GM reaches for only when the invented answer already feels risky,
which is exactly the case that needs it least. [`01-principles.md`](01-principles.md) states this
obligation directly, in the same terms.

## The roll

| | |
|---|---|
| **key** | `oracle-answer` |
| **die** | `1d100` |
| **modifier** | none — the GM's declared likelihood band selects which row set is read, not an
  arithmetic adjustment to the roll |
| **lowest possible total** | `1` |
| **uniqueness** | repeatable |
| **extra row fields** | `band` |

**Why `d100` rather than a dedicated oracle die.** [`03-rules.md`](03-rules.md) §1 already commits
the ruleset to `d100` as its one resolution mechanic. Reusing it here keeps the engine to one die
vocabulary instead of adding a second purely for this family, and a hundred-sided space is enough
resolution to place five likelihood bands and an exceptional degree at each without crowding any
of them into single-digit ranges.

**Before rolling, the GM declares a likelihood band** — a judgment call, the same shape as
declaring a test's difficulty ([`03-rules.md`](03-rules.md) §1): how plausible is a "yes", before
any dice are involved. Five bands, fixed:

| Band | When to choose it |
|---|---|
| **Near Certain** | Almost nothing in the fiction suggests otherwise; asking mostly confirms. |
| **Likely** | The fiction leans toward yes, but a genuine no wouldn't be a surprise. |
| **Even** | No lean either way — a true coin flip. |
| **Unlikely** | The fiction leans toward no, but a genuine yes wouldn't be a surprise. |
| **Near Impossible** | Almost nothing in the fiction suggests otherwise; asking mostly rules it out. |

A GM torn between two adjacent bands picks the one closer to Even — the bands exist to carry a
real lean, not to let a marginal hunch masquerade as near-certainty.

## The table

Each band reads the same four-row shape over the `1d100` total:

| Range | Effect | Description |
|---|---|---|
| 1–5 | `exceptional_yes` | Yes, and more emphatically than asked — nothing about it is in doubt. |
| 6–T | `yes` | Yes. |
| T+1–95 | `no` | No. |
| 96–100 | `exceptional_no` | No, and more emphatically than asked — the opposite of what was hoped is also true. |

where **T** is the band's Yes-threshold:

| Band | T |
|---|---|
| Near Certain | 90 |
| Likely | 70 |
| Even | 50 |
| Unlikely | 30 |
| Near Impossible | 10 |

**The four rows are contiguous and cover every total** for every band in the table above, because
`5 ≤ T ≤ 90` always holds, so neither five-point exceptional row ever collides with the boundary
at `T`. This is computed, not asserted, in
[`tools/check_oracle_answers.py`](../tools/check_oracle_answers.py), which also confirms the
resulting probabilities:

| Band | Exceptional Yes | Yes | No | Exceptional No | Total Yes | Total No |
|---|---|---|---|---|---|---|
| Near Certain (T=90) | 5% | 85% | 5% | 5% | **90%** | 10% |
| Likely (T=70) | 5% | 65% | 25% | 5% | **70%** | 30% |
| Even (T=50) | 5% | 45% | 45% | 5% | **50%** | 50% |
| Unlikely (T=30) | 5% | 25% | 65% | 5% | **30%** | 70% |
| Near Impossible (T=10) | 5% | 5% | 85% | 5% | **10%** | 90% |

The exceptional degrees cost nothing in headline odds — a "yes" band's total Yes probability is
exactly its threshold, `T`, at every band, because the two 5-point exceptional slices sit inside
the yes/no split rather than shifting it. What they add is texture at the extremes: even at Near
Certain, a full 5% of rolls land as an emphatic, unhedged "no" — the near-impossible upset that
makes "near" the honest word in the band's name.

## The relationship to the Wyrd die

**An oracle roll reads the same Wyrd die as every other `d100` roll, with no separate mechanism.**
[`03-rules.md`](03-rules.md) §1 already defines the Wyrd die as the units digit of any natural
`d100` roll — units `0` is an Ill Omen, units `9` a Fair Omen, `1`–`8` nothing. An oracle roll *is*
a `d100` roll, so this applies unmodified: rolling `40` for an Even-band question (T=50) falls in
the `6`–`T` row — `Yes` — and its units digit, `0`, is read as an Ill Omen in the same breath: the
answer is yes, and something also goes wrong with it.

A dedicated oracle complication table was considered and rejected: it would duplicate the Wyrd
die's job under a different name, which is exactly the shadow mechanic
[`03a-tables.md`](03a-tables.md)'s "declared by the family" clause exists to prevent when nothing
about this family's needs differs from any other roll's. "And something else happened" stays one
channel across the whole ruleset, oracle rolls included.

## Recording

An oracle roll's value is that the same question resolves the same way if asked again, so it is
recorded to the beat log with the same provenance shape every roll already carries
([`06-state.md`](06-state.md)), plus this family's own fields:

```json
{"beat": 412, "verb": "oracle", "engine": "0.3.1", "setting": "0.2.0",
 "table": "oracle-answer", "question": "Is the gate barred from inside?",
 "band": "Even", "roll": 63, "outcome": "no", "wyrd": "none"}
```

- **`question`** — the GM's question, stated verbatim, the same way it was asked at the table.
  There is no automated matching of a repeated question worded differently; recognising that two
  questions are "the same one, asked again" is the GM's judgment call, the same way recognising a
  repeated NPC name or location already is.
- **`band`** — the likelihood band declared before rolling.
- **`outcome`** — one of the four row effects (`exceptional_yes`, `yes`, `no`, `exceptional_no`).
- **`roll`** and **`wyrd`** — as for any other roll ([`06-state.md`](06-state.md)).

Nothing new is added to any entity's frontmatter; the record lives entirely in the beat log, the
same as every other roll.

## What a setting may replace

Per [`03a-tables.md`](03a-tables.md): a setting may replace this table's rows — their ranges,
effects and descriptions — under `overrides.tables: {oracle-answer: ...}`. It may not change the
die, the modifier, the uniqueness (repeatable), the five likelihood bands, or the row schema. No
row may carry a setting's name, a system's name, or a tonal register; a setting renames what the
descriptions say, never what the effects do.
