# Feature Specification: Anti-inflation checks for generated content

**Feature Branch**: `163-anti-inflation-checks`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Anti-inflation checks for generated content (issue #421) -- five
deterministic, pure functions implementing specs/161-adventure-and-campaign-generation/spec.md's
FR-007 through FR-011, each evaluating a generated candidate (from #420's GenerationRequest/
GenerationResult shapes) and returning a checks: report entry."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A generated result is gated before it can be offered (Priority: P1)

Whoever calls the (not-yet-built) generation pipeline needs each of the five anti-inflation rules
run against a candidate before it is ever shown for acceptance, so that a rule violation is caught
mechanically rather than by a reviewer's judgment.

**Why this priority**: this is the entire point of the feature — without it, FR-007 through
FR-011 remain prose intentions with no checkable enforcement, and generation could silently drift.

**Independent Test**: call each check function directly against a hand-built `GenerationRequest`/
candidate pair and confirm it returns the correct `checks:` entry — no pipeline needed.

**Acceptance Scenarios**:

1. **Given** a candidate naming a character absent from the setting's entities, the request's
   threads/threat state, and not labelled as an authoring-time invention, **When** the
   entity-membership check runs, **Then** it returns a `reject` outcome naming that entity.
2. **Given** a candidate naming only entities already in the setting, or the request's live
   threads/threat state, **When** the entity-membership check runs, **Then** it returns `pass`.

---

### User Story 2 - A rejection is explainable, not silent (Priority: P1)

A caller reading a `checks:` report needs to know *which* rule failed and *why*, so a rejected
candidate can be revised or discarded with a reason a person can act on.

**Why this priority**: FR-007's issue text and the data model both require this; a bare
pass/reject boolean with no detail fails the spec's own acceptance criteria.

**Independent Test**: run any of the five checks against a failing candidate and confirm the
returned entry carries a non-empty, specific `detail` string alongside its `rule` and `outcome`.

**Acceptance Scenarios**:

1. **Given** a candidate that fails the danger-band check, **When** the check runs, **Then** the
   returned entry's `detail` states the candidate's danger value and the band it exceeded.

---

### User Story 3 - Scale-drift is narrowed or rejected, per the request's own tone (Priority: P2)

Under a suppressed-scale-drift tone contract, an over-escalated candidate needs either an outright
rejection or an automatic narrowing (its escalation reduced to what the contract permits) — which
of the two happens is decided by the request's own mode/tone_contract, not by chance, and either
outcome is visible in the report.

**Why this priority**: FR-010 explicitly requires both outcomes to exist and be distinguishable;
skipping the narrow path would silently collapse it into a plain reject/pass check.

**Independent Test**: run the scale-drift check against two candidates that violate it identically
except for the request field that decides reject vs. narrow, and confirm the two different
outcomes.

**Acceptance Scenarios**:

1. **Given** a `live-play` request under `scale_drift: suppressed` whose candidate raises an
   existing threat's `imminence` beyond what the contract permits, **When** the scale-drift check
   runs, **Then** it returns `narrowed`, and the entry's `detail` states the narrowed value.
2. **Given** the same tone contract and a candidate introducing a wholly new threat with no
   connection to the player or a companion, **When** the scale-drift check runs, **Then** it
   returns `reject` (a new, connectionless threat cannot be narrowed into a valid one).

---

### Edge Cases

- A `setting-authoring`-mode candidate naming a newly invented entity without the inline
  `invented, per Phase 1 Q3` label is rejected by the entity-membership check the same as an
  ungrounded entity in `live-play` mode — the label is what makes an invention legitimate, not the
  mode alone.
- A request whose `tone_contract.scale_drift` is `allowed` never triggers the scale-drift check's
  reject/narrow path — FR-010 binds only under `suppressed`.
- A candidate with no named entities, no threat/imminence/ambient changes, and no coincidence-
  dependent conditions passes all five checks trivially — the checks gate only what a candidate
  actually claims, not fields it doesn't touch.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a pure function implementing FR-007 (entity-membership):
  given a request's known-entity sources (setting `entities/`, `live-play` threads/threat state,
  or `setting-authoring` invention permission) and a candidate's named entities, it MUST return a
  `reject` outcome naming every entity absent from all three closed sources, or `pass` when every
  named entity is accounted for.
