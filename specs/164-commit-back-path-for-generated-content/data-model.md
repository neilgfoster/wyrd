# Data model: Commit-back path for accepted generated content

One additive persisted field shape (`sources[].generated`), one new transient input field
(`thread_updates`, mirroring #421's existing `threat_updates` shape), and one transient output
shape (the commit outcome). No new entity type, no new top-level frontmatter field, no new
persistence file.

## `sources[]` entry — the generated variant (additive)

Applies only to an entry with `generated: true`; every other `sources[]` entry keeps the existing
`{work, pages, licence, path}` shape (`entity.py`'s `validate_source`) unchanged.

| Field | Type | Notes |
|---|---|---|
| `generated` | `true` (literal) | the gate: presence and truthiness select this shape over the authored one |
| `mode` | enum: `live-play`, `setting-authoring` | the `GenerationRequest.mode` (#420) the accepted result was produced under |
| `consumed` | list of strings | the thread/threat ids `GenerationResult.consumed` (#420) already carries — restated here as the entity's own provenance record, not recomputed |

**Validation rules**:
- All three fields required; no field outside `{generated, mode, consumed}` permitted (same
  closed-shape discipline `validate_source` already applies to the authored variant).
- `mode` must be one of `generation.py`'s own `MODES` tuple — this feature imports that constant
  rather than restating it.

## `thread_updates` — transient candidate input (new, symmetric with #421's `threat_updates`)

One entry per thread the candidate's exit conditions create or re-raise. Read only by
`accept_result`; never persisted as its own field — each entry is *consumed into* either a brand
new `thread` entity (via `thread.new_thread`) or an updated heat on an existing one (via
`thread.touch`), both already-persisted via the existing thread entity mechanism.

| Field | Type | Notes |
|---|---|---|
| `action` | enum: `new`, `touch` | which of `thread.py`'s two mutation functions this entry drives |
| `id` | string | the thread's id — for `action: new`, the id to create; for `action: touch`, the existing thread's id, looked up in the caller-supplied `live_threads` mapping |
| `opened` | `{year, month}` | required for `action: new` only — passed straight to `thread.new_thread` |
| `summary` | string | required for `action: new` only |
| `hooks` | list of strings | required for `action: new` only |
| `heat` | integer, 0-5 | optional for `action: new` (defaults as `thread.new_thread` itself does); ignored for `action: touch` (`thread.touch` always raises by exactly one) |

**Validation rules**:
- `action: touch` referencing an id absent from `live_threads` is a caller error (`ValueError`,
  matching `thread.py`'s own validation style) — not a silent no-op, since a candidate cannot
  legitimately reference a thread that does not exist.

## `threat_updates` — transient candidate input (reused unchanged from #421)

Exactly the shape `generation_checks.py`'s `check_scale_drift`/`check_favourable_coincidence`
already read (specs/163's data-model.md) — `{entity_id, imminence_delta, ambient_add,
connection}` — with two additional fields this feature's own consumption needs that #421's checks
never read (and so never validated): required only when `entity_id` is `None`.

| Field | Type | Notes |
|---|---|---|
| `entity_id` | id, or `None` | unchanged from #421: `None` marks a newly introduced threat |
| `imminence_delta` | integer | unchanged from #421 |
| `ambient_add` | list of strings | unchanged from #421 |
| `connection` | string, or `None` | unchanged from #421; required (non-empty) when `entity_id` is `None` |
| `target_entity_id` | id | **new here** — required when `entity_id` is `None`: which existing entity (in the caller-supplied `live_entities` mapping) the new threat block attaches to, passed as `threat.promote`'s `entity` argument |
| `objective` | string | **new here** — required when `entity_id` is `None`: passed straight to `threat.promote` |
| `imminence` | integer, > 0 | **new here** — required when `entity_id` is `None`: the new threat's starting `imminence` (`threat.promote` itself rejects `<= 0`) |

**Validation rules**:
- `entity_id: None` with any of `target_entity_id`/`objective`/`imminence` absent is a caller
  error (`ValueError`) — mirrors `threat.promote`'s own "rejects a threat whose imminence is not >
  0" discipline rather than silently defaulting a required field.
- `entity_id` naming an id absent from `live_entities` is a caller error (`ValueError`).

## Commit outcome (transient — the return value of `accept_result`/`reject_result`)

| Field | Type | Notes |
|---|---|---|
| `committed` | boolean | `True` only on a successful `accept_result` write |
| `path` | path, or `None` | the written entity file's path — present only when `committed` is `True` |
| `entity` | frontmatter dict, or `None` | the written entity's frontmatter — present only when `committed` is `True` |
| `reason` | string, or `None` | `"declined"` (from `reject_result`) or `"checks_failed"` (from `accept_result` on a non-passing result) — present only when `committed` is `False` |
| `detail` | list of strings | the `checks[].detail` of every `reject` entry, when `reason` is `"checks_failed"`; `["no checks were run"]` when `result['checks']` was empty |

## Relationships

- `sources[].generated.consumed` restates `GenerationResult.consumed` (#420) — no independent
  source of truth; `accept_result` copies it verbatim rather than recomputing from
  `thread_updates`/`threat_updates`.
- `thread_updates`/`threat_updates` are read only by `accept_result` — `reject_result` never
  inspects them, matching FR-005's "MUST NOT call any thread/threat mutation function" even if a
  caller mistakenly supplies them on a decline.
- A written entity's `sources[].generated` shape and the rest of its frontmatter are otherwise
  produced by the caller (entity id, type, name, setting, status, body, `entry`/`exit` blocks) —
  `accept_result` does not synthesize any field beyond `sources[].generated` and `status:
  drafted`, matching spec.md's Assumptions ("this feature does not decide *where* a generated
  beat is filed").
