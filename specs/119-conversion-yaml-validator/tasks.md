# Tasks: conversion.yaml schema validator

- [X] T001 Write `tools/check_conversion.py`: schema tables, `check_entry`/`check_file`, CLI
      (`<path>... [--format text|json]`), reusing `check_bestiary.read_yaml`/`YamlError`.
- [X] T002 Write `tests/test_check_conversion.py` covering: valid worked-example file passes;
      missing `from`/`version` rejected; unrecognised top-level field rejected; bad `damage_type`
      rejected; bad `skills.method`/`armour.method` rejected; non-integer/non-positive `version`
      rejected; not-a-list `drop`/`manual` rejected; malformed YAML rejected.
- [X] T003 Document `tools/check_conversion.py` in `docs/design/24-authoring-a-setting.md` next to
      the `check_bestiary.py`/`check_gear.py` references.
- [X] T004 Run `ruff check . && ruff format --check . && python3 -m pytest -q`; fix any findings.
