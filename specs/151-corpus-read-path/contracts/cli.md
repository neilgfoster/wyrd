# CLI contract: `tools/setting_build.py` (corpus read-path change)

Supersedes only the parts of specs/150-setting-build-command/contracts/cli.md that this feature
changes. Invocation, exit codes, and the four corpus-index file shapes are unchanged — restated
here only where they differ.

## Invocation

Unchanged:

```bash
python3 tools/setting_build.py <setting-dir>
python3 tools/setting_build.py <setting-dir> --format json
```

## Behavior (changed step)

Step 4 of the prior contract ("read each present record's file text ... from `library/`") becomes:

4. Compare the current present records' `(path, corpus-text-hash)` set against the cache's
   `documents` map, where a present record's corpus-text-hash is `pass0.hash_file` of
   `corpus/<record.path with its suffix changed to .txt>` **if that file exists**, and the record
   is simply absent from the comparison set otherwise:
   - **Unchanged**: skip the corpus-index step entirely, same as before.
   - **Changed** or **no cache yet**: for every present record whose `corpus/` counterpart exists,
     read that file's text (never `library/<record.path>`), build the corpus-pipeline document
     list from it, call `corpus_pipeline.build_setting_corpus_indexes`, and write the four index
     files then rewrite `index/corpus_build_cache.json` with the corpus-text hashes just used. A
     present record whose `corpus/` counterpart does **not** exist is skipped — never read, never
     included in the built indexes — and its path is collected into the report's
     `not_yet_extracted` list instead.

No exception is raised for a present record with no `corpus/` counterpart; this replaces the prior
implicit assumption that `library/<record.path>` was always UTF-8-decodable text.

## Exit codes

Unchanged from the prior contract — a nonempty `not_yet_extracted` list is not a failure; exit
code stays `0`.

## Output shapes

`index/documents.json`, `index/nouns.json`, `index/terms.json`, `index/tables.json`: unchanged.

`index/corpus_build_cache.json`: same shape, `documents`' values now the `corpus/` text file's
hash rather than the `library/` source's — see [data-model.md](../data-model.md).

`--format json` on stdout — the `corpus` sub-object gains one field:

```json
{
  "processed": ["core/rulebook.md"],
  "removed": [],
  "gaps": 3,
  "conflicts": 0,
  "corpus": {
    "built": true,
    "documents": 5,
    "skipped_reason": null,
    "not_yet_extracted": ["scenarios/the-drowning-well.md"]
  }
}
```

Text format (default) gains a third line naming the gap count when nonzero, appended after the
existing "Corpus indexes: built/skipped" line, e.g.:

```text
Pass 0: 1 processed, 0 removed, 3 gaps, 0 conflicts.
Corpus indexes: built (5 documents).
Not yet extracted: 1 document (scenarios/the-drowning-well.md).
```

The line is omitted entirely when `not_yet_extracted` is empty, so the existing two-line text
output (and the tests that assert its exact shape) is unchanged for every fixture that has no gap.
