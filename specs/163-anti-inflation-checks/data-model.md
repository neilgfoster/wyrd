# Data model: Anti-inflation checks for generated content

One transient output shape (never persisted on its own) and one additive, check-only input field
on the existing candidate shape #420 defines. No change to `GenerationRequest`'s own fields.

## Check entry (transient — one per rule, per check call)

| Field | Type | Notes |
|---|---|---|
| `rule` | enum: `FR-007`, `FR-008`, `FR-009`, `FR-010`, `FR-011` | which anti-inflation rule this entry reports on |
| `outcome` | enum: `pass`, `reject`, `narrowed` | `narrowed` is FR-010-only (data-model.md's `GenerationResult.checks` shape, specs/161) |
| `detail` | string | names the specific field/value responsible for a non-`pass` outcome; empty string permitted only for `pass` |

Matches `specs/161-adventure-and-campaign-generation/data-model.md`'s `GenerationResult.checks`
list-entry shape exactly — this feature produces exactly the values that field's list holds.

## Candidate — the additive `threat_updates` field

The candidate a check function receives is otherwise exactly `GenerationResult.candidate` (a
`beat`/`arc` entity body, per specs/161's data-model.md). This feature adds one field to the
*candidate contract these checks read*, not to the persisted entity schema
(`18-arcs-and-beats.md`): the pipeline feature that assembles a real candidate is expected to
populate it before calling these checks (research.md's "the candidate carries a `threat_updates`
field the entity schema doesn't define" decision).

| Field | Type | Notes |
|---|---|---|
| `threat_updates` | list of `{entity_id, imminence_delta, ambient_add, connection}` | one entry per threat the candidate's exit conditions would change or introduce |
| `threat_updates[].entity_id` | id, or `None` | `None` marks a newly introduced threat; otherwise the existing threat entity being modified |
| `threat_updates[].imminence_delta` | integer | how much the entry raises (or lowers) that threat's `imminence`; `0` for no change |
| `threat_updates[].ambient_add` | list of strings | new `ambient` cost entries the entry would add; `[]` for no addition |
| `threat_updates[].connection` | string, or `None` | required (non-empty) when `entity_id` is `None` — `19-campaign.md`'s "a threat with no connection is scenery" |
| `prophecy_claim` | enum: `none`, `destiny`, `hidden_bloodline`, `prewritten_fate` | default `none`; what FR-008's "any field read by the prophecy tone value" check reads |
| `danger` | integer | the candidate's own stated danger value (FR-009) — already part of the existing `beat`/`arc` schema |
| `named_entities` | list of strings | every character/faction/place name the candidate's body prose names (FR-007) — already-known entities and, in `setting-authoring` mode, entities labelled `invented, per Phase 1 Q3`, are not excluded from this list; the check itself tells them apart |
| `coincidences` | list of `{claim, supported_by}` | every entry/exit condition the candidate's text attributes to chance (FR-011); `supported_by` is the id of the thread/threat/existing-entity the request's own state already grounds it in, or `None` |

**Validation rules**:
- A `threat_updates` entry with `entity_id: None` and an empty/absent `connection` cannot pass
  FR-010 under `scale_drift: suppressed` — it is always `reject` (a new, connectionless threat
  cannot be narrowed into a connected one without inventing the connection itself).
- `prophecy_claim` and `known_to_player` (an existing field on whichever entity a `threat_updates`
  entry targets) are independent fields; either alone can trigger FR-008 under `prophecy:
  forbidden` (spec.md Assumptions).

## Check-run inputs beyond the candidate

Two of the five checks need data #420's `GenerationRequest` does not itself carry (spec.md
Assumptions), so the aggregator and the individual check functions take it as an explicit,
separate parameter rather than reading it off the request:

| Parameter | Type | Used by | Notes |
|---|---|---|---|
| `known_entities` | list of entity ids/names | FR-007 | the setting's `entities/` store — for `setting-authoring` mode this is exactly `request['existing_entities']`; for `live-play` it has no request-object equivalent, so the caller supplies it directly |

## Relationships

- A check entry's `rule` is the only link back to specs/161's FR text — no other cross-reference
  field is introduced.
- `run_checks` (the aggregator) produces the full `checks:` list a `GenerationResult` (#420)
  carries; this feature does not construct a `GenerationResult` itself (`generation.py`'s
  `new_result` already does that, unchanged) — the caller is expected to pass `run_checks`'s
  output as `new_result`'s `checks` argument.
