# Quickstart: Generation Pipeline

Prerequisites: `PYTHONPATH=engine` (matching `tests/engine/`'s convention).

```python
from wyrd import generation, generation_pipeline

request = generation.new_request(
    scale="beat",
    mode="live-play",
    setting_ref="some-setting",
    tone_contract={"prophecy": "rare", "scale_drift": "allowed"},
    written_for=4,
    threads=[{"id": "thread-a"}],
    danger_rating=30,
    era="present",
)
assert generation.validate_request(request) is None

# The caller has already obtained both model responses out of process, and has already
# extracted the structured facts the capable model's prose implies (which entities it named,
# any threat changes, any coincidences it relied on, any prophecy claim). Leaving these at their
# defaults means generation_checks' five checks have nothing to evaluate and pass vacuously.
haiku_response = {"entry_requires_threads": ["thread-a"], "beat_count": None}
capable_prose = "The warehouse is quiet. Someone moved the crates last night."

result = generation_pipeline.run_pipeline(
    request,
    haiku_response=haiku_response,
    capable_prose=capable_prose,
    known_entities=["thread-a"],
    named_entities=["thread-a"],
)

# result is a GenerationResult ready for the already-merged sibling modules, unchanged:
from wyrd import generation_commit
if generation_commit.can_commit(result):
    ...  # generation_commit.accept_result(result, ...)
else:
    generation_commit.reject_result(result)
```

## Validating the model-tier discipline (FR-020)

```python
import pytest

with pytest.raises(TypeError):
    generation_pipeline.assemble_pacing(request, selection, structural, "free prose is wrong here")

with pytest.raises(TypeError):
    generation_pipeline.write_prose(request, paced, {"not": "a string"}, known_entities=[])
```

`select_grounding`/`compute_structural_fields` accept no model-response parameter at all — calling
either with an extra positional argument raises `TypeError` from Python's own signature checking,
which is the test suite's actual FR-020 assertion for those two steps.
