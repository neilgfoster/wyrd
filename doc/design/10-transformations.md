# Transformations

The table a character rolls on **when Taint crosses a threshold**. It is what
[`03-rules.md`](03-rules.md) means by *a Taint threshold forces a Transformation*, and it is the
only place the permanent, physical shape of Taint is defined.

It is a family of the kind [`07-tables.md`](07-tables.md) defines, and everything below is
declared within those conventions.

---

## The thresholds

**A Taint threshold sits at every multiple of 3, starting at 3: 3, 6, 9, 12, and so on.** The first
two coincide exactly with the Wyrd-die bands in [`03-rules.md`](03-rules.md) §1 (0–2 clean, 3–5 the
die starts turning, 6+ it turns further) — the only numeric anchor that section already gave. The
spacing continues past 6 on the same interval, because Taint does not stop being trackable once the
die reaches its worst band ([ADR 0029](../adr/0029-transformation-thresholds-at-every-three-taint.md)).

**Crossing a threshold** means Taint moves from a value below it to a value at or above it in one
event — the Bargain, Exposure, or Invocation ([`03-rules.md`](03-rules.md) §4). Each of those gains
at most 3 Taint in one event, so a single event can cross at most one threshold outright, though it
may still leave the character above it by more than the roll that triggered the crossing removed
(see below).

## Body, never mind

**A Taint threshold always forces a Transformation. It never forces an Affliction.**

[`03-rules.md`](03-rules.md) §4 previously read a threshold as forcing "a Transformation (body) or
an Affliction (mind)," which collided with §5: Afflictions arise only when Trauma — a separate
track — reaches 6+, and a character then tests on every further Trauma point, taking an Affliction
on a failure. Taint and Trauma are independent scores with independent triggers. This document is
the one that resolves the collision: Taint thresholds produce Transformations, full stop; Afflictions
are Trauma's business alone, defined in the affliction table (`11-afflictions.md`, not yet
written) once it lands. Where the two tables disagree in the future, this statement governs until an
ADR supersedes it.

## The roll

| | |
|---|---|
| **key** | `transformation` |
| **die** | `1d6` |
| **modifier** | none |
| **lowest possible total** | `1` |
| **uniqueness** | unique per character |
| **extra row fields** | `severity` |

**The family is unique per character.** Carrying the same permanent change twice is not an
ordinary event the way taking the same wound twice is
([`07-tables.md`](07-tables.md)); a duplicate roll is re-rolled.

**When the table is exhausted** — a character has already taken all six rows — the *hidden
threshold* below has, by construction, already run out first in every realistic case (its range
tops out at 8; see below), so exhaustion of the table itself is not expected to be reachable in
play. If it is ever reached regardless, it is read the same way the hidden threshold running out
is read: the character is lost, and joins the opposition.

## The table

| Range | Severity | Effect | Description |
|---|---|---|---|
| 1 | 1 | Add a minor, cosmetic physical change: skin, eyes, voice, or bearing marks visibly as not-quite-human. No mechanical penalty or bonus. | A small thing shifts and does not shift back — the colour of an eye, the grain of a voice. |
| 2 | 1 | As above, but the change is harder to conceal in ordinary company (clothed, indoors, in company that does not already know). | The change is small, and it is the kind of small that people notice anyway. |
| 3 | 2 | A minor physical capability changes — something is gained and something is lost, net neutral in play, GM's call on the specific trade. | The body starts doing something it did not used to, and stops doing something it did. |
| 4 | 2 | A trait the character can no longer fully mask: it surfaces under stress, injury, or strong feeling, whether or not they will it. | It used to be something they controlled. Now it controls when it shows. |
| 5 | 3 | A substantial physical change that alters how the character is treated by strangers on sight — the first thing anyone notices. | Whatever this is, it is the first thing a stranger's eyes go to now. |
| 6 | 4 | A major, irreversible change to what the character *is*, bodily — a step that cannot be walked back by anything short of exceptional means. | Something that was never coming back has gone, and something that was never there has arrived. |

Every row is a **change**, not a penalty and not a reward — no row grants a net mechanical
advantage or applies a punitive stat loss, and none carries a tone (grim, heroic, comic): what a
row costs or grants in a given chronicle is for the GM to render in that setting's register, never
baked into the row itself.

