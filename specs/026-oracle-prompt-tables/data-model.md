# Data model: Oracle prompt tables

This feature is a design document plus rollable tables, not application code. There is no schema
beyond what `doc/design/07-tables.md` already fixes for every family; this file names the entities
the document introduces and how they map onto that shared row schema.

## Entities

### Prompt family (concept, not a stored entity)

A named category of GM invention the engine constrains with a table instead of leaving to
unconstrained improvisation. Four, fixed: NPC objective, situation truth (why a scene isn't as
presented), thread turn, scene complication. Each produces a **generated content record** (below)
each time it is rolled.

### `oracle-prompt-<family>` tables (variants of the `oracles` family)

- **Keys**: `oracle-prompt-npc-objective`, `oracle-prompt-situation-truth`,
  `oracle-prompt-thread-turn`, `oracle-prompt-complication` — one per family, all variants of the
  `oracles` family entry in `doc/design/07-tables.md`'s index, alongside the sibling `oracle-answer`
  key.
- **Roll**: `1d100`, no modifier — reused from the resolution die, per `research.md`.
- **Uniqueness**: repeatable. Generating "wants the old order restored" for two different NPCs in
  two different scenes is ordinary; unlike transformations, nothing tracks which rows a given
  character already holds.
- **File**: none yet — like all five other table families, the tables exist only as rows in their
  design document (`doc/design/13-oracle-prompts.md`) until Stage 13's engine implementation reads
  them into `engine/tables/oracle-prompt-<family>.yaml`.

### Row (per `doc/design/07-tables.md`'s shared schema, plus one extra field)

| Field | Meaning |
|---|---|
| `range` | the `1d100` totals this row answers to |
| `effect` | the generative seed in a form the target structure can hold (e.g. a short fixed key or phrase naming the objective/turn/complication shape) |
| `description` | what the GM reads and narrates from |
| `checked` | the family's declared extra field: records that this row was read once grim, once comic, and passed both (`doc/design/07-tables.md`'s "a family may declare further fields" clause) |

Every row in every one of the four tables carries `checked`; a row that failed either reading does
not ship, so there is no "failed" value to record — its absence from the table *is* the record,
per the spec's SC-002 requiring the check to be recorded row by row.

### Generated content record (log entry)

Written to the beat log with the same provenance shape as any other table roll
(`doc/design/07-tables.md`'s versioning section; `doc/design/19-state.md`'s log-provenance shape), plus
the family's own fields:

```json
{"beat": 517, "verb": "roll", "engine": "0.3.1", "setting": "0.2.0",
 "table": "oracle-prompt-npc-objective", "subject": "the harbourmaster",
 "roll": 34, "effect": "protect_someone", "outcome": "wants the old order restored — someone she loves depends on it staying that way"}
```

- `table`: one of the four keys above.
- `subject`: what the roll is generating content *for* — an NPC's name, a thread's name, a scene's
  label — the same free-text identification discipline `doc/design/12-oracle-answers.md` already
  uses for `question`, since matching "the same subject asked again" is a GM judgment call, not
  automated string matching (mirrors that document's Recording section).
- `roll` and `effect`: the natural total and the row it landed on.
- `outcome`: the row's description, as narrated.

The result then lands in the structure it was generated for — a companion's objective field
(`doc/design/16-session.md`), a thread's state (`doc/design/18-campaign.md` /
`doc/design/28-arcs-and-beats.md`) — rather than in a second, parallel store; the beat log entry above
is the roll's provenance, not a duplicate of where the content now lives.

### Setting extension (declaration, not a stored entity)

A setting's `setting.yaml` may declare additional rows for a prompt table under `extend:`,
alongside its existing careers/talents/gear/creatures entries:

```yaml
overrides:
  extend: {oracle-prompt-npc-objective: setting/rules/tables/oracle-prompt-npc-objective-extra.yaml}
```

The setting's rows are appended above the engine's own highest range, each carrying the same row
schema (`range`, `effect`, `description`, `checked`) as the engine's rows, with the setting's file
supplying its own ranges contiguous with (not overlapping) the engine's. The `range` of the
combined table's now-last row stays open at the top, per `doc/design/07-tables.md`'s convention.
