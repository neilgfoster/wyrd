# Contract: `find-noun`/`find-rule`/`find-table` CLI verbs

Extends `engine/wyrd/catalog.py`'s `TOOLS` and `engine/wyrd/client.py`'s dispatch (built from
that catalog, per `docs/design/27-tooling.md` section 3) with three new flat verbs — matching
this repo's existing one-verb-per-catalog-entry convention (no nested subcommands under a single
`find` verb; every other verb in `client.py` is flat, e.g. `spend-advance`, `spend-coin`).

## `wyrd find-noun --setting <setting> --name <name> [--setting-dir <path>]`

Calls `corpus_find.find_noun(nouns_index, setting, name)`, then for each `{"doc", "offset"}`
result, resolves `excerpt` via `corpus_excerpt.read_excerpt`. `--setting-dir` defaults to `.`
(the setting repository is expected to be the current working directory, or named explicitly).

**Output** (JSON, matching this module's existing `_run_*` -> dict convention):

```json
{
  "verb": "find-noun",
  "results": [
    {"doc": "doc-a", "offset": 120, "excerpt": "... surrounding text ..."}
  ]
}
```

## `wyrd find-rule --setting <setting> --term <term> [--setting-dir <path>]`

Same shape, over `corpus_find.find_rule`, verb name `"find-rule"`.

## `wyrd find-table --setting <setting> [--dice <d6|d10|d66|d100>] [--about <substring>] [--setting-dir <path>]`

Calls `corpus_find.find_table`, verb name `"find-table"`. A table record's `offset` field is
resolved the same way as noun/rule results.

## Error behavior

- An unknown `--setting` (no documents at all for it) returns `{"verb": "...", "results": []}`,
  never an error — matching every existing `corpus_find.py` function's "empty index/no match ->
  `[]`" contract.
- A result whose excerpt cannot be resolved (missing corpus file, offset past end, etc.) still
  appears in `results`, with `"excerpt": null` — the coordinate lookup and the excerpt resolution
  are independent; one failing does not suppress the other (User Story 3, Acceptance Scenario 2).
- Loading `index/*.json` from `--setting-dir`: a missing `nouns.json`/`terms.json` is treated as
  an empty index (`{}`); a missing `tables.json`/`documents.json` is treated as an empty list
  (`[]`) — the verb reports zero results rather than raising for a setting with no built index.

## Not in this contract

`find_scenario`/`find_doc` remain library-only entry points via `corpus_find.py` directly — out
of this feature's CLI scope (data-model.md): bibliographic results carry no offset, and thematic
scenario results need the `scenarios` index this feature does not touch.
