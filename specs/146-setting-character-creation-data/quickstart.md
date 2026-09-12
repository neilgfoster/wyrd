# Quickstart: Setting-Level Character Creation Data

## Prerequisites

- Python 3.11+ (already the repo's target).
- No installation step — the validator is stdlib-only, matching every other `tools/check_*.py`.

## Validate a setting's character-creation surface

```bash
python3 tools/check_character_creation_data.py <path-to-setting-dir>
```

Expects (or optionally finds) these files directly inside `<path-to-setting-dir>`:
`careers.yaml`, `loyalties.yaml`, `drives.yaml`, `misfortunes.yaml`, `names.yaml`, and optionally
`ancestries.yaml`.

**Expected outcome, correct setting**: exit code 0, one summary line per file
(`careers.yaml: OK (4 careers, 1 entry point)`, etc.), `ancestries.yaml: not present (optional)`
if absent.

**Expected outcome, broken setting**: non-zero exit code, one line per failure naming the file and
the exact problem (e.g. `loyalties.yaml: relation names undeclared Loyalty "the-old-faith"`),
every failure listed rather than stopping at the first.

## Run the tests

```bash
python3 -m pytest tools/test_check_character_creation_data.py -q
```

Each rejected-shape class from `data-model.md`'s Rules sections has its own fixture and its own
test, following `tools/test_check_setting.py`'s existing pattern.

## Full repo check (per CLAUDE.md)

```bash
python3 -m ruff check .
python3 -m ruff format --check .
python3 tools/check_docs.py
python3 -m pytest -q
```
