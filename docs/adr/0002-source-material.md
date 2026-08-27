# ADR 0002 — Read source material natively; do not adopt the system it came from

**Status:** accepted 2026-08-21
**Depends on:** [0001](0001-resolution.md)

## Context

Many settings are derived from published games
([`../26-authoring-a-setting.md`](../design/24-authoring-a-setting.md)). Since Wyrd resolves on
percentiles ([ADR 0001](0001-resolution.md)), it could adopt a percentile source game
wholesale and tune it — inheriting a large body of immediately usable material rather than
converting anything.

Should it?

## Decision

**No. Take the numbers and the content; keep Wyrd's own procedures.**

A source stat block is read **as printed**: a skill of 41 is 41%. Careers, gear, creatures,
prices and adventures need no conversion pass for their *numbers*. Resolution, combat, the
tracks and session structure stay Wyrd's.

## Why not adopt wholesale

**Special-case abilities are the drift risk.** Detailed source games carry a hundred or more
abilities that each modify one situation. Storing them is trivial. *Applying* them is not:
recognising that a narrated action is the one a given ability modifies is judgement, not
lookup. A hundred such judgements per session, sustained across years, is precisely the drift
[`../20-tooling.md`](../design/27-tooling.md) exists to prevent — and the GM will forget them
**inconsistently**, which is worse than not having them at all.

Wyrd's advance economy has no equivalent layer for the same reason
([`../03-rules.md`](../design/03-rules.md)).

**Depth per exchange.** A detailed source game resolves one exchange in roughly twice the
events and three extra lookups: strike, a separate defence roll, damage, where it landed,
protection at that place, a resistance subtraction, then a table keyed to the location. That
turns a five-exchange fight into a whole short session — and session length is the one
requirement Wyrd cannot negotiate away ([`../01-principles.md`](../design/01-principles.md)).

**Character cost.** Wyrd models characters asymmetrically: only the player's carries full
state ([`../19-state.md`](../design/22-state.md)). Adopting a source game wholesale would multiply
bookkeeping for every character the player does not control, which is most of them.

## Consequences

- Settings must declare **conversion rules**, so conversion is repeatable rather than
  improvised each time ([`../26-authoring-a-setting.md`](../design/24-authoring-a-setting.md)).
- Dropped mechanics survive as **prose on the converted entity**: a creature with a rage
  ability is *described* as prone to rage rather than tracked as having it.
- Where one genuinely matters mechanically, express it as a **Wyrd-die outcome** or a
  **difficulty band** — the two mechanisms the engine applies reliably.
- There is a **fidelity gap**: an encounter tuned for its own combat maths plays differently
  here. Accepted, and the **danger rating** is the dial that absorbs it
  ([`../03-rules.md`](../design/03-rules.md)).
