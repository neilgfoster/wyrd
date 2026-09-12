# Quickstart: Setting Build Command

## Prerequisites

- Python 3.11+
- From the repo root, with `engine/` on `PYTHONPATH` for anything that imports `wyrd.*`:
  `export PYTHONPATH=engine`

## Run against a fixture setting

```bash
export PYTHONPATH=engine
cp -r tools/fixtures/setting_build/basic /tmp/setting-build-demo
python3 tools/setting_build.py /tmp/setting-build-demo
```

Expected: prints a Pass-0-style summary line, then a corpus-index summary line reporting the
indexes were built; `/tmp/setting-build-demo/index/` now contains `catalogue.json`,
`gap_report.json`, `documents.json`, `nouns.json`, `terms.json`, `tables.json`, and
`corpus_build_cache.json`.

## Verify idempotence (the feature's own defining property)

```bash
python3 tools/setting_build.py /tmp/setting-build-demo
```

Run again with nothing changed. Expected: the Pass 0 line reports `0 processed, 0 removed`; the
corpus-index line reports `skipped -- no catalogue or corpus-index changes since the last build`;
no file under `index/` changes (diff the directory against its state after the first run — every
file is byte-identical).

## Machine-readable form

```bash
python3 tools/setting_build.py /tmp/setting-build-demo --format json
```

Expected: a single JSON object on stdout with `processed`, `removed`, `gaps`, `conflicts`, and a
`corpus` object (`built`, `documents`, `skipped_reason`) — see
[contracts/cli.md](./contracts/cli.md).

## Run the feature's own tests

```bash
export PYTHONPATH=engine
python3 -m pytest tools/test_setting_build.py -q
```

Expected: all pass, including a test that runs the command twice against a copied fixture and
asserts the second run's report shows nothing processed and every `index/` file byte-identical to
after the first run.