- **FR-002**: The system MUST provide a pure function implementing FR-008 (tone/prophecy): given a
  request's `tone_contract.prophecy` value and a candidate's `known_to_player`/prophecy-tone-read
  fields, it MUST return `reject` when a candidate sets a state that value forbids (closed
  vocabulary: `forbidden` | `rare` | `central`), or `pass` otherwise.
- **FR-003**: The system MUST provide a pure function implementing FR-009 (danger-band): given a
  request's `written_for` and `danger_rating`, and a candidate's `danger` value, it MUST return
  `reject` when the candidate's danger exceeds the band the engine's existing danger-scaling
  arithmetic computes for that `written_for`/`danger_rating` pair, or `pass` otherwise. This
  function MUST call the engine's existing danger-scaling arithmetic rather than recomputing an
  equivalent formula.
- **FR-004**: The system MUST provide a pure function implementing FR-010 (scale-drift): given a
  request's `tone_contract.scale_drift` and mode, and a candidate's threat-state changes
  (`imminence` deltas, `ambient` cost changes, newly introduced threats and their `connection`),
  it MUST, under `suppressed` only, return either `reject` or `narrowed` — never silently `pass` a
  violation — determined by whether the violating change can be reduced to a permitted value
  (`narrowed`) or cannot (a new threat with no connection: `reject`). Under `allowed`, it MUST
  return `pass` regardless of the same changes.
- **FR-005**: The system MUST provide a pure function implementing FR-011 (favourable coincidence):
  given a request's own supplied state (its `threads`/`threat_state` for `live-play`, or
  `existing_entities` for `setting-authoring`) and a candidate's entry/exit conditions, it MUST
  return `reject` when a condition depends on a favourable coincidence not already supported by
  that state, or `pass` otherwise.
- **FR-006**: Each of the five functions MUST return a result carrying exactly the fields the
  `checks:` report requires: which rule it evaluated (`FR-007`..`FR-011`), its outcome (`pass`,
  `reject`, or — FR-010 only — `narrowed`), and a `detail` string specific enough to explain any
  non-`pass` outcome without re-reading the candidate's prose.
- **FR-007**: Every function MUST be pure (no I/O, no mutation of its inputs, deterministic given
  the same inputs) and MUST NOT depend on any other of the five — each is independently callable
  and independently testable.
