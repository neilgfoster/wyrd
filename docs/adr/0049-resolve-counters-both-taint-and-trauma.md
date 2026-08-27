# ADR 0049: Resolve's cap widens to counter both Taint and Trauma, via a dual threshold

**Status:** Accepted
**Date:** 2026-08-27
**Supersedes:** [ADR 0043](superseded/0043-resolve-recovers-at-a-rally-capped-by-taint.md)

## Context

A design review of the full track roster, looking for physical/mental/spiritual mirroring, found
that Taint has Resolve as a counterweight and Fate has Fortune as a counterweight — Trauma has
nothing. `03-rules.md`'s own track table already names Resolve "the spendable counterweight to
Taint" specifically, leaving Trauma the one long-term accrual track with no resource that spends
against it.

Two candidate fixes were investigated:

1. **A new, dedicated track** ("Composure"), mirroring Resolve's shape exactly — same recovery
   cadence, its own cap at Trauma + 3, the same +20-reroll spend — as a third instance of the
   scarce-resource-plus-counterweight pattern ADR 0049's sibling decision
   ([issue #182](https://github.com/neilgfoster/wyrd/issues/182)) named as already used twice
   (Taint/Resolve, Fate/Fortune).
2. **Widening Resolve itself** to counter both tracks, via a dual threshold on its existing cap.

The dedicated-track option was rejected: it would give every character **two** independent
+3-over-threshold pools of the same +20-reroll currency where there is one today — a real
increase in total spendable resource, not a cosmetic reorganisation, with no stated balance
justification. Widening Resolve costs nothing on that front: the total number on the sheet, and
the total spend budget it represents, is unchanged: only what bounds its cap and triggers Spent
changes.

## Decision

**Resolve's cap is `max(Taint, Trauma) + 3`** — the same one threshold-interval of headroom ADR
0043 already established, now measured against whichever of Taint or Trauma is currently higher,
not Taint alone.

**Resolve is Spent when it falls to meet whichever of Taint or Trauma is higher.** The existing
Taint-0 exemption ("a character who has accrued no Taint at all has nothing yet for Resolve to be
a counterweight *to*") generalises per axis, exactly the same reasoning applied twice: exempt
from Spent-via-Taint only when Taint is 0, exempt from Spent-via-Trauma only when Trauma is 0.
Overall Spent is true if either un-exempted axis has been reached — a character with Taint 0 and
Trauma 8 can still be Spent (via Trauma); a character with Taint 8 and Trauma 0 can still be
Spent (via Taint); a character with both at 0 cannot be Spent at all, the same as before.

Everything else about Resolve is unchanged: +1 at a Rally, back to cap at a downtime; spend 1 for
a +20 reroll bonus; distinct from Fortune's plain reroll for the same reason ADR 0043 already
gave. No new narrative description of the Spent state is needed — "will not press a struggle and
will withdraw from danger" already covers either cause without modification.

## Why

- **It closes the actual gap (Trauma has no counterweight) without inflating the resource
  economy.** The dedicated-track alternative was the more symmetric-looking option on paper, but
  symmetry that costs a real, unexamined power increase is the wrong trade — this repo's own
  review passes exist to catch exactly that kind of unstated buff.
- **It tells a coherent single story, not two unrelated ones.** Resolve already reads generically
  — "the resource that measures how much fight is left" (`09-systems-of-power.md`) — not
  intrinsically Taint-specific; only its cap formula tied it to Taint alone. A single reserve of
  willpower, worn down by whichever burden (corruption or trauma) presses harder, is a more
  honest reading of what the resource was already described as measuring than "Taint's
  counterweight" ever was.
- **The per-axis exemption is not a new rule, it is the existing one applied twice.** ADR 0043's
  Taint-0 exemption already had a stated reason ("nothing yet to counter") that generalises
  without needing new justification — the same sentence, read against either track.
- **Verified computationally**, not asserted: `specs/052-resolve-recovery-mechanic/check_resolve.py`
  is extended to check the dual-threshold cap and both exemption cases (Taint 0/Trauma nonzero,
  Trauma 0/Taint nonzero, both 0) across a representative range, proving headroom is always
  positive and Spent is reachable through ordinary play on either axis independently.

## Alternatives rejected

- **A new dedicated track ("Composure") mirroring Resolve exactly.** The more symmetric-looking
  option — three matched pairs instead of two, completing the pattern ADR 0049's sibling decision
  named. Rejected because it doubles the total spendable +20-reroll currency on the sheet with no
  balance argument for characters needing more of it just because the design got tidier. A real
  mechanical increase disguised as a structural one.
- **Leave Trauma without a counterweight.** The status quo. Rejected because the asymmetry is
  real: Taint and Fate both get a resource that spends against their worst outcome, and nothing
  about Trauma's own shape argues it should be structurally different from either.

## Consequences

- `03-rules.md` §4 states the dual-threshold cap and the per-axis Spent exemption, replacing the
  Taint-only formula.
- `check_resolve.py` is extended to verify the dual-threshold formula and both exemption cases,
  not just the Taint-only case ADR 0043 originally proved.
- A new playtest section demonstrates the corrected formula with a worked character — a case
  where Trauma, not Taint, is the binding threshold, since that is the case ADR 0043's own
  verification never had reason to exercise.
- No change to Resolve's recovery cadence, its spend amount, its distinction from Fortune, or to
  Taint's or Trauma's own accrual rules — only what bounds Resolve's cap and triggers Spent.
- #182's shared-pattern passage (Taint/Resolve, Fate/Fortune as one mechanism twice) is
  unaffected by this decision choosing not to add a third instance — the passage describes what
  exists, and what exists is still two dedicated pairs, plus Resolve now doing double duty rather
  than a third pair appearing.
