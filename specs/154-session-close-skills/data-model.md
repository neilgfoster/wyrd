# Data Model: Character, downtime and session-close skills

No new persisted schema is introduced. This feature reads and writes fields that already exist
in `pc.yaml`/`chronicle.yaml` (docs/design/22-state.md), via existing or newly-wired verbs.

## Entities touched

### Player character (`pc.yaml`)

| Field | Read by | Written by |
|---|---|---|
| `advances_unspent` | character skill (view), `spend-advance` | `spend-advance` |
| `standing` | downtime skill (Upkeep) | new `downtime --action upkeep` verb |
| `coin` | downtime skill (Upkeep) | new `downtime --action upkeep` verb |
| `stamina`, `stamina_max` | downtime skill (Rest), Rally | new `downtime --action rest` verb, new `rally` verb |
| `strain` | Rally | new `rally` verb |
| `wounds[]` | downtime skill (Mend) | new `downtime --action mend` verb |
| `career`, skill percentages | character skill (spend) | `spend-advance` (unchanged) |

No new field is added to `pc.yaml`'s schema. The `undertaking` chosen for a downtime period is
not persisted as chronicle state in this feature (per research.md, the state-machine gate is out
of scope) — it is a value the skill's own prose carries for the duration of one invocation.

### Chronicle (`chronicle.yaml`, `recap.md`)

Unchanged by this feature. The end-session skill (part 2) calls the existing `save` and `recap`
verbs exactly as #402/PR #407 defined them.

## New verb request/response shapes

See [contracts/cli-verbs.md](contracts/cli-verbs.md) for the full `downtime` and `rally` verb
contracts.
