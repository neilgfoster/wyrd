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

## Target number: 17, not 20 *(corrected by playtest)*

**The equal-mean argument was wrong in effect.** `3d6` and `d20` do share a mean of 10.5,
but that is irrelevant — what matters is the probability at the range actually rolled, and
Warlock's target of 20 puts starting characters (skills 4-6) in the far tail of a bell
curve:

| Skill | Need vs 20 | d20 | 3d6 |
|---|---|---|---|
| 4 | 16 | 25% | **4.6%** |
| 5 | 15 | 30% | **9.3%** |
| 6 | 14 | 35% | **16.2%** |

Found on the first two rolls of the first playtest: a starting Initiate attempted two things
well within his competence at 9% and 16%. Unplayable.

**Target is 17.** With Warlock's existing difficulty penalties of 2 and 4 intact:

| Skill | Need vs 17 | P(success) | at -2 | at -4 |
|---|---|---|---|---|
| 4 (untrained) | 13 | 25.9% | 16.2% | 9.3% |
| 6 (starting career) | 11 | 50.0% | 37.5% | 25.9% |
| 8 | 9 | 74.1% | 62.5% | 50.0% |
| 10 | 7 | 90.7% | 83.8% | 74.1% |
| 12 (career cap) | 5 | 98.1% | 95.4% | 90.7% |

The bell curve still compresses the top — a maxed career skill is near-certain at its own
speciality. That is acceptable and arguably correct: **Wyrd's lethality comes from combat
criticals and corruption, not from veterans fumbling their own trade.** The 2/4 difficulty
penalties are what keep hard tasks hard for the competent, and they now matter much more
than they did in Warlock, so use them.

Note this means Warlock's printed skill values carry over but its **target number does
not**. Any Warlock material must be read with 17 substituted for 20.

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
