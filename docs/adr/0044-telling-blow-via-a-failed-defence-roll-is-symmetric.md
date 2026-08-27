# ADR 0044: A telling blow via a failed defence roll is computed by the same symmetric procedure the damage-multiplier modelling already assumed

**Status:** Accepted
**Date:** 2026-08-27

## Context

`03-rules.md` §2 states combat degrees are "read from the roll exactly as in §1" and a telling
blow triggers on "win by 6 or more degrees." §1's own convention — degrees only exist on a
success, since a miss has nothing to read them from — is unambiguous for an **attack** roll: the
roll that determines the hit is always the one that must succeed, so degrees are always available
to check against the threshold.

For a **defence** roll, the roll that determines the hit is a *failure* — "Failure means the blow
lands" (§2). Read literally against §1's success-only convention, a blow landing via a failed
defence roll can never be a telling blow, however badly the roll missed, because the roll that
landed it never succeeded and so never produced degrees.

`specs/018-player-facing-combat/check_conversion.py`'s own damage-multiplier modelling — the
figures ADR 0028 published — already computes the opponent's telling-blow rate via
`telling_rate(100 - effective_pct(player_defence, opponent_attack), threshold)`: a failed defence
roll treated as a virtual attack success against the complementary effective%. That is an
aggregate probability technique, not a per-roll procedure a GM could follow by hand at the table,
and `03-rules.md` never states it. #148's playtest hit this gap directly and used the conservative
reading (no telling blow via a failed defence at all) rather than deciding the question.

## Decision

A blow landing via a failed defence roll **can** trigger a telling blow, computed by the same
virtual-roll symmetry `check_conversion.py`'s modelling already assumed:

1. The player rolls the defence roll `r` against `eff_def` as always. `r > eff_def` — the roll
   fails, the blow lands.
2. Read the failed roll as a **virtual attack roll**: `virtual_eff = 100 − eff_def`,
   `virtual_roll = 101 − r`.
3. Degrees are `tens(virtual_eff) − tens(virtual_roll)`, exactly §1's formula, fed the virtual
   inputs instead of the natural ones.
4. Telling blow triggers at degrees ≥ 6, the same threshold as everywhere else (ADR 0028) — one
   threshold, one formula, applied to whichever roll (real or virtual) the situation produces.

This is symmetric with the attack side by construction: a defence roll that misses badly (`r`
close to 100) produces a small `virtual_roll` (close to 1) against a favourable `virtual_eff`,
exactly the shape of a decisive attack success.

## Why

- **It is what ADR 0028's own published figures already assumed.** `check_conversion.py`'s
  `fight_outcome` computes the opponent's telling-blow rate this way already; the attack-only
  reading would mean ADR 0028's damage-multiplier figures were never actually correct for the
  ruleset they claimed to describe. Confirming the existing reading rather than inventing a new
  one is deterministic-over-inference (CLAUDE.md): the model was already committed, only the
  prose that states it was missing.
- **Symmetric telling blows are the more coherent game.** An opponent's attack landing via the
  player's own badly-failed defence is exactly as dramatic a moment as the player's own decisive
  attack — nothing in the fiction (or in ADR 0027's "the opponent never rolls, capability is
  static") suggests an opponent should be structurally unable to land a telling blow.
- **Verified computationally, not asserted**: `specs/056-telling-blow-via-failed-defence/check_defence_telling.py`
  implements the per-roll procedure above by iterating every one of the 100 possible natural rolls
  and independently reproduces `check_conversion.py`'s own `telling_rate(100 − eff_def,
  threshold)` exactly, at every effective% from 5 to 95 in steps of 5. The two computations share
  no code path — one iterates real rolls one at a time, the other sums a closed-form distribution
  — so an exact match across the whole range is real confirmation, not a tautology.

## Alternatives rejected

- **Attack-only: a blow landing via a failed defence roll can never be a telling blow.** The
  textually conservative reading, and the one #148's playtest actually used rather than decide the
  question. Rejected because it contradicts ADR 0028's own modelling and its published figures —
  adopting it here would mean either re-deriving ADR 0028's damage-multiplier numbers under a
  materially different (and less dramatic) combat shape, or leaving a design document and its own
  cited probability script permanently disagreeing with each other. Also a strictly less
  symmetric, less coherent combat model with no stated reason for the asymmetry.
- **A different formula for the defence side** (e.g. reading degrees directly off the natural
  failed roll without the virtual-roll transform, `tens(eff_def) − tens(r)`, which is negative on
  every failure and so would never reach the threshold under a naive reading, or some other ad hoc
  mapping). Rejected because it isn't what `check_conversion.py` already computes and would
  require re-deriving ADR 0028's figures from scratch for no stated benefit — the virtual-roll
  transform is the one formula that already has a verified track record in this ruleset's own
  modelling.

## Consequences

- `03-rules.md` §2 states the per-roll procedure explicitly, replacing the ambiguous "read from
  the roll exactly as in §1."
- ADR 0028's damage-multiplier figures needed no re-derivation — this ADR is a confirmation of the
  model they already used, not a change to it.
- `docs/design/30-playtest-transcript.md` §7's playtest, which used the conservative
  attack-only reading, now has a documented reading it did not use; a note is added there
  pointing to this ADR rather than silently leaving the playtest's own worked example
  inconsistent with the resolved rule.
