# Data model: Adventure and campaign generation

Two transient shapes (never persisted on their own) and one additive change to an existing
persisted entity. No new entity type is introduced — see spec.md's Assumptions.

## GenerationRequest (transient — exists only for one generation call)

| Field | Type | Required | Notes |
|---|---|---|---|
| `scale` | enum: `beat`, `arc`, `campaign-spine` | always | `campaign-spine` is a request-shape alias for "`arc` with no `parent`, `scale: campaign`" (FR-002/FR-003) |
| `mode` | enum: `live-play`, `setting-authoring` | always | FR-003. Governs which of the two state blocks below is present — never both, never neither |
| `setting_ref` | id/path to a setting | always | the setting this request is grounded in |
| `tone_contract` | the setting's `tone:` block (`01-principles.md`) | always | read identically in both modes; drives FR-008/FR-010 |
| `written_for` | integer, party size | required for `beat`/`arc`; absent for `campaign-spine` in `setting-authoring` mode | the scaling input beats already carry (`18-arcs-and-beats.md`) |
| **`live-play` state** (present only when `mode: live-play`) | | | |
| `threads` | list of `{id, heat}` | required, may be empty only if the request also supplies no threat (see spec Edge Cases: a request with neither MUST fail) | the chronicle's live threads (`19-campaign.md`) |
| `threat_state` | list of `{entity_id, imminence, clues_progress}` | optional | active threats in scope |
| `danger_rating` | number | required | current chronicle danger rating, feeds FR-009 |
| `era` | id | required | current era, for register consistency |
| **`setting-authoring` state** (present only when `mode: setting-authoring`) | | | |
| `voice` | the setting's `voice.md` content/register | required | |
| `existing_entities` | list of entity refs, possibly empty | required (may be empty list) | everything already in `entities/` — binding on consistency checks (spec Edge Cases) |
| `invention_permitted` | boolean, must be `true` | required | the create-setting Phase 1 Q3 grant, checked before any generation step runs (FR-005, FR-015) |

**Validation rules**:
- `mode: live-play` request MUST NOT carry `voice`, `existing_entities`, or
  `invention_permitted` — those are `setting-authoring`-only fields (FR-006: the modes differ
  only in available state).
- `mode: setting-authoring` request MUST NOT carry `threads`, `threat_state`, or `danger_rating`
  — there is no chronicle yet (FR-005).
- `mode: setting-authoring` with `invention_permitted` absent or `false` MUST be rejected before
  any generation step runs, with a structured reason (FR-005, FR-015, User Story 2's Edge Case).
- A `live-play` request supplying neither `threads` nor `threat_state` MUST be rejected — nothing
  to ground generation in (spec Edge Cases, first bullet).

## GenerationResult (transient — held only until accepted or discarded)

| Field | Type | Notes |
|---|---|---|
| `candidate` | a `beat` or `arc` entity body, shaped exactly like the entity it would become | see "Committed entity" below for the one schema addition |
| `checks` | list of `{rule: FR-007..FR-011, outcome: pass\|reject\|narrowed, detail}` | makes a rejection explainable (spec.md Key Entities) rather than silent |
| `consumed` | list of thread/threat ids the candidate's entry/exit conditions reference | used verbatim as `sources.generated.consumed` on acceptance (FR-012) |

**Validation rules**:
- A `GenerationResult` with any `checks` entry at `outcome: reject` MUST NOT be offered for
  acceptance (FR-007–FR-011 are gates, not warnings).
- An `outcome: narrowed` entry (FR-010's scale_drift narrowing path) MUST be surfaced to the
  caller in the result, never silently applied and hidden.
- A `GenerationResult` that is discarded (never accepted) MUST leave no trace in persisted state
  (FR-015) — this is a property of the *implementation*, not a field, but is recorded here since
  it constrains how an implementing feature may be built (no write-then-rollback pattern; no
  write until acceptance).

## Committed entity (persisted — an ordinary `arc`/`beat` entity, plus one additive field)

Reuses the existing `arc`/`beat` entity schema (`25-entities.md`, `18-arcs-and-beats.md`) in
full, with exactly one additive change:

| Field | Change |
|---|---|
| `sources` | For a converted beat/arc, unchanged: `[{work, pages, licence}]` (existing shape). For a **generated** beat/arc, a new alternative shape: `{generated: true, mode: live-play\|setting-authoring, consumed: [<thread/threat ids>]}` — additive alternative, not a replacement of the existing shape (FR-012, SC-003) |
| `status` | Unchanged vocabulary (`stub`/`drafted`/`complete`); a generated-and-accepted beat/arc always lands at `drafted` (FR-012) |
| body prose | Unchanged field; per-claim provenance labels (e.g. "invented, per Phase 1 Q3") live inline here as a writing convention, not a new field (Clarifications, research.md) |

**State transitions**: identical to an authored entity's existing `stub → drafted → complete`
lifecycle (`18-arcs-and-beats.md`). A generated entity enters at `drafted` (skipping `stub`, since
it was never an unconverted stub) and, once played, reaches `complete` and is thereafter immutable
in the same way any played content is (FR-014, `29-evolution.md`'s "the past is a fact").

**Relationships**: accepting a generated beat/arc mutates the chronicle's existing `threads:` list
(consuming/emitting) and existing threat entities' `clues`/`imminence` fields through the same
write path authored play already uses (FR-013) — no new relationship type, no new join table, no
parallel ledger.
