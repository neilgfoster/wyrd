# Quickstart: Corpus index retrieval queries (wyrd find)

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import corpus_document, corpus_find, corpus_terms

text = "Fear Tests\n\nIt was Osric the Fair who feared it most.\n"
nouns = corpus_document.build_concordance(text, doc="d1", setting="s1")
terms = corpus_terms.build_terms_index(text, doc="d1", setting="s1")

assert corpus_find.find_noun(nouns, "Osric")[0]["doc"] == "d1"
assert corpus_find.find_rule(terms, "fear")[0]["doc"] == "d1"

tables_index = [{"doc": "d1", "setting": "s1", "offset": 0, "dice": "d100", "row_count": 5, "caption": "Roll Table"}]
assert corpus_find.find_table(tables_index, dice="d100") == tables_index

scenarios_index = [{"id": "the-drowning-well", "settings": ["my-setting"], "scale": "village"}]
assert corpus_find.find_scenario(scenarios_index, scale="village") == scenarios_index

documents_index = [{"id": "wd-098", "system": "a periodical", "edition": "98"}]
assert corpus_find.find_doc(documents_index, work="a periodical", issue="98") == [{"doc": "wd-098"}]
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_find -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_corpus_find.py`, including definition-before-mention ordering and the
empty-index no-error case for all five functions.