- **FR-008**: The system MUST provide one entry point that runs all five checks against a given
  request/candidate pair and returns the list of resulting entries in `FR-007..FR-011` order,
  matching the `checks:` field shape `GenerationResult` (from #420) carries — without itself
  performing any of the five checks' own logic (a thin aggregator, not a sixth check).

### Key Entities

- **Check entry**: one result of running a single anti-inflation rule against a candidate —
  `{rule, outcome, detail}` — matching the `checks:` list entry shape specs/161's data-model.md
  already defines for `GenerationResult`. Transient; never persisted on its own.
- **GenerationRequest / candidate**: the existing shapes #420 defines (`engine/wyrd/
  generation.py`). This feature reads them; it does not change their shape.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every one of the five checks is verifiable by a reviewer as a closed-vocabulary or
  arithmetic comparison against a named field or existing table — zero checks whose pass/fail
  depends on re-reading free-text prose (specs/161 SC-002, restated as this feature's own bar).
- **SC-002**: FR-009's danger-band check produces the identical banding numbers the engine's
  existing danger-scaling arithmetic already produces elsewhere for the same inputs — verifiable
  by a test asserting equality against that existing function's own output, not a separately
  hand-computed number.
- **SC-003**: FR-010's reject-vs-narrow choice is deterministic and covered by tests exercising
  both outcomes from the same starting violation, varying only the field that decides between
  them.
- **SC-004**: Every non-`pass` check entry a reviewer inspects carries a `detail` string naming
  the specific field/value that caused it — zero rejections reporting only "failed" with no further
  detail.

## Assumptions

- The `GenerationRequest`/`GenerationResult`/candidate shapes are exactly as `engine/wyrd/
  generation.py` (#420) already defines and validates; this feature adds fields to neither.
- The candidate body's named entities, threat-state changes, and entry/exit conditions are read
  from plain fields on the candidate dict (matching the `arc`/`beat` entity schema
  `18-arcs-and-beats.md`/`25-entities.md` already define), not parsed out of free prose — FR-007's
  own text ("closed-list membership, not a judgment call") and FR-008's ("checkable... not by
  re-reading the prose") both rule out prose-parsing as this feature's job.
- FR-009's danger-scaling arithmetic reuse means calling `engine/wyrd/corpus_scenario.py`'s
  `scale_danger` directly — the existing wrapper issue #421 itself names — rather than reaching
  past it into `adversary.py`'s internals. A candidate this feature checks is generated fresh for
  the request's own `written_for`, so `party` and `written_for` are the same value at this call
  site and the scaling ratio is exactly `1`; `scale_danger` still runs the comparison through the
  one place the arithmetic lives (research.md).
- FR-010's "reduced to what the tone contract permits" (`narrowed`) applies only to a candidate
  modifying *existing* threat state (an imminence/ambient delta that can be capped); a *new*
  threat introduced with no connection cannot be narrowed into a connected one without inventing
  the connection itself, so it is always `reject`, per `19-campaign.md`'s "a threat with no
  connection is scenery."
- The commit-back path (FR-012-015) and the generation pipeline itself (FR-016-020) are out of
  scope, per issue #421 — these checks are called by, but do not themselves implement, either.
- FR-008's two named fields operationalize as: a candidate-level `prophecy_claim` (closed
  vocabulary: `none | destiny | hidden_bloodline | prewritten_fate`, default `none`) for "any
  field read by the prophecy tone value," and each `threat_updates` entry's `known_to_player`
  (the existing threat-block vocabulary: `none | rumoured | partial | understood`) for the named
  `known_to_player` field. Under `prophecy: forbidden`, a non-`none` `prophecy_claim`, or any
  `threat_updates` entry at `known_to_player: understood`, is rejected; `rare`/`central` never
  gate either field (rejection is `forbidden`'s own behaviour, not a general prophecy filter).
- `GenerationRequest` (#420) carries `existing_entities` only for `setting-authoring` mode — there
  is no equivalent field for `live-play` (its own state block is `threads`/`threat_state`/
  `danger_rating`/`era` only). FR-007(a)'s "already in the setting's `entities/` store" source is
  therefore supplied to `check_entity_membership` as its own explicit parameter (the caller's
  setting-entity lookup), not read off the request object, so this feature does not need to widen
  #420's already-merged request shape to give `live-play` a field it was deliberately not given.
- The existing `beat`/`arc` entity schema (`18-arcs-and-beats.md`) has no structured field for a
  proposed threat mutation (an imminence delta, an added `ambient` cost, or a new threat's
  `connection`) — `exit.changes` is free prose. Since FR-010 must be a structural, non-prose-
  reading check, this feature's candidate contract adds one additional, check-only field the
  entity schema itself does not carry: `threat_updates`, a list of
  `{entity_id: id | None, imminence_delta: int, ambient_add: list[str], connection: str | None}`
  entries (`entity_id: None` marks a newly introduced threat rather than a change to an existing
  one). This is scoped to the checks these functions run, not a change to the committed entity
  schema — the sibling commit-back feature (FR-012-015, out of scope here) decides how, or
  whether, `threat_updates` survives into the accepted entity's own fields.
