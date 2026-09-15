# Contract: `wyrd find` CLI verb

Extends `engine/wyrd/client.py`'s existing `describe`/`roll`/etc. verb dispatch (see `main()`)
with a new `find` verb, following the same `argparse` subcommand pattern already used throughout
that module.

## Sub-shapes

### `wyrd find noun --setting <setting> --name <name>`

Calls `corpus_find.find_noun(nouns_index, setting, name)`, then for each `{"doc", "offset"}`
result, resolves `excerpt` via `corpus_excerpt.read_excerpt`.

**Output** (JSON, matching this module's existing `_run_*` -> dict convention):

```json
{
  "results": [
    {"doc": "doc-a", "offset": 120, "excerpt": "... surrounding text ..."}
  ]
}
```

### `wyrd find rule --setting <setting> --term <term>`

Same shape, over `corpus_find.find_rule`.

### `wyrd find table --setting <setting> [--dice <dice>] [--about <substring>]`

Calls `corpus_find.find_table`. A table record's `offset` field (if present in that index's
schema) is resolved the same way; a table record with no offset returns no `excerpt` key rather
than `null` for a field that was never applicable.

## Error behavior

- An unknown `--setting` (no documents at all for it) returns `{"results": []}`, never an error —
  matching every existing `corpus_find.py` function's "empty index/no match -> `[]`" contract.
- A result whose excerpt cannot be resolved (missing corpus file, offset past end, etc.) still
  appears in `results`, with `"excerpt": null` — the coordinate lookup and the excerpt resolution
  are independent; one failing does not suppress the other (User Story 3, Acceptance Scenario 2).

## Not in this contract

`wyrd find scenario` and `wyrd find doc` are unchanged, library-only entry points via
`corpus_find.py` directly — out of this feature's CLI scope (data-model.md).
