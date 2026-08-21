# Dice design

Working note on Wyrd's resolution mechanic. Open question, not settled.

## The requirement

Warlock's `d20 + skill >= 20` is **binary**. WFRP 3e produces **two-dimensional** outcomes:
did you succeed, *and* what else happened — where a **bane** can land on a success and a
**boon** on a failure. That second axis is where most of the texture lives, and it is
exactly the kind of thing an unconstrained LLM GM otherwise invents freely. Wyrd needs it
structured.

**The axes must be independent.** Any scheme where the side effect is derived from *how
well* you rolled cannot produce the two most valuable results: the hard-won victory that
costs you something, and the failure that hands you an unexpected opening.

## Rejected: margin

Read the side effect from degree of success (bare pass = bane, wide margin = boon). This
collapses both axes into one. A large success can never carry a bane. Same defect as
PbtA's 7-9 band. **Rejected.**

## Rejected: a summed Wyrd die

Roll 3d6, one die a different colour, sum all three for success, read the side effect off
the coloured die. Better, but still correlated — and correlated worst exactly where it
matters:

| Difficulty | success+bane | fail+boon |
|---|---|---|
| Easy (need 8) | 9.7% | **0%** |
| Even (need 11) | 2.8% | 2.8% |
| Hard (need 14) | **0%** | 9.7% |

On a hard task a success *cannot* carry a bane: if the total cleared a high target, the
coloured die cannot have been a 1. **Rejected** — the awkward quadrants vanish precisely
when they would be most dramatic.

## ACCEPTED: d100 roll-under, units digit as the Wyrd die

**Settled 2026-08-21** — see [ADR 0001](../design/adr/0001-d100-resolution.md) and
[ADR 0002](../design/adr/0002-wfrp2-compatibility.md).

> **Roll `d100`, succeed at or under `skill%`.** Success Levels give magnitude; the **units
> digit of the natural roll** is the Wyrd die.

One roll, three independent axes, no extra dice. `skill% = (skill + 1) × 5` converts
Warlock's ladder with zero probability drift, and WFRP 2e / Dark Heresy stat blocks are read
as printed.

The units digit is uniform within both the success and failure sets — exactly so at any
skill that is a multiple of 10, never more than 2 points off otherwise. Better independence
than any separate-dice scheme achieved here.

**The natural roll rule:** the Wyrd die is read from the dice as they first fell, never
modified and never rerolled. Fortune buys the result, not the world's reaction to the first
attempt. *You can change what happened; you cannot change what it cost.*

The history below is retained because the rejections are the reasoning, and because two of
them were only found by playing.

---

## Superseded: d20 for the total, 2d6 alongside it

Two earlier attempts failed, and both failures were instructive.

**Attempt 1 — `3d6 + skill vs 20`.** The equal-mean argument (`3d6` and `d20` both average
10.5) was true and irrelevant. What matters is the probability *at the range actually
rolled*, and target 20 puts starting characters in the far tail of a bell curve. Found on
the first two rolls of the first playtest: a skill-6 test succeeds 16.2% of the time instead
of d20's 35%.

**Attempt 2 — `3d6 + skill vs 17`.** Fixed the bottom by breaking the top:

| Skill | 3d6 vs 17 | d20 vs 20 |
|---|---|---|
| 4 | 25.9% | 25.0% |
| 6 | 50.0% | 35.0% |
| 10 | 90.7% | 55.0% |
| 12 *(career cap)* | 98.1% | 65.0% |
| 14 | **100.0%** | 75.0% |

At skill 14 a character literally cannot fail. A bell curve compresses its tails by nature,
so you can have playable novices **or** fallible veterans, not both.

**The error in both was making the side-effect dice part of the total.** Separate them and
the problem dissolves.

### The mechanic

> **Roll `d20 + skill vs 20` for success** — Warlock, entirely unchanged.
> **Roll `2d6` alongside — the Wyrd dice — which never contribute to the total.**
> **If they match, something else happened. The matched value says what.**

| Wyrd dice | Chance | Result |
|---|---|---|
| 1,1 | 2.8% | **Chaos Star** — something goes wrong in a Chaos-flavoured way |
| 2,2 | 2.8% | **Bane** — a complication |
| 3,3 / 4,4 | 5.6% | **Twist** — a detail, no mechanical weight |
| 5,5 | 2.8% | **Boon** — an advantage |
| 6,6 | 2.8% | **Comet** — a significant break in the player's favour |
| no match | 83.3% | nothing |

Snake eyes is the Chaos Star; boxcars is the Comet.

### Why this one works

- **Warlock's maths is preserved exactly** — 25% at skill 4, 65% at skill 12, 75% at skill
  14. Novices can act; veterans stay fallible. Every Warlock book in the library is usable
  **as printed**, with no substitution and no retuning.
- **The axes are genuinely independent** — not merely orthogonal-ish as with AGE's doubles,
  but statistically unrelated, because the `2d6` contribute nothing to the outcome. Success
  with a Chaos Star and failure with a Comet are equally possible at *every* difficulty.
  This was the original requirement and it is the first scheme to fully meet it.
