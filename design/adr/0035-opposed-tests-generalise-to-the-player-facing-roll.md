# ADR 0035 — Opposed tests generalise to the player-facing roll; ADR 0016 is retired

**Date:** 2026-08-26
**Status:** Accepted
**Supersedes:** [ADR 0016](0016-opposed-tests-need-a-successful-actor.md), in full

## Context

[ADR 0027](0027-combat-rolls-belong-to-the-player.md) converted combat — and only combat — to a
single player-facing roll against `effective%`, leaving the door open rather than closing it:
"outside combat, two-sided opposed tests still exist, and ADR 0016 still governs them." That was a
scope decision, not an argument that they should — the structural problem ADR 0027 fixed (a double
gate wastes 61-84% of a player's rolls) is not unique to combat. Any two-sided opposed test where
one side is an NPC/opponent has the same shape — the acting side must succeed, then beat the
resisting side's degrees — and the same waste.

`check_opposed_generalisation.py` grepped `design/` for every citation of "opposed test" as a
mechanism, excluding ADR 0016's own historical definition and every other accepted ADR's
historical text quoting or reasoning about it (accepted ADRs are never edited, and a citation
inside one is not a live use to rewrite). Exactly one live file remained:
[`03-rules.md`](../03-rules.md) §1, which both defines the two-sided shape and states its own
carve-out for the case neither side is acting. No other document depends on the two-sided shape as
a mechanism.

## Decision

**Wherever a player character or companion is opposed by an NPC/opponent, the test resolves as a
single player roll against `effective% = clip(50 + (skill − opponent_skill_or_baseline), 5, 95)`,
exactly as combat already does. The opponent's dice are never consulted.**

1. **The roll.** The acting player character or companion rolls once against `effective%`. On
   success, degrees are read `tens(effective%) − tens(roll)` — unchanged from `03-rules.md` §1's
   existing formula, fed the same input combat already feeds it.
2. **A failure simply fails the action.** No resisting-side roll, no degrees comparison — the
   same shape ADR 0027 already established for an attack or a defence.
3. **The Wyrd die is always read from the player's own roll**, because there is no roll on the
   opponent's side for it to belong to instead.
4. **Assistance, declaration and the untrained-10% rule compose with the generalised roll exactly
   as they already do with combat's attack/defence rolls** — `check_opposed_generalisation.py`
   confirmed no new or divergent interaction is needed.
5. **A contest between two player-controlled entities keeps the existing carve-out**, restated
   explicitly rather than left implicit: where neither side is an NPC/opponent — a PC and a
   companion arm-wrestling, a dice-off between two companions — there is no opponent skill to set
   `effective%` against, and the GM either names an actor and calls one ordinary test, or treats
   it as two ordinary tests. This is the same rule `03-rules.md` §1 already stated for "where
   neither is acting"; it is retained here because a genuine PC-vs-companion contest has an actor
   but still no NPC/opponent side, and no design rationale distinguishes the two cases.

**ADR 0016 is retired in full, not further narrowed.** `check_opposed_generalisation.py`'s grep
found no remaining live use of the two-sided roll-both shape anywhere in `design/` outside ADR
0016's own historical text and other ADRs' historical references to it. ADR 0027 had already
carved combat out; this record carves out everything ADR 0027 left open, and nothing was left for
ADR 0016 to still govern.

## Consequences

**The engine-wide goal #77 named — the whole system leans toward player rolls only — is now true
for every opposed test, not only combat.** Any place a player character or companion is opposed by
an NPC/opponent resolves as one roll; the double-gate waste ADR 0027 removed from combat is removed
everywhere else it existed.

**`03-rules.md` §1's "Opposed tests" subsection is rewritten in place**, stating the player-facing
shape directly (generalised from §2's wording rather than duplicating it) and the
two-player-controlled-entities carve-out as its own explicit rule. §2's combat text is unchanged in
substance — its cross-reference to §1 as a different shape no longer applies, since §1 now states
the same shape §2 already does.

**ADR 0016's five provisions describe a shape the engine no longer has anywhere.** They remain
accurate as a historical record of the resolution mechanic that preceded ADR 0027 and this record,
and the accepted-ADR-is-never-edited rule keeps them intact for that purpose.

**Nothing about combat itself changes.** ADR 0027 and ADR 0028's findings — the telling-blow
threshold, the damage-multiplier consequence, starting Stamina — are untouched; this record only
extends where the shape ADR 0027 established applies.

## Alternatives rejected

**Narrow the ADR 0016 scope again instead of retiring it**, the way ADR 0027 narrowed it from
"everything" to "outside combat." Rejected because `check_opposed_generalisation.py`'s grep found
no live use of the two-sided shape left to narrow it *to* — a narrowing record implies a remaining
scope, and stating one that does not exist would be the kind of stale-but-plausible specification
CLAUDE.md names as a recurring fault.

**Give the two-player-controlled-entities case a new mechanic** (e.g. a straight opposed roll
between the two entities' skills, reintroducing a form of the two-sided shape for this one case).
Rejected: `03-rules.md` §1 already anticipated a contest with no clear opposing NPC ("where neither
is acting") and answered it with the GM naming an actor or calling two ordinary tests; nothing
about a PC-vs-companion contest specifically needs a different answer, and a second resolution
shape for a case this rare would be complexity without a use case that has come up in play.
