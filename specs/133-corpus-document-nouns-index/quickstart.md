# Quickstart: Bibliographic and concordance indexes (documents.json, nouns.json)

## Prerequisites

- Python 3.11+, repo checked out, `PYTHONPATH=engine`.

## Try it

```python
from wyrd import corpus_document as cd

text = "The ledger-keeper vanished. Osric the Fair swore he saw Brannoc take it."

record = cd.build_document_record(
    id="wd-098", path="periodicals/wd98.txt", system="a periodical", edition="98",
    document_type="magazine", page_count=40, extraction_method="text_layer", text=text,
    setting="my-setting",
)
assert record["ocr_confidence"] > 0.8  # clean text

concordance = cd.build_concordance(text, doc="wd-098", setting="my-setting")
assert "Osric" in concordance
assert "Brannoc" in concordance
assert "The" not in concordance  # sentence-initial and stop-listed
```

## Run the tests

```bash
cd /root/source/neilgfoster/wyrd
PYTHONPATH=engine python3 -m unittest tests.engine.test_corpus_document -v
```

## Expected outcome

Every scenario in spec.md's User Scenarios & Testing section is covered by an explicit test in
`tests/engine/test_corpus_document.py`, including the OCR-confidence comparison and the
sentence-initial exclusion.
