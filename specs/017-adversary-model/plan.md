# Implementation Plan: The adversary model

**Branch**: `017-adversary-model` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Define the **adversary block** — the complete set of fields the ruleset reads off an opponent —
give `setting/bestiary.yaml` a schema and a validator over it, and settle how danger scaling reaches
an opponent's skill percentages as well as its numbers. Write a new design document for the
adversary, rewrite in place the four documents that currently describe an opponent by not describing
one, and record two decisions as ADRs. Every figure is computed before it is written, including the
skill-adjustment curve, which is derived from the party sizes a real chronicle has rather than
chosen and justified afterwards.

## The load-bearing decisions

**An adversary is a thin block, and a named antagonist is that block inside a person.** The
character model ([`03b-the-character.md`](../../doc/design/04-the-character.md)) carries Taint, Trauma,
Strain, Resolve, Fate, Luck, a career, a career history, a Loyalty and an advancement economy. None
of that exists for the thing a character kills in a corridor, and giving it all of that would mean
running an advancement economy for a wolf. The block carries only what a published rule reads. A
nemesis is not a second model: it is a `character` entity ([`14-entities.md`](../../doc/design/27-entities.md)
already says a nemesis is a `character` with `role: nemesis`) that *also* carries an adversary block.
One description of an opponent, reached two ways. The alternative — adversaries as full characters —
is the rejected option in the ADR, and it is not a straw man: it is what most percentile systems do,
and it is why most of them are slow to run.

**The block is absolute. Scaling happens to the encounter, never to the entry.** A bestiary entry
means one thing whatever content refers to it. This is what keeps a lookup table a lookup table, and
it is what stops the same creature reading differently in two arcs.

**An opponent tests an unlisted skill at its baseline.** One required field. The untrained 10% is a
rule about people who never learned a thing, and opposition is not that; worse, against a 10%
fallback the crowd rule's *ahead by 20 or more* test qualifies almost anything a merely competent
character is rolling against, which would quietly convert the crowd rule from a bounded exception
into the default way fights resolve.

**Traits come from a closed vocabulary.** A trait is a display name plus an effect the engine
defines, acting only on difficulty, damage, Stamina, armour or the Wyrd die. This is the line
between *retune* and *add a mechanism*
([`13-authoring-a-setting.md`](../../doc/design/26-authoring-a-setting.md)), and it is a line the
validator can hold, which free text is not. The vocabulary is small on purpose and is allowed to grow
later by an engine change, which is the correct cost.

**Danger scales skill values as well as counts, additively, bounded, and exactly zero at the
identity case.** `03-rules.md` §7 has always claimed both, and it stands. But a percentage cannot be
multiplied by `danger_effective` — 45 × 2.64 is not a skill — so the ratio resolves to a **points
adjustment added to the percentage**, which is how every other modifier in this engine works. Three
properties are non-negotiable, and the third is the one that decides the shape:

1. **Additive**, in the engine's own units.
2. **Exactly +0 when the party matches `written_for`**, or the identity case that
   [ADR 0024](../../doc/adr/0024-a-party-is-worth-less-than-its-head-count.md) exists to protect
   is lost on the second of the two quantities §7 scales.
3. **Bounded inside the difficulty ladder.** The ladder is the engine's entire vocabulary for how
   much harder a thing can get. An adjustment that runs past it is describing a difficulty the
   engine has no word for.

## What the check script has to settle

`check_adversary.py`, stdlib only, exact arithmetic (`Fraction`) wherever a figure is exact. Fight
resolution is the expensive part here — unlike 016, which was arithmetic — so **the exchange
distribution is memoised up front** and every derived figure is read from that table rather than
re-resolving the fight. Each figure correction is otherwise a full re-run.

1. **The achievable ratio range.** `party_effective / H(written_for)` across every party size and
   `written_for` a chronicle plausibly produces. This is the *input domain* of the adjustment curve
   and it has to be computed before the curve is fitted, not assumed to be "about 0.5 to 2".
2. **The adjustment curve, derived rather than picked.** Fit the coefficient by requiring the
   extremes of that computed range to land on ladder rungs, then check the result at every realistic
   pairing. A logarithmic form is the leading candidate because it is the only one that is symmetric
   in the ratio — a party of one against content for six and a party of six against content for one
   should be equal and opposite — and because it composes with §7's own harmonic curve rather than
   fighting it. **The candidate is not the conclusion**: if the fitted coefficient puts realistic
   pairings on values the engine cannot express, the form is rejected and a stepped table is fitted
   instead.
3. **The identity case, exactly.** Party of `p` against `written_for: p` yields adjustment `+0` for
   every `p` in range — an exact equality, not a near one, and asserted as such.
4. **The bound at both ends**, and what happens past it: an adjusted skill that would exceed the top
   of the ladder or fall below zero. Both are reachable and both need a stated answer.
5. **The rounding granularity.** Whether the adjustment rounds to 5s (the advancement step) or 10s
   (the ladder step), decided by which one preserves the identity case and the monotonicity — the
   adjustment must never *rise* as the party shrinks.
