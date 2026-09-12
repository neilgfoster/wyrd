# Phase 0 Research: Setting Build Command

## Decision: entry-point shape

**Decision**: A new `tools/setting_build.py`, importing `tools/setting_pass0.py` (already on
`sys.path` via the `tools/` directory itself, same pattern `tools/test_setting_pass0.py` uses) and
`engine.wyrd.corpus_pipeline`/`engine.wyrd.corpus_document` (already importable with
`PYTHONPATH=engine`, this repo's existing convention for every `engine/wyrd/*` test and tool).

**Rationale**: Issue #388 and CLAUDE.md's `tools/` convention both call for a script sibling to
`setting_pass0.py`, not a new package or a change to either existing module. Importing rather than
shelling out to `setting_pass0.py` as a subprocess keeps the run in a single process (one clear
report, one exit code) and avoids parsing the other script's stdout as an interface.

**Alternatives considered**:
- A subprocess-based wrapper (`subprocess.run(["python3", "tools/setting_pass0.py", ...])`) —
  rejected: fragile (parses text/JSON stdout as a contract that isn't documented as one), and
  makes propagating a `ValueError` from `build_setting_corpus_indexes` (FR-012) awkward across a
  process boundary for no benefit.
- Merging the corpus-index step directly into `setting_pass0.py` — rejected: #100 and #101 are
  closed, separately-specified, separately-tested pieces; issue #388 is explicit that this feature
  wires them together, not that it merges them.

## Decision: document-dict construction from a catalogue record

**Decision**: For each `present`-status catalogue record, read `library/<record.path>` as UTF-8
text (matching Pass 0's own `classify_document`, which already does exactly this read) and build:

```python
{
    "id": record.id,
    "path": record.path,
    "system": "unspecified",
    "edition": "unspecified",
    "document_type": record.kind,
    "page_count": 0,
    "extraction_method": "plain-text",
    "text": text,
    "setting": setting_name,
    "world_category": None,  # Pass 0's CatalogueRecord carries no such field today
}
```

`setting_name` is the setting directory's own basename (`setting_dir.name`) — stable across runs,
requires no new input, and matches how a `wyrd-setting-<name>` repo is already named.

**Rationale**: `build_setting_corpus_indexes` (#101) requires these fields but neither #100's
catalogue record nor this feature adds new extraction capability to derive them precisely (spec's
own Assumptions section already documents this default). `document_type` is filled from Pass 0's
own `kind` since that's the closest existing signal Pass 0 already computes; the rest are
placeholder defaults a setting repo's own tooling can override later without this feature blocking
on inventing a second classification scheme.

**Alternatives considered**:
- Leaving these fields as `None`/absent — rejected: `build_document_record` (in
  `corpus_document.py`) is not guaranteed to accept missing keys; using a `.get()` with defaults at
  the call site keeps the caller (this new module) responsible for satisfying the pipeline's own
  documented contract, rather than silently weakening it.
- Reading `world_category` from Pass 0's front matter directly here (bypassing the catalogue
  record) — rejected: Pass 0's `classify_document` does not currently surface `world_category` as
  a `CatalogueRecord` field; per FR-002 (reuse `setting_pass0.py` unmodified) this feature reads
  only what the existing `CatalogueRecord` already exposes, and `CatalogueRecord` has no
  `world_category` field today, so `world_category` is left unset (`None`) for every document.
  This is documented as a known simplification — no fixture exercises it distinctly from "not set"
  (a fixture with a `world_category` front-matter key simply has that key ignored) — and is a fair
  reading of "reuse unmodified" applied literally.

**Note on `id` uniqueness**: `record.id` is always `record.path`, and `Catalogue.records` is
already a `dict` keyed by path — so a genuine duplicate-`(setting, id)` collision can never arise
from this command's own document construction. `build_setting_corpus_indexes`'s duplicate check
(FR-012) is exercised in this feature's tests by directly injecting a failure (patching that
function), not via a naturally-occurring fixture — testing the propagation contract, not a
scenario this command can actually produce.
  — and is a fair reading of "reuse unmodified" applied literally.

## Decision: idempotence / staleness cache

**Decision**: A new `index/corpus_build_cache.json` in the setting directory, `{relative_path:
content_hash}` for every document last fed into `build_setting_corpus_indexes`. On each run:
compare the current Pass 0 catalogue's `present`-status records' `content_hash` values against
this cache; if the set of `(path, content_hash)` pairs is unchanged since the cache was written,
skip the corpus-index step entirely (no writes to `documents.json`/`nouns.json`/`terms.json`/
`tables.json`) and report every present document as skipped ("unchanged since last build"). If
anything changed (added, removed, or a hash changed), rebuild the full corpus-index set from
every present document (the pipeline's four builders are whole-document-set functions, not
per-document incremental ones — #101's own `build_setting_corpus_indexes` takes the whole
`documents` list each call) and rewrite the cache.

**Rationale**: FR-006 requires reusing Pass 0's own `content_hash` as the sole staleness signal —
this cache is exactly that, keyed the same way Pass 0's own catalogue already is. Rebuilding the
full set (rather than a per-document merge) when anything changes keeps this feature's own logic
trivially correct and matches how `build_setting_corpus_indexes` is actually shaped (whole-set in,
whole-set out) — attempting a partial merge would require re-deriving merge semantics for `nouns`
(concordance merging) and `terms` (posting-list merging) that #101 already owns internally via
`build_setting_corpus_indexes`, which this feature must not re-derive (FR-002).

**Alternatives considered**:
- Comparing output file mtimes instead of a hash cache — rejected: not content-based, and #100's
  own idempotence is explicitly content-hash-based (`docs/design/27-tooling.md`'s
  deterministic-over-inference rule) — mtimes would diverge from that on any checkout/clone that
  doesn't preserve mtimes (e.g. a `git clone`), which is exactly the environment a scheduled CI
  job (docs/design/26-corpus-index.md's "Scheduled execution") runs in.
- Hashing the four output JSON files themselves and comparing to a stored hash — rejected: this
  would still require rebuilding the indexes first to compute their hash, defeating "does no work"
  (FR-005's "no writes" requirement is trivially satisfiable by only writing on an actual content
  change, but "does no work" (spec SC-002) implies not even recomputing).

## Decision: reporting shape

**Decision**: Mirror `tools/setting_pass0.py`'s own `run()`/`main()` split and `--format
text|json` flag. The combined report carries Pass 0's own summary (`processed`, `removed`,
`gaps`, `conflicts`) plus a `corpus` sub-summary: `{"built": bool, "documents": N, "skipped_reason":
str | None}`.

**Rationale**: FR-008 explicitly asks this feature to mirror the existing flag; reusing the exact
field names Pass 0 already reports keeps this a strict addition rather than a divergent second
reporting convention (CLAUDE.md's "two documents describing one thing differently" fault applies
equally to two report shapes for sibling tools).

**Alternatives considered**: A wholly separate reporting schema — rejected for the reason above.
