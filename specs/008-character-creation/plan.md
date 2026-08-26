# Implementation Plan: Character creation

**Branch**: `008-character-creation` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Write `doc/design/05-character-creation.md` and ADR 0014, with starting Stamina derived by
[`check_creation.py`](./check_creation.py) rather than picked.

The shape: **a character is chosen, not generated.** Nothing is rolled — there are no
characteristics to roll (ADR 0013), skills come from the career at the same 25% door an advance
uses, and Stamina, Luck and Fate are flat.

## Deriving Stamina

Four merged facts constrain it. The script models the fight and reports which candidate values
satisfy all of them, across a *band* of weapon damage — weapon damage is setting data, so a value
worth shipping has to hold across the band rather than at one convenient point.

| Constraint | Source |
|---|---|
| +1 per completed career is "the only durable toughening" | `03-rules.md` §6 |
| "A character ten years in is not harder to kill" | `03-rules.md` §6 |
| A drop of 1–3 below zero is ordinary; 1–12 is the modelled range | `check_aftermath.py`, merged |
| Armour subtracts 1d3 / 1d6 / 2d6, minimum 1 through | `03-rules.md` §2 |

**The script rejected its own first threshold**, which is the argument for having written it. It
initially judged the *worst* case — a martial weapon, telling blow, unarmoured — by the "1–3 is
ordinary" bar, and nothing passed at any Stamina. The bar belongs to the *ordinary* case; the worst
case is meant to be grim, and `check_aftermath.py` models overshoots to 12 precisely because they
happen. Judging a worst case by an ordinary threshold is a subtle error that reads as rigour.

Values 5–10 then all pass, so a tiebreak is stated rather than smuggled: above 6 the career gain
thins below 15% and an armoured fight runs past five exchanges, which does not fit the twenty-minute
session `01-principles.md` requires.

## The background

Raised in review: creation as first written had no background, and step 7 asked where a character was
from while nothing read the answer — decorative data that reads as if it matters.

The answer is to **tie the background to the first career**. Every granted skill opens at 25%, then
six free advances are spent *inside that career*. How they are spent is the background, and the
character starts part-way through career one rather than at its very beginning.

This beats a separate background skill list on a rule already in place: advances may only raise
career-granted skills, so a background skill from outside the career would sit at 25% for the entire
chronicle. It also needs no new setting data — careers already declare their skills.

Six is derived, not chosen: it is the largest pool that cannot open a character at *expert*
(60%+ in `10-diegesis.md`'s bands). Seven would.

## Fate by mortality

`low` 2, `standard` 3, `high` 4 — rising with lethality. Fate is the anti-frustration valve as much
as the death valve, so the setting that reaches for it most gets the most. The opposite arrangement
compounds instead of balancing: a deadlier setting killing faster *and* giving less to spend is a
difficulty spiral, not a tone.

Never zero, because Fortune equals Fate and a character with no Fortune has no daily resource at all.

## Steps

1. `check_creation.py` — derive Stamina; model Luck erosion.
2. `doc/design/05-character-creation.md` — the procedure, the values, the setting's obligations.
3. ADR 0014 — chosen, not rolled.
4. Indexes; verify nothing else describes creation as rolled.

## Risks

**The weapon band is an assumption.** Weapon damage is setting data and Stage 6 may fix a narrower
range. The script models 1d3–2d6 and the chosen value holds across all of it, so a later narrowing
cannot invalidate it — only widening past 2d6 could, and that would make armour decorative.

**Taking *every* career skill makes a career's skill list load-bearing.** A career declaring twenty
skills produces a very different character from one declaring four. The engine cannot police it,
having no skill vocabulary. Recorded in the ADR as a setting-authoring consequence.