6. **A complete exchange against a written opponent**, resolved from the rules as written: opposed
   test, degrees, telling blow, damage, armour subtraction, the minimum of 1, the drop below zero,
   the critical table selected by damage type, and Aftermath.
7. **The crowd lookup against both a written mob body and a written nemesis**, landing on opposite
   sides, with the deciding field named — and the boundary case where a character's skill is exactly
   20 ahead.
8. **Agreement with every figure earlier issues already published**, so a change here cannot silently
   contradict them: the one-blow band (**67%–100%** at Stamina 1 unarmoured, **11%** in the lightest
   armour, **33%** at Stamina 2), the free clear's **1.25×–1.82×** discount, and the drop rates
   **14.8%** and **48.6%**. Non-zero exit on any disagreement.

## The validator

`tools/check_bestiary.py`, stdlib only, following the conventions `tools/check_docs.py` already
sets. It takes a `bestiary.yaml` path, and:

- rejects a **missing required field**, naming entry and field;
- rejects an **unrecognised field** rather than ignoring it — the quiet path by which a setting adds
  a mechanism;
- rejects an **out-of-range value**: an armour rank outside the published set, a damage type outside
  the closed four ([ADR 0022](../../doc/adr/0022-four-damage-types-named-for-the-wound.md)), a
  percentage outside the scale in `03b-the-character.md` §2;
- rejects a **trait effect outside the closed vocabulary**;
- exits non-zero on any failure, and reports **every** failure rather than the first.

It ships with a fixture bestiary that exercises each rejection, because a validator with no failing
case is a validator nobody has seen fail.

## The worked example

`worked-exchange.md`: one written opponent and one written character taken through a complete fight
from the rules as written, every figure produced by the check script. It is where the block is either
shown sufficient or shown to be missing a field — the only place every rule that reads an opponent
appears together. It also carries the same encounter prepared at three party sizes, so the count
scaling and the skill adjustment are visible in one place rather than described separately.

## Where the rules land

| Document | Change |
|---|---|
| `doc/design/06-the-adversary.md` | **new**: the adversary block, the baseline, the trait vocabulary, what an opponent does on a turn, what happens when one drops |
| `doc/design/04-the-character.md` §4 | rewritten in place — it currently says the adversary model "is not yet decided" |
| `doc/design/03-rules.md` §7 | the skill-value half of the scaling made explicit: the adjustment, the identity case, the bound. §7's claim stands; what is added is how it is evaluated |
| `doc/design/26-authoring-a-setting.md` | `bestiary.yaml` gains its schema and an example, in the shape the other setting files already use |
| `doc/design/27-entities.md` | the `creature` row says what a creature carries; the nemesis note says a `character` used as opposition carries an adversary block |
| `doc/README.md` | the new document linked from the hub, or `check_docs.py` fails |
| `doc/adr/0025` | the thin adversary block, against the full character model |
| `doc/adr/0026` | the skill adjustment: additive, identity-exact, ladder-bounded, against multiplying the percentage |

## The order of work

The computation comes first and is allowed to reject the curve before it is written into anything —
including rejecting the logarithmic form. The validator and its fixtures come second, because they
are what make the schema real rather than a table of field names. The worked exchange comes third and
is allowed to expose a missing field in the block. The design documents are written last, from what
survived, and the two ADRs record what was rejected. Finally the guards — `check_adversary.py`,
`tools/check_bestiary.py`, `tools/check_docs.py`, `tools/backlog.py check`, and a grep for setting
vocabulary and for any term named but not defined — are run rather than assumed.

## Constitution Check

Evaluated against `CLAUDE.md` and the accepted ADRs, per `.specify/memory/constitution.md`.

| Gate | How this feature satisfies it |
|---|---|
| Nothing unpublishable | The block is a field list and a curve. No source text, no quotation, no catalogue. The example opponent is invented for the purpose. |
| No setting or system names | The block names no creature and no system; the example uses descriptive English. Verified by grep. |
| Engine labels are descriptive English | *baseline*, *armour rank*, *damage type*, *trait* — none requires having read a particular book. |
| Tone is a setting property | The block says what an opponent rolls and survives, never how frightening it is meant to feel. Dread is a track that already exists and is not extended here. |
| Computed, not inferred | Every figure comes from `check_adversary.py`, which fails on disagreement — including with the figures #13, #8 and #11 already published. The curve is fitted before it is written down. |
| Forward only | Scaling is computed when content is prepared; nothing already played is recomputed (`09-evolution.md`). |
| Design docs describe the present | The four existing documents are rewritten in place, present tense, no changelog. Rejected alternatives live in the ADRs. |
| A setting may never add a mechanism | The closed trait vocabulary is the enforcement, and the validator holds it. |
| Spec Kit cycle, `specs/` committed | This directory is committed with the change. |

### One gate worth naming explicitly

**A new design document must be reachable from `README.md`.** Four indexes went stale silently
before `check_docs.py` existed. `doc/design/06-the-adversary.md` is linked from the hub in the same
commit that creates it, and the check is run rather than assumed.
