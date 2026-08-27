# Wyrd — action resolution

How an action actually resolves against state: the base mechanism every mechanic in
[`03-rules.md`](03-rules.md) composes with. Not combat-specific — resolution, Exposure,
Terror tests, systems of power, advancement rolls all use the same shape.

This document specifies the **base** mechanism only: one roll, resolved once, nothing
cascading and nothing rerolled mid-resolution. Cascading resolution (a mutation that crosses a
threshold and spawns a further roll), partial reroll (a player spending Fortune/Resolve/the
Bargain against a proposed result), and Omen carryover across more than one roll are each their
own document, extending this one — see the parent epic's own children for the full set.

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

## What this document does not specify

- **Cascading resolution** — a mutation that itself crosses a threshold (a Taint gain crossing 3,
  a Trauma gain crossing 6) and spawns a further roll inside the same proposal, deterministically
  and re-derivably. A separate document, once specified.
- **Partial reroll** — a player spending Fortune, Resolve, or the Bargain against a proposed
  result, and which staged steps survive versus are discarded and re-resolved. A separate
  document, once specified.
- **Omen carryover** — a pending ±10 modifier from one roll applying to the actor's own next roll
  within the same proposal, and unwinding correctly if the roll that produced it is later
  discarded. A separate document, once specified.