**A result consumes Taint equal to its severity** ([`03-rules.md`](03-rules.md) §4), dropping the
character back toward the threshold. If Taint is still at or over the threshold just crossed, roll
again (re-rolling a duplicate row as above). [`check_transformation.py`](../../tools/check_transformation.py)
computes that this always terminates — see below.

## Termination of the re-roll loop

Two independent guarantees, both computed rather than asserted
([`tools/check_transformation.py`](../../tools/check_transformation.py)):

**1. The severities are large enough that the loop clears quickly in practice.** Across every
Taint value from 0 to 20 and every legal single-event gain (1, 2 or 3 — the Bargain and Exposure's
maximum), the loop's worst case within that scan is **3 re-rolls**, and its expected case ranges
from **1.00** (a 1-point gain, which never overshoots a threshold) to **1.74** (a 3-point gain,
crossing a threshold by up to 2):

| Taint before gain | Gain | Threshold crossed | Worst-case re-rolls | Expected re-rolls |
|---|---|---|---|---|
| 2 | 1 | 3 | 1 | 1.00 |
| 2 | 2 | 3 | 2 | 1.33 |
| 2 | 3 | 3 | 3 | 1.74 |
| 5 | 3 | 6 | 3 | 1.74 |
| 11 | 3 | 12 | 3 | 1.73 |
| 20 | 3 | 21 | 3 | 1.73 |

**2. Even if severities were smaller, the table itself bounds the loop.** It holds six rows and is
unique per character, so no re-roll burst can exceed **6** re-rolls before the *table exhausted*
outcome fires — which this document reads identically to the hidden threshold running out (below).
That is a hard ceiling independent of the severity numbers chosen, and it is why the table above is
safe even against a future re-tuning of its severities: termination does not depend on getting the
severity values exactly right, only on the table staying finite and unique, which
[`07-tables.md`](07-tables.md) already requires of every family in this class.

## The hidden threshold

On the character's **first** Transformation, the GM secretly rolls **1d6 + 2** (range **3–8**) and
writes it to `chronicle.yaml` as the character's hidden threshold — how many Transformations this
character can endure before they are lost. **The player never sees this number, in any form,
including as unease** ([`23-diegesis.md`](23-diegesis.md)): the "never shown" visibility class
covers it explicitly.

**It is written once and never re-rolled.** A hidden threshold rolled on a later Transformation
would mean the number the character has already been narrated against silently changed underneath
them; the roll happens exactly once, at the first Transformation, and stands for the rest of the
character's life.

**When the count of Transformations the character has taken reaches the hidden threshold, the
character is lost.** Concretely, to the chronicle:

- The player character (or companion) is removed from `status: with-party`
  ([`19-state.md`](19-state.md)) and is no longer played by the operator.
- They become a character the **GM controls**, from that point on — an NPC, and specifically one
  available to the opposition. They do not die and they do not simply vanish from the story; they
  join it from the other side.
- This is not a death and does not touch Fate ([`03-rules.md`](03-rules.md) §3) — Fate is a valve
  against dying, and this is a different kind of loss entirely, one no resource buys back.
- For a player character, this ends that character's chronicle in the ordinary way a lost
  protagonist does ([`18-campaign.md`](18-campaign.md)): a successor may follow. For a companion,
  the party simply loses them, the way any companion can be lost.

## Dread

**Each Transformation adds Dread equal to its severity**, the same number that was just spent on
Taint — one measured quantity read twice, rather than a second number invented to track the same
thing ([ADR 0029](../adr/0029-transformation-thresholds-at-every-three-taint.md)). Dread accumulates and does not fade; it is a running total across every Transformation the
character carries.

**When a transformed character is seen** by anyone who does not already know them well enough to
have made their peace with it (the GM's call, grounded in the fiction — a stranger, a crowd, an
official), any reaction or social test that party makes toward the character is penalised by the
character's total Dread, applied the same way every other points modifier in this engine applies
(the difficulty ladder in [`03-rules.md`](03-rules.md) §1 is +20 to −40; Dread stacks onto it, and
the same clip applies — a percentage cannot fall below 0). Dread is Taint's social cost: what marked
the body also marks how the world responds to it, and unlike Taint itself, Dread is not spent away
by anything — it is the standing price of being seen.
