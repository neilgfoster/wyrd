# Quickstart: Setting build pipeline — scheduled execution and web augmentation policy

This feature has two deliverables: a design/policy extension to
[`docs/design/26-corpus-index.md`](../../docs/design/26-corpus-index.md), and a small pure
Python module, `engine/wyrd/corpus_provenance.py`, that a setting repository's own tooling can
import. There is no CLI and no live network call to run — validate both deliverables as follows.

## Prerequisites

- Python 3.11+, this repo's own virtualenv/interpreter (standard library only — no install step).
- Run everything from the repository root.

## Validating the design/policy extension

Read the extended section of `docs/design/26-corpus-index.md` and confirm, without needing to ask
anyone (SC-001, SC-002):

1. It states whether scheduled execution is recommended, where the workflow lives (inside a
   `wyrd-setting-<name>` repo), and which pipeline steps it covers vs. excludes.
2. It states the public-augmentation rule and can be used to classify three example sources:
   - a page copied from a private rulebook → **out of bounds** (library-only, not public)
   - a public-domain reference work → **in bounds**
   - a fan wiki of unknown/unclear licence → **out of bounds** ("found on the open internet"
     alone does not qualify)
3. `python3 tools/check_docs.py` still passes — the extension does not break the document's
   reachability from `README.md` or its link policy.

## Validating the provenance record module

```bash
cd /path/to/wyrd
PYTHONPATH=engine python3 - <<'EOF'
from wyrd.corpus_provenance import build_provenance_record

# A library-sourced fact: no reference needed.
record = build_provenance_record(origin="library")
assert record == {"origin": "library", "reference": None}

# A public-sourced fact: reference is required.
record = build_provenance_record(origin="public", reference="Public Domain Bestiary, 1911, p. 42")
assert record["origin"] == "public"
assert record["reference"]

# Invalid: public origin with no reference raises.
try:
    build_provenance_record(origin="public")
    raise SystemExit("expected ValueError")
except ValueError:
    pass

# Invalid: library origin with a reference raises.
try:
    build_provenance_record(origin="library", reference="anything")
    raise SystemExit("expected ValueError")
except ValueError:
    pass

print("ok")
EOF
```

Expected outcome: prints `ok`, no assertion or exception escapes uncaught.

## Running the test suite

This repo's engine tests use stdlib `unittest`, not pytest (docs/design/27-tooling.md section 6):

```bash
python3 -m unittest tests.engine.test_corpus_provenance -v
python3 -m ruff check engine/wyrd/corpus_provenance.py tests/engine/test_corpus_provenance.py
python3 -m ruff format --check engine/wyrd/corpus_provenance.py tests/engine/test_corpus_provenance.py
```

Expected outcome: all tests pass; ruff reports no findings and no reformatting needed.

## What this quickstart does NOT cover

- No GitHub Actions workflow file is created or runnable in this repository — the scheduled
  workflow's actual YAML lives in a `wyrd-setting-<name>` repo, outside this repo's scope
  (CLAUDE.md's repository table; plan.md's Summary).
- No live web fetch of any kind — this repo ships no such capability, by design (FR-006).
