# ADR 0015 — Loyalty has three relations, not two

**Date:** 2026-08-25
**Status:** Accepted

## Context

Some settings divide their world deeply enough that two people from opposite sides of the line would
never share a road. The engine has to know, because the player runs one character and **the GM runs
everyone else** ([`04-session.md`](../04-session.md)) — so "may this companion join?" is a question
answered dozens of times across a chronicle, unprompted. Left to judgement it drifts, and the drift
is invisible: nothing about a party that should never have formed looks wrong.

It is engine work by the hard rule in
[`13-authoring-a-setting.md`](../13-authoring-a-setting.md): a setting may extend, retune, rename or
disable, and may **never add a mechanism**. A constraint on party composition is a mechanism.

Nothing like it existed. The character record had a career and no notion of what a character serves,
and the party track measured tension without any concept of who could be in the party at all.

## Decision

**Every character carries a `Loyalty`. Between any two Loyalties a setting declares one of three
relations, and only the interesting ones are written down.**

| Relation | Effect |
|---|---|
| *(undeclared)* | nothing |
| **strained** | Party Tension rises **twice as fast** while both are in the party |
| **irreconcilable** | the companion **cannot join**; the engine refuses rather than asking |

The engine fixes nothing about *which* Loyalties exist. A setting declares them and names them, the
same way it declares skills ([ADR 0013](0013-the-engine-names-no-skill.md)).

`strained` reuses **Party Tension** ([`04-session.md`](../04-session.md)) rather than introducing a
track of its own. When a Loyalty changes mid-chronicle and makes an existing pairing
irreconcilable, **Tension breaks immediately** — a departure, a betrayal, a refusal at the worst
moment — which is what the existing track already does at 6.

The name is **Loyalty** because everything better was taken: *Allegiance* is organisational standing
a character accumulates ([`03-rules.md`](../03-rules.md) §6), *faction* is an entity type
([`14-entities.md`](../14-entities.md)), *Bond* and *Drive* are companion and character mechanics
already. *Alignment* is a published system's term and fails the naming rule in
[`CLAUDE.md`](../../CLAUDE.md) on sight.

## Consequences

**Three relations cost a setting almost nothing to declare.** Only non-default pairs are written
down, so a setting with one dividing line writes one line, and a setting with none writes nothing and
never thinks about it again.

**The middle case is the one that makes it playable.** A pious knight and a thief is a *party* — a
tense one. A boolean would force it into being either forbidden, which makes most settings
unrunnable, or unremarkable, which discards the friction that was the point of noticing.

**`strained` gets its outcome for free.** Tension already becomes visible at 3 and breaks at 6 with a
departure or betrayal. A strained party is not a special case; it is a party on a shorter fuse, and
the fuse already exists and already resets.

**No moral register enters the engine.** The engine never says which Loyalty is the good one, and
cannot — it has no vocabulary for them at all, exactly as it has none for skills. A setting where the
division is religious, one where it is biological and one where it is political all use the same
mechanism ([ADR 0004](0004-tone-belongs-to-the-setting.md)).

**The player's character is not exempt.** A player whose Loyalty changes may find the party they
spent years building will no longer ride with them. That is a real consequence and the chronicle
records it rather than softening it.

**The engine now refuses something.** Irreconcilable is the first party rule that makes the engine
say no to the GM. That is deliberate: the alternative is a rule the GM is asked to remember, and
[ADR 0002](0002-source-material.md) is explicit that rules relying on the GM to remember them get
forgotten inconsistently, which is worse than not having them.

## Alternatives rejected

**A boolean: compatible or not.** The obvious shape and it has no room for the case most settings
actually contain. Every tense-but-possible pairing has to be flattened into forbidden or
unremarkable, and both readings lose something the setting was trying to say.

**A full N×N compatibility matrix.** Complete, and it costs a setting a declaration for every pair,
nearly all of them saying "nothing". Declaring only the non-default pairs is the same expressiveness
at the size of the interesting part, and a matrix that is 90% default is a table nobody keeps current
— the staleness `CLAUDE.md` warns about, in its most predictable form.

**A numeric distance on a single axis**, with incompatibility past a threshold. Elegant for a world
with one spectrum and wrong for one with three unrelated divisions, which is the commoner case. It
also asks a setting author to invent coordinates, which is a worse authoring task than naming a pair.

**Forbid nothing; let strained cover everything.** Attractive, because it never blocks the GM. It
fails the case the mechanism exists for: some pairings are not tense, they are impossible, and a
witch hunter travelling with what they hunt at double Tension is still travelling with what they hunt.

**A separate track for Loyalty friction.** Would let strained pairings escalate on their own clock.
Rejected as a second thing measuring what Party Tension already measures — and two tracks of one
quantity is the drift class this repository is corrected for most often.
