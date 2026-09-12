# Quickstart: Generalise corpus extraction and indexing for any setting repo

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import corpus_pipeline

mechanical_doc = {
    "id": "rules-01", "path": "library/core.pdf", "system": "a setting",
    "edition": "1st", "document_type": "rules", "page_count": 10,
    "extraction_method": "text-layer", "setting": "my-setting",
    "text": "Fear Tests\n\nOsric the Fair rolls against Fear.\n01-05 A shudder\n06-10 A scream\n",
}
world_doc = {
    "id": "gazetteer-01", "path": "library/atlas.pdf", "system": "a setting",
    "edition": "1st", "document_type": "setting", "page_count": 40,
    "extraction_method": "text-layer", "setting": "my-setting",
    "world_category": "geography",
    "text": "The Ford at Cray\n\nOsric the Fair once feared crossing here.\n01-05 the shallows\n",
}

bundle = corpus_pipeline.build_setting_corpus_indexes([mechanical_doc, world_doc])

assert len(bundle["documents"]) == 2                 # both documents catalogued
assert "Osric" in bundle["nouns"]                     # both contribute to the concordance
assert len(bundle["nouns"]["Osric"]) == 2
assert "fear" in bundle["terms"]                      # only the mechanical document
assert all(p["doc"] == "rules-01" for p in bundle["terms"]["fear"])
assert all(t["doc"] == "rules-01" for t in bundle["tables"])  # world doc's table-shaped run is skipped

# The scenario/arcs index: lazy, cached, generator injected (never called by this module itself)
cache: dict = {}
calls = []

def fake_generate(document):
    calls.append(document["id"])
    return {"id": document["id"], "tone": ["investigation"]}

docs = [
    {"id": "rules-01", "setting": "my-setting", "content_hash": "h1"},
    {"id": "gazetteer-01", "setting": "my-setting", "content_hash": "h2"},
]
records, cache = corpus_pipeline.build_scenario_index(docs, cache, fake_generate, schema_version=1)
assert sorted(calls) == ["gazetteer-01", "rules-01"]   # both missing from an empty cache

# Re-run unchanged: nothing regenerated.
calls.clear()
records, cache = corpus_pipeline.build_scenario_index(docs, cache, fake_generate, schema_version=1)
assert calls == []
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_pipeline -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_corpus_pipeline.py`: multi-setting scoping and duplicate-id detection (User
Story 1), the world-building/mechanical index boundary (User Story 2), and all four cache
freshness cases plus the generator-exception edge case (User Story 3).
