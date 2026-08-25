# ADR 0025 — An adversary is a thin block, and a named antagonist wears one

**Date:** 2026-08-25
**Status:** Accepted

## Context

**Nothing in `design/` said how an opponent was represented.** Adversary, opponent and statblock
returned no matches across every design document.

Two documents gestured at it and neither delivered. [`13-authoring-a-setting.md`](../13-authoring-a-setting.md)
listed `setting/bestiary.yaml` in the setting layout with the parenthetical "creature stat blocks (a
lookup table)" — no schema, no field list, no example. [`14-entities.md`](../14-entities.md) listed
`creature` as an entity type and described it as "a stat block — a kind of thing, not an
individual", which says what a creature is *not*.

Meanwhile the ruleset had been reading fields off an opponent for four stages: a skill to resist
with, an armour rank, current and maximum Stamina, a damage type, and whether it could shoot. The
sharpest case is the crowd rule ([ADR 0019](0019-a-crowd-is-defined-by-one-blow-and-a-skill-gap.md)),
which states itself as *"a lookup, and nothing else"* over three fields — maximum Stamina, armour,
and the opponent's relevant skill — **none of which was defined anywhere as belonging to anything.**
A rule whose entire claim to determinism is that it reads values rather than judging them was
reading values off a record with no schema.

So a setting author had no contract to fill, and the GM invented an opponent's numbers at the table.
That is precisely the judgement call the rules do not cover.

The decision had two real alternatives, and the second is the one that nearly won.

## Decision

**An adversary carries a deliberately thin block**: a stable id, a name, a **baseline** percentage,
maximum Stamina, an armour rank, and skills — plus, optionally, what its blows are, whether it can
shoot, and traits from a closed vocabulary. Six required fields. Nothing else.

**The test for membership is that a published rule reads it.** A field no rule reads does not enter
the block, and an unrecognised field in a bestiary is an error rather than a curiosity.

**A named antagonist is not a second model.** A nemesis, a rival, a hostile companion — anyone the
chronicle follows — is a `character` entity that *also* carries this block. The person layer already
exists in [`04-session.md`](../04-session.md); the fighting layer is this. One description of an
opponent, reached two ways.

**An opponent tests any skill its block does not list at its baseline**, which is why the baseline
is required rather than optional.

The block is in [`03d-the-adversary.md`](../03d-the-adversary.md), the schema and validator in
[`13-authoring-a-setting.md`](../13-authoring-a-setting.md) and `tools/check_bestiary.py`.

## Why not the full character model

**Adversaries as characters** is what most percentile systems do, and it is not a straw man: it
means one schema instead of two, a nemesis needs no special case, and any rule that works on a
character works on an opponent for free.

It was rejected because **every track a character carries accrues, and a thing met once has nowhere
to accrue to.** Taint transforms you at thresholds; Trauma breaks into Afflictions; Strain recovers
at a Rally; Resolve is spent against Taint; a career caps skills and an advancement economy raises
them. All of that models a person the chronicle follows for years. Giving it to the thing killed in
a corridor means running an advancement economy for a wolf, and — worse — it means the GM answering
questions the fiction never asked: what is this creature's Loyalty, what career granted it that
skill, how much Resolve has it spent.

The one thing the full model buys that the thin one does not is the nemesis, and the thin model buys
that back by composition instead: a nemesis is a character *and* a block, which is strictly more
expressive than a creature pretending to be a character.

## Why not the untrained 10% as the fallback

The obvious economy is to carry no baseline and let an opponent test an unlisted skill at the
untrained 10% ([`03-rules.md`](../03-rules.md) §1), exactly as a character does. One fewer required
field, and no new rule at all.

It was rejected on two grounds, the second decisive:

**The untrained rule is about people.** It exists because a person who never learned a thing has
nothing to fall back on — the engine has no characteristics to derive a base from
([ADR 0013](0013-the-engine-names-no-skill.md)), so it names 10. A thing that hunts is not untrained
at noticing; it is simply not written down as noticing, and those are different claims.

**It would unmake the crowd rule from underneath.** The clearing test is *ahead by 20 or more*.
Against a 10 fallback, any character with a merely competent skill clears almost any opponent for
free at anything off its short list — and a bounded exception, computed and argued for in ADR 0019,
silently becomes the ordinary way fights resolve. A baseline that can sit above 30 keeps that test
doing the work it was given.

## Why the trait vocabulary is closed

Traits could have been free text the GM interprets. That is the most expressive option and the one a
setting author would ask for.

It is also **the one option under which a setting can add a mechanism**, which
[`13-authoring-a-setting.md`](../13-authoring-a-setting.md) forbids outright: a setting may extend,
retune, rename or disable, and never add. A trait reading "regenerates 2 Stamina each round" is not
a retune — it is a new mechanism, arriving in a lookup table where nobody reviews it. And it is
inference where a rule could be deterministic
([ADR 0005](0005-deterministic-over-inference.md)).

The alternative at the other end — **no traits at all**, an opponent is only its numbers — is
leaner and needs no policing. It was rejected because it makes every monster a man with different
numbers, and a setting will route around that by writing the trait into the `notes:` field where
nothing checks it.

So: a trait is a display name and an effect drawn from a closed list, every entry of which acts on a
mechanism that already exists — difficulty, damage, damage type, Stamina, armour rank, the Wyrd die.
The list grows by an engine change, which is the correct cost. A mechanism added deliberately, once,
is a different thing from one that arrived in a stat block and was never noticed.

## Consequences

- A setting author has a contract, and `tools/check_bestiary.py` fails when it is not met.
- The crowd rule's three-field lookup resolves against a schema, so it is a lookup in fact and not
  only in wording.
- `bestiary.yaml` holds kinds of thing. Individuals live in `entities/character/`, carrying a block.
- Adding a field to the block is an engine change, gated on a published rule reading it.
- The engine still holds no capability score for a **companion**
  ([ADR 0024](0024-a-party-is-worth-less-than-its-head-count.md)), and this record does not
  introduce one. A companion is a person the party carries; an adversary is a thing it fights. That
  they could share a schema is not a reason to give companions numbers the scaling rule has
  deliberately declined to read.
