# ADR 0029 — Taint thresholds sit at every 3 points, and Dread equals severity

**Date:** 2026-08-26
**Status:** Accepted

## Context

`03-rules.md` §4 said a Taint threshold forces a Transformation without ever stating a value, and
the only numeric anchor in the section was the Wyrd-die bands in §1 (0–2 clean, 3–5 the die starts
turning, 6+ it turns further). Two things had to be decided that were not forced by that anchor
alone:

1. **Where thresholds sit past 6.** The bands stop naming a boundary after "6+"; Taint itself does
   not stop there (it is uncapped in the current rules), so a scheme was needed for every value a
   long-running character could actually reach.
2. **What Dread measures.** §4 says Transformations carry Dread and says nothing about its size.

Both are load-bearing for [`03a-3-transformations.md`](../03a-3-transformations.md)'s termination
proof and social consequence, and both had a real alternative that a future pass could plausibly
re-propose having forgotten why it was rejected.

## Decision

**Thresholds sit at every multiple of 3, starting at 3 (3, 6, 9, 12, …).** This extends the two
values the die-band table already anchors (3 and 6) at the same interval indefinitely, rather than
inventing a second interval past 6 or leaving Taint's upper range without thresholds at all.

**Dread equals the severity just consumed**, accumulated across every Transformation. One measured
quantity is read twice — into Taint's reduction and into Dread's total — rather than a second,
independently-tuned number tracking materially the same fact (how large a change this
Transformation was).

## Alternatives considered and rejected

**Thresholds only at 3 and 6, with no further threshold past 6.** This was the most literal reading
of §1's own table, which stops at "6+" with no further band. Rejected because it leaves every
Taint point past 6 doing nothing to the Transformation mechanic while still bending the Wyrd die
further — a character deep in Taint would keep getting worse dice with no matching consequence
layer, which contradicts the stated purpose of the mechanic (Taint's cost is meant to compound, not
plateau after two thresholds). A future author re-reading only §1's table, as this issue's own
context notes was already happening, could plausibly re-propose stopping at 6 having forgotten this
was tried and rejected — which is exactly the case for recording it.

**Widening spacing past 6** (e.g., thresholds every 5 points once Taint exceeds 6, on the theory
that a heavily-Tainted character should cross them less often). Rejected for the same reason ADR
0019's crowd rule and ADR 0024's danger scaling both reject unmotivated special-casing: a second
interval needs its own justification and its own re-derivation of the termination proof in
[`03a-3-transformations.md`](../03a-3-transformations.md), for a benefit (fewer high-Taint
Transformation rolls) nothing in play has yet shown is needed. The uniform interval is simpler,
already computed, and extends without a seam.

**Dread as an independently-tuned number per row**, rather than reusing severity. Rejected because
it is the two-numbers-for-one-fact pattern `CLAUDE.md`'s fault list warns is a staleness magnet: a
future severity re-tuning (which the termination proof already anticipates as plausible — see
`03a-3-transformations.md`'s note that termination does not depend on the exact severities) would
leave a hand-authored Dread column silently out of step with it. Reusing severity means a re-tune of
one automatically re-tunes the other correctly.

## Consequences

- [`03a-3-transformations.md`](../03a-3-transformations.md) states both numbers as computed facts,
  and [`tools/check_transformation.py`](../../tools/check_transformation.py) checks the threshold
  scheme's termination property rather than asserting it.
- A later re-tuning of the severity table is expected to be possible without touching Dread's
  definition, only its resulting numbers.
- If play later shows thresholds every 3 points cross too often at high Taint (many Transformations
  stacking Dread faster than the fiction can carry), that is grounds for a **new** ADR widening the
  interval past some value — this one stands as the reasoning for why the uniform interval was
  chosen first.
