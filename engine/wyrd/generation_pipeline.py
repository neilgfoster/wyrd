"""The generation pipeline: model-tiered orchestration end to end (#423).

specs/161-adventure-and-campaign-generation (#99, merged) specifies adventure/campaign generation
at any scale; its FR-016 through FR-020 describe the steps that actually produce a candidate
`GenerationResult` in the first place -- the piece #420 (`generation.py`), #421
(`generation_checks.py`), and #422 (`generation_commit.py`) all assumed already existed. This
module is that piece: it does not redefine the `GenerationRequest`/`GenerationResult` shapes, does
not re-implement the five anti-inflation checks, and does not write anything to disk -- it
produces the candidate those three modules already operate on, and composes them into one call
sequence (FR-021).

Four pipeline steps, each pinned to exactly one model tier by its own signature (FR-020), never a
runtime choice:

- `select_grounding` (FR-016, no model) -- matches the request's own grounding state against a
  caller-supplied candidate pool of existing stub/decomposed entities, reusing
  `arc_selection.select`'s thread-subset-match/`leads_to`-fallback primitive unchanged rather than
  re-deriving hook matching.
- `compute_structural_fields` (FR-017, no model) -- computes `danger`/`written_for`/`status`/
  `scale_drift_bounds` from the request alone. `danger` reuses the same arithmetic
  `generation_checks.check_danger_band` calls (`corpus_scenario.scale_danger`, in turn
  `adversary.danger_effective`): setting a candidate's baseline `danger` to the request's own
  `danger_rating` at the request's own `written_for` produces an effective danger that is exactly
  `danger_rating`, since `danger_ratio(x, x)` is the identity ratio -- the single correct answer
  given the request's state, not a re-derived formula. `scale_drift_bounds` imports
  `generation_checks`'s own suppressed-mode constants rather than restating the numbers.
- `assemble_pacing` (FR-018, Haiku tier) -- takes the Haiku model's already-produced response as
  an ordinary `dict` argument (never calls a model itself), mirroring
  `corpus_pipeline.build_scenario_index`'s injected-`generate`-result precedent
  (`26-corpus-index.md`'s "Build and maintenance": "that stays injected by the caller").
- `write_prose` (FR-019, capable tier) -- takes the capable model's already-generated prose as an
  ordinary `str` argument (never calls a model itself), and is the only step in this pipeline
  accepting free-form text (FR-020, SC-003). Also takes the caller's own structured extraction of
  that same model call -- `named_entities`/`threat_updates`/`coincidences`/`prophecy_claim` -- so
  #421's five checks have real content to evaluate rather than vacuous defaults.

`run_pipeline` composes all four in order, then runs `generation_checks.run_checks`, returning a
`GenerationResult` ready for `generation_commit.accept_result`/`reject_result` with no reshaping
(FR-021, SC-001).

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import arc_selection, generation, generation_checks


def _grounded_ids(request: dict) -> set:
    """The request's own grounding ids: `threads`/`threat_state` for `live-play`,
    `existing_entities` for `setting-authoring` (generation.py's mode-exclusive field split)."""
    ids = {t.get("id") for t in (request.get("threads") or [])}
    ids |= {t.get("entity_id") for t in (request.get("threat_state") or [])}
    ids |= set(request.get("existing_entities") or [])
    ids.discard(None)
    return ids


def select_grounding(
    request: dict,
    *,
    candidate_pool: list[dict] | None = None,
    current: dict | None = None,
) -> dict:
    """FR-016: no model. Matches `request`'s own grounding state against `candidate_pool` (an
    existing stub/decomposed entity pool this generation might continue or decompose), reusing
    `arc_selection.select` unchanged for the actual thread-subset-match/`leads_to` fallback.

    Returns `{"consumed": [...], "selected_candidates": [...]}` -- `consumed` is always the
    request's own grounded ids, sorted; `selected_candidates` is `arc_selection.select`'s own
    return value when `candidate_pool` is given, or `[]` when it is not (a request grounded
    purely in threads/entities, continuing no existing entity).

    Deterministic: identical arguments always produce identical output. Never raises for an empty
    grounding set.
    """
    grounded = _grounded_ids(request)
    selected: list[dict] = []
    if candidate_pool is not None:
        selected = arc_selection.select(grounded, candidate_pool, current=current)
    return {"consumed": sorted(grounded), "selected_candidates": selected}


def compute_structural_fields(request: dict, selection: dict) -> dict:
    """FR-017: no model. Computes a candidate's structural fields from `request` alone
    (`selection` is accepted for a uniform pipeline-step signature but not read -- the structural
    fields this step computes do not depend on which existing entity, if any, was selected).

    `danger`/`written_for`: for a `live-play` request, `danger` is set to `request
    ['danger_rating']` and `written_for` to `request['written_for']` -- at that party size,
    `adversary.danger_effective`'s `danger_ratio(x, x)` is the identity ratio, so
    `corpus_scenario.scale_danger` (the arithmetic `generation_checks.check_danger_band` already
    calls) returns exactly `danger_rating` for this candidate later, rather than a value this
    step would need a second formula to derive. A `setting-authoring` request carries no
    `danger_rating` (generation.py's `_SETTING_AUTHORING_FIELDS` split) so both fields are
    `None`, matching `check_danger_band`'s own pass-unconditionally behaviour for that case.

    `scale_drift_bounds`: `None` under `tone_contract.scale_drift: allowed`; otherwise the exact
    `{"imminence_delta_max", "ambient_add_max"}` pair `generation_checks.check_scale_drift`
    itself enforces, imported from its own constants rather than restated here -- informational
    only, so `assemble_pacing`/`write_prose` can stay inside the bound by construction, while
    `check_scale_drift` remains the sole enforcement point.

    `status`: `"drafted"`, matching `generation_commit.accept_result`'s own FR-012 shape.
    """
    mode = request.get("mode")
    if mode == "live-play":
        danger = request.get("danger_rating")
        written_for = request.get("written_for")
    else:
        danger = None
        written_for = None

    scale_drift_bounds = None
    if (request.get("tone_contract") or {}).get("scale_drift") == "suppressed":
        scale_drift_bounds = {
            "imminence_delta_max": generation_checks._MAX_SUPPRESSED_IMMINENCE_DELTA,
            "ambient_add_max": generation_checks._MAX_SUPPRESSED_AMBIENT_ADD,
        }

    return {
        "danger": danger,
        "written_for": written_for,
        "scale_drift_bounds": scale_drift_bounds,
        "status": "drafted",
    }


def assemble_pacing(
    request: dict,
    selection: dict,
    structural: dict,
    haiku_response: dict,
) -> dict:
    """FR-018/FR-020: Haiku tier. `haiku_response` MUST already be the Haiku model's produced
    output -- a structured mapping, mirroring `corpus_pipeline.build_scenario_index`'s own
    injected-result precedent (`26-corpus-index.md`) -- this function never calls a model itself.

    Raises `TypeError` when `haiku_response` is not a `dict`, the FR-020 boundary a caller (or a
    test asserting the model-tier discipline) relies on: this is the one pipeline step that
    accepts *structured* model output, never free prose.

    Merges `haiku_response`'s `entry_requires_threads`/`exit_emits_threads`/`beat_count` into
    `structural`'s fields as `entry`/`exit`/`beat_count`, each defaulting to `None` when the
    response omits it.
    """
    if not isinstance(haiku_response, dict):
        raise TypeError(
            f"assemble_pacing (Haiku tier) requires a structured dict response, "
            f"got {type(haiku_response).__name__}"
        )

    entry = None
    if haiku_response.get("entry_requires_threads") is not None:
        entry = {"requires_threads": haiku_response["entry_requires_threads"]}

    exit_block = None
    if haiku_response.get("exit_emits_threads") is not None:
        exit_block = {"emits_threads": haiku_response["exit_emits_threads"]}

    return {
        **structural,
        "entry": entry,
        "exit": exit_block,
        "beat_count": haiku_response.get("beat_count"),
    }


def write_prose(
    request: dict,
    paced_candidate: dict,
    capable_prose: str,
    known_entities: list[str],
    *,
    named_entities: list | None = None,
    threat_updates: list[dict] | None = None,
    coincidences: list[dict] | None = None,
    prophecy_claim: str = "none",
    consumed: list[str] | None = None,
) -> dict:
    """FR-019/FR-007/FR-020: capable tier -- the only step in this pipeline accepting free-form
    text. `capable_prose` MUST already be the capable model's generated body text (and, under
    `setting-authoring`'s `invention_permitted`, any Q3-permitted invented detail written inline);
    this function never calls a model itself.

    Raises `TypeError` when `capable_prose` is not a `str` -- the FR-020 boundary distinguishing
    this step from `assemble_pacing`'s structured-only input.

    `named_entities`/`threat_updates`/`coincidences`/`prophecy_claim` are the structured facts a
    caller has already extracted from that same capable-model call (naming which entities the
    prose mentions, which threats it updates, which coincidences it relies on, and what it claims
    about prophecy) -- not free prose, so accepting them as ordinary structured arguments does not
    weaken FR-020's "capable tier is the only step accepting free-form text" boundary. Each
    defaults to an empty/neutral value so a caller with nothing to declare need not pass them, but
    every one of them MUST be populated for `generation_checks.run_checks`'s five checks (FR-007
    through FR-011) to have anything to actually evaluate -- leaving them at their defaults means
    every check passes vacuously, not that nothing was generated.

    `known_entities` is accepted (matching `generation_checks.check_entity_membership`'s own
    required parameter) so a caller building `named_entities` can consult it, but this function
    does not itself run the membership check -- that stays `generation_checks.run_checks`'s job,
    run by `run_pipeline` immediately after this step.

    Returns a finished `GenerationResult` (`generation.new_result`'s shape) with `checks: []` --
    unpopulated until `generation_checks.run_checks` runs -- and `consumed` set from the caller-
    supplied `consumed` (normally `select_grounding`'s own output, threaded straight through by
    `run_pipeline`), defaulting to `[]` when this function is called on its own.
    """
    if not isinstance(capable_prose, str):
        raise TypeError(
            f"write_prose (capable tier) requires a free-form str response, "
            f"got {type(capable_prose).__name__}"
        )

    candidate = {
        **paced_candidate,
        "body": capable_prose,
        "named_entities": list(named_entities or []),
        "threat_updates": list(threat_updates or []),
        "coincidences": list(coincidences or []),
        "prophecy_claim": prophecy_claim,
    }
    return generation.new_result(candidate, consumed=list(consumed or []))


def run_pipeline(
    request: dict,
    *,
    candidate_pool: list[dict] | None = None,
    current: dict | None = None,
    haiku_response: dict,
    capable_prose: str,
    known_entities: list[str],
    named_entities: list | None = None,
    threat_updates: list[dict] | None = None,
    coincidences: list[dict] | None = None,
    prophecy_claim: str = "none",
) -> dict:
    """FR-021: the documented call sequence a caller (a future `/wyrd-*` skill, or
    `create-setting`'s Q3 path) follows end to end -- selection (FR-016) -> structural computation
    (FR-017) -> Haiku-tier assembly (FR-018, injected) -> capable-tier prose (FR-019, injected) ->
    `generation_checks.run_checks`. Returns the populated `GenerationResult`, ready for
    `generation_commit.accept_result`/`reject_result` with no further adaptation (SC-001).

    Both `haiku_response` and `capable_prose` must already be the caller's own model calls' actual
    output -- this function, like every step it composes, never calls a model itself.
    `named_entities`/`threat_updates`/`coincidences`/`prophecy_claim` are `write_prose`'s own
    structured extraction of that same capable-model call, threaded straight through unchanged --
    leaving them at their defaults means `generation_checks.run_checks`'s five checks have nothing
    to evaluate and every one passes vacuously, which is correct for a caller with nothing to
    declare but not a substitute for a real caller populating them.
    """
    selection = select_grounding(request, candidate_pool=candidate_pool, current=current)
    structural = compute_structural_fields(request, selection)
    paced = assemble_pacing(request, selection, structural, haiku_response)
    result = write_prose(
        request,
        paced,
        capable_prose,
        known_entities,
        named_entities=named_entities,
        threat_updates=threat_updates,
        coincidences=coincidences,
        prophecy_claim=prophecy_claim,
        consumed=selection["consumed"],
    )
    result["checks"] = generation_checks.run_checks(request, result["candidate"], known_entities)
    return result
