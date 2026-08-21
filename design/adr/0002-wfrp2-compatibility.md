# ADR 0002 — 2e/Dark Heresy compatibility without adopting the system

**Status:** proposed
**Date:** 2026-08-21
**Depends on:** [0001](0001-d100-resolution.md)

## Context

If Wyrd goes percentile ([ADR 0001](0001-d100-resolution.md)), the obvious next step is to
adopt WFRP 2e (and Dark Heresy, its 40k sibling) wholesale and tweak. The library argument
that justified d100 seems to argue for this too: ~700 PDFs of native material.

Should we?

## Decision

**No. Adopt 2e's *numbers and content*; keep Warlock's *procedures*.**

> **2e-compatible, Warlock-paced.**

Wyrd reads a 2e or Dark Heresy stat block natively, and resolves it with Warlock's loop.

## Why not full 2e

### 1. Talents are the real weight, and they are the drift risk

2e has ~100 talents; Dark Heresy more. Each is a conditional that must fire at the right
moment — *Strike Mighty Blow* here, *Sure Shot* there, *Lightning Reflexes* only in that
circumstance.

State is not the problem: the CLI can hold a hundred talents trivially. **Applying** them is
the problem, because noticing that a narrated action is the one a given talent modifies is a
judgment call, not a lookup. A hundred such judgments per session, across years, is exactly
the drift that [`../07-tooling.md`](../07-tooling.md) exists to prevent. An LLM GM will
forget talents *inconsistently*, which is worse than not having them.

Warlock has no talent layer at all. That is a feature here.

### 2. Combat depth per exchange

| | Warlock / Wyrd | WFRP 2e |
|---|---|---|
| Attack | opposed roll | attack roll |
| Defence | (same roll) | separate dodge/parry roll |
| Damage | 1 roll | 1 roll |
| Location | — | reversed digits |
| Armour | subtract dice | look up by location |
| Toughness | — | subtract TB |
| Wounds | stamina | wounds |
| Critical | if below 0, one table by damage type | critical table **by location**, per point over |

Roughly double the events and three extra lookups per swing. In a twenty-minute session on a
phone, a five-exchange fight is the whole session under 2e and one beat of it under Warlock.

The founding brief was explicit: narrative-focused, simple, no detailed maps. Full 2e
contradicts it.

### 3. NPC modelling cost

[`../06-state.md`](../06-state.md) already commits to **asymmetric NPCs** — companions and
enemies are cheap to model, only the PC carries full state. Adopting 2e wholesale would
mean a party of five NPC companions each carrying nine characteristics, thirty skills and a
talent list. That is a 5× bookkeeping increase for characters the player does not control.

## What we take instead

**Numbers, read as printed.** A 2e stat block gives `WS 41, BS 32, T 35, W 12`. Wyrd uses
`WS 41` directly as the weapon skill percentage, `T` for soak, `W` as stamina. No
conversion, no translation pass. This is the entire benefit that motivated d100 and it does
not require adopting the procedures.

**Content.** Careers and their advance schemes, skill lists, gear and prices, creature stat
blocks, NPC write-ups, and the whole adventure corpus — usable directly. Dark Heresy's career
list becomes the 40k setting's career data with no work.

**Difficulty ladder.** 2e's six bands (Easy +20 … Very Hard −40), replacing Warlock's two.

**Characteristics as an optional depth.** Wyrd's flat skill model can read a 2e characteristic
as the skill value where no specific skill exists. `Ag 38` *is* the dodge score.

## What we leave

- **Talents** — treated as descriptive notes on a stat block, not mechanics. A creature with
  *Frenzy* is described as frenzied; the GM does not track a talent.
- **Hit locations** — Warlock's damage-type critical tables are better for text anyway, since
  they describe an injury rather than a coordinate.
- **Separate parry/dodge rolls** — Warlock's single opposed roll stands.
- **Toughness Bonus subtraction** — armour dice already do this job.
- **Advance schemes as gates** — Wyrd keeps Warlock's advance triggers and 1e's career exits
  ([`../../reference/wfrp1-voice.md`](../../reference/wfrp1-voice.md)), which are better
  suited to a chronicle than a percentage ladder.

## Consequences

- The library is readable without a conversion layer, which was the point.
- Combat stays fast enough for a twenty-minute session.
- There is a **fidelity gap**: a 2e adventure's tuned encounter will play differently under
  Warlock's combat maths. Accepted — Wyrd adapts scenarios anyway
  ([`../05-campaign.md`](../05-campaign.md)), and scenario Threat rating `T` is the tuning
  dial.
- Talents being descriptive means some published NPCs lose mechanical distinctiveness. Where
  one genuinely matters, express it as a **bane/boon on the Wyrd die** or a difficulty band —
  both of which the engine already has.

## Alternative considered

**Adopt 2e fully and lean on the CLI to carry the weight.** Rejected: the CLI can carry
state but not judgment, and talents are judgment. It would also break the session-length
constraint, which is the one requirement Wyrd cannot negotiate away — a system that needs
forty minutes per fight cannot be played on a train.
