# ADR 0045: A failed invocation that pushes Strain past a multiple of maximum Stamina costs Trauma

**Status:** Superseded by [ADR 0047](../0047-strain-threshold-crossing-checks-cumulative-strain.md)
**Date:** 2026-08-27

## Context

`09-systems-of-power.md` states cost is "paid once the roll resolves, regardless of outcome" —
the declared `strain_cost`/`resolve_cost` applies identically whether an invocation succeeds or
fails. `intensity_tiers` scales that cost and the Ill-Omen Taint consequence for a more ambitious
declaration, stated purpose "ties ambition to consequence."

#151's playtest spammed 26 consecutive `major`-tier invocations with a fresh character, no Rally
in between. Every attempt failed. It did not matter: Strain climbed to 208 with no stated
consequence anywhere in `docs/design/` for high or accumulated Strain — no cap, nothing analogous
to Taint's transformation table or Trauma's sawtooth. Strain fully resets at the next Rally
(`03-rules.md` §5), so none of that accumulation persists past it. The only cost that survives a
Rally is the Ill Omen's Taint, which fires at a flat, skill-independent rate regardless of how
many times the same declaration was retried. The difficulty ladder does essentially no work here:
a 90% failure rate costs the same as a 10% one, because outcome never touches cost.

**First resolution attempt, superseded within this same decision.** An earlier version of this
ADR keyed the brake off a failure *streak of the same declared power*: 1 Trauma on a failed
invocation immediately following another failed invocation of the *same* system of power, in the
same scene. Re-playtesting it against a character with **two** systems of power, alternating
between them on every attempt, found it trivially defeated: identical fail rate, identical Strain
and Taint accrual, **zero Trauma**, purely because the streak condition only ever compared a power
against itself (raised and tracked as #172). Any player who knows two systems of power has a
strictly dominant strategy over spamming one.

## Decision

**A failed invocation of a system of power that pushes accumulated Strain past a multiple of the
character's maximum Stamina costs 1 Trauma; the remainder past that multiple carries forward as
the new Strain.** This is Trauma's own existing "6 is the floor, not itself a further point... it
fires on the next point past it" convention (`08-afflictions.md`), restated for Strain, with
maximum Stamina as the modulus instead of a fixed number:

1. Strain accrues exactly as `09-systems-of-power.md` already states — `strain_cost` paid every
   invocation, win or lose.
2. **Only a failed invocation is checked against the threshold.** A success that happens to push
   Strain past the same multiple costs nothing extra — the brake targets *failure*, matching the
   stated intent this fix answers to ("players can try if they want, but repeated failures have a
   real cost"), not sheer volume of use.
3. When a failed invocation's resulting Strain total crosses one or more multiples of the
   character's **maximum Stamina**, the character gains 1 Trauma per multiple crossed (mirroring
   how a single large Trauma gain can cross the Affliction floor more than once,
   `08-afflictions.md`), and Strain is reduced to its remainder past the last multiple crossed —
   not reset to zero outright.
4. **When a setting has disabled Strain and/or Trauma** (`overrides.disable`,
   `24-authoring-a-setting.md`), this brake applies no consequence at all — the same graceful
   degradation `09-systems-of-power.md` already states for a Taint-disabled setting's Ill Omen. A
   setting choosing to disable both is choosing consequence-free power use as a genre feature, on
   purpose, through the same override mechanism that already lets it drop Taint; the engine states
   this plainly rather than inventing a fallback consequence path that would itself be a second
   mechanism (ADR 0036).

## Why

- **Targets failure specifically, not volume.** Keying the check to only fire on a failed
  invocation, while letting the underlying Strain track accrue win-or-lose exactly as before,
  keeps a skilled, mostly-succeeding practitioner from paying a tax merely for heavy legitimate
  use — verified computationally: a mixed-outcome run (eff. 50%) shows real separation between
  "any outcome counts" and "failure only" (11 vs. 8 Trauma over the same 26 attempts), and the
  operator's own stated intent ("repeated *failures* have a real cost") is the failure-only
  reading.
- **Maximum Stamina is not a stretch as the tie-in.** `03-rules.md` §2 already states Stamina "is
  not meat... it is cuts, bruises, and losing control of the fight" — composure is already part
  of what Stamina represents in this engine, not purely physical toughness. Reusing it as the
  modulus is not cross-domain borrowing; it is the one other small, stable, per-character capacity
  number the character sheet already carries (`10-the-character.md`: "nothing else is numeric"
  beyond skills, Stamina, the tracks, Fate/Fortune, career), avoiding a flat engine-wide constant
  that a wide range of setting-declared `strain_cost` values would inevitably sit awkwardly
  against.
- **Precedented shape, not a new mechanism.** Both the sawtooth-crossing shape (Taint's every-3
  threshold, Trauma's every-point-past-6 test) and "one track's bound is another track's value"
  (Resolve's cap at Taint + 3, ADR 0043) already exist in this ruleset; this composes both
  patterns rather than inventing either.
- **Closes the rotation loophole by construction, not by special-casing it.** Because the check
  only ever reads the character's own Strain total and maximum Stamina — never which system of
  power produced the latest failure — there is no "same power" comparison left to defeat by
  rotating between declarations. Verified: an identical roll sequence run as a single-power spam
  and as a two-power A/B rotation produces identical Trauma in both cases, at every maximum
  Stamina value tested (6 through 10).
- **Verified against a re-run of a comparable spam sequence, not asserted**: `check_spam_brake.py`
  replays a fresh seeded `major`-tier spam sequence at every realistic maximum Stamina value (6
  through 10) and confirms real, non-zero Trauma accrues — comparable in magnitude to the
  superseded same-power-streak version — while an ordinary, non-spam use sequence and a
  mostly-successful mixed sequence both confirm the brake stays inert exactly where it should.

## Alternatives rejected

- **A failure-streak of the same declared power** (this ADR's own first draft). Rejected: defeated
  outright by rotating between two known systems of power, verified computationally (#172) — zero
  Trauma from 26 consecutive failures, identical Strain/Taint to the single-power case. A brake
  that a player can switch off by knowing two spells is not a brake.
- **A cap or consequence on accumulated Strain before a Rally, using a flat engine-wide number**
  (e.g. a fixed threshold like 6, reusing Trauma's own Affliction floor directly). Rejected: a flat
  number sits awkwardly against the wide range of setting-declared `strain_cost` values — at
  threshold 6 with the worked example's `major`-tier cost of 8, *every single* attempt crosses the
  threshold regardless of streak, which is too blunt (it does not distinguish "tried once,
  ambitiously" from "spammed"). A per-character number (maximum Stamina) scales more sensibly
  across settings with different cost scales without the engine needing to fix one.
- **Any outcome (success or failure) counted toward the threshold**, not only failure. Considered
  and workable — it would have needed no outcome-gating logic at all, matching the existing
  win-or-lose cost philosophy exactly — but rejected because it taxes heavy *successful* use
  identically to heavy *failed* use, which does not match the operator's own stated intent
  ("repeated failures have a real cost") and would discourage a competent practitioner from using
  their own trained ability, not just discourage failing repeatedly.
- **Trying to keep the brake alive when a setting disables Strain or Trauma.** Rejected: both
  tracks are already in the engine's own published disable-able set
  (`24-authoring-a-setting.md`); inventing a fallback consequence for a setting that has
  deliberately switched the relevant track off would itself be a new mechanism, exactly what ADR
  0036 forbids. The existing precedent (Taint-disabled settings already lose the Ill Omen's
  consequence with no substitute) is followed instead of invented around.

## Consequences

- `03-rules.md` §5 states the max-Stamina-threshold Trauma trigger, replacing the superseded
  same-power-streak wording.
- `09-systems-of-power.md`'s cost section states the rule, including the disabled-track
  degradation, and cross-references `03-rules.md` §5.
- `docs/design/30-playtest-transcript.md` §10 gains a note pointing to this ADR and the reworked
  `check_spam_brake.py`, without rewriting its own worked spam sequence (a historical record of
  the gap as found).
- #172 (the rotation loophole) closes as resolved by this same decision — no separate fix needed.
- No change to Strain's own reset-at-a-Rally mechanic, the Ill Omen consequence, or
  `intensity_tiers` — this composes alongside all three unchanged.
