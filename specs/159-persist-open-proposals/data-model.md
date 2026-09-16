# Phase 1 Data Model: Proposals survive across separate CLI invocations

## Persisted proposal record

One JSON file per open proposal, at `<proposals_dir>/<proposal_id>.json`
(`proposals_dir` defaults to `log/proposals/`, cwd-relative — research.md Decision 1).

```json
{
  "proposal_id": "p-3a91f0c218ab",
  "steps": [
    {
      "step_id": 0,
      "kind": "roll",
      "mechanic": "exposure",
      "roll": 86,
      "outcome": "fail",
      "depends_on": [],
      "mutations": [
        {"entity": "chronicle/entities/senna-vask.md", "field": "taint", "op": "+",
         "value": 3, "produced_by_step": 0}
      ],
      "inputs": {"actor": "chronicle/entities/senna-vask.md", "mechanic": "exposure", "...": "..."}
    }
  ],
  "mutations": [
    {"entity": "chronicle/entities/senna-vask.md", "field": "taint", "op": "+",
     "value": 3, "produced_by_step": 0}
  ]
}
```

- **`proposal_id`**: also the filename stem — carried inside the file too so a record is
  self-describing if ever inspected directly (`wyrd doctor`-style tooling, not in this feature's
  scope, but nothing about the shape prevents it later).
- **`steps`**: exactly the list `propose_batch`/`reroll` already build in memory today — every
  field already JSON-serializable (`_normalize_request` already stringifies `actor`/`target`
  before a step is ever built, per resolution.py:1294/1297). No new fields, no renamed fields —
  this is a direct `json.dumps` of the existing Python structure, not a new schema.
  `step["inputs"]` is `None` for a cascade-produced step (`transformation`, `weapon-damage`,
  `armour`, `critical`) and the original request dict for a top-level step — unchanged from
  today's in-memory shape.
- **`mutations`**: the flattened `mutations` list, exactly as returned to a caller from
  `propose`/`propose_batch`/`reroll` today.
- **No `"open"` flag.** The file's existence *is* the open state (research.md Decision 1); `commit`
  and `discard` both end by deleting the file, which is what makes the id no longer resolve.

## State transitions

```
propose_batch(...)  ──creates──▶  <proposals_dir>/<id>.json  (open)
reroll(id, ...)      ──rewrites─▶  <proposals_dir>/<id>.json  (still open, revised in place)
commit(id)           ──deletes──▶  (gone — resolved)
discard(id)          ──deletes──▶  (gone — resolved)
commit(id) | discard(id), file absent  ──▶  ProposalError("no open proposal: <id>")
```

There is no "closed" state stored anywhere — a resolved proposal simply has no file, identically
to a proposal id that was never issued (Acceptance Scenario, User Story 3). This is a deliberate
simplification versus the in-memory version's `{"open": False}` tombstone, which existed only to
distinguish "committed already" from "never existed" for a marginally clearer error message that
the error text itself never actually differentiated.

## Relationship to existing entities

Not a new entity type under `entities:`/`overlay:` (docs/design/22-state.md). It participates in
none of that document's entity invariants (`id` uniqueness, `[[link]]` resolution, parent
cycles) — it is closer in kind to `log/`'s existing per-beat outcome records than to a character
or thread. `chronicle.yaml`'s `pending.rolled` field is unchanged in shape: still the bare
`proposal_id` string naming *which* file (if any) is open across a session boundary — this
feature is what makes that string resolvable to real content from a separate process, not a
change to what `pending.rolled` itself stores.
