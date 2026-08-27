# Implementation Plan: The damage-type critical tables

**Branch**: `015-damage-type-criticals` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Enumerate four damage types, write one critical table for each in `docs/design/05-criticals.md` on the
`1d6 + points below zero` ladder, and settle where a critical stops and Aftermath starts. Compute the
modifier distribution at the values a real character has *before* drawing a single range, play a
worked fight by hand before settling the rows, and record the enumeration and the mortal-blow
composition as ADRs.

## The load-bearing decisions

**Four types, named for the shape of the wound.** `slashing`, `piercing`, `blunt`, `searing`. Naming
by wound shape rather than by weapon or by element is what keeps the set setting-agnostic: a weapon
taxonomy would need extending for every setting's armoury, and an element taxonomy would smuggle a
genre in. The first three also keep the two surviving fragments in the repo true — the
`critical-slashing` override example and "Blunt 5" — so nothing goes stale. `searing` is the
flexible fourth: fire in one setting, a beam weapon in another, renamed where it is neither.

**Four tables that actually differ, not one table said four ways.** The tables share the die, the
modifier and the row schema, and differ in **where each becomes mortal and what it leaves behind**.
This is the decision that makes the family worth having: if all four carried identical ranges and
differed only in prose, then damage type would be a rename with a mechanic's costume on, and the
ruleset's instruction to roll "on the table for the damage type" would mean nothing. A puncture
kills more readily than a bruise and cripples less; the tables have to say so or the distinction is
decorative.

**A critical never kills during the fight.** The worst row marks the blow **mortal**, and a mortal
blow is read on Aftermath's `death` row when the fight ends. This is the mirror of the re-read
`03a-2-aftermath.md` already publishes for Fate — one mechanism, running in both directions — so
Fate and `mortality: low` keep answering death exactly as they do now, deferred death survives
intact, and Aftermath's declared single modifier stays single. *High results are lethal*
(`03-rules.md`) stays true; the lethality is deferred, like every other death in this ruleset.

**No row charges Trauma.** `03-rules.md` §5 already charges 1 per critical taken. A row that charged
it again would price one blow twice, and the two counts would eventually disagree.

**Effects come from the set that already exists.** A critical row's effect is *nothing lasting*, a
wound record with one of `stamina_max: -N` / `skill: -N` / `dread: +N`, or `mortal`. Nothing new is
invented: `03a-2-aftermath.md` already declares that closed set and makes anything outside it a load
error, and the Mend undertaking (`04-session.md`) already knows how to step exactly those three.

**The family is repeatable, and declares no extra field.** Taking the same wound twice across a
chronicle is ordinary. Severity is not carried, because no rule consumes a critical's severity — and
a field nothing reads is how a table goes quietly stale (`03a-tables.md`).

**The lowest possible total is 2.** The die's lowest face is 1, and a critical means at least one
point below zero. Every table's first row starts there, because `03a-tables.md` requires a family's
ranges to begin at its lowest possible total.

## What the check script has to settle

`check_criticals.py`, stdlib only, exact arithmetic (`Fraction`), no sampling. Memoize the damage
model up front — it is re-run on every figure correction:

1. **The modifier distribution.** Points below zero, across the weapon band (`1d3`/`1d6`/`1d8`/`2d6`),
   armour (none / light `1d3` / modest `1d6` / heavy `2d6`, minimum 1 through), the telling blow's
   doubling, and remaining Stamina from 1 to 7 — not at a midpoint. This is what says whether the
   rows cover the range that actually occurs or trail off below it.
2. **The extreme.** The largest modifier the rules can produce at all, and how far out on the tail it
   lives, so the open top is a stated property rather than a hope.
3. **Every range is whole**, for every table: contiguous, non-overlapping, starting at 2, last row
   open at the top, and every total from 2 to well past the extreme landing on exactly one row.
4. **What each table weighs** — the chance of nothing lasting, of a lasting mark, and of a mortal
   blow, per damage type, at the modifiers that actually occur. This is where the four tables are
   shown to differ mechanically rather than in prose.
5. **The composed lethality.** A mortal critical fixes Aftermath at `death`, so per-type death odds
   must be computed *through* both tables and read against the 23% Aftermath already publishes. If
   criticals push the chronicle's death rate somewhere the ruleset does not intend, that is a
   finding, not a rounding error.
6. **Agreement with the figures merged issues computed** — 1.56 through modest armour and 4.5 hits
   to drop (`specs/013-the-mob-rule/check_mobs.py`), and Aftermath's 71% / 23%
   (`docs/design/06-aftermath.md`). A private damage model would make everything here internally tidy
   and wrong.
7. **Every figure the new document publishes**, asserted against the model, so drift fails loudly.

## The playtest

A worked fight, by hand, in `worked-criticals.md`: a character and a companion taking real blows of
different types at real Stamina, each critical resolved through the table and then through Aftermath.
Rules settle by being played here; paper reasoning about this ruleset has broken twice inside two
rolls. The worked fight is allowed to change the rows.

## Where the rules land

| Document | Change |
|---|---|
| `docs/design/05-criticals.md` | **new** — the four types, the four tables, the composition with Aftermath, what a setting may replace |
| `docs/design/04-tables.md` | the Criticals index row gains its link; the `critical-slashing` example stays true |
| `docs/design/03-rules.md` §2 | the critical rule points at the new file and names the types |
| `docs/design/06-aftermath.md` | the boundary table gains the mortal-blow row; the death-row section gains its mirror |
| `docs/design/24-authoring-a-setting.md` | the override example verified against the published keys |
| `docs/README.md` | the new document linked, so `tools/check_docs.py` passes |
| `docs/adr/` | two ADRs: the enumeration, and the mortal blow |

## The order of work

The computation comes first and is allowed to reject a row before it is written. The worked fight
comes second and is allowed to add what the computation cannot see. The design documents are written
last, from what survived, and the ADRs record what was rejected. Finally the guards —
`check_criticals.py`, `tools/check_docs.py`, `tools/backlog.py check`, and a grep for setting
vocabulary — are run rather than assumed.

## Constitution Check

Evaluated against `CLAUDE.md` and the accepted ADRs, per `.specify/memory/constitution.md`.

| Gate | How this feature satisfies it |
|---|---|
| Nothing unpublishable | The tables are written from the engine's own mechanics. No source text, no quotation, no catalogue. |
| No setting or system names | Type names are wound shapes in plain English; the fourth exists precisely so no setting's element becomes the engine's. Verified by grep. |
| Tone is a setting property | Descriptions say what happened and nothing about how it feels. A setting rewrites every word without touching an effect. |
| Computed, not inferred | Every range and every probability comes from `check_criticals.py`, which fails on disagreement — including with figures earlier issues computed. |
| Forward only | Table changes are tuning and additive (`09-evolution.md`); no rolled result is recomputed. |
| Design docs describe the present | `03a-1-criticals.md` is written in the present tense with no changelog; the decisions live in the ADRs. |
| Spec Kit cycle, `specs/` committed | This directory is committed with the change. |
