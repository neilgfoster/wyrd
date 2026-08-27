# Wyrd — action resolution

How an action actually resolves against state: the base mechanism every mechanic in
[`03-rules.md`](03-rules.md) composes with. Not combat-specific — resolution, Exposure,
Terror tests, systems of power, advancement rolls all use the same shape.

This document covers the propose/commit/discard mechanism and cascading resolution (a mutation
that crosses a threshold and spawns a further roll, inside the same proposal). **Partial reroll**
(a player spending Fortune/Resolve/the Bargain against a proposed result) and **Omen carryover**
across more than one roll are not yet specified — see the parent epic's remaining children for
those, extending this same document once landed rather than fragmenting into separate ones for
what is genuinely one mechanism.

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
mutation that crossed it, which depends on the roll that produced that mutation. Nothing here
uses that dependency yet; it is what the dependency-graph partial-reroll mechanism (a later,
dependent feature) consumes to work out what a mid-batch reroll invalidates.

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
