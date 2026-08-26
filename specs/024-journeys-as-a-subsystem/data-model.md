# Data model: Journeys as a subsystem

Design-document feature — this "data model" is the frontmatter shape `design/17-journeys.md`
will document in prose, following the same convention `15-arcs-and-beats.md` and
`03d-the-adversary.md` already use (a fenced YAML example, not a JSON Schema). No engine code
and no persisted state format changes; a journey is state the same way any other arc/beat is
(`design/06-state.md` — chronicle state is entities).

## Journey (a `scale: journey` arc)

| Field | Type | Required | Notes |
|---|---|---|---|
| `id`, `type: arc`, `scale: journey` | — | yes | Ordinary arc identity fields, per `15-arcs-and-beats.md`. |
| `name` | string | yes | The route's name — "the road to \<place\>", GM's choice. |
| `from`, `to` | entity ref | yes | Places (`14-entities.md`), the journey's endpoints. |
| `pace` | string | no | What one leg covers (distance or time), e.g. "one day's travel". Default: the GM narrates the whole journey as a single summarised leg — no pace needed for a journey with no structure below the whole. |
| `hazard_rating` | integer 0-9 | no | Per-leg trigger chance is `rating × 10` on `d100`, mirroring Threat imminence (`05-campaign.md`). Default 0 — no hazard rolls. |
| `hazards` | table | no | Entries as `{roll_range, name, skill, difficulty, effect}` — the same shape a Threat's `effects:` table already uses. Default: empty; a triggered roll with no matching entry is a no-op. |
| `roles` | list of strings | no | Named travel-role slots (e.g. navigator, forager, lookout). No engine-defined effect — see research.md. Default: empty. |
| `children` | list of legs | yes | The journey's legs, in order — ordinary arc/beat containment. |

## Leg (an arc or beat, child of a journey)

Carries every field an ordinary arc/beat already carries (`15-arcs-and-beats.md`), plus:

| Field | Type | Required | Notes |
|---|---|---|---|
| `mode` | `played` \| `summarised` | yes (already required on beats) | Author-declared, per the 2026-08-26 clarification — never chosen at runtime. |
| Hazard roll | — | n/a | Not a stored field — resolved live: `d100` against the parent journey's `hazard_rating × 10` when the leg is reached. A trigger consults the parent's `hazards` table and resolves through the core roll (`03-rules.md`). |

## State touched at resolution

No new state shape. A journey's consequences land in the same places any beat's do
(`06-state.md`): elapsed time via `wyrd advance-time` (summarised legs, or the whole journey's
span on early termination — FR-007), Standing/coin/condition via the material economy
(ADR 0033), threads via the ordinary `emits_threads`/`requires_threads` exit/entry fields.

## Relationships

```
Journey (arc, scale: journey)
  ├─ from/to → place entities (14-entities.md)
  ├─ hazard_rating → per-leg d100 roll (mirrors Threat imminence, 05-campaign.md)
  └─ children[] → Leg (arc or beat)
                    ├─ mode: played      → resolves as an ordinary beat
                    └─ mode: summarised  → resolves via wyrd advance-time (05-campaign.md)
```
