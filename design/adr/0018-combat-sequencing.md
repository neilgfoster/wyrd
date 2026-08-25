# ADR 0018 — Turn order is read off the fiction; space is one bit; surprise costs a whole round

**Date:** 2026-08-25
**Status:** Accepted

## Context

Combat existed in outline and could not be run. `03-rules.md` §2 specified what an attack *is* — an
opposed test, armour subtracting dice, a telling blow, a critical below zero Stamina — and nothing
about when anyone does it. **The word *initiative* appeared in no design document.** There was no
round, no turn order, no ranged combat, no fleeing, no surprise.

That is not a neutral silence. [`07-tooling.md`](../07-tooling.md) and
[ADR 0005](0005-deterministic-over-inference.md) hold that anything with a correct answer is
computed rather than inferred, and every question the rules decline to answer becomes a judgement
call made differently each session. An unsequenced exchange is a rule delegated to improvisation.

Four questions, each with a failure mode that does not show up in prose.

**What decides who acts first?** The obvious answer is an initiative roll. The engine cannot make
one: [ADR 0013](0013-the-engine-names-no-skill.md) means there are no characteristics and no named
skill, so an initiative roll has nothing to roll against without inventing an attribute for the
purpose — a parallel mechanic introduced to solve a sequencing problem.

**How much space does the engine carry?** Text play has no map. Anything imported from a tactical
game — a grid, movement rates, ranges in metres — cannot be run here, because nothing in a chronicle
records the facts it needs. But with *no* spatial state at all, an archer never has a reason to stop
shooting.

**What does surprise do?** The range runs from a small modifier to a free round, and the difference
is the difference between an ambush being worth setting and not.

**How does anyone leave?** A fight nobody can be trapped in has no stakes; a fight nobody can leave
punishes the correct response to a fight going badly.

## Decision

**Whoever started the exchange acts first.** No roll, no attribute, no ordering step before play
begins. Within a side, order is the fiction's and carries no mechanical weight. Where neither side
started it, the side already holding a weapon goes first; if both are armed or neither is, the
player's side does.

**A turn is one action.** Attack, close, break off, ready or use, or act on the fiction.

**Space is one bit: in close engagement, or not.** Closing costs the closing combatant their action.
Being closed with is not refusable except by breaking off. Ranged difficulty is read off the
existing ladder from cover, light and engagement — never from a distance, because there is not one.

**Breaking engagement always works and always costs a parting blow**; getting away from the scene is
a group test in the *everyone must get through* shape, at a difficulty the pursuit sets.

**A surprised side does not act in the first round at all, and still defends.** Ambush — prepared
surprise — eases the first round's attacks by +20 and nothing after.

## Why

**Turn order read off the fiction costs nothing and is never ambiguous.** It also makes surprise the
*same* rule at its limit rather than a second system beside it: the exchange began, and one side did
not know. That is a smaller engine than one with an initiative rule plus a surprise rule, and it is
smaller in the way that matters — one idea instead of two.

**One bit is the least the engine can carry and still hold ranged and close combat in tension.** The
whole balance rests on a single exchange rate: a fighter spends a turn to arrive, an archer spends a
parting blow to get clear. Neither free, neither impossible.

**Surprise is worth a whole round because the computation says it can afford to be.** Across
realistic pairings a free round moves the surprising side's odds by **4 to 8 points** and never past
**83%** ([`check_sequencing.py`](../../specs/012-combat-sequencing/check_sequencing.py)). It is
decisive without being deciding — the fight still happens. Intuition puts a free round far higher
than that, and the reason it is lower is that fights run 5 to 14 rounds at real skills, so one round
is a smaller share of the fight than it feels like. This is the third combat probability in this
repository that intuition had wrong; it is the first that was checked before it shipped.

**+20 for an ambush is a rung of the existing ladder, not a new number.** It is also the ceiling of
the declaration bonus in §1, which fixes its meaning: preparing an ambush is worth exactly as much
as declaring an action perfectly, and no more.

## Alternatives rejected

**An initiative roll, from a new attribute.** The standard answer, and it requires inventing the
characteristic the engine deliberately does not have (ADR 0013), then rolling it every fight. It
would buy variable order — genuinely interesting — at the cost of an attribute that exists for one
subsystem and a roll before anything happens.

**Named range bands** (close / near / distant) with rules for moving between them. Rejected as
positioning in English clothes. Bands are the thing a grid becomes when you file the numbers off,
and a chronicle cannot record which band anyone is in any more than it can record coordinates.

**No spatial state at all**, ranged combat being a pure difficulty call from the fiction. Simplest
of all, and it leaves exactly the judgement call this record exists to remove: nothing would stop an
archer shooting forever.

**Free disengagement.** Cleanest to run, and it removes the stakes — nothing could ever be trapped,
so no fight could ever go badly enough to matter.

**Surprise as a modifier rather than a lost round.** Softer and less swingy, and it makes preparing
an ambush not worth the preparation. The computation showed the harsher rule is affordable, so the
softer one buys nothing.

**Two actions a turn.** More tactical texture, and the prose budget will not carry it. Sessions
happen on a phone; a round has to fit in a few lines.

## Consequences

The mutual-encounter fallback — the player's side acting first — is **decided from outside the
fiction**, and it is the only rule in §2 that is. It is small, it resolves a real ambiguity, and
naming it here is better than leaving it to be found and argued about later.

Nothing in §2 now depends on the opponent rolling except the group test to get away, which is stated
as a difficulty. That is deliberate: the direction set on #44 converts combat to player-facing rolls,
and none of this obstructs it.

The mob rule ([#13](https://github.com/neilgfoster/wyrd/issues/13)) now has the turn order it was
always written against — *each round a character also clears petty opponents* means something once a
round exists.

Playing an exchange by hand found three rules that were not there and were needed within five rounds
([`worked-exchange.md`](../../specs/012-combat-sequencing/worked-exchange.md)): that a surprised
combatant still defends, that shooting into someone else's fight needs a difficulty and a
consequence for an Ill Omen, and that flight needs a stated difficulty ladder rather than a GM's
guess. None was visible while the rules were being written.
