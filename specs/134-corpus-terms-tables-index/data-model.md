# Data Model: Curated term and structural table indexes (terms.json, tables.json)

## Function signatures (pure, no I/O) — `engine/wyrd/corpus_terms.py`

- `CURATED_TERMS: frozenset[str]` — the fixed vocabulary (lowercase): `fear`, `terror`, `taint`,
  `transformation`, `critical`, `career exit`, `trauma`, `fate`.

- `build_terms_index(text: str, doc: str, setting: str) -> dict`
  Returns `{term: [{"doc": doc, "setting": setting, "offset": int, "rank": "definition" |
  "mention"}, ...]}` for every case-insensitive occurrence of a `CURATED_TERMS` entry in `text`
  (FR-001, FR-002, FR-003, FR-007). Keys are the canonical lowercase term.

- `build_tables_index(text: str, doc: str, setting: str) -> list[dict]`
  Returns one record per detected table run: `{"doc": doc, "setting": setting, "offset": int,
  "dice": "d6" | "d10" | "d66" | "d100" | None, "row_count": int, "caption": str | None}`
  (FR-004, FR-005, FR-006, FR-007). `offset` is the character position of the run's first row
  line.

## Example

```python
text = """Fear Tests

When a character faces something Fear-inducing, roll a Fear test.

Roll under normal circumstances only if you fear something entirely different -- a fear of
heights, say -- which the rules do not otherwise govern.

Roll Table
01-10  You freeze.
11-30  You flee.
31-70  You fight through it.
71-90  You act rashly.
91-100 You are unshaken.
"""

terms = build_terms_index(text, doc="core-rules", setting="my-setting")
# terms["fear"][0]["rank"] == "definition"  -- "Fear Tests" heading precedes it

tables = build_tables_index(text, doc="core-rules", setting="my-setting")
# tables[0]["dice"] == "d100"
# tables[0]["row_count"] == 5
# tables[0]["caption"] == "Roll Table"
```
