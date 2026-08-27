# ADR 0050: Action resolution proposes a result before it commits, rather than writing immediately

**Status:** Accepted
**Date:** 2026-08-27

## Context

Every mechanic in `03-rules.md` has the same shape: an actor's roll resolves, produces an
outcome, and — on the outcomes that call for it — implies a state mutation (Taint gained on a
failed Exposure test, Strain gained on a failed mental test, Stamina lost on a landed blow).
Reroll resources — Fortune, Resolve, the Bargain — mean a roll's outcome is not necessarily
final: a player may spend one, after seeing a failure, to try again. If the engine commits a
roll's implied mutation the moment the roll resolves, a subsequent reroll has nothing left to
supersede cleanly — the first attempt's mutation already happened, and either has to be manually
reversed or is simply layered under a second one, with no clean record of which attempt actually
counts.

`02-architecture.md`'s current CLI sketch shows `wyrd roll <skill>` returning "full structured
result" with no stated write-timing — reasonably read either way, and never actually specified.
Raised while designing #187/#188 (the read/query surface) and generalised in #192's own scoping
discussion: this needed to be decided explicitly, once, as the base mechanism every other action
in the ruleset composes with, not re-decided per mechanic.

## Decision

**A roll's outcome and its implied mutations are computed and returned (`propose`), but not
written to state, until a separate call (`commit`) confirms them — or `discard` explicitly
abandons them.** `propose` looks up everything it needs from state itself (the actor's skill, an
opponent's baseline, a declaration bonus the caller has already decided) and returns roll data
plus a staged mutation set and an id. Nothing on disk changes until `commit` is called with that
id; `discard` invalidates it with nothing written either.

## Why

- **It is what a reroll resource requires to compose cleanly.** Fortune, Resolve, and the
  Bargain all exist specifically to let a player act on a roll's outcome after seeing it — an
  immediate-write model would need every reroll-spending mechanic to also know how to undo a
  prior commit, duplicating the same reversal logic in three places instead of the propose model
  needing zero reversal logic anywhere (an uncommitted proposal simply never happened).
- **It matches the engine's own stated job.** `01-principles.md`'s GM contract already treats the
  dice roller as something that must not be left to the GM's freehand judgment; proposing before
  committing extends the same discipline to *when* a result becomes real, not only *what* the
  result is.
- **It is a small, general primitive, not a mechanic-specific one.** Every action in the
  ruleset gets the same propose/commit/discard shape; a mechanic that needs a different write
  timing would be the exception, and none currently do.

## Alternatives rejected

- **Commit immediately on every roll, reversed by a subsequent reroll if needed.** The status quo
  implied (never stated) by the current CLI sketch. Rejected: it pushes reversal logic onto every
  reroll-granting mechanic individually, and reversal is not always clean — a mutation that
  itself triggered a further cascade (a Taint gain that crossed a threshold and rolled a
  Transformation) would need the reversal to also unwind whatever that cascade did, which the
  propose model avoids by never having committed it in the first place.
- **Commit immediately, and treat a reroll as a wholly new, independent action** (not connected
  to the first attempt at all). Rejected: this contradicts how rerolls are actually described in
  `03-rules.md` (a reroll *of the failed test*, not a fresh unrelated one) and would double-count
  any mutation the first attempt's failure already applied before the reroll even happens.

## Consequences

- `docs/design/31-action-resolution.md` is a new design document specifying `propose`/`commit`/
  `discard` concretely, with a worked example.
- `02-architecture.md`'s CLI sketch gains these three verbs alongside the existing ones.
- Cascading resolution (#194), partial reroll (#195), and Omen carryover (#196) all build on this
  base without needing to revisit whether write timing should be immediate — that question is
  answered once, here.
- No change to any individual mechanic's own rule (Exposure's Taint gain, a reroll's cost or
  bonus) — only when the mutation it implies is written.
