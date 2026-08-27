# ADR 0047: The Strain-threshold Trauma check reads cumulative Strain, not a per-invocation delta

**Status:** Accepted
**Date:** 2026-08-27
**Supersedes:** [ADR 0045](superseded/0045-failed-invocation-crossing-max-stamina-in-strain-costs-trauma.md)

## Context

ADR 0045 gave a failed system-of-power invocation a real, persistent cost: when a failure pushed
accumulated Strain past a multiple of the character's maximum Stamina, it cost 1 Trauma, with
Strain carrying forward at its remainder. A success crossing the same multiple was explicitly
exempted — "costs nothing extra."

The exemption was implemented, and stated, as **edge-triggered**: the check compared this one
invocation's own before-and-after Strain values, and charged Trauma only if *this specific
increment* straddled a fresh multiple. Nothing wrong with exempting a success from paying — that
was always the intent. The bug is what edge-triggering does to the boundary itself: if a success
is the invocation that carries Strain past a multiple, no failure will ever be charged for that
boundary. The next failure only pays if *its own* increment reaches the *next* multiple further
out. The crossing is not deferred — it is erased.

Found by re-playtesting #176's minor-tier spam sequence (`docs/design/30-playtest-transcript.md`
§15) and discussing the result: attempt 26 failed while Strain was already 6.3× the character's
maximum Stamina — accumulated almost entirely through successes — and cost zero Trauma, because
its own +2 increment didn't happen to straddle a fresh boundary. §15's own headline finding ("only
29% of failures cost Trauma at minor tier, working as intended") was itself a symptom of this bug,
not a clean confirmation: a skilled, mostly-successful character is exactly the case where
successes silently carry Strain past boundary after boundary for free, which is backwards from
"ties ambition to consequence."

## Decision

**The check reads the character's current, cumulative Strain directly against the modulus, not a
delta scoped to one invocation — and needs no extra bookkeeping to do it.** On a failed
invocation:

```
gained = (strain - 1) // max_stamina
if gained > 0:
    trauma += gained
    strain -= gained * max_stamina
```

Strain is never reduced on a success — exactly as ADR 0045 already stated — so it keeps
accumulating, unexamined, through any run of successes. The first failure that comes along
computes `gained` against Strain's *true, currently-accumulated* value, which already contains
every multiple silently passed by every success since the last charge. No separate "how many
multiples has this character already paid for" counter is needed: Strain's own uncapped magnitude
already carries that information, because it is only ever reduced at the moment it is charged.

Everything else ADR 0045 decided is unchanged: still failure-only, still 1 Trauma per multiple of
maximum Stamina crossed, still composes with `strain_cost`/`resolve_cost` unmodified, still
degrades gracefully when a setting disables Strain and/or Trauma.

## Why

- **It is the minimal fix that actually closes the gap, not a patch around it.** The bug was a
  scoping error (checking one invocation's delta instead of the character's running total), not a
  missing feature — the fix is a smaller, simpler check than the one it replaces, not a more
  complex one.
- **Verified by direct computation, and it is never *less* punishing than the original.** Re-run
  against both existing spam sequences on their own real rolls: `major` tier's raw Trauma accrual
  rises from 23 to 34 over the same 26-attempt sequence; `minor` tier's rises from 2 to 8. Neither
  case gets more lenient — the fix only closes the erasure, it never invents a new cost.
- **Ordinary play and rotation-immunity are both re-verified unchanged.** Three invocations with
  one isolated failure among successes still costs 0 Trauma at every maximum-Stamina value tested
  — the fix changes *when* a failure catches up, not whether an isolated one is punished. The
  #172 rotation-immunity property is untouched by construction: the corrected check still never
  reads which power failed, only the character's own Strain and maximum Stamina.

## Alternatives rejected

- **Track a separate "highest multiple already charged" counter alongside Strain**, updating both
  in lockstep. Considered and implemented first, in a form that turned out subtly wrong (mixing a
  cumulative counter against a Strain value that had already been locally reduced produces
  under-counting in some sequences — caught by re-deriving the arithmetic by hand rather than
  trusting the first draft). Rejected once the simpler form above was found to give the same
  correct answer with no separate state to keep synchronized — Occam's razor, not merely
  "also works."
- **Leave ADR 0045 as written**, treating the erasure as an acceptable quirk since it only ever
  under-charges, never over-charges. Rejected: it defeats the mechanism's own stated purpose for
  exactly the character type most likely to exercise it in ordinary play — a competent,
  mostly-successful caster — which is a bigger gap than "a rare edge case," not a smaller one.

## Consequences

- `03-rules.md` §5 and `09-systems-of-power.md` restate the rule under the corrected check.
- `specs/057-systems-of-power-spam-brake/check_spam_brake.py` uses the corrected logic; its
  existing assertions (real Trauma on spam, zero on ordinary play, rotation-immunity,
  failure-gating) are re-verified, not dropped.
- `docs/design/30-playtest-transcript.md` gains a new section correcting §10/§14's major-tier and
  §15's minor-tier Trauma figures under the fixed check, with fresh real rolls proving the
  corrected outcome — §10/§14/§15's original text is not edited, per this repo's own convention
  for a historical record.
