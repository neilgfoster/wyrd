# The 40k line — what belongs in the engine, and what is setting

Read for a specific question: does the 40k material change **engine** design, and where does
the line fall between common machinery and setting data?

Sourced from *Only War*, *Deathwatch* and *Black Crusade* core rulebooks (402pp each, all
with text layers). All are WFRP 2e descendants, so the resolution core is already covered by
[wfrp-mechanics](wfrp-mechanics.md); this note records only what is *new or clarifying*.

---

## Three findings that affect the engine

### 1. Comrades — companions as a relationship, not a stat block

*Only War* gives each player a **Comrade**: a personal squadmate who has **no character
sheet**. A Comrade is either **in Cohesion** with their character or not, and that binary
plus a short list of **Orders** is the entire mechanical surface.

> "For the next Round, all Player Characters with their Comrade in Cohesion gain a +10 to all
> Dodge Tests."

This is a published, playtested version of the asymmetric-NPC decision in
[`../design/06-state.md`](../design/06-state.md), and it is more radical than what Wyrd
currently proposes. Wyrd's companions carry skills and stamina; Only War's carry *presence*.

**Take:** make companions explicitly **two-layer**.

- **Narrative layer** — agenda, flaw, bond, secret, arc. Rich, because this is what makes them
  people and what makes their loss land ([`../design/04-session.md`](../design/04-session.md)).
- **Mechanical layer** — deliberately thin. Present or absent; in cohesion or not; one or two
  standing effects. No full sheet.

That keeps companions dramatically heavy and mechanically cheap, which is exactly the ratio a
one-player game needs. A party of four should cost almost nothing to run and everything to
lose.

### 2. Cohesion — the positive counterpart to Party Tension

*Deathwatch* runs **Solo Mode** and **Squad Mode**, with **Cohesion** as a spendable pool
available only in the latter:

> "When a Kill-team is in Squad Mode, they have access to a resource known as Cohesion.
> Cohesion may be spent to trigger certain effects and abilities that benefit the group."

Wyrd currently models the party in one direction only — **Party Tension**, which rises toward
a break ([`../design/04-session.md`](../design/04-session.md)). Friction is represented;
functioning is not.

**Take:** the party track should run **both ways**. Whether that is two resources or one axis
with two ends is a playtest question, but the shape is clear: a party that has been through
something together should be able to *spend* that, not merely avoid falling apart.

This also gives the Interlude session real mechanical weight — a beat spent on a companion's
problem currently only lowers Tension, and should also build something usable.

Deathwatch's mode toggle is worth stealing too: a lone protagonist and a protagonist working
as part of a unit are different characters, and saying which one you are right now is cheap.

### 3. Corruption has a *direction*, not only a magnitude

*Black Crusade* is the inversion: characters have already chosen Chaos, and Corruption is
**advancement**. Crossing an **Alignment Threshold** determines which of the four Powers
claims you; crossing a **Mutation Threshold** changes your body. Fate is replaced by
**Infamy** — the same resource, earned by reputation rather than destiny.

Wyrd's corruption is currently a scalar with a hidden doom clock, ending in damnation and the
character becoming an NPC ([`../design/03-rules.md`](../design/03-rules.md)).

**Take:** corruption should carry a **direction as well as a quantity**, and Wyrd already has
the mechanism — the **Corruption Weakness** derived from the character's Passion and Cruel
Misfortune ([tor-concepts](tor-concepts.md)). Black Crusade shows what to do with it: the
direction should determine *what you become*, not merely flavour the descent.

It also offers an alternative endgame worth recording. Wyrd's damnation removes the character
from the player's hands. Black Crusade's keeps them playable and simply changes whose they
are. For a chronicle meant to run years, "you may keep playing, but you belong to something
now" may be the better answer than "make a new character" — and it sits well beside the
succession rules in [`../design/05-campaign.md`](../design/05-campaign.md).

---

## Confirmed engine-level (not setting)

Present across every book in the line, identically:

- **Fate points** (Infamy in Black Crusade) — same mechanic, different noun
- **Corruption** and **Insanity** as parallel tracks
- **Fear and Terror** tests
- **Criticals** past zero wounds, by damage type
- Percentile resolution, characteristics, careers-as-archetypes

That this survives four different games with four different premises is good evidence these
belong in `engine/` and not in `settings/`.

## Confirmed setting-level

- **Psychic phenomena / Perils of the Warp** — structurally the miscast table; reskin only
- **The theology** — four named Powers with distinct alignments, against the Old World's
  vaguer Ruinous Powers. Alignment thresholds are 40k-shaped and want a Fantasy equivalent
  rather than a copy
- **Careers, gear, creatures, calendar, names** — data, as expected
- **Voice** — confirmed as the hardest part. Only War's register is bureaucratic doom, Black
  Crusade's is exultant, Deathwatch's is liturgical. These are not one setting with three
  moods; the register is per-line

## Not taken

- **Vehicles** — Only War has a full vehicle subsystem. Out of scope: no maps, no positioning.
- **Squad Mode ability trees** — the concept transfers, the ~40 purchasable abilities do not.
  Same reasoning as talents in [ADR 0002](../design/adr/0002-wfrp2-compatibility.md).
- **Ranged-dominant combat pacing.** 40k combat is gun-first, which changes the *feel*
  markedly but needs no new rules — Warlock's ranged attacks already work. Worth noting for
  `settings/imperium/voice.md`: a firefight is not a swordfight and should not be narrated
  like one.

---

## Consequence for the design

Two changes to make, both small and both improvements:

1. **Split companions into narrative and mechanical layers**, with the mechanical layer
   deliberately thin. Amends [`../design/04-session.md`](../design/04-session.md) and
   [`../design/06-state.md`](../design/06-state.md).
2. **Give the party track a positive direction**, and give corruption a direction as well as
   a magnitude. Amends [`../design/03-rules.md`](../design/03-rules.md) and
   [`../design/04-session.md`](../design/04-session.md).

Neither is urgent enough to apply unilaterally — both change how play *feels*, so they want
a decision rather than a commit.
