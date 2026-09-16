# Phase 0 research: Adventure and campaign generation

No `NEEDS CLARIFICATION` markers remain in `plan.md`'s Technical Context — every field there
resolves to "N/A, no code in this feature" or "inherits the engine's existing constraint," both
settled by the issue's own Definition of Done rather than needing investigation. This document
instead records the design decisions that *would* otherwise have needed a `NEEDS CLARIFICATION`
marker, and why each resolves to a specific answer from the existing design documents rather than
an open question.

## Decision: campaign spine is a request-shape alias, not a fourth entity scale

**Decision**: A `campaign-spine`-scale request is specified as "an `arc` entity request with no
`parent` and `scale: campaign`" (spec.md FR-002/FR-003), reusing the arc scale-label vocabulary
`25-entities.md` already recognises (`campaign | adventure | scenario | situation`).

**Rationale**: [ADR 0003](../../docs/adr/0003-recursive-containment.md) already rejected a fixed
ladder of structural types precisely because it forces an arbitrary decision about which rung
something occupies. Inventing a fourth structural `scale` (or a parallel entity type) for
"campaign spine" would be exactly the mistake that ADR closed — the containment model already has
everything needed: `parent` absence marks top-level, and `campaign` is already a valid arc scale
label.

**Alternatives considered**:
- A dedicated `campaign_spine` entity type — rejected outright: reintroduces the fixed-ladder
  problem ADR 0003 already settled, and would need its own schema maintained in parallel to `arc`.
- A new `scale: campaign-spine` label distinct from `scale: campaign` — rejected: no design
  document draws a line between "a campaign" and "a campaign spine" as different things; the
  issue's own title uses "campaign" language, and `19-campaign.md`'s "Top-level arcs" section
  already describes exactly the arcs a campaign spine would be.

## Decision: the two invocation modes share one request contract, distinguished by available state

**Decision**: `live-play` and `setting-authoring` are values of one `mode` field (spec.md FR-003),
not two separate request/response contracts. Anti-inflation rules (FR-007–FR-011) apply
identically regardless of mode; only which state exists to ground a result differs (FR-004 vs
FR-005), per the issue's own comment thread.

**Rationale**: the issue comment is explicit that the two invocations "differ in what state exists
to consume... not in the anti-inflation/grounding rules that bind the output either way." Two
independent contracts would duplicate FR-007–FR-011 (five checkable rules) in two places, exactly
the two-lists-of-the-same-thing drift `CLAUDE.md` warns against for backlog and documentation
alike, generalised here to a data contract.

**Alternatives considered**:
- A separate `SettingAuthoringGenerationRequest` and `LivePlayGenerationRequest` type — rejected:
  duplicates the anti-inflation rule set, and risks the two drifting the way `CLAUDE.md`'s fault
  class 3 (two documents describing one thing differently) already names as a recurring failure
  here.
- Inferring the mode from whether a chronicle reference is present, rather than an explicit field
  — rejected: an explicit `mode` plus FR-005's explicit `invention_permitted: true` requirement
  makes the setting-authoring path's permission check a simple field-presence test (FR-015's
  reject-before-generating path), rather than requiring the caller to prove chronicle-absence
  negatively.

## Decision: per-claim provenance is a prose convention, not a new structured field

**Decision** (already recorded in spec.md's Clarifications, restated here as the researched
choice): `invented, per Phase 1 Q3` and similar per-claim labels live inline in the generated
body prose, the same convention `create-setting`'s `SKILL.md` already establishes for setting
authoring, rather than a new structured field on every claim.

**Rationale**: the commit-back path's own acceptance criterion (issue #99, "does not fork state
from the threat/thread machinery") generalises naturally to "does not introduce new machinery
anywhere it doesn't have to." A structured per-claim provenance list would be new schema surface
with no existing consumer; the prose convention already exists, is already how a human or GM
session reads generated content's grounding, and keeps SC-003's "exactly one new field"
(`sources.generated`) true.

**Alternatives considered**:
- A `claims:` array on `sources:`, each entry `{text, provenance}` — rejected: no other Wyrd
  entity carries claim-level structured provenance (a converted beat's `sources:` records
  document-level provenance, not per-sentence), so this would be a new pattern introduced for one
  feature rather than reuse of an existing one.

## Decision: model tiers map onto the existing three-tier table without a new tier

**Decision**: every generation step (thread/threat selection, structural computation, hook/pacing
assembly, prose/invention) maps onto one of the three tiers `27-tooling.md` §5 already defines
(no-model, Haiku, capable) — spec.md FR-016–FR-020.

**Rationale**: `27-tooling.md` §5 states its target precisely: "the capable model's own job
shrinks to exactly what genuinely needs it... and nothing else leaks onto it," verified "by
auditing the CLI surface... not by running a model at all." Generation is new surface being added
to that same audited catalogue, so it must be classified against the same table rather than
inventing a generation-specific tiering scheme.

**Alternatives considered**:
- A dedicated "structure model" tier between no-model and Haiku for generation's hook-matching
  step — rejected: `27-tooling.md` §5 already names "matching arc hooks against live threads" as
  a named Haiku-tier example, so the work already has a tier; adding a new one would fragment a
  table this project has already gone to some length to keep authoritative and singular.
