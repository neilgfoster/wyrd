# Research: The Aftermath table

**Feature**: 002-aftermath-table | **Date**: 2026-08-22

The decisions behind the plan, and what was rejected. Four of these were settled by the operator in
the clarification session and are recorded in [spec.md](./spec.md#clarifications); this document
holds the reasoning and the alternatives, so that a reader in a year can see why not.

---

## D1 — The roll is `d100 + (5 × points below zero)`

**Decision**: percentile, modified by the number the ruleset already computes when a combatant drops.

**Why**: `design/03-rules.md` already distinguishes a combatant who dropped by 1 from one who dropped
by 12 — it computes exactly that number for the critical. Discarding it would make every knockdown
equally survivable and would waste a distinction the ruleset already draws. Percentile matches the
rest of the engine, and 100 faces give a setting room to tune rows finely; `1d6` gives about a dozen
meaningful totals, so each row becomes a large probability step that cannot be adjusted without
lurching.

**Rejected**:

- **`1d6 + points below zero`**, mirroring the critical table exactly. Attractive for idiom — two
  tables in one fight sharing one roll — but far too coarse. With six faces, a single row is worth
  ~17%, so the difference between "a lasting mark is common" and "death is common" cannot be
  expressed without a wholesale re-cut.
- **Flat `d100`, no modifier.** Simplest, and rejected because it makes deferred death a coin-flip
  independent of the blow. A character who dropped by 1 and one who was nearly cut in half would
  face the same odds, which contradicts the ruleset's own "high results are lethal".

**Consequence**: the lowest possible total is `1 + 5 = 6`, and the first row must start there rather
than at 1. The modifier is unbounded above, so the last row must be open at the top — which is what
`design/03a-tables.md` already requires of every family.

---

## D2 — `mortality` is an application rule, not a roll modifier

**Decision**: the tone contract's `mortality` value does not touch the total. At `mortality: low` the
death rows are **closed** and re-read as the worst non-death row. At `standard` and `high` the table
is read as written.

**Why**: this one was found by the script, not by reading. The first draft made `mortality` a
`±10` adjustment to the total, which is the obvious design and is wrong in two ways that no amount of
re-reading the prose would have surfaced:

1. At `mortality: low` the lowest possible total became `1 + 5 − 10 = −4`, so the table's first row
   no longer sat at the family's lowest possible total. `design/03a-tables.md` requires ranges to
   start there, and a table that leaves a total unanswered does not load. The table would have been
   structurally invalid at one of the three legal `mortality` values.
2. At `mortality: high` a combatant dropped by only **1** could reach the death row — destroying the
   exact property deferred death exists to provide, that a light knockdown is survivable.

Both are recorded as regression checks in `check_aftermath.py`.

The replacement is also a closer reading of what `design/01-principles.md` actually claims:
`mortality` governs "how the Aftermath table is **applied**". Closing the death rows is an
application rule. Changing the total is not.

**Rejected**: `±10` to the total (above); and giving each `mortality` value its own table, which
would be three tables to keep in step and is exactly the staleness `CLAUDE.md` warns tables breed.

**Reuse**: closing the death rows is the *same mechanism* a spent Fate point uses (D3). One mechanism
serves both, so there is nothing extra to learn or to keep consistent.

---

## D3 — Fate closes the death rows; it does not suppress the roll

**Decision**: a character who spends Fate against a death result re-reads that result on the worst
non-death row. The Aftermath roll still happens and still leaves a mark.

**Why**: `design/03-rules.md` already guarantees that a character who spends Fate "survives and is
**not better off**". If Fate suppressed the roll, a spent Fate would cost the character nothing
lasting — the guarantee would be prose with no mechanism under it, which is fault class 4 in
`CLAUDE.md`: a plausible specification that no longer matches what the engine does.

Re-reading on the worst non-death row makes the guarantee mechanical, and deterministically: no
second roll, no GM judgement, one outcome. Since the worst non-death row is the recurring wound, a
spent Fate point reliably leaves a wound that wakes before every future fight — a durable, diegetic
reminder of a spent resource, which is precisely the "not better off" the ruleset asks for.

**Rejected**:

- **Fate suppresses the roll entirely.** Simpler, and it hollows out the guarantee.
- **Fate declared before the roll.** More tense, but the player commits blind, and it converts Fate
  from a death valve into a gamble — `design/03-rules.md` is explicit that Fate is spent *to avoid
  death*, which presupposes knowing death is on the table.

**Boundary preserved**: Fate still buys against dice and never against agendas
(`design/03-rules.md` §3). Fate may only be spent against a **death** result; it may not be spent to
improve any other row.

---

## D4 — Companions roll the same table, with no Fate of their own

**Decision**: one table, one modifier, one set of rows, for player character and companion alike. The
only asymmetry is the valve: companions have no Fate, so a death row stands unless the player is
present, able to act, and spends their own.

**Why**: the asymmetry the engine wants already exists and is already written down. `design/03-rules.md`
§3 says companions have no Fate and rely on the player's; `design/01-principles.md` says the GM may
kill a companion subject to the player's right to spend Fate against a death they are present for.
Introducing a companion-specific modifier or table would add a *second* source of companion
fragility on top of the one the ruleset already has, and the two would drift.

It also keeps the design claim honest: companions are "the engine's reliable source of loss" because
they lack the valve, not because the dice are rigged against them.

**Rejected**:

- **Same table, harsher modifier** — double-counts the fragility, as above.
- **Companions simply die, no roll** — discards four of the five outcome shapes for exactly the
  characters most likely to suffer them. A companion who is captured, disfigured or turned into a
  nemesis is far more useful to a chronicle than a dead one, and the ruleset already wants companion
  loss to be *various* rather than binary.

---

## D5 — The family declares no extra row field

**Decision**: rows carry range, effect and description. No severity, no weight, no tags.

**Why**: `design/03a-tables.md` is explicit that severity is family-specific and that "a field
nothing reads is how a table goes quietly stale". No rule reads a severity for aftermath —
Transformations and Afflictions consume Taint equal to severity, but nothing consumes anything equal
to an Aftermath severity. Adding one in anticipation of R1.2 would be inventing a field for a rule
that does not exist yet and may not want it.

R1.2 can add a field when it has a rule that reads one. That is an additive change under
`design/09-evolution.md` and costs nothing to defer.

---

## D6 — The family is repeatable

**Decision**: repeatable, like criticals. No exhaustion outcome is required.

**Why**: `design/03a-tables.md` sets the test — "taking the same wound twice is ordinary, so criticals
repeat; carrying the same permanent change twice is not, so transformations do not". A character who
is left for dead twice across a decade has simply been left for dead twice. Nothing about an
Aftermath result is a slot that can only be filled once.

Because the family is repeatable, the convention's "when a unique family runs out" clause does not
apply, and the document says so rather than leaving a reader to work it out.

---

## D7 — The recurring wound costs `−10` to the fight, not a new mechanic

**Decision**: at the start of every fight, a recurring wound applies **−10 to the character's combat
skill for that fight**.

**Why**: `design/03-rules.md` §1 already establishes that difficulty modifies the *skill*, never the
roll, and already publishes `−10` as the "Challenging" step. Reusing that step means the recurring
wound needs no new machinery, no new number, and no explanation — and critically it keeps the Wyrd
die clean, because it touches the skill rather than the roll.

**Rejected**:

- **1 Strain at the start of each fight.** Tempting — Strain is the engine's short-term pressure
  track and this is short-term pressure. Rejected because `design/03-rules.md` §5 says where Strain
  comes from and when it clears, but **never says what Strain does**. Building the recurring wound on
  it would make the wound's effect depend on an undefined mechanic, which is not applicable without a
  judgement call — the exact thing this feature exists to remove.
- **A test each fight, with the wound flaring on a failure.** More texture, and it adds a roll to
  every single fight for the rest of the chronicle. The ruleset's own rule is "only roll when it is
  dramatic"; a wound flaring for the two-hundredth time is not.

---

## D8 — Death is the last row, and the numbers are computed

**Decision**: death occupies `111+`. The distribution is computed by
[`check_aftermath.py`](./check_aftermath.py), not asserted.

**Why**: `design/03-rules.md` claims "most results are a lasting mark rather than death". `CLAUDE.md`
records that probability claims in this repository have been wrong twice and that both were caught
only by computing them. The claim is therefore a check, not a sentence.

What the computation shows, for the rows as written:

| Dropped by | A lasting mark | Death | Nothing lasting |
|---|---|---|---|
| 1 | 75% | 0% | 25% |
| 3 | 80% | 5% | 15% |
| 6 | 80% | 20% | 0% |
| 9 | 65% | 35% | 0% |
| 12 | 50% | 50% | 0% |

Across drops of 1–12, unweighted: **a lasting mark 70.8%, death 22.9%**. The ruleset's claim holds.

Two consequences worth stating rather than discovering later:

- **A drop of 1 or 2 cannot produce death at all** (the highest reachable total is 105 and 110
  against a death row starting at 111). Deferred death makes a light knockdown survivable *by
  construction*, not by luck.
- **Death overtakes marks only past a drop of 12** — a blow that beat a typical character's whole
  remaining Stamina twice over. The document states this rather than claiming death is always rare.

---

## What this feature deliberately does not decide

- **Whether a lasting wound ever heals.** R1.2 of epic #1. The wound record is defined so the
  question can be asked; no wording here presupposes an answer.
- **The critical tables.** A sibling issue. This document states the relationship — criticals resolve
  *during* the fight per damage type, Aftermath resolves *after* it, once per combatant who dropped —
  so the sibling has a fixed boundary to write against.
- **`engine/tables/aftermath.yaml`.** There is no `engine/` directory yet. The data file follows when
  the engine does.
