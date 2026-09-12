# CLI contract: `tools/setting_build.py`

A script, not a network API — its contract is its command-line surface and JSON output shape, in
`tools/setting_pass0.py`'s own style.

## Invocation

```bash
python3 tools/setting_build.py <setting-dir>
python3 tools/setting_build.py <setting-dir> --format json
```

`<setting-dir>` is a directory containing a `library/` subdirectory — the same precondition
`tools/setting_pass0.py` already enforces.

## Behavior

1. Run Pass 0's existing `run()` against `<setting-dir>` (catalogue build, gap report) —
   unchanged behavior from `tools/setting_pass0.py`.
2. Load the resulting catalogue's `present`-status records.
3. Load `<setting-dir>/index/corpus_build_cache.json` if present.
4. Compare the current present records' `(path, content_hash)` set against the cache's
   `documents` map:
   - **Unchanged** (same setting name, same set): skip the corpus-index step entirely — no reads
     of `library/` file text, no writes to any corpus index file.
   - **Changed** (added, removed, or a hash differs) or **no cache yet**: read each present
     record's file text, build the corpus-pipeline document list, call
     `corpus_pipeline.build_setting_corpus_indexes`, and write `index/documents.json`,
     `index/nouns.json`, `index/terms.json`, `index/tables.json`, then rewrite
     `index/corpus_build_cache.json`.
5. Print a summary combining Pass 0's own report with the corpus-index step's outcome (built or
   skipped, and why).

The scenarios/arcs (fifth) index is never built by this command (FR-009).

## Exit codes

- `0`: ran successfully — a non-empty gap report, or a fully skipped corpus-index step, is not a
  failure.
- `1`: `<setting-dir>` does not exist, or has no `library/` subdirectory (same as
  `tools/setting_pass0.py`).
- `1`: `corpus_pipeline.build_setting_corpus_indexes` raised — in practice a duplicate
  `(setting, id)` across present catalogue records, since this command always passes
  `world_category=None` and so never triggers that function's own invalid-`world_category` check
  — the error's message is printed to stderr; no corpus index file is written or left partially
  updated for that run (FR-012).

## Output shapes

`index/documents.json`, `index/nouns.json`, `index/terms.json`, `index/tables.json`: unchanged
from `build_setting_corpus_indexes`'s own existing return-value shapes (#101) — this contract adds
no new field to any of them.

`index/corpus_build_cache.json`: see [data-model.md](../data-model.md).

`--format json` on stdout:

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

Text format (default) prints a one-line Pass-0-style summary followed by a one-line corpus-index
summary, e.g.:

```text
Pass 0: 1 processed, 0 removed, 3 gaps, 0 conflicts.
Corpus indexes: built (5 documents).
```

or, on a no-op second run:

```text
Pass 0: 0 processed, 0 removed, 3 gaps, 0 conflicts.
Corpus indexes: skipped -- no catalogue or corpus-index changes since the last build.
```
