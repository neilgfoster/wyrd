"""Corpus extraction/indexing orchestration: generalising the pipeline for any setting repo (#101).

`docs/design/26-corpus-index.md` describes five indexes; #354/#355 (`corpus_document.py`,
`corpus_terms.py`) already built four of them as pure, per-document, no-I/O functions -- each one
already takes `setting` as an explicit argument and never hard-codes anything about a specific
setting. What was still missing is the layer that actually **runs those functions together across
a whole document set** -- the thing issue #101 calls "a pipeline any `wyrd-setting-*` repo can run
against its own `library/`." This module is that orchestration layer.

Like every sibling module in this epic, this is deliberately a **pure, no-I/O** slice: a setting
repo's own tooling extracts its `library/` into plain text (unchanged, existing concern -- PDF/OCR
extraction never belongs in this repo, CLAUDE.md), reads each document's text, calls the functions
here, and writes the returned indexes to its own `index/` directory -- the same "engine supplies
pure logic, a setting-scoped script does the I/O" split `check_bestiary.py`/`check_gear.py`
already use for setting data.

Two things this module deliberately does NOT do, both by design (specs/148-generalise-corpus-
extraction/research.md):

- It never hashes document text itself. A document's content hash is always caller-supplied --
  hashing strategy is an extraction-step concern (#97's own "full-path hashing" fix), not this
  module's.
- It never calls a model itself. The scenario/arcs (fifth) index's thematic generation is
  "Haiku-tier" per `docs/design/27-tooling.md` -- the actual call is always an injected callable,
  so this module's own behaviour stays fully deterministic and testable without any live call.

Python 3.11+, standard library only.
"""

from __future__ import annotations

from wyrd import corpus_document, corpus_terms

WORLD_BUILDING_CATEGORIES = frozenset({"geography", "factions", "history", "daily-life"})


def build_setting_corpus_indexes(documents: list[dict]) -> dict:
    """Orchestrate #354/#355's per-document builders across `documents`, returning
    `{"documents": [...], "nouns": {...}, "terms": {...}, "tables": [...]}` (FR-001).

    Raises `ValueError` naming the offending `(setting, id)` pair when two documents share both
    (FR-002) -- a duplicate `id` across *different* settings is not an error, since id uniqueness
    is scoped per setting like every other corpus record.

    A document carrying an optional `world_category` (one of `WORLD_BUILDING_CATEGORIES`)
    contributes to `documents`/`nouns` exactly as any other document does, but contributes no
    postings to `terms`/`tables` (FR-003) -- mechanical-vocabulary/table-shape detection has
    nothing to find in prose world-building material, and running it anyway risks false
    positives. Raises `ValueError` naming the offending value when `world_category` is set but
    not in the closed vocabulary (FR-004).
    """
    seen_ids: set[tuple[str, str]] = set()
    document_records = []
    concordances = []
    terms_index: dict[str, list[dict]] = {}
    tables_index: list[dict] = []

    for doc in documents:
        key = (doc["setting"], doc["id"])
        if key in seen_ids:
            raise ValueError(
                f"duplicate document id {doc['id']!r} within setting {doc['setting']!r}"
            )
        seen_ids.add(key)

        world_category = doc.get("world_category")
        if world_category is not None and world_category not in WORLD_BUILDING_CATEGORIES:
            raise ValueError(
                f"world_category {world_category!r} is not one of "
                f"{sorted(WORLD_BUILDING_CATEGORIES)}"
            )

        document_records.append(
            corpus_document.build_document_record(
                id=doc["id"],
                path=doc["path"],
                system=doc["system"],
                edition=doc["edition"],
                document_type=doc["document_type"],
                page_count=doc["page_count"],
                extraction_method=doc["extraction_method"],
                text=doc["text"],
                setting=doc["setting"],
            )
        )
        concordances.append(
            corpus_document.build_concordance(doc["text"], doc=doc["id"], setting=doc["setting"])
        )

        if world_category is None:
            for term, postings in corpus_terms.build_terms_index(
                doc["text"], doc=doc["id"], setting=doc["setting"]
            ).items():
                terms_index.setdefault(term, []).extend(postings)
            tables_index.extend(
                corpus_terms.build_tables_index(doc["text"], doc=doc["id"], setting=doc["setting"])
            )

    return {
        "documents": document_records,
        "nouns": corpus_document.merge_concordances(concordances),
        "terms": terms_index,
        "tables": tables_index,
    }


def scenario_cache_status(
    doc_id: str, setting: str, content_hash: str, schema_version, cache: dict
) -> str:
    """`"missing"` when `(setting, doc_id)` has no cache entry, `"stale"` when the entry's
    `content_hash` or `schema_version` differs from the values given, `"fresh"` otherwise
    (FR-005)."""
    entry = cache.get((setting, doc_id))
    if entry is None:
        return "missing"
    if entry["content_hash"] != content_hash or entry["schema_version"] != schema_version:
        return "stale"
    return "fresh"


def documents_needing_scenario_generation(
    documents: list[dict], cache: dict, schema_version
) -> list[dict]:
    """Filter `documents` (each carrying `id`, `setting`, `content_hash`) to those whose
    `scenario_cache_status` against `schema_version` is not `"fresh"` (FR-005)."""
    return [
        doc
        for doc in documents
        if scenario_cache_status(
            doc["id"], doc["setting"], doc["content_hash"], schema_version, cache
        )
        != "fresh"
    ]


def build_scenario_index(
    documents: list[dict], cache: dict, generate, schema_version
) -> tuple[list[dict], dict]:
    """Build the scenario/arcs index lazily: `generate(document)` is called only for documents
    whose cache status is stale or missing (FR-006); a fresh document's cached `record` is reused
    unchanged. Returns `(scenario_records, updated_cache)` -- `cache` itself is never mutated.

    If `generate` raises for one document, every entry already computed earlier in this same call
    (both freshly generated and reused-fresh) is preserved in the propagated exception's
    `partial_cache`/`partial_records` attributes rather than lost, though the exception itself
    still propagates to the caller (Edge Cases: one document's generation failure must not corrupt
    the others' already-computed results)."""
    updated_cache = dict(cache)
    records = []
    stale_or_missing = {
        (doc["setting"], doc["id"])
        for doc in documents_needing_scenario_generation(documents, cache, schema_version)
    }

    for doc in documents:
        key = (doc["setting"], doc["id"])
        if key in stale_or_missing:
            try:
                record = generate(doc)
            except Exception as exc:
                exc.partial_cache = updated_cache
                exc.partial_records = records
                raise
            updated_cache[key] = {
                "content_hash": doc["content_hash"],
                "schema_version": schema_version,
                "record": record,
            }
        else:
            record = updated_cache[key]["record"]
        records.append(record)

    return records, updated_cache
