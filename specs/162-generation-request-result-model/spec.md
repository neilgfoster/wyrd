# Feature Specification: Generation request/result data model and mode validation

**Feature Branch**: `162-generation-request-result-model`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Generation request/result data model and mode validation (issue
#420) -- implement specs/161-adventure-and-campaign-generation's FR-001 through FR-006: a
GenerationRequest shape shared by beat/arc/campaign-spine scales, a GenerationResult shape
carrying a checks: report, and mode validation (live-play vs setting-authoring), as pure,
testable functions. No persistence, no anti-inflation checks (FR-007-011), no commit-back
(FR-012-015), no actual content generation (FR-016-020) -- those are separate, dependent sibling
features (#421, #422, #423)."

## User Scenarios & Testing *(mandatory)*

<!--
  This is a foundation layer with no direct human user: its "user" is the code that will call
  into it from the three sibling features once they land, and the setting/chronicle authors
  whose requests those callers construct. Each story below is a distinct shape the constructor
  and validator must accept or reject correctly, exercised directly by unit tests until a
  sibling feature wires a real caller.
-->

### User Story 1 - Construct and validate a request for any scale (Priority: P1)

A caller building a generation request for a beat, an arc, or a campaign spine needs one shape to
construct against, with validation that tells it exactly which field is missing for the scale and
mode it chose, before any generation work is attempted.

**Why this priority**: this is the foundation the other three features build on — without a
correctly validating request shape, nothing downstream (anti-inflation checks, commit-back,
generation itself) has a trustworthy input to work from.

**Independent Test**: construct a `GenerationRequest` for each of the three scales with a required
field omitted; verify validation rejects each with a structured reason naming the missing field,
and accepts an otherwise-identical request with the field present.

**Acceptance Scenarios**:

1. **Given** a `beat`-scale request missing `written_for`, **When** it is validated, **Then**
   validation rejects it naming `written_for` as the missing required field.
2. **Given** a `campaign-spine`-scale request in `setting-authoring` mode with no `written_for`,
   **When** it is validated, **Then** validation accepts it — `written_for` is not required for
   this scale/mode combination.
3. **Given** a request with `scale: campaign-spine`, **When** it is validated, **Then** it is
   confirmed to be exactly an `arc`-shaped request with no `parent` and `scale: campaign` — never
   a fourth structural type.

---

### User Story 2 - Reject a live-play request with insufficient grounding (Priority: P2)

A caller assembling a `live-play`-mode request has a chronicle with no live threads and no active
threat. The request must be rejected before any generation step runs, rather than silently
proceeding to invent content ungrounded in the chronicle's own state.

**Why this priority**: this is the specific failure mode the spec's Edge Cases section calls out
by name — the second most important behaviour after the request shape itself validating
correctly, since a caller that doesn't get this rejection would otherwise degrade straight to
unconstrained invention.

**Independent Test**: construct a `live-play` request with empty `threads` and no `threat_state`;
verify validation rejects it with a structured reason. Construct one with at least one live
thread; verify it passes this check.

**Acceptance Scenarios**:

1. **Given** a `live-play` request with `threads: []` and no `threat_state`, **When** it is
   validated, **Then** it is rejected with a structured reason naming the absence of any
   grounding state.
2. **Given** the same request but with one live thread added, **When** it is validated, **Then**
   this check passes (other required fields being present).

---

### User Story 3 - Reject a setting-authoring request missing the Q3 grant (Priority: P2)

A caller assembling a `setting-authoring`-mode request has not recorded `invention_permitted` as
`true`. The request must be rejected before any generation step runs, naming the missing
permission, so the caller can surface exactly why nothing was generated.

**Why this priority**: this is the spec's explicit, named rejection contract (FR-005, FR-015) —
getting it wrong would let unpermitted invention through, which is the exact failure the Q3 gate
exists to prevent.

**Independent Test**: construct a `setting-authoring` request with `invention_permitted` absent,
then with it `false`, then with it `true`; verify only the last one passes this check.

**Acceptance Scenarios**:

1. **Given** a `setting-authoring` request with no `invention_permitted` field, **When** it is
   validated, **Then** it is rejected with a structured reason naming the missing permission.
2. **Given** the same request with `invention_permitted: false`, **When** it is validated,
   **Then** it is rejected the same way.
3. **Given** the same request with `invention_permitted: true` and every other required field
   present, **When** it is validated, **Then** this check passes.

### Edge Cases

- What happens when a request carries fields belonging to the *other* mode (e.g. a `live-play`
  request that also sets `voice` or `invention_permitted`)? Validation MUST reject it — FR-006
  requires the two modes to differ only in which state exists, so a request straddling both is
  malformed, not merely redundant.
- What happens when `scale` is `beat` or `arc` (not `campaign-spine`) but `written_for` is
  omitted? Validation MUST reject it — `written_for` is required for `beat` and `arc` regardless
  of mode (FR-003).
- What happens when a `campaign-spine`-scale request is made in `live-play` mode? Per spec.md's
  own Edge Cases, this behaves as an ordinary top-level `arc`-scale, `live-play` request —
  `written_for` and the `live-play` state block are both required exactly as they would be for
  any other `live-play` `arc` request; the `setting-authoring`-only exemption for `written_for`
  never applies here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide one `GenerationRequest` shape shared by all three named
  scales (`beat`, `arc`, `campaign-spine`), varying only in which fields are required — never
  three independent shapes.
- **FR-002**: The system MUST treat a `campaign-spine`-scale request as an alias for "an `arc`
  request with no `parent` and `scale: campaign`," and MUST provide a validation function that
  confirms this mapping explicitly rather than accepting `campaign-spine` as a fourth structural
  type.
- **FR-003**: The system MUST validate, for every request, that `scale`, `mode`, `setting_ref`,
  and `tone_contract` are present, and that `written_for` is present for `beat`/`arc` scale and
  for a `campaign-spine` request made in `live-play` mode, but MAY be absent for a
  `campaign-spine` request made in `setting-authoring` mode.
- **FR-004**: The system MUST validate that a `live-play`-mode request carries `threads`,
  `danger_rating`, and `era`, and that at least one of `threads`/`threat_state` is non-empty,
  rejecting the request with a structured reason otherwise.
- **FR-005**: The system MUST validate that a `setting-authoring`-mode request carries `voice`,
  `existing_entities`, and `invention_permitted: true`; a request where `invention_permitted` is
  absent or `false` MUST be rejected with a structured reason naming the missing permission,
  before any generation step would run.
- **FR-006**: The system MUST validate that a request carries exactly the state fields belonging
  to its own `mode` — a `live-play` request MUST NOT also carry `voice`, `existing_entities`, or
  `invention_permitted`, and a `setting-authoring` request MUST NOT also carry `threads`,
  `threat_state`, or `danger_rating`; a request violating this MUST be rejected. This is the
  boundary FR-006 (of specs/161) draws: the two modes differ only in available state, never in
  which downstream rule would apply to the output — a claim this feature's own tests assert
  directly, even though the rules themselves (FR-007-011 of specs/161) are out of scope here.
- **FR-007**: The system MUST provide a `GenerationResult` shape carrying a `candidate` field (an
  unaccepted beat/arc body), a `checks` field (a list of rule/outcome/detail entries), and a
  `consumed` field (thread/threat ids referenced) — matching data-model.md's shape exactly. This
  feature only defines the shape; populating `checks` with real anti-inflation outcomes is out of
  scope (FR-007-011 of specs/161).
- **FR-008**: Every rejection produced by this feature's validation functions MUST be structured
  data naming which specific rule/field failed, never a bare exception or an unexplained boolean.

### Key Entities *(include if feature involves data)*

- **GenerationRequest**: the input contract for one generation call — `scale`, `mode`,
  `setting_ref`, `tone_contract`, `written_for` (conditionally required), plus the mode-specific
  state block (`live-play`'s `threads`/`threat_state`/`danger_rating`/`era`, or
  `setting-authoring`'s `voice`/`existing_entities`/`invention_permitted`). Transient — never
  persisted on its own.
- **GenerationResult**: an unaccepted candidate beat/arc body plus a `checks` report and a
  `consumed` list of referenced thread/threat ids. Transient — held only until a sibling feature
  implements acceptance or discard.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every one of the three named scales, constructing a `GenerationRequest` with any
  single required field missing is rejected, and constructing one with every required field
  present for that scale/mode combination is accepted — verifiable by a table-driven test
  covering every scale/mode/field combination in FR-003 through FR-006.
- **SC-002**: A `campaign-spine`-scale request is confirmed, by a dedicated validation function,
  to be structurally identical to an `arc` request with no `parent` and `scale: campaign` — never
  treated as a fourth type anywhere in the implementation.
- **SC-003**: A `setting-authoring`-mode request without `invention_permitted: true` is rejected
  in 100% of tested cases, with zero code path in this feature that could construct a valid
  result from such a request.
- **SC-004**: A test explicitly asserts that the only difference between a valid `live-play`
  request and a valid `setting-authoring` request is which state fields are present — not any
  divergence in which downstream rule would later apply (FR-006's own invariant, verified here
  even though the rules themselves are implemented by a sibling feature).

## Assumptions

- This feature implements FR-001 through FR-006 of specs/161-adventure-and-campaign-generation's
  spec.md only. FR-007-011 (anti-inflation checks), FR-012-015 (commit-back), and FR-016-020
  (the generation pipeline and model tiers) are separate, dependent sibling features (#421, #422,
  #423) and are explicitly out of scope here.
- No persistence is introduced: both shapes are plain in-memory data structures with pure
  validation functions, matching data-model.md's "transient, never persisted on its own" framing.
- `GenerationResult.checks` exists as a field in this feature's shape but is never populated with
  real rule outcomes here — a sibling feature (#421) is what will compute real `checks` entries.
- The engine is setting-agnostic: no setting or system name appears in the shape or its
  validation logic, per this repo's own working rules.
- `setting_ref` and `tone_contract` are treated as opaque values this feature only checks for
  presence — validating their internal shape belongs to whichever existing code already owns
  `tone:` blocks and setting references, not to this feature.
