# Quickstart: validating a generation request

This feature adds no CLI verb and no caller — it is a library layer three sibling features build
on. Validation is exercised directly, from Python, or via its test suite.

## Prerequisites

- Python 3.11, repo dependencies installed as usual for this repo (no new dependency added).

## Run the test suite

```bash
PYTHONPATH=engine python3 -m pytest tests/engine/test_generation.py -q
```

Expected: all tests pass, covering:

- `GenerationRequest` construction/validation for each of the three scales (`beat`, `arc`,
  `campaign-spine`) crossed with both modes, per data-model.md's field table.
- The campaign-spine alias check (`is_campaign_spine_shape`, or equivalent) confirming a
  `campaign-spine` request is exactly an `arc` request with no `parent` and `scale: campaign`.
- The FR-004/FR-005 mode-specific state checks, including the `invention_permitted` rejection
  path and the live-play "at least one of threads/threat_state" rejection path.
- The FR-006 mode-boundary invariant: a `live-play` and a `setting-authoring` request differ only
  in which state fields are set, never in which downstream rule would apply.

## Try it directly

```python
from wyrd.generation import GenerationRequest, validate_request

request = GenerationRequest(
    scale="beat",
    mode="live-play",
    setting_ref="some-setting",
    tone_contract={...},
    written_for=4,
    threads=[{"id": "t1", "heat": 2}],
    danger_rating=3,
    era="era-1",
)
error = validate_request(request)
assert error is None  # valid request
```

An invalid request (e.g. `setting-authoring` mode with no `invention_permitted`) returns a
structured error naming the missing field/rule, per contracts/generation-request.md's Error
Shapes section — never a bare exception.

## Ruff / lint

```bash
python3 -m ruff check engine/wyrd/generation.py tests/engine/test_generation.py
python3 -m ruff format --check engine/wyrd/generation.py tests/engine/test_generation.py
```
