# Data Model: Corpus retrieval is scoped to a setting, never unfiltered

## Function signatures (pure, no I/O) — `engine/wyrd/corpus_find.py`, revised

- `find_noun(nouns_index: dict, setting: str, name: str) -> list[dict]`
- `find_rule(terms_index: dict, setting: str, term: str) -> list[dict]`
- `find_table(tables_index: list[dict], setting: str, dice: str | None = None, about: str | None = None) -> list[dict]`
- `find_scenario(scenarios_index: list[dict], setting: str, **filters) -> list[dict]`
  (`setting_in` removed — `setting` now performs the same membership check unconditionally.)
- `find_doc(documents_index: list[dict], setting: str, work: str | None = None, issue: str | None = None) -> list[dict]`

Every function's first filtering step, before any other criterion: for postings/records with a
singular `setting` field, `== setting`; for scenario records with a `settings` list,
`setting in record.get("settings", [])`. A record/posting missing the relevant field never
matches (FR-004).
