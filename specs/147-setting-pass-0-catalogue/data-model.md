# Phase 1 Data Model: Setting build pipeline — Pass 0

## `CatalogueRecord`

One per file under `library/`.

| Field | Type | Notes |
|---|---|---|
| `id` | str | stable id, derived from the relative path |
| `path` | str | path relative to `library/` |
| `kind` | str | closed vocabulary: `core-rules`, `expansion`, `community`, `scenario`, `unclassified` |
| `authority_tier` | int | 0=core-rules, 1=expansion, 2=community, 3=scenario, 4=unclassified — lower sorts first |
| `subject` | str \| null | optional topical signal used only for conflict detection |
| `content_hash` | str | sha256 hex digest of file bytes |
| `status` | str | `present`, `removed`, or `unreadable` |
| `provides` | list[str] | setting-authoring requirement ids this document/file evidences coverage for, if any (e.g. `voice`, `bestiary`) |

## `Catalogue`

| Field | Type | Notes |
|---|---|---|
| `records` | list[CatalogueRecord] | one per file ever seen |
| `generated_at` | str | ISO timestamp of the last run that changed anything |

## `ProcessingOrder`

Derived, not stored separately: `records` sorted by `(authority_tier, path)`. Exposed as a
function, `processing_order(catalogue) -> list[CatalogueRecord]`, not a persisted artefact of its
own — issue #100 asks for "an authority-ordered processing list," not a fourth file.

## `GapReportEntry`

| Field | Type | Notes |
|---|---|---|
| `requirement` | str | id from the docs/design/24-authoring-a-setting.md requirement table (e.g. `bestiary`) |
| `reason` | str | human-readable statement of what is missing |

## `ConflictRecord`

| Field | Type | Notes |
|---|---|---|
| `kind` | str | shared classified kind |
| `subject` | str | shared subject signal |
| `documents` | list[str] | the `id`s of the two (or more) conflicting `CatalogueRecord`s, across at least two distinct authority tiers |

## Relationships

- A `Catalogue` owns many `CatalogueRecord`s (1:N), keyed by `id`/`path`.
- A `GapReportEntry` references zero `CatalogueRecord`s directly — it is a statement about the
  *absence* of coverage, computed from the whole `Catalogue.records` set against the fixed
  setting-authoring requirement table.
- A `ConflictRecord` references two or more `CatalogueRecord`s by id, drawn from different
  `authority_tier` values, and never mutates either referenced record.

## State transitions (`CatalogueRecord.status`)

`present` (first seen, file readable) → `present` (unchanged, hash matches — no reclassification)
→ `present` (hash changed — reclassified) → `removed` (file no longer found). `unreadable` is
entered instead of `present` when the file exists but cannot be read, and can transition back to
`present` on a later run if the file becomes readable with an unchanged-or-different hash.
