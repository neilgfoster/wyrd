# One arc, three parties

The same arc record, scaled at three points in one chronicle's life. Every figure below comes from
`check_party.py`; nothing here is reasoned on paper. The point of working it by hand is the
rounding: `danger_effective` is never rounded, so the three quantities this record builds each
round separately, and this is the only place all three appear together.

## The record

```yaml
id: the-drowning-well
danger: 3
written_for: 4
```

What the arc's own text builds from `danger`, written for its stated party of four:

| Written quantity | At `danger: 3`, as the text has it |
|---|---|
| a flooded stair, `(danger / 3)d6` | `1d6` |
| the cult in the undercroft, `2 × danger` bodies | 6 |
| the watch on the road, `danger` bodies | 3 |
| the prior's own skill, `+5 × danger` over his trade | +15 |

The effective size of a party of four is 2.083, and that is the denominator throughout.

---

## Year one: the character alone

One body. `party_effective` is 1.000, the ratio is **0.480**, and `danger_effective` is
**1.440** — the arc as written, run at not quite half strength.

| Quantity | Scaled | Rounded at use |
|---|---|---|
| flooded stair | 0.48 dice | **1d6** |
| the cult | 2.88 bodies | **3** |
| the watch | 1.44 bodies | **1** |
| the prior | +7.2 | **+7** |

Two things to notice, and both are the rounding rule earning its place.

The stair is the floor doing its work. Half a die is not a thing that can be thrown, and rounding
half up would have given 0 — a trap that is not a trap. A quantity the text wrote as at least one
never comes out as none, so a lone character still gets wet and still risks drowning; the arc is
softened, not deleted.

The watch rounds *down*, from 1.44 to 1. This is the first place the lone character's ratio is
visibly cheaper than a share: three watchmen become one, not two. That is correct and it is worth
saying plainly — the arc is a good deal harder for one person than for four, and the scaling is
what makes it playable at all rather than what makes it fair.

---

## Year three: two companions

Three bodies. `party_effective` is 1.833, the ratio is **0.880**, and `danger_effective` is
**2.640**.

| Quantity | Scaled | Rounded at use |
|---|---|---|
| flooded stair | 0.88 dice | **1d6** |
| the cult | 5.28 bodies | **5** |
| the watch | 2.64 bodies | **3** |
| the prior | +13.2 | **+13** |

This is the case `docs/design/26-corpus-index.md` used to answer with "roughly danger 2". It is 2.64,
and the difference is not academic: at 2 the cult is four bodies, at 2.64 it is five, and the
undercroft fight is the whole middle of the arc.

The watch rounds *up* here, 2.64 to 3, while the cult rounds down, 5.28 to 5. Had
`danger_effective` been rounded to an integer up front — to 3, say — the watch would still be 3 but
the cult would be 6, and the arc would run a body harder than the party earned. Rounding once is
cheap and wrong in exactly the place the arc is heaviest. That is the decision vindicated.

---

## Year eight: a retinue of five

Six bodies. `party_effective` is 2.450, the ratio is **1.176**, and `danger_effective` is
**3.528** — above the written danger, because six bodies are more than four.

| Quantity | Scaled | Rounded at use |
|---|---|---|
| flooded stair | 1.18 dice | **1d6** |
| the cult | 7.06 bodies | **7** |
| the watch | 3.53 bodies | **4** |
| the prior | +17.6 | **+18** |

Five companions — a household, not a party — buy 1.176. Four companions bought 1.096, three bought
1.000. The fifth companion buys 0.080 where the first bought 0.240 — a third as much — and that is
the curve's whole argument: the retinue is fiction the player has earned, not a difficulty setting
they have found.

The stair is still `1d6`. It was `1d6` for the lone character too. A quantity written as one die
stays one die from 0.48 all the way to 1.49, and it takes thirteen bodies to push it to two. Small
written quantities are insensitive to scaling by construction, which is the right behaviour: the
arc's texture survives, and it is the *counts* that move.

---

## What the working found

- **The floor is load-bearing, and it is the only special case.** Everything else falls out of
  round-half-up. Without it the lone character's flooded stair throws no dice at all — the one
  quantity in this arc small enough for the ratio to erase, and the one the arc opens with.
- **Rounding once up front is wrong at the heaviest point.** The cult is the arc's largest count
  and therefore the most sensitive to precision lost early; it is the one quantity where a
  pre-rounded `danger_effective` and an exact one disagree.
- **The rule did not need amending after playing it.** Three parties, four quantities, twelve
  roundings, no case where round-half-up-with-a-floor-of-one produced something unplayable.
