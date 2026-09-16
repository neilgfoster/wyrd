# Phase 0 research: Anti-inflation checks for generated content

No `NEEDS CLARIFICATION` markers remain in spec.md's Technical Context — the two decisions below
were resolved during specification (recorded there as Assumptions) and are restated here with
their rejected alternatives, per this document's own purpose.

## Decision: FR-009 calls `corpus_scenario.scale_danger` directly

**Decision**: `check_danger_band` calls `engine/wyrd/corpus_scenario.py`'s
`scale_danger({"danger": candidate["danger"], "written_for": request["written_for"]},
request["written_for"])` — the existing wrapper issue #421 itself names — and rejects when the
result exceeds `request["danger_rating"]`.

**Rationale**: `03-rules.md` §7 defines `danger_rating`
(`engine/wyrd/state.py`'s chronicle-level field) as the *current* number newly written/generated
content should be pitched at, and `written_for` as the party a piece of content is written for.
A candidate this feature checks is generated fresh *for* the request's own `written_for` — it was
never written for anyone else — so `party` and `written_for` are the same value at this call site,
and `danger_ratio(x, x)` is exactly `1` (`adversary.danger_ratio`'s own docstring: "a table of
four bodies runs content written for four exactly as written"). `scale_danger` therefore returns
the candidate's own `danger` unchanged in this particular call shape, which is the *correct*
behaviour of the shared formula for same-party content, not a sign the reuse is hollow — banding
still runs through the one place `03-rules.md`/ADR 0024 define the arithmetic, so a future change
to the curve (e.g. `effective_party_size`) changes this check's behaviour too, automatically.

**Alternatives considered**:
- Call `adversary.danger_effective` directly, bypassing `scale_danger` — rejected: `scale_danger`
  is the existing, already-tested wrapper issue #421 names first, and calling it directly (rather
  than reaching past it into `adversary.py`'s internals) is the closer reading of "reuse... rather
  than reimplement."
- Reimplement the ratio formula locally — rejected outright by issue #421's own constraint and by
  `docs/adr/0024`'s standing rule that this arithmetic lives in one place.

## Decision: the candidate carries a `threat_updates` field the entity schema doesn't define

**Decision**: `check_scale_drift` (FR-010) and `check_favourable_coincidence` (FR-011) read a
`threat_updates` list from the candidate dict — `{entity_id, imminence_delta, ambient_add,
connection}` per entry (`entity_id: None` for a newly introduced threat) — a field this feature
adds to the candidate contract for these checks' own use, not to the persisted `beat`/`arc` entity
schema.

**Rationale**: the existing entity schema's `exit.changes` is free prose (`18-arcs-and-beats.md`);
FR-010's own text requires a "structural, non-prose-reading" check. Something has to carry the
structured delta for a mechanical check to run against, and specs/161 assigns "assembling a
generation result's entry/exit shape" to the (out-of-scope) generation-pipeline sibling feature —
this feature only consumes that shape, so it names the minimal field it needs and leaves whether/
how it survives into the committed entity to the commit-back sibling feature (FR-012-015).

**Alternatives considered**:
- Parse `exit.changes` prose for keywords — rejected: FR-010's own text and FR-007/FR-008's
  parallel wording both rule out prose-reading as the check mechanism.
- Wait for the pipeline feature to define this field, blocking this feature — rejected: issue
  #421 explicitly scopes this feature to the five check *functions*, decoupled from the pipeline
  that will call them; the aggregator's contract (below) is what the pipeline feature integrates
  against, so this feature must name its own input shape now.
