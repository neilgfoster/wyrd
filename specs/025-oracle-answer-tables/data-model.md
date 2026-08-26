# Data model: Oracle answer tables

This feature is a design document plus a data table, not application code. There is no schema
beyond what `design/03a-tables.md` already fixes for every family; this file names the entities the
document introduces and how they map onto that shared row schema.

## Entities

### Oracle (concept, not a stored entity)

The GM procedure of rolling rather than inventing an answer to an unsettled question. Has no
on-disk representation of its own; it produces an **oracle roll record** (below) each time it is
used.

### `oracle-answer` table (the family)

- **Key**: `oracle-answer` (single table, per `design/03a-tables.md`'s naming convention — no
  variant suffix, since the family holds one table shared across all bands).
- **Roll**: `1d100`, no modifier (the modifier is expressed as the GM's choice of likelihood band,
  which selects which of five row sets to read — see below — not as an arithmetic modifier added to
  the roll).
- **Uniqueness**: repeatable — the same question, asked twice as two separate events, may resolve
  differently, and re-rolling a stored answer is never done (§ Recording).
- **File**: none yet — like the four already-defined families, the table exists only as the rows
  in its design document (`design/03a-5-oracle-answers.md`) until the engine implementation
  (Stage 13) reads it into `engine/tables/oracle-answer.yaml`, per `design/03a-tables.md`'s naming
  convention for where that file will live.

### Row (per `design/03a-tables.md`'s shared schema, plus one extra field)

| Field | Meaning |
|---|---|
| `range` | the `1d100` totals this row answers to, within one band |
| `effect` | one of the four fixed outcome keys: `exceptional_yes`, `yes`, `no`, `exceptional_no` |
| `description` | what the GM says at the table for that outcome |
| `band` | which of the five likelihood bands this row belongs to (the family's declared extra
  field, per `design/03a-tables.md`'s "a family may declare further fields" clause) |

Five bands × four rows = 20 rows total, each independently contiguous per band per the maths in
`research.md`.

### Likelihood band (enum, not a stored entity)

One of: `Near Certain`, `Likely`, `Even`, `Unlikely`, `Near Impossible`. Declared by the GM before
rolling; not read from state, not itself persisted except as a field on the oracle roll record
below.

### Oracle roll record (log entry)

Written to the beat log exactly like any other roll's provenance (`design/06-state.md`'s
log-provenance shape), with the family's own fields added:

```json
{"beat": 412, "verb": "oracle", "engine": "0.3.1", "setting": "0.2.0",
 "table": "oracle-answer", "question": "Is the gate barred from inside?",
 "band": "Even", "roll": 63, "outcome": "no", "wyrd": "none"}
```

- `table`: always `oracle-answer`.
- `question`: the GM's question, verbatim, as stated at the table — the key a later GM re-reads to
  recognise a repeat (`design/03a-tables.md`'s recording convention names no automated matching; a
  human/GM judgment call, per the spec's edge cases).
- `band`: the likelihood band declared for this roll.
- `roll`: the natural `1d100` total.
- `outcome`: one of the four row-effect keys.
- `wyrd`: `none` / `ill` / `fair`, read from the same roll's units digit exactly as
  `design/03-rules.md` §1 already defines it.

No new state file and no new frontmatter field on any entity — the record lives entirely in the
existing beat log.
