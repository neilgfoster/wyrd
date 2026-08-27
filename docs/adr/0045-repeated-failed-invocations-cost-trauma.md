# ADR 0045: A repeated failed invocation of the same system of power costs Trauma

**Status:** Accepted
**Date:** 2026-08-27

## Context

`09-systems-of-power.md` states cost is "paid once the roll resolves, regardless of outcome" —
the declared `strain_cost`/`resolve_cost` applies identically whether an invocation succeeds or
fails. `intensity_tiers` scales that cost and the Ill-Omen Taint consequence for a more ambitious
declaration, stated purpose "ties ambition to consequence."

#151's playtest spammed 26 consecutive `major`-tier invocations with a fresh character, no Rally
in between. Every attempt failed (90% failure rate at that difficulty). It did not matter: Strain
climbed to 208 with no stated consequence anywhere in `docs/design/` for high or accumulated
Strain — no cap, nothing analogous to Taint's transformation table or Trauma's sawtooth. Strain
fully resets at the next Rally (`03-rules.md` §5), so none of that accumulation persists past it.
The only cost that survives a Rally is the Ill Omen's Taint, which fires at a flat,
skill-independent rate regardless of how many times the same declaration was retried. The
difficulty ladder — how the rest of the ruleset prices ambition — does essentially no work here: a
90% failure rate costs the same as a 10% one, because outcome never touches cost.

## Decision

**A failed invocation of a system of power costs 1 Trauma, in addition to its stated Strain/
Resolve cost, when it immediately follows another failed invocation of the *same* system of power
in the same scene.** The first failure of a scene costs nothing extra — a character is free to
try, exactly as before. A success, or a failed invocation of a *different* system of power, resets
the streak: the next failure of the original power is once again a scene's "first" failure.

This is added to `03-rules.md` §5's existing Trauma-gain list, alongside "1 per critical taken, 1
per failed Terror test" — the same shape, the same rate, one more trigger in a list that already
exists, not a new mechanism.

## Why

- **Targets the actual behaviour, not a proxy for it.** The gap is specifically about *repeated
  failure* of the *same* declaration — a player who fails once, or who fails at different powers
  across a scene, was never the problem #163 raised. A Strain-level threshold (Strain crosses some
  fixed number) would also fire on an unlucky mix of several *different* systems, or on ordinary
  play with a cheap `strain_cost`, which is not the behaviour found. Keying directly off
  consecutive-same-power failure hits the actual spam pattern #151's playtest demonstrated (26
  identical `major`-tier attempts in a row) without touching a character who tries a handful of
  different things and fails some of them.
- **Composes with the existing mechanism, invents nothing new** (ADR 0036's "one configurable
  power mechanism" constraint). Trauma already has a stated list of what causes it; this is one
  more bullet in that list, at the same 1-point rate every other trigger uses. No new track, no
  new table, no new dice roll.
- **The cost is real and persists past a Rally** — unlike Strain, Trauma does not reset at a Rally
  (`03-rules.md` §5: "long-term and sticky"), and at 6+ Trauma every further point risks an
  Affliction (`08-afflictions.md`). Spamming a failing declaration now has a cost that survives
  exactly the boundary (a Rally) that let it be consequence-free before.
- **Verified against a re-run of a comparable spam sequence, not asserted**: `check_spam_brake.py`
  replays a fresh seeded `major`-tier spam sequence and confirms the new rule accrues real,
  non-zero Trauma — including crossing the Affliction threshold — where the published (pre-fix)
  rule accrued none, directly satisfying #163's own acceptance criterion that the fix "actually
  changes the outcome rather than only changing the prose."

## Alternatives rejected

- **A cap or consequence on accumulated Strain before a Rally.** Rejected: Strain's `strain_cost`
  varies per declared system, so a fixed cap would fire at wildly different attempt counts for
  different systems, and a *scaling* cap would need its own new threshold table — closer to
  inventing a second consequence shape than reusing the one Trauma already has. It also does not
  distinguish "several different declarations, ordinary play" from "the same declaration, spammed"
  — the actual behaviour in question.
- **A cost that escalates with each retry within a scene** (e.g. `cost_multiplier` climbing 1x,
  2x, 3x... per repeated attempt). Considered and workable, but rejected in favour of tying the
  brake to Taint/Trauma, matching the resolution's own request: a real, persistent cost on
  repeated failure specifically, not merely a steeper version of the same Strain cost that already
  resets at every Rally and was already shown not to matter.
- **Tying the brake to Taint instead of Trauma.** Rejected: Taint already has a dedicated channel
  for systems of power (the Ill Omen consequence, `09-systems-of-power.md`); adding a second Taint
  path for the same mechanism would duplicate that channel rather than compose with it. Trauma has
  no systems-of-power channel yet, and Strain and Trauma are already grouped together as the two
  tiers of mental harm (`03-rules.md` §5) — a failed strenuous effort escalating from the
  short-term tier to the long-term one on repetition is the same shape "1 per failed Terror test"
  already uses.

## Consequences

- `03-rules.md` §5 gains one Trauma-gain bullet.
- `09-systems-of-power.md`'s cost section states the new rule and cross-references it, so it
  reads next to the cost rule it modifies rather than only in the Trauma list.
- `docs/design/30-playtest-transcript.md` §10 gains a note pointing to this ADR and the
  `check_spam_brake.py` re-run, without rewriting its own worked spam sequence (a historical
  record of the gap as found).
- No change to Strain's own mechanic, the Ill Omen consequence, or `intensity_tiers` — this
  composes alongside all three unchanged.
