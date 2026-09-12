# Data Model: Generalise corpus extraction and indexing for any setting repo

## `PipelineDocument` (input, plain dict)

One entry in the list `build_setting_corpus_indexes` and the scenario-index functions take.

| Field | Type | Notes |
|---|---|---|
| `id` | `str` | Unique within `(setting, id)` — enforced by FR-002. |
| `path` | `str` | Passed straight through to `corpus_document.build_document_record`. |
| `system` | `str` | " |
| `edition` | `str` | " |
| `document_type` | `str` | " (`rules`/`setting`/`adventure`/`magazine`/`fanzine` per `docs/design/26-corpus-index.md`) |
| `page_count` | `int` | " |
| `extraction_method` | `str` | " |
| `text` | `str` | The already-extracted plain text; fed to every builder that needs it. |
| `setting` | `str` | Required on every document — FR-008; no record with no setting is ever produced. |
| `world_category` | `str \| None` | Optional. One of `WORLD_BUILDING_CATEGORIES` (`geography`, `factions`, `history`, `daily-life`) or `None`/absent for mechanical content (FR-003, FR-004). |

## `IndexBundle` (output of `build_setting_corpus_indexes`, plain dict)

```python
{
    "documents": [ ... ],   # corpus_document.build_document_record shape, one per input document
    "nouns": { ... },       # corpus_document.merge_concordances shape, mechanical + world-building
    "terms": { ... },       # corpus_terms.build_terms_index shape, mechanical documents only
    "tables": [ ... ],      # corpus_terms.build_tables_index shape, mechanical documents only
}
```

No new record shapes — every entry is exactly what #354/#355's existing builders already
produce for that document; this module only decides *which* builders run per document and
merges their output.

## `ScenarioCacheEntry` (plain dict, keyed by `(setting, doc id)`)

| Field | Type | Notes |
|---|---|---|
| `content_hash` | `str` | Caller-supplied (research.md: hashing is an extraction-step concern, not this module's). |
| `schema_version` | `int \| str` | Caller-supplied; compared for equality only, never ordered. |
| `record` | `dict` | The cached scenario/arcs record (#356's shape) — returned unchanged when fresh. |

## `ScenarioCache` (plain dict)

`{(setting, doc_id): ScenarioCacheEntry, ...}` — a plain dict keyed by a `(setting, doc_id)`
tuple, matching every other per-setting-scoped index's own scoping rule
(`docs/design/26-corpus-index.md`, "indexes are scoped to a setting").

## Function signatures

```python
WORLD_BUILDING_CATEGORIES: frozenset[str]  # {"geography", "factions", "history", "daily-life"}

def build_setting_corpus_indexes(documents: list[dict]) -> dict:
    """Returns an IndexBundle. Raises ValueError naming the id on a same-setting duplicate
    (FR-002) or an invalid world_category (FR-004)."""

def scenario_cache_status(
    doc_id: str, setting: str, content_hash: str, schema_version, cache: dict
) -> str:
    """Returns "fresh", "stale", or "missing" (FR-005)."""

def documents_needing_scenario_generation(
    documents: list[dict], cache: dict, schema_version
) -> list[dict]:
    """Filters `documents` (each carrying `id`, `setting`, `content_hash`) to those whose
    cache status against `schema_version` is not "fresh" (FR-005)."""

def build_scenario_index(
    documents: list[dict], cache: dict, generate, schema_version
) -> tuple[list[dict], dict]:
    """Returns (scenario_records, updated_cache). Calls `generate(document) -> dict` only for
    stale/missing documents (FR-006); reuses cached records unchanged for fresh ones. A
    generator exception for one document does not corrupt cache entries already computed for
    others in the same call (Edge Cases)."""
```

## Validation rules

- `build_setting_corpus_indexes` raises `ValueError` naming the offending `(setting, id)` pair on
  a same-setting duplicate (FR-002); a duplicate `id` across *different* settings is not an error
  (Edge Cases).
- `build_setting_corpus_indexes` raises `ValueError` naming the offending value when
  `world_category` is set but not in `WORLD_BUILDING_CATEGORIES` (FR-004).
- Every function requires `setting` on every document it touches — omitting it (or passing an
  empty string) is treated as any other invalid/missing required field, never silently defaulted
  (FR-008, matching `corpus_find.py`'s own "omitting it is a `TypeError`, not a silently-unscoped
  query" precedent for the *shape* of this enforcement, adapted here to a `ValueError` since these
  are construction functions rather than a query filter).
