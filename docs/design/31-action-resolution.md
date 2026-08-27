# Wyrd — action resolution

How an action actually resolves against state: the base mechanism every mechanic in
[`03-rules.md`](03-rules.md) composes with. Not combat-specific — resolution, Exposure,
Terror tests, systems of power, advancement rolls all use the same shape.

This document covers the propose/commit/discard mechanism, cascading resolution (a mutation that
crosses a threshold and spawns a further roll, inside the same proposal), and partial reroll (a
player spending Fortune/Resolve/the Bargain against one step of a proposed result, without
disturbing what didn't depend on it). **Omen carryover** across more than one roll is not yet
specified — see the parent epic's remaining child for that, extending this same document once
landed rather than fragmenting into a separate one for what is genuinely one mechanism.

---

## Propose, then commit

**A roll's outcome and its implied state mutations are computed and returned, but not written,
until a separate call confirms them** ([ADR 0050](../adr/0050-action-resolution-proposes-before-it-commits.md)).
Three verbs:

- **`propose`** — resolves one roll against state, returns the roll data and any mutations it
  implies, and an id. Writes nothing.
- **`commit`** — given a proposal id, applies exactly its staged mutations, atomically, and
  invalidates the id.
- **`discard`** — given a proposal id, writes nothing, and invalidates the id.

Calling `commit` or `discard` with an id that does not resolve to an open proposal (already
resolved, or never issued) is an error — distinct from either succeeding as a no-op, since a
caller must never be able to mistake "nothing to do" for "your commit went through."

## What `propose` takes

- **`actor`** — the entity id whose action this is. `propose` looks up its own skill values,
  tracks, and other state directly — the caller never supplies a skill percentage.
- **`mechanic`** — which rule this invokes (`ordinary-test`, `exposure`, `terror-test`,
  `system-of-power:<id>`, and so on) — a closed vocabulary matching the engine's own rules,
  never a setting addition (consistent with [ADR 0036](../adr/0036-one-configurable-power-mechanism.md)'s
  "one configurable mechanism" and the general rule that a setting never adds a mechanism).
  The mechanic is what tells the engine which mutation, if any, a given outcome implies — the
  caller never states "and on failure, gain 2 Taint" itself, because that mapping already
  belongs to the mechanic's own rule, not to the caller invoking it.
- **`skill`** — the setting's own skill name being tested, for mechanics that test one. The
  engine names no skill ([ADR 0013](../adr/0013-the-engine-names-no-skill.md)), so the caller
  always names it.
- **`target`** *(optional)* — an opponent/baseline entity, for an opposed or combat test; its
  own skill or baseline is looked up from state the same way the actor's is.
- **`difficulty`** *(optional, default Average)* — a difficulty band.
- **`declaration_bonus`** *(optional, default 0)* — an already-decided numeric value (0, +10,
  +20, or −20 per `03-rules.md`'s own Declaration table). **`propose` never parses free narrative
  text to decide this itself** — whether a stated action is "specific and leveraging something
  established" is exactly the freehand judgment the engine principles say a human (or the GM
  layer) must make, not code. The caller states the bonus already decided; the engine only
  applies it consistently once stated.

## What `propose` returns

```json
{
  "proposal_id": "p-...",
  "roll": {"actor": "senna", "mechanic": "exposure", "roll": 77, "effective_pct": 40,
            "degrees": null, "wyrd_die": "none", "outcome": "fail"},
  "mutations": [
    {"entity": "senna", "field": "taint", "op": "+", "value": 2}
  ]
}
```

An outcome with no implied consequence (many ordinary tests) returns an empty `mutations` list —
not an error; a roll that changes nothing is a common, valid result.

## A worked example

Senna Vask, `bargaining: 40`. A moderate (2) Exposure source, not running with the grain of her
Fault Line — no bias. Real `d100` draw, seeded `20260852`: roll **77** — fails against `eff. 40`.

**`propose`** (`actor: senna`, `mechanic: exposure`, `skill: bargaining`, tier: moderate):

```json
{
  "proposal_id": "p-8f2c",
  "roll": {"actor": "senna", "mechanic": "exposure", "roll": 77, "effective_pct": 40,
            "outcome": "fail"},
  "mutations": [{"entity": "senna", "field": "taint", "op": "+", "value": 2}]
}
```

**State immediately after `propose`**: unchanged. Senna's `taint` field on disk still reads
whatever it read before this call — the proposal exists only as the returned response, not as a
write.

**`commit("p-8f2c")`**: Senna's `taint` field increases by 2, exactly the staged mutation. The
proposal id no longer resolves to anything further.

**Had `discard("p-8f2c")` been called instead**: Senna's `taint` field is untouched, and the id
no longer resolves — as if the roll had never been proposed.

## Cascading resolution

**A staged mutation that crosses a threshold spawns a further step inside the same proposal,
rather than requiring prose to notice the threshold and call the engine again.** Every track
with a threshold already has its own rule for what happens at it — Taint every 3 points rolls a
Transformation ([`07-transformations.md`](07-transformations.md)); Trauma past 6 tests on every
further point, and a failed test rolls an Affliction
([`08-afflictions.md`](08-afflictions.md)); a Strain gain crossing a multiple of maximum Stamina
costs Trauma ([ADR 0047](../adr/0047-strain-threshold-crossing-checks-cumulative-strain.md)),
which can itself cross Trauma's own threshold. `propose` checks every mutation it stages against
its track's threshold rule and, on a crossing, stages the further roll(s) that rule calls for as
additional steps in the same proposal — recursively, since a sub-roll's own mutation can cross a
further threshold in turn (Taint's own every-3 spacing already allows more than one crossing from
a single large gain).

**Each staged step records what it depends on** — the sub-roll a crossing spawns depends on the
mutation that crossed it, which depends on the roll that produced that mutation. This is what
partial reroll (below) consumes to work out what a mid-batch reroll invalidates.

**This does not need its own termination proof.** Each track's own cascade shape already
terminates by a proof that already exists — the Transformation hidden-threshold loop terminates
in the worst case per `check_transformation.py`; the Affliction sawtooth is bounded by its own
−6-per-success shape. A proposal's cascade is a finite composition of finitely many
already-terminating cascades, so it terminates too, without this mechanism needing to reprove
what each track's own rule already established.

**Not every consequence cascades into the same proposal.** A critical, rolled the moment damage
takes a combatant below 0 Stamina, does **not** spawn an immediate Aftermath step — Aftermath is
explicitly rolled "after the fight, once they have dropped"
([`06-aftermath.md`](06-aftermath.md)), a deliberately deferred consequence, not an immediate
one. Cascading resolution only ever stages what the triggering rule itself says happens
immediately; a rule that defers its own consequence stays deferred.

### A worked example: a Taint-threshold cascade into a Transformation

The same real rolls already played in `30-playtest-transcript.md` §8, reused here to show what
the cascade looks like through `propose`/`commit`, not fresh dice: Senna Vask buys her way past a
locked gate (a moderate Exposure source running with the grain of her Fault Line, biased one tier
worse — moderate 2 becomes major 3). Resist, `eff. 35`: roll **86** — fails. Taint `1 → 4`,
crossing the threshold at 3.

**`propose`** stages this as two steps in one proposal:

```json
{
  "proposal_id": "p-3a91",
  "steps": [
    {"step_id": 0, "kind": "roll", "mechanic": "exposure", "roll": 86, "outcome": "fail",
     "depends_on": []},
    {"step_id": 1, "kind": "roll", "mechanic": "transformation", "roll": 6, "severity": 4,
     "depends_on": [0]}
  ],
  "mutations": [
    {"entity": "senna", "field": "taint", "op": "+", "value": 3, "produced_by_step": 0},
    {"entity": "senna", "field": "taint", "op": "-", "value": 4, "produced_by_step": 1},
    {"entity": "senna", "field": "dread", "op": "+", "value": 4, "produced_by_step": 1},
    {"entity": "senna", "field": "hidden_threshold", "op": "set", "value": 3,
     "produced_by_step": 1}
  ]
}
```

Step 0's mutation (`taint +3`, landing at 4) crosses the threshold at 3, so `propose` stages
step 1 — the Transformation roll (`1d6 = 6`, severity 4) — without prose ever having to notice
the crossing itself. Step 1's own mutations (`taint -4`, back to 0; `dread +4`; the hidden
threshold set once, secretly, at first Transformation, per `07-transformations.md`) are staged
in the same proposal, depending on step 0.

