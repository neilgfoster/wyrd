# Phase 1 Data Model: Setting Build Command

This feature introduces no new persistent entity beyond one small cache file; everything else is
read from or written by the two pieces it orchestrates (#100, #101).

## `index/corpus_build_cache.json` (NEW)

Tracks which content hash each present document's corpus-index contribution was last built from,
so a second run can determine "nothing changed" without recomputing the corpus indexes.

```json
{
  "generated_at": "2026-09-12T00:00:00Z",
  "setting": "setting",
  "documents": {
    "core/rulebook.md": "sha256:...",
    "expansions/monster-manual.md": "sha256:..."
  }
}
```

- `generated_at`: timestamp of the corpus-index build this cache reflects (unchanged if the build
  was skipped, matching Pass 0's own `generated_at` convention).
- `setting`: the setting name (`setting_dir.name`) the corpus indexes were built under — a
  mismatch (setting directory renamed/reused) forces a full rebuild rather than trusting a stale
  cache.
- `documents`: `path -> content_hash` for every `present`-status catalogue record that
  contributed to the last corpus-index build. Compared, as a whole set, against the current
  catalogue's present records each run.

## Corpus document dict (in-memory only, not persisted)

Constructed per `present`-status `CatalogueRecord`, consumed once per run by
`corpus_pipeline.build_setting_corpus_indexes` — see research.md's "document-dict construction"
decision for the exact field mapping. Not written to disk by this feature; the pipeline's own
`documents.json` output (an existing #101 shape) is what persists.

## Run report (in-memory / stdout only)

```json
{
  "processed": ["core/rulebook.md"],
  "removed": [],
  "gaps": 3,
  "conflicts": 0,
  "corpus": {
    "built": true,
    "documents": 5,
    "skipped_reason": null
  }
}
```

- `processed`/`removed`/`gaps`/`conflicts`: unchanged from `tools/setting_pass0.py`'s existing
  `run()` return shape (FR-008's mirroring requirement).
- `corpus.built`: whether the corpus-index step actually rebuilt `documents.json`/`nouns.json`/
  `terms.json`/`tables.json` this run.
- `corpus.documents`: count of present documents fed into (or, when skipped, that would have been
  fed into) the corpus pipeline.
- `corpus.skipped_reason`: `None` when built; otherwise a short string such as `"no catalogue or
  corpus-index changes since the last build"` (FR-007).

## Existing entities this feature reads/writes but does not define

- `CatalogueRecord` / `Catalogue` (`tools/setting_pass0.py`) — read after Pass 0's own step runs.
- `documents.json`, `nouns.json`, `terms.json`, `tables.json` — the four corpus index shapes
  `engine/wyrd/corpus_pipeline.py`/`corpus_document.py`/`corpus_terms.py` already define; this
  feature writes them (as new files under `index/`) using `build_setting_corpus_indexes`'s return
  value unchanged.
