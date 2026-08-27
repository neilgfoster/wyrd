# A worked exchange against a written opponent

Every figure here is produced by [`check_adversary.py`](check_adversary.py), which fails on
disagreement. Nothing below is asserted.

This document exists to answer one question the schema cannot answer by itself: **is the block
sufficient?** A field list is only right if a whole fight can be run off it without the GM
inventing anything, and this is the only place every rule that reads an opponent appears together.

---

## The opponent, as written

```yaml
- id: the-hunter
  name: A named antagonist
  baseline: 35
  stamina_max: 7
  armour: modest
  skills:
    blade: 55
    tracking: 60
  damage: 1d6
  damage_type: slashing
  ranged: false
  traits:
    - name: Unhurried
      effect:
        difficulty: -10
```

Ten fields, six of them required. Every one is read by a published rule, and the table in
[`docs/design/12-the-adversary.md`](../../docs/design/12-the-adversary.md) names which.

---

## What the fight consumed

A starting character, Stamina 6, modest armour, an ordinary weapon. Both resolution models are
computed — the opposed test as it stands, and the player-facing mapping #69 will adopt — because
the block has to survive the conversion.

| model | character | p(character drops) | p(opponent drops) | rounds |
|---|---|---|---|---|
| opposed | 25% | 97.9% | 2.1% | 9.58 |
| opposed | 35% | 92.7% | 7.3% | 10.06 |
| opposed | 45% | 80.8% | 19.2% | 10.47 |
| opposed | 55% | 60.4% | 39.6% | 10.55 |
| mapped | 25% | 96.9% | 3.1% | 6.04 |
| mapped | 35% | 89.5% | 10.5% | 6.64 |
| mapped | 45% | 75.8% | 24.2% | 7.15 |
| mapped | 55% | 56.9% | 43.1% | 7.45 |

A named antagonist at 55% and Stamina 7 beats a practised character more often than not, and beats
a newly trained one almost always. That is the correct shape for a nemesis and it is a computed
property of the block, not a claim about how frightening the thing is meant to be.

**Every field the exchange consumed came off the block**: the skill it resisted with, the armour
that subtracted dice, the Stamina it had to lose, and the dice its own blows roll. The one thing the
GM chose was the difficulty of the shot, which is what the difficulty ladder is for.

The `damage` field earns its place by changing the answer. The same opponent, same skill, same
armour, swinging `2d6` instead of `1d6`, drops a 45% character **92.7%** of the time rather than
**75.8%**.

### The critical, and what is not rolled

When the character wins, damage takes the opponent below 0 and the critical rule applies: `1d6 +
points below zero`, on the table for **the block's own damage type**. Against this opponent the
totals run **2 to 11**, mean **5.12**, and the whole distribution's mass equals the chance the
opponent dropped at all.

The lowest reachable total is 2, which is exactly where the critical tables' first row starts
([`03a-1-criticals.md`](../../docs/design/05-criticals.md)) — a blow that drops someone is at least one
point below zero, and the die adds at least one more. The table has no row for 1 because no roll can
produce one.

**The Aftermath table is not rolled here.** It is rolled once per *character or companion* who
dropped ([`03-rules.md`](../../docs/design/03-rules.md) §2), and an adversary is neither — the same rule
§2 already states for a crowd. A named antagonist is a `character` entity and so does roll, but not
because it is important: because it is a character, which is the test the rule already applies.

---

## The crowd lookup, against the same schema

[ADR 0019](../../docs/adr/0019-a-crowd-is-defined-by-one-blow-and-a-skill-gap.md) calls itself
"a lookup, and nothing else". Here it is, resolving entirely from declared fields:

| opponent | character | skill tested | result | deciding field |
|---|---|---|---|---|
| `mob-body` | 45% | brawl | **crowd** | stamina_max 1, no armour, gap 25 |
| `mob-body` | 45% | guile | **crowd** | stamina_max 1, no armour, gap 35 |
| `the-hunter` | 45% | blade | rolled | `stamina_max 7 > 1` |
| `the-hunter` | 75% | blade | rolled | `stamina_max 7 > 1` |
| `mob-body` | 35% | brawl | rolled | `skill gap 15 < 20` |
| `mob-body` | 40% | brawl | **crowd** | gap exactly 20 |

Three things fall out, and none of them is a judgement:

1. **The nemesis fails on the first test**, `stamina_max`, before skill is consulted at all. Even a
   75% character does not sweep it aside. The rule never becomes an opinion about what an opponent
   is worth.
2. **The gap boundary is exact.** 40% clears a 20% body; 35% does not.
3. **Row two is the one the baseline earns its place on.** Asked for a skill the block does not
   list, the body tests at its baseline of 10 — not at a value the GM invents on the spot, and not
   at an absent field. Without the baseline this row has no answer.

---

## Danger reaching the opponent

One written encounter — **6 opponents at 45%, `danger: 3`, `written_for: 4`** — prepared for each
party a chronicle actually has. Both quantities `03-rules.md` §7 scales are shown together, which
is the only way to see that they move in the same direction:

| party | ratio | `danger_effective` | opponents | their skill |
|---|---|---|---|---|
| 1 | 0.48 | 1.44 | 3 | 30% |
| 2 | 0.72 | 2.16 | 4 | 40% |
| 3 | 0.88 | 2.64 | 5 | 40% |
| **4** | **1.00** | **3.00** | **6** | **45%** |
| 5 | 1.10 | 3.29 | 7 | 45% |

**The identity row is exact on both quantities.** Four bodies meet six opponents at 45%, which is
the encounter as written. That is what makes §7 a ratio rather than a discount, and it now holds on
the skill half as well as the count half.

A lone character meets three opponents at 30% rather than six at 45% — fewer, and each fifteen
points easier. Neither alone would have been enough: six 30% opponents is still six fights, and
three 45% opponents is still three fights a solo character loses.

---

## What the exchange changed about the block

The worked fight is allowed to expose a missing field, and it exposed one. **`ranged` had been
optional** in the first draft of the block, on the grounds that most opponents are not archers. But
[`03-rules.md`](../../docs/design/03-rules.md) §2's engagement rule branches on it every time an opponent
is not in close engagement — *closing costs the closing combatant their action* only matters if the
answer to "can it shoot instead?" is known. An absent `ranged` is a question the GM has to answer,
which is the fault the block exists to remove. It stays optional in the schema, but it **defaults to
false and the default is published**, so the question always has an answer.

The floor on an adjusted skill was found the same way, by computation rather than by reading: an
opponent already at the untrained 10, in content written for six, met by a lone character, takes the
full −20 and lands at −10. A percentage is not a negative number. It floors at 0, and §1 already
says what a test at or below zero is — it is not attempted. No new rule was needed, but without
running the numbers the design would have published a negative percentage and nothing about it would
have looked wrong.
