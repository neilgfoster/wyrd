# Research: Generation Pipeline

No `NEEDS CLARIFICATION` markers remain in the Technical Context — this feature composes three
already-merged sibling modules whose shapes are fixed, so the open questions were about *how* to
reuse each one's existing logic rather than about unknown technology.

## Decision: FR-016's selection reuses `arc_selection.select`, not `arc_selection._thread_match`

**Decision**: `select_grounding` takes an optional `candidate_pool` (existing stub/decomposed
`arc`/`beat` entities carrying `entry`/`exit` blocks) and, when given, calls
`arc_selection.select(live_threads, candidate_pool, current=current)` unchanged to pick which
existing entity a new generation continues or decomposes. The request's own grounded ids (its
`threads` ids and `threat_state` entity ids for `live-play`, or `existing_entities` for
`setting-authoring`) are computed directly as a set union/intersection — trivial set arithmetic
that is not `arc_selection`'s logic to reuse, since `arc_selection` has no notion of a request's
own grounding state at all.

**Rationale**: `arc_selection.select`'s thread-subset-match plus `leads_to` fallback is exactly
"the same deterministic thread/hook matching `18-arcs-and-beats.md` already specifies for stub
selection" the issue names — reusing the public `select` function (not its private
`_thread_match` helper) keeps this feature calling `arc_selection`'s own documented contract
rather than reaching into its internals.

**Alternatives considered**:
- Reimplementing subset matching inline — rejected, this is precisely the duplication issue #423
  and CLAUDE.md's reuse discipline forbid.
- Importing `_thread_match` directly — rejected, it is a private helper; `select` is the module's
  intended public entry point and already composes it with the `leads_to` fallback FR-016 also
  needs (an arc/beat's stub decomposition should fall back the same way `arc_selection` itself
  documents).

## Decision: FR-017's danger computation sets `candidate['danger'] = request['danger_rating']`

**Decision**: for a `live-play` request, the structural step sets the candidate's baseline
`danger` field equal to `request['danger_rating']` and copies `written_for` from the request
unchanged. For `setting-authoring` (which carries no `danger_rating`), `danger` is left `None`,
matching `check_danger_band`'s own documented pass-unconditionally behaviour for that case.

**Rationale**: `adversary.danger_effective(danger, party, written_for)` computes
`danger * danger_ratio(party, written_for)`, and `danger_ratio(x, x)` is the identity ratio — so
setting `danger = danger_rating` and `written_for` to the request's own value makes
`corpus_scenario.scale_danger` (the same arithmetic `check_danger_band` already calls) return
exactly `danger_rating` when `check_danger_band` runs later. This is a real, checkable
computation (not a placeholder): a request built for a party of 4 at `danger_rating: 30` produces
a candidate whose computed `danger` field, once banded through the shared arithmetic, is exactly
30 for that same party — the single correct answer FR-017 asks for, using the identical function
`check_danger_band` itself will call, never a duplicate of `scale_danger`'s formula.

**Alternatives considered**:
- Re-deriving `danger_ratio`'s formula locally to compute an "equivalent" baseline for a different
  assumed party size — rejected as an unrequested extra degree of freedom; nothing in the request
  shape supplies a baseline party distinct from `written_for`, and inventing one would not be "a
  single correct answer given the request's state" (27-tooling.md §1).

## Decision: FR-017's scale-drift bounds are surfaced, not re-enforced

**Decision**: `compute_structural_fields` includes a `scale_drift_bounds` field —
`None` under `tone_contract.scale_drift: allowed`, or the exact
`{"imminence_delta_max", "ambient_add_max"}` pair `generation_checks` already defines as
`_MAX_SUPPRESSED_IMMINENCE_DELTA`/`_MAX_SUPPRESSED_AMBIENT_ADD` under `suppressed` — imported
directly from `generation_checks`, not restated as new literals.

**Rationale**: FR-010's actual gating (reject/narrow) is `generation_checks.check_scale_drift`'s
job, already merged; FR-017 only needs to make the bound visible to the assembly/prose steps so
whatever they invent stays inside it by construction rather than relying on `check_checks`'s
narrowing after the fact. Importing the same module-level constants (rather than hand-copying the
numbers `1` and `1`) is what keeps this a single source of truth if that policy ever changes.

**Alternatives considered**:
- Duplicating the two integer literals locally — rejected outright as exactly the "reimplementing
  a third time" issue #423 calls out, even though the values themselves are small.

## Decision: FR-018/FR-019's injected-response shape mirrors `corpus_pipeline.build_scenario_index`

**Decision**: `assemble_pacing(request, selection, structural, haiku_response: dict)` and
`write_prose(request, candidate, capable_prose: str, known_entities: list[str])` both take their
model's output as an ordinary keyword/positional argument — never a callback, never an internal
model client. `assemble_pacing` raises `TypeError` if `haiku_response` is not a `dict` (guarding
FR-020's "never free text" boundary); `write_prose` requires `capable_prose` to be a non-empty
`str`.

**Rationale**: `docs/design/26-corpus-index.md`'s "Build and maintenance" section states the
scenario index's expensive step "stays injected by the caller, so building this decision is fully
testable without ever reaching a real model" — `corpus_pipeline.build_scenario_index` implements
that exactly via its own `generate` parameter, called once per document needing regeneration.
FR-018/FR-019 differ only in degree (a single already-produced response per call, not a
per-document callback invoked lazily), since a generation request produces one candidate per
call, not a batch — the injection principle (the caller always supplies the already-computed
model output; this module never reaches out itself) is identical.

**Alternatives considered**:
- A `generate` callback parameter matching `build_scenario_index`'s exact shape — rejected as
  over-fitting a batch-lazy-cache pattern (built for "regenerate only what's stale across many
  documents") onto a single-request pipeline that has no cache and no batch to iterate; the
  issue's own wording ("takes the model's response as an argument") asks for the simpler,
  already-produced-value shape, which this feature adopts.
