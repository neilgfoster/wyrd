# Contract: the five anti-inflation check functions

`engine/wyrd/generation_checks.py` — six functions, all pure, all returning (or aggregating) a
check entry `{rule, outcome, detail}` per data-model.md. Every function takes a `GenerationRequest`
dict (#420's shape) and a candidate dict (data-model.md's shape, an extension of #420's candidate)
as its first two positional parameters, plus whatever extra parameter its own check needs — no
function reads global state or performs I/O.

```python
def check_entity_membership(
    request: dict, candidate: dict, known_entities: list[str]
) -> dict:
    """FR-007. `known_entities` is the setting's entities/ store (spec.md Assumptions: not a
    GenerationRequest field for live-play). Rejects naming every entity absent from all three
    closed sources: known_entities, request['threads']/request['threat_state'] ids (live-play),
    or candidate['named_entities'] entries the candidate itself has labelled
    'invented, per Phase 1 Q3' when request['mode'] == 'setting-authoring' and
    request['invention_permitted'] is True."""

def check_prophecy(request: dict, candidate: dict) -> dict:
    """FR-008. Closed-vocabulary comparison only: request['tone_contract']['prophecy'] against
    candidate['prophecy_claim'] and each candidate['threat_updates'][i]['known_to_player']."""

def check_danger_band(request: dict, candidate: dict) -> dict:
    """FR-009. Calls engine.wyrd.corpus_scenario.scale_danger(
    {"danger": candidate["danger"], "written_for": request["written_for"]},
    request["written_for"]) -- the existing wrapper issue #421 names -- and rejects when the
    result exceeds request['danger_rating']. Never recomputes the ratio formula locally
    (research.md)."""

def check_scale_drift(request: dict, candidate: dict) -> dict:
    """FR-010. Only gates when request['tone_contract']['scale_drift'] == 'suppressed' (returns
    pass unconditionally under 'allowed'). Inspects candidate['threat_updates']: an
    imminence_delta or ambient_add beyond what the contract permits narrows (outcome: narrowed,
    detail states the narrowed value); an entry with entity_id None and no connection rejects
    outright (outcome: reject) -- narrowing cannot invent a connection. Reuses
    engine.wyrd.threat.validate_connections for the connectionless-new-threat leg."""

def check_favourable_coincidence(request: dict, candidate: dict) -> dict:
    """FR-011. For each candidate['coincidences'] entry, rejects if supported_by is None or not
    among the ids in request['threads']/request['threat_state'] (live-play) or
    request['existing_entities'] (setting-authoring)."""

def run_checks(
    request: dict, candidate: dict, known_entities: list[str]
) -> list[dict]:
    """Runs all five checks in FR-007..FR-011 order and returns their entries as a list, matching
    GenerationResult.checks' shape (#420). A thin aggregator: no check logic of its own."""
```

## Outcome vocabulary (per entry)

| Outcome | Produced by |
|---|---|
| `pass` | any of the five, when its rule is satisfied |
| `reject` | any of the five |
| `narrowed` | `check_scale_drift` only (FR-010) |

## Error shapes

None of the six functions raises for a well-formed `request`/`candidate` pair — every outcome,
including a violation, is a normal return value (a check entry), per this repo's report-don't-
raise convention for cross-cutting invariant checks (`engine/wyrd/threat.py`'s
`validate_connections` already follows the same rule). A malformed input (missing required field)
is not this feature's concern: `generation.py`'s `validate_request` (#420) is the gate that runs
before any check here is reached, per specs/161's Processing step 5 ("no-model: run the FR-007-
011... checks against the assembled candidate").

## Consumer contract

The (not-yet-built) generation pipeline calls `run_checks`, then passes its return value straight
into `generation.py`'s `new_result(candidate, checks=...)` — this feature's output is exactly that
function's `checks` argument, with no reshaping in between.
