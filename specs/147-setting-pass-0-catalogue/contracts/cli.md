# CLI contract: `tools/setting_pass0.py`

This is a script, not a network API — its contract is its command-line surface and JSON output
shapes, in `tools/check_settings_catalogue.py`'s style.

## Invocation

```bash
python3 tools/setting_pass0.py <setting-dir>
python3 tools/setting_pass0.py <setting-dir> --format json
```

`<setting-dir>` is a directory containing a `library/` subdirectory (and, for the gap report, a
`setting/` subdirectory in the shape docs/design/24-authoring-a-setting.md describes — its
absence is not an error, it just means every requirement is reported as a gap).

## Behavior

1. Enumerate every regular file under `<setting-dir>/library/`, recursively.
2. Load the existing catalogue from `<setting-dir>/index/catalogue.json` if present.
3. For each enumerated file: hash it; if unreadable, record `status: unreadable`; if the hash
   matches the existing record, leave that record untouched; otherwise (re)classify it into
   `kind`/`authority_tier`/`subject`/`provides` and write a new or updated record.
4. For each previously-recorded file no longer found on disk, set `status: removed` (record kept,
   not deleted).
5. Detect conflicts across the resulting record set (same `kind`+`subject`, different
   `authority_tier`).
6. Build the gap report by comparing the record set's `provides` union against the fixed
   setting-authoring requirement list.
7. Write `<setting-dir>/index/catalogue.json` and `<setting-dir>/index/gap_report.json`.
8. Print a summary: files processed this run (added/updated/removed), gap count, conflict count.

## Exit codes

- `0`: ran successfully (a non-empty gap report is not a failure — Pass 0 reports gaps, it does
  not enforce them).
- `1`: `<setting-dir>` does not exist, or has no `library/` subdirectory.

## Output shapes

`index/catalogue.json`:

```json
{
  "generated_at": "2026-09-12T00:00:00Z",
  "records": [
    {
      "id": "core/rulebook.pdf",
      "path": "core/rulebook.pdf",
      "kind": "core-rules",
      "authority_tier": 0,
      "subject": null,
      "content_hash": "sha256:...",
      "status": "present",
      "provides": ["bestiary"]
    }
  ]
}
```

`index/gap_report.json`:

```json
{
  "gaps": [
    {"requirement": "bestiary", "reason": "no catalogued document evidences bestiary coverage"}
  ],
  "conflicts": [
    {
      "kind": "core-rules",
      "subject": "fear-rules",
      "documents": ["core/rulebook.pdf", "community/house-fear-rules.md"]
    }
  ]
}
```

`--format json` on stdout emits `{"processed": [...], "removed": [...], "gaps": N, "conflicts": N}`
for the run just performed, in addition to writing the two files above.
