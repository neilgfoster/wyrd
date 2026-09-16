# Feature Specification: Generation Pipeline

**Feature Branch**: `165-generation-pipeline`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "The generation pipeline: model-tiered orchestration end to end (issue #423)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a beat/arc from an already-decided model-tier answer (Priority: P1)

A caller (a future `/wyrd-*` skill, or `create-setting`'s Q3 path) holds a well-formed
`GenerationRequest` (#420) plus the Haiku-tier and capable-model responses it has already
obtained, and needs one deterministic call sequence that turns those into a `GenerationResult`
ready for #421's checks and #422's commit-back path.

**Why this priority**: without this, #420-422 are three shapes and a checks/commit path with
nothing that actually produces a candidate to run them against — "generate an arc" does not work
end to end.

**Independent Test**: build a request, a live-thread/threat/entity pool, and canned Haiku/capable
responses; run the pipeline; confirm the resulting `GenerationResult` passes straight into
`generation_checks.run_checks` and `generation_commit.accept_result` with no field renaming or
reshaping.

**Acceptance Scenarios**:

1. **Given** a `live-play` request and a pool of live threads/threats, **When** the selection step
   runs, **Then** it returns the subset grounded in the request's own `threads`/`threat_state`
   with no model call.
2. **Given** a selection and the request's `danger_rating`/`written_for`, **When** the structural
   step runs, **Then** it returns `danger`, `scale_drift` bounds, `written_for` scaling, and
   `status`/`sources:` bookkeeping deterministically, with no model call.
3. **Given** the structural result and a Haiku-shaped response (entry/exit thread ids, a beat
   count, pacing labels), **When** the assembly step runs, **Then** it merges that response's
   entry/exit shape and pacing into the candidate without ever calling a model itself.
4. **Given** the assembled candidate and a capable model's prose plus the setting's known-entity
   list, **When** the prose step runs, **Then** it returns a finished `GenerationResult` whose
   `checks` field #421's `run_checks` populates unchanged.

### User Story 2 - Model tier is fixed by the step, not chosen per call (Priority: P2)

A reviewer (or a future maintainer) needs to confirm by inspection, not by reading every call
site, that no step in this pipeline can silently escalate its own tier at runtime.

**Why this priority**: `27-tooling.md` §5's whole discipline collapses if a step's tier becomes a
per-invocation judgment call rather than a property of the function itself.

**Independent Test**: inspect each step's signature — the no-model steps take no model-response
parameter at all; the Haiku-tier step's parameter is a structured mapping, never free text; the
capable-tier step is the only one accepting a free-form prose string.

**Acceptance Scenarios**:

1. **Given** the selection and structural functions, **When** their signatures are inspected,
   **Then** neither accepts any argument representing a model's response.
2. **Given** the Haiku-tier assembly function, **When** it is called with a plain string in place
   of its structured response argument, **Then** it raises rather than silently accepting prose.
3. **Given** the capable-tier prose function, **When** it is called, **Then** it is the only
   pipeline function whose model-response argument is an unstructured string.

### Edge Cases

- A request with no matching threads/threats at all (a wholly new thread being introduced): the
  selection step returns an empty grounding set rather than failing — #421's own checks (FR-011,
  FR-007) are what reject an unsupported claim later, not this step.
- A Haiku-tier response naming a thread id the selection step never selected: the assembly step
  passes it through as given — validating that a named id is actually grounded is #421's job
  (FR-007/FR-011), not this step's, matching the existing division of labour between generation
  and generation_checks.
- A `setting-authoring` request with `invention_permitted: true`: the prose step is the only place
  an invented name/detail may appear, and it must be labelled `invented` per FR-007's convention
  so #421's `check_entity_membership` recognizes it.
- `campaign-spine` scale: per #420's `is_campaign_spine_shape`, it is handled as an ordinary `arc`
  request with no `parent` — the pipeline does not special-case it beyond what `validate_request`
  already enforces.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-016**: The pipeline MUST provide a no-model step that selects which live threads/threats/
  entities a generation request is grounded in, matching request state against a caller-supplied
  thread/threat pool and the setting's `entities/` store, reusing `arc_selection.py`'s existing
  deterministic thread-matching logic where its shape applies rather than reimplementing
  hook-matching from scratch.
- **FR-017**: The pipeline MUST provide a no-model step that computes a candidate's structural
  fields — `danger` (via `generation_checks.check_danger_band`'s own `corpus_scenario.scale_danger`
  arithmetic, not a third implementation), whether an escalation sits within `scale_drift` bounds,
  `written_for` scaling, and `status`/`sources:` bookkeeping matching `generation_commit`'s FR-012
  shape — from the request and the selection step's output alone.
- **FR-018**: The pipeline MUST provide a Haiku-tier step that assembles a candidate's entry/exit
  shape (which threads it consumes/emits) and pacing (child-beat count and length, for an
  arc-scale request). This step MUST take the Haiku model's response as an injected argument
  (a structured mapping, mirroring `corpus_pipeline.build_scenario_index`'s `generate(document)`
  precedent of the caller supplying an already-produced result) and MUST NOT call a model itself.
- **FR-019**: The pipeline MUST provide a capable-tier step that takes the capable model's
  already-generated prose (and, under `setting-authoring` mode's `invention_permitted`, any
  invented names/details) as an injected free-form string, applies FR-007's entity-membership/
  labelling rule, and returns a finished `GenerationResult` (`generation.new_result`'s shape).
  This step MUST NOT call a model itself.
- **FR-020**: Each step's model tier MUST be fixed by its own signature, never a runtime choice:
  the no-model steps (FR-016/FR-017) accept no model-response parameter; the Haiku-tier step
  (FR-018) accepts only a structured mapping and rejects a free-form string; the capable-tier step
  (FR-019) is the only step accepting free-form prose.
- **FR-021**: The pipeline MUST expose one documented call sequence — a single function or an
  ordered set of functions with a documented order — that a caller can follow from a validated
  `GenerationRequest` through to a `GenerationResult` ready for `generation_checks.run_checks` and
  `generation_commit.accept_result`/`reject_result`, without reshaping any field along the way.

### Key Entities *(include if feature involves data)*

- **Selection**: the no-model output of FR-016 — the subset of live threads/threats/entities a
  request is grounded in, plus which existing stub (if any) the request continues.
- **Structural fields**: the no-model output of FR-017 — `danger`, `scale_drift` narrowing,
  `written_for`, and the `status`/`sources:` bookkeeping later steps and `generation_commit`
  consume unchanged.
- **Haiku response**: the caller-supplied structured input to FR-018 — entry/exit thread ids and
  pacing counts, never free prose.
- **Capable response**: the caller-supplied free-form prose input to FR-019 — the only
  unstructured input anywhere in this pipeline.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A `GenerationResult` produced by this pipeline is accepted by
  `generation_checks.run_checks` and `generation_commit.accept_result`/`reject_result` with no
  field renaming or reshaping, for all three scales (beat/arc/campaign-spine).
- **SC-002**: The no-model steps (FR-016/FR-017) are deterministic — identical input always
  produces identical output, verified by test.
- **SC-003**: Every one of the four steps (FR-016-FR-019) is verifiably assigned to exactly one of
  the three `27-tooling.md` §5 tiers, checkable by inspecting each function's own parameter list
  rather than any call site.
- **SC-004**: No function in this pipeline performs a live call to a model API — every model-tier
  step's model-derived input arrives as an ordinary argument.

## Assumptions

- This feature builds only on #420 (`generation.py`), #421 (`generation_checks.py`), and #422
  (`generation_commit.py`) — all three merged — and does not modify any of them.
- "Reusing `arc_selection.py`'s logic where applicable" means reusing its thread-subset-match
  primitive and its `entity.resolve_wikilink`-based `leads_to` fallback; FR-016's grounding
  selection operates over a live thread/threat/entity pool rather than `arc_selection.select`'s
  candidate-entity pool, so the two serve adjacent but distinct purposes and this feature adapts
  the matching primitive rather than calling `select` unchanged.
- Actually invoking a live model and wiring this pipeline into a real Claude Code skill is
  out of scope (per issue #423) — that is separate follow-up work.
- "Caller-supplied thread/threat pool" and "the setting's `entities/` store" are ordinary
  in-memory arguments (dicts/lists), matching every other `engine/wyrd/*` module's no-persistence
  convention (`arc_selection.py`'s own stated contract).
