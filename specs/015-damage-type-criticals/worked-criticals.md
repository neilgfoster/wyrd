# A fight, played through the critical tables

`CLAUDE.md`: prefer playing a rule over arguing about it. The one playtest this engine has had
corrected the resolution mechanic three times inside two rolls, none of it visible on paper. So
before the tables were settled, this fight was played — dice rolled in order, nothing re-rolled,
nothing chosen after the fact. The roll log is at the bottom and every number below comes from it.

## The combatants

| | Skill | Weapon | Damage type | Armour | Stamina | Fate |
|---|---|---|---|---|---|---|
| **The character** | 45% | spear `1d8` | piercing | modest `1d6` | 6 | 2 |
| **The companion** | 35% | club `1d6` | blunt | light `1d3` | 6 | none |
| **Three at the ford** | 35% | axe `1d6` / knife `1d3` / torch `1d3` | slashing / piercing / searing | none | 3 each | none |
| **The mailed man** | 55% | greatsword `2d6` | slashing | heavy `2d6` | 8 | none |

The three at the ford are not a crowd: Stamina 3 clears the first test of the crowd rule
(`doc/design/03-rules.md`), so every one of them is fought a roll at a time.

## Round 1 — the ambush

They started the exchange, so they take the whole first round.

**The axe** swings at the character: **51** against 35. It fails; the character is not troubled.

**The knife** goes for the companion: **17**, a success at two degrees. The companion rolls **64**
and fails, so there is nothing to compare. `1d3` = **3**, light armour `1d3` = **3**, and the
minimum of 1 gets through regardless. The companion is at **5**.

**The torch** is swung at the character: **64**. It fails.

## Round 2 — the party answers

**The character** spears the axeman: **29**, two degrees. He rolls **85** and fails. `1d8` = **5**
against no armour. He is at 3, so this takes him to **−2**: two points below zero, and a critical.

> `critical-piercing`, `1d6` = **1**, `+2` → **3** → `piercing-grazed`. Nothing lasting.

He is out of action for the rest of the fight and will roll Aftermath when it ends. The critical
cost him 1 Trauma, by `doc/design/03-rules.md` §5 — the table charged him nothing.

**The companion** clubs the knifeman: **13**, two degrees. He rolls **76** and fails. `1d6` = **5**
takes him from 3 to **−2**.

> `critical-blunt`, `1d6` = **4**, `+2` → **6** → `blunt-winded`. Nothing lasting.

Two criticals, two opening rows, nothing carried away. That is the shape the tables are meant to
have: at the modifiers a light drop produces, most criticals are the fight being lost rather than
the body being ruined.

## Rounds 3–9 — the torchbearer

Seven rounds in which almost nothing lands: **61**, **98**, **82**, **85**, **58**, **91**, **86**.
Two exchanges are worth keeping.

**The tie.** The character attacks on **45** — a success at exactly zero degrees. The torchbearer
resists on **31**, also zero degrees. Ties go to the resisting side, so the attack simply fails.

**The floor.** The torchbearer lands on **30** against the character's failed **77**. `1d3` = **1**
against modest armour `1d6` = **6**, and the minimum of 1 still gets through. The character is at
**5**. Armour never makes a blow into nothing.

## Round 10 — the mailed man

He comes up the bank while the torchbearer is still swinging, and goes at the companion.

**15**, a success at four degrees. The companion resists on **45** — a success, but at zero. The
margin is four, so it is a **telling blow** and the damage doubles: `2d6` = **9**, doubled to
**18**, less light armour `1d3` = **2**. Sixteen points reach a companion standing at 5.

> Eleven points below zero. `critical-slashing`, `1d6` = **4**, `+11` → **15** →
> `slashing-hamstrung`. A wound record, effect `skill: -10`.

The companion is down, out of action, and carrying something that will not be gone next week. One
Trauma, once.

**What a mortal blow would have looked like.** It did not happen here, and that is worth saying
plainly rather than staging: `slashing-mortal` begins at 21, which needs fifteen points below zero
*and* a six on the die — 1.8% of slashing criticals, computed. Had the roll been
one, the composition is this and no more: the companion would still have been out of action, not
dead, until the fight ended; the Aftermath roll would then have been read on `death`; and the
character — present and able to act — could have spent their own Fate to re-read it onto the
recurring wound. Exactly what happened below, by a different road.

## Rounds 11–14 — the character alone

