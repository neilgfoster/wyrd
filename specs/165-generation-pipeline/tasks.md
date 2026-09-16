# Tasks: Generation Pipeline

**Input**: plan.md, data-model.md, contracts/generation-pipeline.md, quickstart.md

## T001 — `select_grounding` (FR-016)

Implement `select_grounding(request, *, candidate_pool=None, current=None)` in a new
`engine/wyrd/generation_pipeline.py`. Computes the grounded id set from the request's own
`threads`/`threat_state` (live-play) or `existing_entities` (setting-authoring), and — only when
`candidate_pool` is given — calls `arc_selection.select(grounded_ids, candidate_pool,
current=current)` unchanged for `selected_candidates`. Returns
`{"consumed": sorted(grounded_ids), "selected_candidates": [...]}`.

## T002 — `compute_structural_fields` (FR-017)

Implement `compute_structural_fields(request, selection)`. Sets `danger`/`written_for` per
research.md's identity-ratio decision (live-play only; `None`/`None` under setting-authoring),
`status: "drafted"`, and `scale_drift_bounds` sourced from `generation_checks`'s own
`_MAX_SUPPRESSED_IMMINENCE_DELTA`/`_MAX_SUPPRESSED_AMBIENT_ADD` constants (imported, not
restated) when `tone_contract.scale_drift == "suppressed"`, else `None`.

## T003 — `assemble_pacing` (FR-018/FR-020)

Implement `assemble_pacing(request, selection, structural, haiku_response)`. Raises `TypeError`
if `haiku_response` is not a `dict`. Merges `entry_requires_threads`/`exit_emits_threads`/
`beat_count` from `haiku_response` into `structural`'s fields as `entry`/`exit`/`beat_count`,
defaulting each to `None` when absent from the response.

## T004 — `write_prose` (FR-019/FR-007/FR-020)

Implement `write_prose(request, paced_candidate, capable_prose, known_entities)`. Raises
`TypeError` if `capable_prose` is not a `str`. Builds the final `candidate` dict (`body`,
`named_entities`, `threat_updates`, `coincidences`, `prophecy_claim` default `"none"`, plus
`paced_candidate`'s fields) and returns `generation.new_result(candidate, consumed=selection[
"consumed"])`.

## T005 — `run_pipeline` (FR-021)

Implement `run_pipeline(request, *, candidate_pool=None, current=None, haiku_response,
capable_prose, known_entities)`, composing T001-T004 in order, then setting
`result["checks"] = generation_checks.run_checks(request, result["candidate"], known_entities)`
before returning `result`.

## T006 — FR-020 signature/tier tests

`tests/engine/test_generation_pipeline.py`: assert `select_grounding`/`compute_structural_fields`
raise `TypeError` when called with an extra positional model-response-shaped argument (proving
neither accepts one); assert `assemble_pacing` raises `TypeError` given a bare string;
assert `write_prose` raises `TypeError` given a non-`str`, and succeeds given a `str`.

## T007 — FR-016/FR-017 reuse + determinism tests

Assert `select_grounding` calls through to `arc_selection.select` unchanged (patch/spy, or a
candidate-pool fixture whose `leads_to` fallback only `arc_selection.select` implements) and is
deterministic across repeated calls with identical arguments; assert
`compute_structural_fields`'s `danger` output, once passed through
`generation_checks.check_danger_band`, agrees exactly with `request['danger_rating']` (identity
check per research.md); assert `scale_drift_bounds`'s values equal
`generation_checks`'s own constants by reference, not a hand-copied literal.

## T008 — End-to-end composition test, all three scales

For `beat`, `arc`, and `campaign-spine` (per `generation.is_campaign_spine_shape`): build a
request, run `run_pipeline`, and assert the returned `GenerationResult` is accepted unchanged by
`generation_checks.run_checks` (already run inside the pipeline) and by
`generation_commit.can_commit`/`accept_result` (or `reject_result`) with no field renaming
(SC-001).

## T009 — Ruff clean + doc note

Run `python3 -m ruff check .` and `python3 -m ruff format --check .` after all of the above.
Since this closes epic #27's fourth and final child, leave a one-line pointer in
`docs/design/27-tooling.md`'s (or 18-arcs-and-beats.md's, whichever already references the
generation pipeline) existing text only if it currently describes the pipeline as not-yet-built —
otherwise no design-doc change is needed (design docs already describe the target state, not a
changelog).
