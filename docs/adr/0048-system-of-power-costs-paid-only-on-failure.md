# ADR 0048: System-of-power costs (Strain, Resolve) are paid only on a failed invocation

**Status:** Accepted
**Date:** 2026-08-27

## Context

`09-systems-of-power.md` states cost is "paid once the roll resolves, regardless of outcome" —
the declared `strain_cost` always applies, and `resolve_cost`, if present, "applies identically."
This is the only mechanism anywhere in the engine that costs a resource on a *success*. A grep of
the whole design corpus for "regardless of outcome" / "win-or-lose" turns up nothing outside
`09-systems-of-power.md` and its own citations — no other mechanic is win-or-lose. `03-rules.md`
§5's own generic definition of Strain is "today — From failed mental tests, terror, exhaustion,"
already stated as failure-driven everywhere else it is fed. `09-systems-of-power.md`'s own
justification for the carve-out — "the same shape any strenuous, risky effort already has in this
engine" — does not hold under inspection: nothing else actually charges on success.

Raised in conversation, after ADR 0047 fixed the Trauma-threshold check's own bug (a success
could silently erase a crossing a later failure should have paid for): a competent,
mostly-successful caster accrues Strain invisibly through every successful cast under the
win-or-lose rule, with nothing at the table signalling it is happening, until a failure —
correctly, now that ADR 0047 is fixed — charges the entire backlog at once. That is a real
design smell even with the crossing bug fixed: the *size* of a legitimate charge is unpredictable
and detached from anything the player did wrong, purely a function of how many successes happened
to precede the failure.

Quantified against the two sequences already on record
(`docs/design/30-playtest-transcript.md` §10/§14/§15/§16, seeds `20260842` and `20260850`), under
the corrected ADR 0047 check: switching Strain to failure-only accrual reduces raw Trauma from 34
to 30 on the major-tier (mostly-failing) sequence, and from 8 to 2 — a 75% reduction — on the
minor-tier (mostly-succeeding) sequence. The drop is concentrated exactly where the problem was:
a character who mostly succeeds.

## Decision

**Both `strain_cost` and `resolve_cost` are paid only when the invocation fails.** A success
costs neither. `resolve_cost` follows `strain_cost` rather than the two fields diverging — one
failure-only, one win-or-lose would be a harder rule to hold in your head at the table for no
stated benefit, and nothing about `resolve_cost`'s own purpose ("distinct from Fortune's plain
reroll... costs the resource that measures how much fight is left") argues for a different
timing rule than Strain's.

Nothing else about the schema changes: `strain_cost`/`resolve_cost` remain required/optional
exactly as ADR 0036 declared them, `intensity_tiers` still scales both fields identically, the
Ill Omen consequence is entirely unaffected (it is read from the Wyrd die on every invocation,
win or lose, exactly as before — only the *cost* fields change timing, not the resolution roll
itself).

## Why

- **It removes the design's only win-or-lose exception, replacing it with the rule the rest of
  the engine already uses.** Strain is defined, generically, as failure-driven; this closes a gap
  between that stated definition and one mechanism's own carve-out from it, rather than inventing
  a new rule.
- **It removes the silent-backlog problem at its source, not only how the backlog is charged.**
  ADR 0047 fixed the crossing check's own bug — a real, necessary fix — but a mostly-successful
  character could still watch Strain climb invisibly through their own competent play and take an
  unpredictably large hit on their first slip. Failure-only accrual means Strain (and now the
  Trauma it can feed) tracks *what actually went wrong*, not *how many times the character tried
  something, regardless of whether it worked*.
- **Verified against the exact sequences that exposed the original problem, not a fresh, more
  favourable sample.** The 75% reduction on the minor-tier sequence is the direct, measured
  effect of the fix, computed on rolls already on record — not asserted, not cherry-picked.
- **`resolve_cost` follows `strain_cost` for the same reason ADR 0043's own Resolve-recovery
  cadence deliberately reused Strain's rate rather than inventing a third number**: two cost
  fields on the same schema, timed differently, is exactly the kind of inconsistency this
  engine's own review passes keep finding and correcting.

## Alternatives rejected

- **Leave cost win-or-lose, rely on ADR 0047's fixed crossing check alone.** Rejected: the
  crossing check being correct doesn't address that a mostly-successful character's Strain (and
  therefore Trauma exposure) was never meant to be a function of raw attempt count in the first
  place — `03-rules.md` §5 never said that, `09-systems-of-power.md` did, without support
  elsewhere in the engine.
- **Make `strain_cost` failure-only but leave `resolve_cost` win-or-lose.** Considered, and
  workable in isolation, but rejected on the operator's own direction: the two cost fields
  diverging in timing, with no stated reason one differs from the other, is the same class of
  unexamined inconsistency ADR 0047 itself was found and fixed to correct — better closed now
  than left to be found again later.

## Consequences

- `09-systems-of-power.md`'s Resolution section, its Trauma-threshold paragraph, and both worked
  examples restate cost as failure-only.
- `check_spam_brake.py` is updated for failure-only accrual; every property it already verified
  (real Trauma on spam, zero on ordinary play, rotation-immunity, failure-gating) is re-verified,
  not dropped, plus a direct win-or-lose-vs-failure-only comparison on the same two sequences.
- `docs/design/30-playtest-transcript.md` gains a new section replaying every scenario this
  change touches — the major/minor-tier spam sequences, the "ordinary use" worked example (where
  a success previously paid cost and now does not), and the Resolve-recurrence check (which
  previously demonstrated payment on a success and now needs an actual failure to demonstrate
  it) — with real seeded rolls, not asserted. Original sections are not edited.
- ADR 0047's cumulative-Strain-crossing check is unaffected and stays adopted: it remains correct
  general-purpose defense — nothing about this decision prevents some future Strain source from
  ever being win-or-lose — even though the specific scenario that motivated ADR 0047 can no
  longer arise through `strain_cost` once this decision lands.
- ADR 0036's schema description ("`strain_cost` — paid on every invocation, mandatory") is
  unaffected: "mandatory" describes the field's required-ness, not its payment timing, which
  `09-systems-of-power.md` — not ADR 0036 — has always been the document that states.
