# Quickstart: validating corpus excerpt retrieval

## Prerequisites

- A checkout of this repo (`wyrd`) with the feature branch's code.
- A real setting repo with a built corpus index, e.g. `wyrd-setting-titan` (sibling checkout,
  per this session's earlier work) or `wyrd-setting-darkfuture`.

## 1. Library-level check (no CLI)

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -c "
import json, pathlib
from wyrd import corpus_excerpt

titan = pathlib.Path('../wyrd-setting-titan')
documents = json.loads((titan / 'index' / 'documents.json').read_text())['documents'] \
    if 'documents' in json.loads((titan / 'index' / 'documents.json').read_text()) \
    else json.loads((titan / 'index' / 'documents.json').read_text())

doc_id = documents[0]['id']
excerpt = corpus_excerpt.read_excerpt(documents, 'titan', titan, doc_id, offset=1000)
print(excerpt)
"
```

**Expected outcome**: prints ~800 characters of real Titan corpus text surrounding offset 1000
of the first indexed document — not `None`, not an exception.

## 2. Failure modes return `None`, never raise

```bash
PYTHONPATH=engine python3 -c "
from wyrd import corpus_excerpt
print(corpus_excerpt.read_excerpt([], 'titan', __import__('pathlib').Path('.'), 'no-such-doc', 0))
"
```

**Expected outcome**: prints `None`.

## 3. CLI end-to-end

```bash
cd ../wyrd-setting-titan
python3 -m wyrd.client find noun --setting titan --name Azzur
```

**Expected outcome**: JSON with at least one result naming `doc`, `offset`, and a non-null
`excerpt` containing the name "Azzur" (Port Blacksand's ruler, per this repo's own
`entities/faction/port-blacksand.yaml`).

## 4. Unit tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_excerpt -v
```

**Expected outcome**: all tests pass, covering every FR-004 failure mode plus the determinism
and real-corpus checks above.
