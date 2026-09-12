# Quickstart: validating Pass 0

## Prerequisites

- Python 3.11+, no extra dependencies.
- A test fixture library tree, e.g. `tools/fixtures/pass0/basic/` (created as part of this
  feature) — never a real `wyrd-setting-*` repo.

## Run

```bash
python3 tools/setting_pass0.py tools/fixtures/pass0/basic
```

Expected: prints a one-line summary (files processed, gaps, conflicts) and writes
`tools/fixtures/pass0/basic/index/catalogue.json` and `.../index/gap_report.json`.

## Validate idempotence (User Story 3)

```bash
python3 tools/setting_pass0.py tools/fixtures/pass0/basic   # second run, no changes
```

Expected: summary reports zero files processed; `index/catalogue.json` is byte-for-byte
unchanged except `generated_at` staying at its prior value (no write occurs at all when nothing
changed).

## Validate the gap report (User Story 2)

```bash
python3 tools/setting_pass0.py tools/fixtures/pass0/empty
```

Expected: `index/gap_report.json` lists every setting-authoring requirement as a gap.

## Validate authority ordering and conflicts (User Stories 1 and 4)

Run against `tools/fixtures/pass0/conflicting/`, which contains one core-rules document and one
community document both tagged with the same `subject:`. Expected: `index/gap_report.json`'s
`conflicts` array names both documents; neither document's own `index/catalogue.json` record is
altered by the other's presence.

## Automated coverage

`python3 -m unittest tools/test_setting_pass0.py` (or `python3 -m pytest tools/test_setting_pass0.py`)
exercises every FR/SC in `spec.md` — the fixture trees above are used by the test module directly
via `tempfile`, not read from disk paths committed as `library/` content in the repo (the fixture
files under `tools/fixtures/pass0/` are themselves tiny, repo-authored stand-ins, never real
extracted source material).
