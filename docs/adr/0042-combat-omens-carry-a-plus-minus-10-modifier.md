# ADR 0042 — In combat, an Omen carries a ±10 modifier on the roller's own next roll

**Date:** 2026-08-27
**Status:** Accepted

## Context

The Wyrd die (`03-rules.md` §1, the units digit of a natural roll) reads Ill Omen (0) or Fair
Omen (9), 20% of rolls. By default it has no fixed mechanical effect — "something also goes
wrong" / "something also breaks your way" is left to the GM to narrate, the same shape as
invoking a Drive. Specific rules opt individual situations into a concrete consequence: shooting
into someone else's fight ("an Ill Omen means the ally is hit instead," `03-rules.md` §2), and
systems of power (an Ill Omen adds Taint, `09-systems-of-power.md`).

Raised during an operator feedback round on 2026-08-27, after three playtest-epic features
(#147, #148, #149) each noted the Wyrd die faithfully but gave it nothing beyond narrative color
— the documented default working as designed, but the operator's read of the actual play was that
combat specifically wants the Omen to carry weight, not just flavor.

## Decision

**In combat (`03-rules.md` §2's attack and defence rolls), an Ill Omen applies −10 to the
roller's own next roll in the same fight; a Fair Omen applies +10.** The mechanical effect is
additive to the existing narrative framing, not a replacement for it — the GM still narrates
"something also goes wrong," and now that something also measurably costs (or buys) ten points on
the character's next roll.

**Precisely scoped:**

- **The roller's own next roll**, not the opponent's — since the opponent never rolls
  (`ADR 0027`), every Omen in a fight belongs to the player (the Wyrd die "always belongs to the
  player making the roll, attack or defence," `03-rules.md` §2), and so does its consequence.
  "Next roll" is the very next roll of any kind (attack or defence) the same character makes, in
  the order the fight actually produces them — the same round's defence roll if the Omen fell on
  that round's attack, or the following round's attack roll if it fell on a defence.
- **Does not stack.** A second Omen before the pending modifier is spent replaces it; it does not
  add to it.
- **Lapses unused** if the fight ends before the character rolls again.
- **Does not interact with the opt-in Omen consequences already established** (the crowd-shooting
  rule, systems of power's Ill-Omen-Taint). Those are a different kind of consequence — a
  narrative branch or a track cost, not a roll modifier — and apply independently alongside this
  one, the same roll's Omen doing both jobs where both rules are in play.

## Why

**It gives the mechanic the teeth actual play showed it was missing, without inventing a new
resource or track.** The Omen already exists, already fires at a known, computed 20% rate, and
already reads as independent of success/failure (`03-rules.md` §1's own "genuinely independent"
framing). Attaching a ±10 modifier reuses a number already established at this scale (the
declaration bonus's own +10 step, the assistance cap) rather than picking a new one.

**It keeps the narrative framing, rather than replacing it with pure mechanism.** The operator's
explicit instruction was additive, not substitutive — "keep the narrative weight as well, so it's
not just mechanical." A GM narrating "her blade catches a fold of his coat" now also has ten real
points riding on what that costs her next roll, which is exactly the shape §2's own "Stamina is
not meat" register already uses elsewhere: a mechanical fact rendered through a fictional lens,
never the other way round.

**The maths were checked rather than assumed** (`specs/049-combat-omen-mechanical-effect/check_omen_effect.py`),
extending `specs/018-player-facing-combat/check_conversion.py`'s own Markov model with one extra
state dimension (the pending modifier) rather than re-deriving its numbers differently. Across the
same representative pairing span ADR 0028 already used, the shift in expected damage per round
tops out at **0.029** — under a tenth of a Stamina point per round, in either direction, at every
pairing — well under the materiality threshold this feature set for itself. See Consequences below
for the full table.

## Alternatives rejected

**Leave Omens narrative-only in combat too, matching the documented default everywhere else.**
The status quo, and a legitimate position — three playtests already exercised it faithfully with
no mechanical complaint from the rules themselves. Rejected because the operator, reviewing the
same actual play, judged it under-weighted specifically in combat: "these should carry a material
benefit," not just color, in the one context where a roll's outcome is already tracked in hard
numbers (Stamina, degrees) rather than left to pure fiction.

**Apply the modifier to the opponent instead of the roller.** Considered and explicitly rejected
by the operator's own confirmed proposal ("+10/-10... to the roller's own next roll"). Since the
opponent never rolls at all, there is no roll of the opponent's to modify — the only coherent
target is the player's own next roll, whichever side of the exchange it resolves.

## Consequences

- `docs/design/03-rules.md` §2 states the modifier explicitly, alongside its existing narrative
  framing, scoped to combat only — ordinary (non-combat) tests keep the narrative-only default.
- `specs/049-combat-omen-mechanical-effect/check_omen_effect.py` extends
  `specs/018-player-facing-combat/check_conversion.py`'s fight model with a pending-modifier
  state dimension, computed rather than assumed, confirming ADR 0028's published damage-multiplier
  figures do not need re-deriving:

  | pairing (player v opponent) | expected damage dealt/round, base | with the Omen effect | delta |
  |---|---|---|---|
  | 25v25 | 0.778 | 0.797 | +0.019 |
  | 40v40 | 0.778 | 0.797 | +0.019 |
  | 35v30 | 0.856 | 0.875 | +0.019 |
  | 55v40 | 1.241 | 1.243 | +0.002 |
  | 50v30 | 1.574 | 1.574 | +0.000 |
  | 60v30 | 1.986 | 1.986 | +0.000 |
  | 70v35 | 2.063 | 2.063 | +0.000 |
  | 60v20 | 2.397 | 2.373 | −0.023 |
  | 80v40 | 2.397 | 2.373 | −0.023 |
  | 100v50 | 2.474 | 2.446 | −0.029 |

  Largest shift, either direction, across every pairing: **0.029** damage per round.
- A future setting or houserule wanting the modifier at a different magnitude retunes a stated
  number, not an undocumented GM habit.
