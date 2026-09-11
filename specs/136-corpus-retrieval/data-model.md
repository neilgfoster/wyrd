# Data Model: Corpus index retrieval queries (wyrd find)

## Function signatures (pure, no I/O) — `engine/wyrd/corpus_find.py`

- `find_noun(nouns_index: dict[str, list[dict]], name: str) -> list[dict]`
  Flattens every posting's `offsets` list into one `{"doc": ..., "offset": ...}` entry each
  (FR-001). Returns `[]` for a name not in `nouns_index`, or an empty `nouns_index` (FR-006).

- `find_rule(terms_index: dict[str, list[dict]], term: str) -> list[dict]`
  Returns `terms_index.get(term.lower(), [])`'s postings (each already `{doc, setting, offset,
  rank}`), sorted so every `"definition"` entry precedes every `"mention"` entry, stable
  otherwise (FR-002).

- `find_table(tables_index: list[dict], dice: str | None = None, about: str | None = None) -> list[dict]`
  Filters `tables_index` by `dice` (exact match, when given) and `about` (case-insensitive
  substring of `caption`, when given; a `None` caption never matches a non-`None` `about`)
  (FR-003).

- `find_scenario(scenarios_index: list[dict], **filters) -> list[dict]`
  Filters `scenarios_index` by exact match on every key in `filters` that is present on a
  record (FR-004) — e.g. `find_scenario(index, scale="village", setting_in="my-setting")` is
  read as: every `filters` key except `setting_in` matches the record's own field by equality;
  `setting_in`, if given, checks membership in the record's `settings` list (reusing #356's
  `is_eligible_for_setting` semantics without importing it, per this module's own no-hard-
  dependency convention).

- `find_doc(documents_index: list[dict], work: str | None = None, issue: str | None = None) -> list[dict]`
  Filters `documents_index` by `work` (matched against `system`) and `issue` (matched against
  `edition`), returning `[{"doc": record["id"]} for record in matches]` (FR-005) — no offset,
  since a bibliographic record has no in-document position (Edge Cases).

## Example

```python
nouns_index = {"Osric": [{"doc": "d1", "setting": "s1", "count": 1, "offsets": [42]}]}
find_noun(nouns_index, "Osric")  # -> [{"doc": "d1", "offset": 42}]

terms_index = {
    "fear": [
        {"doc": "d1", "setting": "s1", "offset": 10, "rank": "mention"},
        {"doc": "d1", "setting": "s1", "offset": 3, "rank": "definition"},
    ]
}
find_rule(terms_index, "Fear")  # -> definition (offset 3) first, mention (offset 10) second
```
