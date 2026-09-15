# Phase 1 Data Model: Corpus-build reads extracted text from corpus/, not library/

No new persistent entity is introduced. This feature changes the meaning of one existing cache
field and adds one new field to one existing report shape.

## CorpusBuildCache (existing, `tools/setting_build.py`)

Unchanged shape:

```python
@dataclass
class CorpusBuildCache:
    generated_at: str
    setting: str
    documents: dict[str, str]  # path -> hash
```

**Changed meaning only**: `documents`' values were the corresponding `CatalogueRecord.content_hash`
(a hash of the `library/` source file). They become the hash of that record's `corpus/` text file
(`pass0.hash_file(corpus_file)`), computed and compared the same way. The field name, type, and
storage location (`index/corpus_build_cache.json`) are unchanged.

## Corpus report sub-object (existing, returned by `run_corpus_step`)

Before:

```python
{"built": bool, "documents": int, "skipped_reason": str | None}
```

After — one field added:

```python
{
    "built": bool,
    "documents": int,               # count of records actually built into the indexes this run
    "skipped_reason": str | None,
    "not_yet_extracted": list[str], # present records' paths with no corpus/ counterpart, sorted
}
```

`not_yet_extracted` is populated on every call (both the built and skipped branches), since a gap
is worth reporting regardless of whether a rebuild happened this run.

## CatalogueRecord (existing, `tools/setting_pass0.py`)

Unchanged — no new field. `record.path` continues to be the relative `library/` path this feature
maps to its `corpus/` counterpart via `Path(record.path).with_suffix(".txt")`.

## New helper: corpus text path mapping

Not a data entity, but the one new pure function this feature introduces:

```python
def corpus_text_path(setting_dir: Path, record_path: str) -> Path:
    """The corpus/ file a present catalogue record's extracted text would live at."""
    return setting_dir / "corpus" / Path(record_path).with_suffix(".txt")
```

Deterministic, no I/O of its own — callers check `.is_file()` and `.read_text()`/`hash_file()` as
needed.
