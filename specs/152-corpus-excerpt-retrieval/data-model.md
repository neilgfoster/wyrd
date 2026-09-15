# Phase 1 Data Model: Corpus excerpt retrieval

No new persisted entity or index schema (spec.md's Key Entities section, and FR-007). This
feature reads two things that already exist and changes neither's shape:

## `documents.json` record (existing, `engine/wyrd/corpus_document.py`)

The fields this feature reads (all already present, confirmed by `build_document_record`):

| Field | Type | Used for |
|---|---|---|
| `id` | `str` | matching the `doc` id an excerpt request names |
| `path` | `str` | a `library/`-relative path; derives the corpus text file location |
| `setting` | `str` | scoping — never resolve a document outside the requested setting |

## Corpus text file (existing, a setting repo's own `corpus/` tree)

Plain UTF-8 text, one file per document, at `<setting_dir>/corpus/<path with suffix -> .txt>` —
the same layout `tools/setting_build.py`'s `corpus_text_path` and the `create-setting` skill's
Phase 0 (`corpus/extract.sh`) already produce and consume. This feature only reads from it.

## New function signature (`engine/wyrd/corpus_excerpt.py`)

```text
read_excerpt(
    documents_index: list[dict],
    setting: str,
    setting_dir: Path,
    doc: str,
    offset: int,
    window: int = 400,
) -> str | None
```

- `documents_index` / `setting` / `doc` / `offset` / `window`: as in spec.md's FR-001–FR-005.
- `setting_dir`: the filesystem root of the setting repository whose `corpus/` this call reads —
  an explicit parameter (this function is not itself setting-repo-aware the way a CLI entry point
  is; the caller, e.g. the new `find` verb, supplies it).
- Returns `None` for every failure mode in FR-004; otherwise a `str` of length `<= 2 * window`
  (less at document start/end, per the Edge Cases' `window=0` case producing a valid, possibly
  minimal result).

## CLI verb (`engine/wyrd/client.py`, new)

```text
wyrd find noun  --setting <setting> --name <name>
wyrd find rule  --setting <setting> --term <term>
wyrd find table --setting <setting> [--dice <d6|d10|d66|d100>] [--about <substring>]
```

Each returns the underlying `corpus_find.py` function's result list, with every entry that
carries a `doc`/`offset` extended with an `excerpt` field from `read_excerpt` (User Story 3,
FR-006). `find_scenario`/`find_doc` are out of this feature's CLI scope (bibliographic/thematic
results either carry no offset or need the scenarios index this feature does not touch) —
`corpus_find.py`'s own functions for those remain library-only for now, unchanged.
