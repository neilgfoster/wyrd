# Quickstart: verifying the corpus/ read path

## Prerequisites

```bash
cd /path/to/wyrd
export PYTHONPATH=engine
```

## Run the automated tests

```bash
python3 -m pytest tools/test_setting_build.py tools/test_setting_pass0.py -q
```

Expect all tests green, including the new coverage this feature adds:
- an extracted-text-present case (a fixture whose `library/` and `corpus/` both have every present
  record's counterpart) builds indexes from `corpus/` text.
- a not-yet-extracted case (a fixture with one present record missing its `corpus/` counterpart)
  completes without raising, excludes that record from the built indexes, and reports its path in
  `not_yet_extracted`.

## Manual smoke test

```bash
python3 tools/setting_build.py tools/fixtures/setting_build/basic --format json
```

Expected: `corpus.built == true`, `corpus.not_yet_extracted == []` (the `basic` fixture's
`corpus/` tree mirrors every present record).

```bash
python3 tools/setting_build.py tools/fixtures/setting_build/partial_extraction --format json
```

Expected: exits `0`, `corpus.documents` counts only the extracted record,
`corpus.not_yet_extracted` names the un-extracted record's path — proving a present record with no
`corpus/` counterpart is reported cleanly rather than raising `UnicodeDecodeError`.

```bash
python3 tools/setting_build.py tools/fixtures/setting_build/basic --format json
```

Run a second time with nothing changed: expected `corpus.built == false`, confirming idempotence
still holds under the relocated (`corpus/`-hash-keyed) cache.

## Ruff

```bash
python3 -m ruff check tools/setting_build.py tools/test_setting_build.py
python3 -m ruff format --check tools/setting_build.py tools/test_setting_build.py
```
