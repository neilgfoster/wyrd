# ADR 0032 — Career caps sit at 70%, and maximum Stamina stops climbing at 10

**Date:** 2026-08-26
**Status:** Accepted

## Context

`03-rules.md` §6 already wrote "to that career's cap" (the only in-career advance) and called
completing a career ("every granted skill at its cap") "the only durable toughening," but never
stated the cap's value or where the Stamina gain it names — +1 per completion — stops. Completing
a career is the single durable growth mechanic in the game, so leaving either open left the whole
power curve unbounded. Two things had to be decided:

1. **The cap's value**, and whether it is one figure per career or one per (career, skill) pair.
2. **Whether maximum Stamina climbs forever**, and if not, where it stops.

Both are load-bearing for a chronicle played across years — the exact situation `05-character-creation.md`
already reasoned about when it fixed *starting* Stamina at 6, and a future pass re-reading only
"career's cap" or "the only durable toughening" could plausibly re-propose an unbounded reading,
having forgotten the reasoning below.

## Decision

**The cap is 70%, one figure per career.** 70% is the top of the *expert* band (`23-diegesis.md`,
60–70%), leaving "it is part of who you are" (75%+) reachable only by something beyond ordinary
career advancement. It applies uniformly to every skill a career grants, matching how §6 already
writes "career's cap" as a single number rather than a per-skill table.

**Maximum Stamina stops climbing at 10.** `05-character-creation.md` already used a computed
threshold to fix the *starting* value: a completion's +1 gain must stay large enough, relative to
current Stamina, for "the only durable toughening" to keep reading as true, and states the
boundary directly — "much above 10 [...] the sentence stops being true." This decision reuses that
same boundary rather than inventing a new one: `1/10 = 10%` is exactly where a further +1 first
drops below a meaningful gain, computed and asserted in
[`../../tools/check_advancement.py`](../../tools/check_advancement.py). A career completed after
the ceiling is reached still grants its Mark; it grants no further Stamina.

**Completion is tracked per career-instance, not per career-for-life.** A character may complete
the same career twice across a lifetime — the career graph may loop — and each instance is its
own span with its own completion check, so a second finishing of the same career grants its
Stamina and Mark again.

## Alternatives considered and rejected

**A per-skill cap table**, letting a career declare a different ceiling for each skill it grants.
Rejected: careers are setting data (`CLAUDE.md`), and a per-skill numeric table would need setting
authors to supply and maintain numbers the engine has no principled way to check for consistency —
it also contradicts §6's own "to that career's cap" phrasing, which already reads as one number.

**75% as the cap**, matching the bottom of "it is part of who you are" rather than the top of
*expert*. Rejected: 75%+ is described in `23-diegesis.md` as identity-level mastery, and letting
ordinary career advancement alone reach it would collapse the distinction the band names — nothing
in the engine currently marks *how* a character crosses into that band, and leaving the door open
at the career cap would make that omission load-bearing rather than incidental.

**An unbounded Stamina gain**, +1 per completion forever. Rejected as the entire reason this ADR
exists: `05-character-creation.md` already computed that the "only durable toughening" framing
stops holding well above 10, and a chronicle played across years with no Stamina ceiling would
make a sufficiently long-lived character harder to kill — directly contradicting §6's own claim
("harder to replace, not harder to kill").

**A round-number ceiling picked without computation** (e.g. 12, or "roughly double starting
Stamina"). Rejected per `CLAUDE.md`'s "check the maths" convention and the precedent
`check_creation.py` already set: a bound asserted without running the numbers is exactly the fault
class this repository keeps being corrected for.

## Consequences

- `03-rules.md` §6 states the 70% cap and the Stamina ceiling directly, no longer leaving either
  open.
- [`check_advancement.py`](../../tools/check_advancement.py) is the durable record of the
  computation; a future re-tune of the meaningful-gain floor recomputes the ceiling rather than
  hand-editing a number.
- A setting's career graph is unaffected: careers still declare their own entries, exits, and
  granted-skill lists; only the cap value and the completion grant are now engine-fixed.
