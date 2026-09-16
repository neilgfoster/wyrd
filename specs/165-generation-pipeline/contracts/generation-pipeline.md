# Contract: `engine/wyrd/generation_pipeline.py`

Five public functions, no persistence, no live model call.

## `select_grounding(request, *, candidate_pool=None, current=None)`

- **Model tier**: no model.
- **Input**: a validated `GenerationRequest` (`generation.py`); an optional `candidate_pool`
  (existing `arc`/`beat` entities to match, `arc_selection.select`'s own candidate shape); an
  optional `current` entity for the `leads_to` fallback.
- **Output**: `{"consumed": [...], "selected_candidates": [...]}` (see data-model.md).
- **Guarantee**: deterministic — identical arguments always produce identical output. Never
  raises for an empty grounding set; returns `"consumed": []`.

## `compute_structural_fields(request, selection)`

- **Model tier**: no model.
- **Input**: the request; `select_grounding`'s output (only `consumed` is read).
- **Output**: `{"danger", "written_for", "scale_drift_bounds", "status"}` (see data-model.md).
- **Guarantee**: deterministic; reuses `corpus_scenario.scale_danger`'s arithmetic identity
  (`danger_ratio(x, x) == 1`) rather than a new formula, and `generation_checks`'s own
  scale-drift constants rather than restating them.

## `assemble_pacing(request, selection, structural, haiku_response)`

- **Model tier**: Haiku (structured input only).
- **Input**: the request; the two prior steps' output; `haiku_response` — a `dict` the caller
  already obtained from a Haiku-tier call (never fetched by this function).
- **Output**: a partial candidate dict carrying `entry`/`exit`/`beat_count` alongside
  `structural`'s fields.
- **Guarantee**: raises `TypeError` if `haiku_response` is not a `dict` — this is the FR-020
  boundary check other steps rely on for the "Haiku takes structure, not prose" assertion.

## `write_prose(request, paced_candidate, capable_prose, known_entities, *, named_entities=None, threat_updates=None, coincidences=None, prophecy_claim="none", consumed=None)`

- **Model tier**: capable (Sonnet/Opus) — the only step accepting free-form text.
- **Input**: the request; `assemble_pacing`'s output; `capable_prose` — a non-empty `str` the
  caller already obtained from the capable model; `known_entities` — the setting's known-entity
  list (`generation_checks.check_entity_membership`'s own required parameter);
  `named_entities`/`threat_updates`/`coincidences`/`prophecy_claim` — the caller's own structured
  extraction of that same capable-model call (not free prose, so accepting them here does not
  weaken the free-form-text boundary); `consumed` — normally `select_grounding`'s own output,
  threaded through by `run_pipeline`.
- **Output**: a finished `GenerationResult` (`generation.new_result`'s shape) — `checks: []`,
  `consumed` set from the `consumed` argument (`[]` if omitted).
- **Guarantee**: raises `TypeError` if `capable_prose` is not a `str`. Applies FR-007's labelling
  convention: an invented name under `setting-authoring`'s `invention_permitted` must appear in
  `candidate["named_entities"]` as `{"name": ..., "invented": True}`, never a bare string, so
  `check_entity_membership` recognizes it. Leaving `named_entities`/`threat_updates`/
  `coincidences`/`prophecy_claim` at their defaults makes every one of `generation_checks`'s five
  checks pass vacuously (nothing to reject) — correct for a caller with nothing to declare, never
  a substitute for a real caller populating them from its own model call.

## `run_pipeline(request, *, candidate_pool=None, current=None, haiku_response, capable_prose, known_entities, named_entities=None, threat_updates=None, coincidences=None, prophecy_claim="none")`

- **Model tier**: N/A (orchestrator only — no model tier of its own).
- Runs the four functions above in order, then `generation_checks.run_checks`, and returns the
  populated `GenerationResult` — ready for `generation_commit.accept_result`/`reject_result` with
  no further adaptation (FR-021, SC-001).
