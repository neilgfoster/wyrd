# Quickstart: Curated term and structural table indexes (terms.json, tables.json)

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import corpus_terms as ct

text = """Fear Tests

When a character faces something Fear-inducing, roll a Fear test.

01-10  You freeze.
11-30  You flee.
31-70  You fight through it.
71-90  You act rashly.
91-100 You are unshaken.
"""

terms = ct.build_terms_index(text, doc="core-rules", setting="my-setting")
assert terms["fear"][0]["rank"] == "definition"

tables = ct.build_tables_index(text, doc="core-rules", setting="my-setting")
assert tables[0]["dice"] == "d100"
assert tables[0]["row_count"] == 5
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_terms -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_corpus_terms.py`, including all four dice types and the stray-single-line
non-table case.
