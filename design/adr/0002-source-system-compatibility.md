# ADR 0002 — Read source material natively; do not adopt a source system

**Status:** accepted 2026-08-21
**Depends on:** [0001](0001-d100-resolution.md)

## Context

Wyrd's settings are largely derived from published games
([`../13-authoring-a-setting.md`](../13-authoring-a-setting.md)). Since Wyrd is percentile
([ADR 0001](0001-d100-resolution.md)), it could simply adopt a percentile source system
wholesale and tweak it — inheriting a vast body of directly usable material.

Should it?

## Decision

**No. Take the numbers and the content; keep Wyrd's own procedures.**

A source stat block is read **as printed** — a skill of 41 is 41%. Careers, gear, creatures,
prices and adventures are usable without a conversion pass. Resolution, combat, tracks and
session structure remain Wyrd's.

## Why not adopt wholesale

**Talents are the drift risk.** Detailed source systems carry a hundred or more special-case
abilities, each a conditional that must fire at the right moment. State is not the problem —
the CLI holds a hundred talents trivially. *Applying* them is, because noticing that a
narrated action is the one a given talent modifies is judgment rather than lookup. A hundred
such judgments per session, across years, is exactly the drift
[`../07-tooling.md`](../07-tooling.md) exists to prevent. An LLM will forget them
*inconsistently*, which is worse than not having them.

**Combat depth.** A detailed source resolves an exchange in roughly twice the events and
three extra lookups — attack, separate defence roll, damage, hit location, armour by
location, toughness subtraction, then a location-specific critical table. That turns a
five-exchange fight into an entire twenty-minute session. Session length is the one
requirement Wyrd cannot negotiate away.

**Character cost.** Wyrd commits to asymmetric characters — only the player's carries full state
([`../06-state.md`](../06-state.md)). Adopting a source system wholesale would multiply
bookkeeping for characters the player does not control.

## Consequences

- Settings must declare **conversion rules** so conversion is repeatable rather than
  improvised ([`../13-authoring-a-setting.md`](../13-authoring-a-setting.md)).
- Dropped mechanics survive as prose on the converted entity: a creature with a rage ability
  is *described* as enraged rather than tracked.
- Where one genuinely matters, express it as a Wyrd-die outcome or a difficulty band — the
  two mechanisms the engine reliably applies.
- There is a **fidelity gap**: a source encounter tuned for its own combat maths will play
  differently here. Accepted; the danger rating is the tuning dial.