**Committing this proposal** applies all four mutations atomically: Taint ends at 0 (not 4), not
because two separate calls happened, but because the cascade already resolved and staged both
legs before anything was confirmed.

## Partial reroll

**Rerolling one step discards exactly what causally depends on it, and nothing else.** A
proposal can contain more than one step — independent branches from separate actions batched
together (§ A worked example below), or a cascade's own dependent chain (§ Cascading resolution
above). When a player spends a reroll resource (Fortune, Resolve, or the Bargain) against one
staged step, `reroll` computes the **downstream set** — every step that `step_id` names, or anything
that in turn depends on it, transitively — from the `depends_on` edges cascading resolution
already records. Every step in the downstream set is discarded and freshly resolved, starting
from the rerolled step under the resource's own modifier (Resolve's `+20`, Fortune's plain
reroll at the same odds, the Bargain's plain reroll for 1 Taint). **Every step outside the
downstream set is untouched** — its roll data and mutations stand exactly as first staged,
whether or not it happens to sit later in the proposal.

A freshly-resolved step can itself cascade again, under cascading resolution's own rule — a
reroll that turns a failure into a success removes whatever mutation the failure implied; a
reroll that still fails may cross a threshold the original roll didn't, staging a new cascade
the same way `propose` would have the first time.

**The resource's own cost is itself a staged mutation on the reroll**, not a separate call —
Resolve/Fortune spent, or Taint gained for the Bargain, is added to the proposal alongside
whatever the re-resolved steps produce.

