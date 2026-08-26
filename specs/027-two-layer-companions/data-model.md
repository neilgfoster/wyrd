# Phase 1 data model: Two-layer companions and a positive party track

This feature has no application data store — it defines terminology and field grouping inside an
existing design document (`docs/design/16-session.md`'s companion record, `docs/design/19-state.md`'s state
schema). This document is the authoritative field list `tools/check_companion_layers.py` checks
against.

## Companion record — the two layers

The existing companion record (`docs/design/16-session.md`) is unchanged in its field set. This
feature groups those fields into two named layers and adds nothing new except Bond's positive
mechanical effect.

### Narrative layer — who this person is

| Field | Type | Meaning |
|---|---|---|
| `objective.wants` | string | what they are actually here for |
| `objective.next_step` | string | what they will do about it next |
| `flaw` | string | the thing that gets them into trouble |
| `secret` | string | something the player does not know |
| `arc` | string | the choice this companion is heading toward |

No field on this layer is read by any resolution rule (a die roll, a table, a threshold). It
exists entirely for the GM to write and play the character.

### Mechanical layer — what they can do, what state they're in

| Field | Type | Meaning | Consumed by |
|---|---|---|---|
| `career` | career-id | bounds the skill % a test uses | resolution (`03-rules.md` §"Careers", career cap) |
| `bond` | -3..+3 | relationship to the player character | Tension gain (`04-session.md`); this feature's positive effect (below) |
| `taint` | integer | corruption accrued | transformation table (`design/03a-4-transformation.md`) |
| `strain` | integer | short-term wear | recovers at Rally (`04-session.md`) |
| `wounds` | list of wound records | lasting effects from Aftermath | same Aftermath table and rows as the player character (`03-rules.md` §3) |

**Five fields, closed.** No sixth field is added by this feature. A companion has no Stamina
track of its own separate from `wounds` (a wound's `stamina_max: -N` effect already covers it,
per `research.md`) and no capability score (`03-rules.md`'s existing rule, unchanged).

**Party-size bound (FR-002):** running a party of the largest size the design's own effective-size
table countenances (`03-rules.md`, danger scaling — 5 companions plus the player character = 6
bodies) means holding at most 5 × 5 = 25 mechanical values in mind at once, none requiring a
lookup beyond what the player character's own turn already requires (a career cap, a wound
effect). This bound is what `tools/check_companion_layers.py` asserts arithmetically rather than
by eye.

## Bond's positive mechanical effect (new)

Bond already modifies Tension gain in the negative direction (a strained-Loyalty pairing doubles
the *rate*; nothing today ties an individual companion's Bond to the *amount* an event adds).
This feature completes that:

> **An event that would raise Party Tension and names a specific companion adds 1 point of
> Tension per point that companion's Bond sits *below* 0, and 1 point *fewer* (minimum 0) per
> point their Bond sits *above* 0.**

Worked cases:
- Bond +3, an event that would add 1 Tension → adds 0 (floored, not negative).
- Bond +1, an event that would add 1 Tension → adds 0.
- Bond 0, an event that would add 1 Tension → adds 1 (today's rule, unchanged).
- Bond -2, an event that would add 1 Tension → adds 3.

This makes Bond the single mechanism underlying both directions of "how is the party doing" —
there is no second track to reconcile it against, and every companion's contribution is legible
from one number the design already tracks. A generic event that does not name a specific
companion (e.g. "the party goes hungry") is unaffected by any single companion's Bond and applies
at the stated rate, matching today's behaviour.

## ADR: `docs/adr/0034-bond-is-the-positive-party-track.md`

Records the rejected alternative (a standalone Cohesion-style track mirroring Tension) and the
reasoning above, per `CLAUDE.md`'s ADR criteria (a real alternative rejected; a future contributor
would plausibly propose it again).

## Confirmed, unchanged: companion advancement and succession

`docs/design/03-rules.md`'s existing sentences are confirmed against this model with one added
cross-reference, no substantive change:

- "Companions advance rarely and simply — one competence gained or limitation lost at a downtime"
  → the advance lands on the mechanical layer (most naturally: `career`, by widening what tests it
  legally covers, or a wound's effect on the mechanical layer being lessened — Mend already covers
  that case).
- "A successor inherits none of the competence and all of the position" → the successor's
  mechanical layer starts fresh (baseline `career`, `bond: 0`, `taint: 0`, `strain: 0`, no
  `wounds`); the position (their role in the party, the objective slot they fill) carries over;
  their narrative layer is written fresh, same as any new companion.
