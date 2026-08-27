# ADR 0019 — A crowd is defined by one blow and a skill gap, and it answers once

**Date:** 2026-08-25
**Status:** Accepted

## Context

The mob rule was one sentence:

> Each round a character also clears petty opponents weaker than themselves, so one character plus
> companions can face a crowd without a roll per body.

It carried no numbers. It defined neither *petty* nor *weaker* — the two words the whole rule turns
on — and it said nothing about what the crowd does back. Whether the rule applied to a given group
was therefore a judgement call made fresh each session, which is precisely what
[`27-tooling.md`](../design/27-tooling.md) and [ADR 0005](0005-deterministic-over-inference.md) exist to
remove.

It also could not be written until [ADR 0018](0018-combat-sequencing.md) landed. *Each round* means
nothing without a round; *clears* means nothing without a turn to clear on.

Three questions had to be answered with numbers, and each had a failure mode invisible in prose.

**Which opponents qualify?** Too generous and the rule deletes fights the engine meant to be
fights. Too narrow and it never fires, and a crowd is sixty `d100` rolls.

**How many are cleared?** The rule buys out a roll per body, so it is generous by construction. The
question is by how much, and whether the shortcut ever beats taking a real action.

**What does the crowd do back?** A crowd that cannot hurt anyone is scenery, and a rule that makes
crowds safe makes the numbers on the other side meaningless.

## Decision

**A character or companion in close engagement with a crowd clears one crowd member at the start of
their turn, without a roll and without spending their action.** A cleared body is out of action and
does not act that round.

**A crowd member is a lookup on three numbers**, all read from sheets that already exist: maximum
Stamina **1**, **no** armour, and the character's relevant skill ahead of theirs by **20 or more**.
No judgement is exercised at any point.

**A crowd engaged with a character attacks once per round, not once per body**, eased by **+10 per
body on that target beyond the first**, to a ceiling of **+20**. Its parting blow against a
departing combatant is one attack on the same terms.

**The word *petty* is not kept.** Neither is *weaker*. Both are replaced by the numbers above, and
the mechanic is called the **crowd** rule.

## Why

**The Stamina-1, no-armour line is where one blow stops being enough**, and it was found by
computing rather than chosen ([`check_mobs.py`](../../specs/013-the-mob-rule/check_mobs.py)). Across
the whole plausible span of weapon damage, one ordinary hit takes such a body below zero **67% to
100%** of the time. The same body in the *lightest* armour falls to **11%** on the worst weapon in
the band, and a body of Stamina 2 to **33%**. The rule therefore removes only opponents the dice
would have removed anyway, which is the only honest basis for skipping the dice.

The first draft of this record set the line at Stamina 3 in light armour. The script rejected it: a
body like that is dropped by a mid-band weapon **16.7%** of the time, so the free clear would have
been inventing removals, not compressing them. That is the fourth combat probability in this
repository that intuition had wrong.

**The 20-point gap is anchored to numbers already merged**, not picked. Untrained is a flat 10% and
a skill opens at 25% and rises by 5 ([`10-the-character.md`](../design/10-the-character.md)), so a gap of
20 puts the rule one advance past a newly opened skill. A gap of 15 would have handed it to a
character on the day they opened the skill, which would make *weaker than themselves* mean *trained
at all*.

**One body a round is the honest rate, and the discount is bounded.** Under the player-facing
mapping recorded for #44 — slope 1, clipped 5–95 — attacking a qualifying body and rolling for it
removes **0.55 to 0.80** bodies a round across real skills. The free clear removes 1: a discount of
**1.25× to 1.82×**, which is what buying out a roll per body costs and no more. Under today's
opposed test the same comparison reads as high as **5.0×**, and that number is reported and
deliberately not designed around: it is an artefact of a test in which a competent character misses
an untrained one two times in three, which is the fault #44 exists to correct.

**Clearing two would beat attacking**, and a character does one thing on their turn
([`03-rules.md`](../design/03-rules.md) §2). One is the largest number that leaves the crowd subordinate to
the fight it is part of.

**The crowd answering once is the same idea applied to the other side.** A rule that spares the
player sixty rolls and then makes the GM roll sixty is not a rule, it is a rebate. Weight of numbers
converts bodies into the existing difficulty ladder instead, and stops at **+20** because that is
the top rung the ladder has — going further would invent one.

**The numbers leave the fight where it should be.** A lone unarmoured character clears six bodies in
6 rounds and is dropped by them in **5.7**: they lose. In modest armour they last **12.9**. A party
of four clears twelve in 3 rounds. So the answers to a crowd are armour and companions, and the rule
is a way not to roll sixty times rather than a way to win alone.

**On *petty*.** [`CLAUDE.md`](../../CLAUDE.md) requires engine labels to be descriptive English
carrying no genre or moral register, and *petty* fails that squarely: it is a judgement about an
opponent's worth, not a description of their capability, and it presumes a register in which
enemies can be beneath contempt. Nothing mechanical was lost by dropping it — the mechanic was never
about worth, it was about a body one blow removes, and the definition now says that. *Weaker* was
harmless but empty; a number replaced it.

## Alternatives rejected

**Keep *petty* and define it.** The cheapest change, and it leaves a moral judgement embedded in a
mechanic where a setting cannot remove it. A setting that wants the word can have it in its
`rename:` block.

**Define a crowd member by their skill alone** — anyone untrained, say. Checkable, and wrong: it
would let a character clear an armoured, healthy opponent for free on the grounds that they are
unskilled, which is a different and much larger rule.

**Scale the clear with degrees or with the skill gap** — one body, plus one per further margin.
More texture, and it reintroduces the arithmetic the rule exists to avoid, on the round where the
player is already tracking a real fight.

**Let the crowd roll per body.** Symmetrical and honest, and it costs the GM exactly what the rule
saves the player. Rejected on the prose budget: sessions happen on a phone.

**No ceiling on weight of numbers.** Twenty bodies would reach certainty against one defender, and
the engine holds that no roll should be certain
([`check_mapping.py`](../../specs/012-combat-sequencing/check_mapping.py)). Capping at the ladder's
top rung keeps numbers meaningful without letting them decide.

## Consequences

**Numbers past three on one target do nothing to that target.** What a large crowd buys is reaching
more of the party at once — a party of four faces a full-strength crowd from twelve bodies on. This
is a real change in how a crowd fight plays: spreading out matters below that size and not above it.

**The Aftermath table is not rolled for a crowd.** Twenty Aftermath rolls is the same fault as
twenty attack rolls. It is rolled once per character and companion, and what became of the crowd is
the fiction's to say.

**This constrains the adversary model** ([#54](https://github.com/neilgfoster/wyrd/issues/54)),
which is not yet decided. An adversary representation must be able to state a maximum Stamina and an
armour rating, or this rule cannot be looked up. It need state nothing else.

**Playing a crowd fight by hand found three rules that were not there**
([`worked-crowd.md`](../../specs/013-the-mob-rule/worked-crowd.md)): that the clear requires close
engagement, or a character clears bodies while shooting from across the yard; that companions clear
too, which the drafted wording left to be argued; and that breaking off from a crowd costs one
parting blow rather than one per body, which had put back exactly the rolls the rule removes. None
was visible while the rule was being written.

**The rule is stated against both resolution models** — today's opposed test and the player-facing
mapping — so the conversion on #44 does not reopen it.
