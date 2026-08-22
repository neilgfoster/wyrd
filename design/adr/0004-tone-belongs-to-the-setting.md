# ADR 0004 — Tone is declared by the setting, not built into the engine

**Status:** accepted 2026-08-21

## Context

Wyrd began as an engine for one register. Four of its seven founding principles were
statements about that register: nothing is fated about the player, victory is usually
mitigation, power stays flat, and most sessions stay small.

They read as engine principles. They are not.

## Decision

**Tone is a setting property.** Each setting declares a **tone contract** in `setting.yaml`
— `prophecy`, `victory`, `power_curve`, `scope`, `scale_drift`, `mortality`, `register` — and
the engine's job is to **hold that line against its own drift, in whichever direction the
setting points** ([`../01-principles.md`](../01-principles.md)).

Under `prophecy: forbidden` the engine refuses to invent a destiny even where the story would
be neater with one. Under `prophecy: central` it builds one. The discipline is identical;
only the direction differs.

A chronicle may narrow the contract in `houserules.yaml`, never widen it.

## Alternatives rejected

**Keeping tone in the engine.** Simpler, and it produced a coherent engine — for exactly one
kind of game. Any second setting in another register would have had to fight the engine
rather than configure it, and "setting-agnostic" would have meant "agnostic about content,
opinionated about mood", which is not agnostic.

**Dropping the constraints entirely** on the grounds that they were tone. Rejected because
one of them was not. *Significance must be earned* survives as an engine principle, restated
neutrally: a heroic chronicle also needs its significance earned, or its triumphs mean
nothing. The others genuinely were tone and moved out.

## Consequences

- Violating the declared tone became a GM contract **MUST NOT**, alongside retconning a roll.
- `power_curve` makes the advancement economy a **configuration**, not a fixed rule: the flat
  curve described in [`../03-rules.md`](../03-rules.md) is one setting of a dial.
- Engine mechanics needed **neutral default labels**, because the names themselves carried
  genre — a track called Corruption presumes moral decay. Settings rename freely, and the
  rename is presentation-only.
- Several later corrections came from this: era sequences that assumed decline, succession
  text that assumed rot, a campaign layer that assumed escalation. Each had baked a tone into
  a mechanism's *description* rather than its vocabulary, which is the harder kind to find.
