# Data Model: Generation Pipeline

No new persisted entity. Every shape below is a transient `dict` passed between this module's own
functions and the three already-merged sibling modules — matching `generation.py`/
`generation_checks.py`/`generation_commit.py`'s existing convention.

## Selection (FR-016 output)

```text
{
    "consumed": [<id>, ...],           # grounded thread/threat/entity ids, sorted
    "selected_candidates": [<entity>, ...],  # arc_selection.select's own return value, or []
}
```

- `consumed` seeds `GenerationResult.consumed` (#420's shape) unchanged.
- `selected_candidates` is `arc_selection.select`'s output verbatim when a `candidate_pool` was
  given; `[]` when none was (a request grounded purely in threads/entities, continuing nothing).

## Structural fields (FR-017 output)

```text
{
    "danger": <int | None>,            # request['danger_rating'] for live-play, None otherwise
    "written_for": <int | None>,       # echoed from the request
    "scale_drift_bounds": <dict | None>,  # generation_checks's own suppressed-mode bounds, or None
    "status": "drafted",               # generation_commit's own status value (FR-012 shape)
}
```

- `danger`/`written_for` feed directly into the candidate dict `assemble_pacing`/`write_prose`
  build up; `generation_checks.check_danger_band` reads them back unchanged.
- `scale_drift_bounds` is informational only — `generation_checks.check_scale_drift` remains the
  sole enforcement point; this field lets `assemble_pacing`/`write_prose` stay inside the bound by
  construction rather than relying solely on post-hoc narrowing.

## Haiku response (FR-018 input, caller-injected)

```text
{
    "entry_requires_threads": [<id>, ...],   # optional
    "exit_emits_threads": [{"tag": <str>, "if": <str | None>}, ...],  # optional
    "beat_count": <int | None>,              # arc-scale only: how many child beats to decompose into
}
```

A plain `dict` a small model would realistically produce — structured slots, no free prose.
`assemble_pacing` raises `TypeError` if given anything but a `dict`.

## Capable response (FR-019 input, caller-injected)

A single free-form `str` — the finished body text (and any Q3-permitted invented names/details
inline within it). This is the *only* unstructured input anywhere in this pipeline (FR-020,
SC-003).

Alongside it, `write_prose` also takes the caller's own **structured extraction** of that same
capable-model call — `named_entities`, `threat_updates`, `coincidences`, `prophecy_claim` — since
these are discrete facts about what the model produced, not free prose, and accepting them here
does not weaken FR-020's "capable tier is the only step accepting free-form text" boundary. Each
defaults to an empty/neutral value; leaving them all at their defaults means `generation_checks`'s
five checks (FR-007-FR-011) have nothing to evaluate and every one passes vacuously — a valid
choice for a caller with nothing to declare, never evidence the checks actually ran against real
content.

## Candidate (built incrementally, final shape matches `generation.new_result`'s `candidate`)

```text
{
    "danger": <int | None>,
    "written_for": <int | None>,
    "entry": {"requires_threads": [...]} | None,
    "exit": {"emits_threads": [...]} | None,
    "beat_count": <int | None>,
    "body": <str>,
    "named_entities": [<str | {"name": str, "invented": bool}>, ...],
    "threat_updates": [...],
    "coincidences": [...],
    "prophecy_claim": "none",
}
```

`write_prose` is the step that finalizes this shape and wraps it via `generation.new_result` into
a `GenerationResult` — `{"candidate": ..., "checks": [], "consumed": <the consumed argument, "[]"
if omitted>}` — ready for `generation_checks.run_checks` to populate `checks` in place.

## Call sequence (FR-021)

```text
selection   = select_grounding(request, candidate_pool=..., current=...)
structural  = compute_structural_fields(request, selection)
paced       = assemble_pacing(request, selection, structural, haiku_response)
result      = write_prose(
    request, paced, capable_prose, known_entities,
    named_entities=..., threat_updates=..., coincidences=..., prophecy_claim=...,
    consumed=selection["consumed"],
)
result["checks"] = generation_checks.run_checks(request, result["candidate"], known_entities)
# then: generation_commit.accept_result(result, ...) or generation_commit.reject_result(result)
```

`run_pipeline(request, *, candidate_pool=None, current=None, haiku_response, capable_prose,
known_entities, named_entities=None, threat_updates=None, coincidences=None,
prophecy_claim="none")` performs exactly this sequence (threading `selection["consumed"]` into
`write_prose` itself) and returns the populated `GenerationResult` — a caller may call it
directly, or call the four functions individually if it needs to inspect an intermediate step
(e.g. to build its own Haiku-tier prompt from `structural`'s output before that model call is
made).