- **Difficulty** stays Warlock's penalty of 2 or 4 to skill.

### The known cost

Side-effect frequency drops from AGE's 44% to **16.7%** — roughly one in six rolls, so
perhaps one per short session. That may prove too sparse.

It is the safer direction to be wrong in, and it is tunable without an engine release
(see [`../design/09-evolution.md`](../design/09-evolution.md)): widen by treating any single
`1` on a Wyrd die as a bane even without a match, which adds ~14%.

### Corruption still bends the dice

Following TOR's Eye-of-Sauron precedent, the threat is gated by state:

| Corruption | Reads as Chaos Star |
|---|---|
| 0-2 | 1,1 |
| 3-5 | 1,1 and 2,2 |
| 6+ | 1,1 · 2,2 · 3,3 |

The world goes wrong around you more often as you rot, and your competence is untouched.

## Prior art

| System | Mechanism | Independent? |
|---|---|---|
| **WFRP 3e / Genesys** | Separate symbol sets: success/failure and advantage/threat resolved independently | Yes — the reference |
| **Wrath & Glory** | One die in the pool is the **Wrath die**; a 1 is a Complication "regardless of whether you failed or succeeded" — a "yes, but" / "no, and", explicitly not a fumble | Yes, but relies on a *large* pool so one die barely moves the total |
| **Dragon Age / AGE** | `3d6 + ability`, one die is the **Dragon Die**; **doubles** on any two dice trigger a stunt, magnitude = Dragon Die | **Yes** — doubles are orthogonal to the sum |
| **D6 System (Wild Die)** | Distinguished die: 6 explodes, 1 signals a complication | Partly |
| **Cortex Prime** | A "hitch" on any 1, regardless of outcome | Yes |
| **The One Ring** | Feat die icons (Gandalf rune / Eye of Sauron) **override** the outcome | No — crit/fumble, not a side axis |
| **PbtA** | 7-9 partial success | No — margin-based |

TOR contributes something different and valuable: **state-gating**. The Eye of Sauron is
always on the die, but *"when a Miserable hero makes a roll and gets an Eye of Sauron on his
Feat die, he suffers a bout of madness."* The face only bites once your spiritual state has
already gone bad.

## Proposed: AGE-style doubles + Wyrd die

> **Roll 3d6 + skill vs 20.** One die is a different colour — the **Wyrd die**.
> - **The total** decides success or failure.
> - **Doubles** (any two dice matching) decide *whether something else happened*.
> - **The Wyrd die** decides *what kind*.

| Wyrd die | Side effect (only if doubles) |
|---|---|
| 1 | **Chaos Star** — something goes wrong in a Chaos-flavoured way |
| 2 | Bane — a complication |
| 3-4 | Neutral — a twist, no mechanical weight |
| 5 | Boon — an advantage |
| 6 | **Comet** — a significant break in your favour |

Doubles occur **44.4%** of the time overall, and can occur at *any* total — that is the
property that makes this work. Every quadrant is reachable at every difficulty:

| Difficulty | success + bad | failure + good |
|---|---|---|
| Easy (need 8) | 6.9% | 0.5% |
| Even (need 11) | 1.9% | 1.9% |
| Hard (need 14) | 0.5% | 6.9% |

Nothing is zero. The awkward quadrants stay rare — which is right; a victory that costs you
something should be memorable, not routine.

Residual skew remains (a hard-won success carries a bane only 0.5% of the time), but
"rare" is categorically different from "impossible", and rarity is what makes it land.

**Why this suits an LLM GM specifically:** three independent reads from three dice, all
deterministic, all checkable, and it produces an explicit narration hook rather than
leaving "what else happened" to invention. It reads in one line of text:
`3d6+skill: 5 5 2 +6 = 18 vs 20 — failure. Doubles (5,5). Wyrd die 5 — boon.`

## The corruption hook

Because the Wyrd die is read separately, **the corruption and insanity tracks can bend it**
— following TOR's precedent exactly. As Corruption rises, the Chaos Star range widens:

| Corruption | Chaos Star on |
|---|---|
| 0-2 | 1 |
| 3-5 | 1-2 |
| 6+ | 1-3 |

The world goes wrong around you more often as you rot, without touching your competence at
all. Mechanically tiny, thematically large, and it makes corruption **felt on every roll**
rather than only at thresholds — which was the gap identified in both WFRP 3e and 4e.

It pairs with, rather than duplicates, 3e's **GM Invocation** (a deliberate spend) and 4e's
**Dark Deal** (a deliberate player choice). This is the ambient third leg.

## Open questions

- Does 44% side-effect frequency prove too busy in play? Tuning knob is the neutral band
  (widen 3-4 to 2-5).
- Should **triples** be distinguished from doubles as a rarer, larger effect? AGE does not,
  but Wyrd has room.
- Does the Wyrd die contributing to the total matter, given the *trigger* is doubles? It
  reintroduces mild skew; the alternative is a fourth, non-summing die.
- Read **Dragon Age's stunt tables** before finalising — they are effectively a pre-written
  boon list across combat, spell, roleplaying and exploration. See
  [library-triage.md](library-triage.md).