**52**, **78**, then **17**: a success at three degrees against his failed **82**. Three degrees is
a telling blow. `1d8` = **5**, doubled to **10**, less heavy armour `2d6` = **7**. Three points
through — he is at 5 of 8 and unbothered. He takes the ford, takes the fallen, and withdraws with
the character still standing over the companion.

## Aftermath

Rolled once for everyone who dropped, `d100 + 5 ×` points below zero.

| | Below zero | Roll | Total | Row |
|---|---|---|---|---|
| The axeman | 2 | 78 | 88 | `taken` — he wakes held |
| The knifeman | 2 | 17 | 27 | `out-of-action` — nothing lasting |
| **The companion** | 11 | 82 | **137** | `death` |

The companion's roll is a death. The character is present, able to act, and spends **one of their
two Fate points**, which re-reads it onto the worst non-death row: `recurring-wound`. The companion
lives, and carries a wound that wakes before every fight for the rest of the chronicle — on top of
the hamstringing the critical already wrote.

That pairing is the whole argument for keeping the two tables separate. The critical said what the
sword did. Aftermath said what it cost. Neither could have said both.

## What the play found

1. **The two opening rows carry the fight.** Three of the four criticals rolled landed in the first
   two rows of their table. A critical is ordinary; the tables have to be readable at the top far
   more often than at the bottom, and the ranges were widened there before being settled.
2. **The telling blow is where the modifier comes from.** Every large modifier in this fight came
   from a doubled blow, not from a big weapon. Which means the reading — *the damage rolled doubles,
   and then armour subtracts* — is load-bearing for the whole modifier distribution, and
   `doc/design/03-rules.md` had not said it in so many words. It says it now.
3. **The worst row is genuinely rare, and staging it would have been a lie.** No mortal blow
   occurred in fourteen rounds. The document says how rare rather than implying it never happens.
4. **Opponents roll Aftermath too**, and its rows answer for them without a special case: the
   axeman was `taken` rather than killed, which is a scene the GM did not have to invent.
5. **One question this fight raised belongs to another issue.** When the acting side succeeds and
   the resisting side *fails*, `doc/design/03-rules.md` does not say what the margin is — and the
   telling blow reads the margin. It was played here as the acting side's own degrees, which is the
   only reading consistent with ADR 0016. It is noted rather than settled, because opposed tests are
   not this issue's to change.

## The roll log

Seeded, in order, nothing discarded. Reproduce with `random.seed(1517)` and
`random.randint` in the order `d100, d6, d3, 2d6, d8` per line.

```
 0  d100 51  d6 4  d3 1  2d6 5  d8 1      8  d100 61  d6 3  d3 3  2d6 8  d8 5
 1  d100 17  d6 6  d3 3  2d6 5  d8 4      9  d100 98  d6 6  d3 2  2d6 9  d8 2
 2  d100 64  d6 6  d3 3  2d6 7  d8 2     10  d100 82  d6 4  d3 2  2d6 6  d8 4
 3  d100 29  d6 4  d3 2  2d6 2  d8 4     11  d100 85  d6 5  d3 1  2d6 6  d8 4
 4  d100 85  d6 1  d3 3  2d6 6  d8 5     12  d100 58  d6 3  d3 3  2d6 4  d8 7
 5  d100 13  d6 1  d3 3  2d6 9  d8 1     13  d100 91  d6 2  d3 1  2d6 10 d8 1
 6  d100 76  d6 5  d3 2  2d6 2  d8 5     14  d100 86  d6 3  d3 2  2d6 10 d8 2
 7  d100 94  d6 4  d3 2  2d6 9  d8 6     15  d100 34  d6 6  d3 2  2d6 7  d8 1
16  d100 99  d6 5  d3 3  2d6 6  d8 1     25  d100 15  d6 4  d3 2  2d6 9  d8 1
17  d100 80  d6 4  d3 2  2d6 5  d8 8     26  d100 45  d6 4  d3 2  2d6 9  d8 8
18  d100 45  d6 3  d3 3  2d6 8  d8 7     27  d100 49  d6 4  d3 1  2d6 10 d8 1
19  d100 31  d6 4  d3 1  2d6 8  d8 1     36  d100 52  d6 2  d3 1  2d6 8  d8 1
20  d100 30  d6 2  d3 3  2d6 9  d8 5     37  d100 78  d6 6  d3 1  2d6 2  d8 4
21  d100 77  d6 6  d3 1  2d6 4  d8 1     38  d100 17  d6 6  d3 1  2d6 4  d8 5
22  d100 63  d6 6  d3 1  2d6 10 d8 3     39  d100 82  d6 4  d3 3  2d6 7  d8 5
```
