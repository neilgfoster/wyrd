# Phase 1 Data Model

## `settings.yaml` (repository root, existing file, rewritten)

```yaml
settings:
  - id: wfrp-1e
    title: "Warhammer Fantasy Roleplay, 1st edition"
    repo: wyrd-setting-wfrp-1e
    visibility: private
    status: library-loaded
    group: null          # omitted in the file when absent; present here to show the field
```

| Field | Type | Meaning |
|---|---|---|
| `id` | string | catalogue identifier, independent of the repo name |
| `title` | string | human-readable setting name (this file, unlike `design/`, may name real systems) |
| `repo` | string | the exact live repository name |
| `visibility` | `private` \| `public` | matches the repo's actual GitHub visibility |
| `status` | `stub` \| `library-loaded` \| `indexed` \| `playable` | real, currently-observed progress |
| `group` | string, optional | shared-world identifier (`wh40k`, `maelstrom`); omitted when the setting stands alone |

**Validation rules**: `repo` must match a live `wyrd-setting-*` repository (checked by the drift
check, not enforced at parse time — a temporarily-dangling entry is a reported drift, not a
parse error). `status` must be one of the four closed values. `visibility` must match the
repo's actual GitHub visibility.

## Drift report (`check_settings_catalogue.py`'s output shape)

```json
{
  "missing_from_catalogue": ["wyrd-setting-darkfuture"],
  "dangling_catalogue_entries": [{"id": "old-id", "repo": "wyrd-old-name"}],
  "clean": false
}
```

- `missing_from_catalogue`: live `wyrd-setting-*` repo names with no matching `settings.yaml`
  entry.
- `dangling_catalogue_entries`: catalogue entries whose `repo:` matches no live repository.
- `clean`: `true` only when both lists are empty; drives the script's exit code.
