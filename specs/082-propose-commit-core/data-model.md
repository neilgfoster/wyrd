# Phase 1 Data Model: Propose/commit/discard core

## Proposal

An unpersisted, process-local record produced by `propose` (`docs/design/31-action-resolution.md`).

| Field | Type | Notes |
|---|---|---|
| `proposal_id` | `str` | Opaque, unique per call to `propose`. |
| `roll` | `dict` | `{actor, mechanic, skill, target, roll, effective_pct, degrees, wyrd_die, outcome}` — the resolved roll, exactly as returned to the caller. |
| `mutations` | `list[dict]` | Zero or more staged mutations (see **Mutation** below); may be empty. |
| `open` | `bool` | `True` until `commit` or `discard` resolves this id; both set it `False` and it can never resolve again afterward. |

Not written to any durable store. Held only in `resolution.py`'s in-memory proposal store for
the lifetime of the process.

## Mutation

A staged, not-yet-applied change to one field of one entity's state.

| Field | Type | Notes |
|---|---|---|
| `entity` | `str` | Entity id (matches an id `state.py`/`character.py` can load). |
| `field` | `str` | Field name on that entity (e.g. `taint`). |
| `op` | `str` | One of `+`, `-`, `set`. |
| `value` | `int` | The operand. |

`commit` applies each mutation in order: `+`/`-` add/subtract `value` from the field's current
value (defaulting to `0` if absent); `set` writes `value` directly, overwriting whatever was
there.

## Mechanic (registry entry, not a persisted entity)

A closed vocabulary entry mapping a mechanic name to two functions:

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | e.g. `ordinary-test`, `exposure`. |
| `resolve` | `Callable` | Takes the looked-up actor/target state plus `propose`'s own kwargs (skill, difficulty, declaration_bonus, tier for `exposure`), returns roll data via `rules.py`'s primitives. |
| `mutate` | `Callable` | Takes the resolved roll data, returns the `mutations` list this outcome implies (possibly empty). |

This feature registers exactly two mechanics — `ordinary-test` (never implies a mutation) and
`exposure` (gains Taint on failure, per the design doc's worked examples) — sufficient for this
feature's own acceptance criteria. Adding a further mechanic later is additive: a new registry
entry, no change to `propose`/`commit`/`discard` themselves.

## Relationships

```text
propose(actor, mechanic, skill, target?, difficulty?, declaration_bonus?)
  -> looks up actor (+ target) state via state.py/character.py
  -> resolves via rules.py, using the named mechanic's `resolve`
  -> computes mutations via the mechanic's `mutate`
  -> stores a Proposal {proposal_id, roll, mutations, open: True} in the in-memory store
  -> returns {proposal_id, roll, mutations} (no `open` field in the response — internal only)

commit(proposal_id)
  -> looks up the Proposal; error if missing or open=False
  -> applies every Mutation to the named entity's state via state.py's atomic write
  -> sets Proposal.open = False

discard(proposal_id)
  -> looks up the Proposal; error if missing or open=False
  -> writes nothing
  -> sets Proposal.open = False
```
