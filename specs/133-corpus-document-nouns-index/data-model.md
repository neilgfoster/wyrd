# Data Model: Bibliographic and concordance indexes (documents.json, nouns.json)

## Function signatures (pure, no I/O) — `engine/wyrd/corpus_document.py`

- `ocr_confidence(text: str) -> float`
  The fraction of whitespace-split tokens in `text` matching a "plausible word" shape
  (research.md), in `[0.0, 1.0]`. `0.0` for empty text (no tokens to be confident about).

- `build_document_record(*, id: str, path: str, system: str, edition: str, document_type: str, page_count: int, extraction_method: str, text: str, setting: str) -> dict`
  Returns `{id, path, system, edition, document_type, page_count, extraction_method,
  ocr_confidence: ocr_confidence(text), setting}` (FR-001, FR-002, FR-006).

- `build_concordance(text: str, doc: str, setting: str) -> dict`
  Returns `{name: [{"doc": doc, "setting": setting, "count": int, "offsets": [int, ...]}]}` for
  every capitalised, non-sentence-initial, non-stop-listed token in `text` (FR-003, FR-004,
  FR-005, FR-006). Offsets are character positions of each occurrence in `text`.

- `merge_concordances(entries: list[dict]) -> dict`
  Merges multiple single-document `build_concordance` outputs into one combined concordance,
  keeping each document's own postings list separate under the same name key (FR-003, SC-003) --
  never summing counts across documents into one entry.

## Example

```python
text = "The ledger-keeper vanished. Osric the Fair swore he saw Brannoc take it."
record = build_document_record(
    id="wd-098", path="periodicals/wd98.txt", system="a periodical", edition="98",
    document_type="magazine", page_count=40, extraction_method="text_layer", text=text,
    setting="my-setting",
)
# record["ocr_confidence"] close to 1.0 -- clean, well-formed text

concordance = build_concordance(text, doc="wd-098", setting="my-setting")
# "Osric" and "Brannoc" are recorded (mid-sentence capitalised)
# "The" is NOT recorded (sentence-initial, and stop-listed either way)
# "Fair" IS recorded (mid-sentence, capitalised, not stop-listed)
```
