# Quickstart: Corpus retrieval is scoped to a setting, never unfiltered

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import corpus_find as cf

nouns_index = {
    "Osric": [
        {"doc": "d1", "setting": "setting-a", "count": 1, "offsets": [10]},
        {"doc": "d2", "setting": "setting-b", "count": 1, "offsets": [20]},
    ]
}

results = cf.find_noun(nouns_index, "setting-a", "Osric")
assert results == [{"doc": "d1", "offset": 10}]  # setting-b's posting never appears

# setting is required -- this raises TypeError:
# cf.find_noun(nouns_index, "Osric")
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_find -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered, for all five
functions, including the `TypeError` on omission and the missing-field exclusion.