**`reroll` does not invalidate the proposal id.** The proposal stays open, revised in place —
only `commit` or `discard` (against the id, once the player is done spending resources against
it) ends it, exactly as before.

### A worked example: an independent branch survives a reroll elsewhere in the batch

Senna Vask, Taint `0`. Two unrelated Exposure sources in the same scene, proposed together as
step `0` (`eff. 35`) and step `1` (`eff. 45`), neither depending on the other. Real `d100`
draws, seeded `20260854`:

- Step `0`: roll **91** — fails. A minor Exposure source, Taint `+1` staged.
- Step `1`: roll **38** — succeeds. Nothing staged.

**`propose`** returns both as independent steps (`depends_on: []` for each) — one mutation
(step `0`'s Taint `+1`), one no-op (step `1`).

Senna's player spends **the Bargain** against step `0` specifically. `reroll(proposal_id,
step=0, resource=bargain)` computes the downstream set for step `0`: just itself — nothing
depends on it, and it depends on nothing. Step `1` is untouched. Rerolled at the same odds
(the Bargain grants a plain reroll): roll **39** — still fails against `eff. 35`. An honest
outcome — the reroll doesn't guarantee success.

**The revised proposal**: step `0`'s mutation is still Taint `+1` (from the new roll, which also
failed), *plus* the Bargain's own cost, Taint `+1` — Taint `+2` total from that branch. **Step
`1`'s own result (success, nothing staged) is exactly what `propose` first returned, untouched
by the reroll happening elsewhere in the same proposal.**

**Committing this proposal** applies Taint `+2` (from step `0`'s failed reroll and the Bargain's
cost) and nothing from step `1` — the same outcome step `1` would have committed to on its own,
confirming the independent branch was never at risk from a reroll it had nothing to do with.
